"""手写神经网络（只依赖 numpy）：BPNN 与 CNN，含反向传播与数值梯度检查。

BPNN: 49 维特征 -> 隐层(tanh) -> 6 类 softmax
CNN : 32x32 log-Mel 谱图 -> 3x3 卷积 -> ReLU -> 2x2 最大池化 -> 全连接 -> softmax
两者都用交叉熵 + Adam，反向传播逐项推导，不调用任何框架。
"""
from __future__ import annotations
import os
import csv
import time
import numpy as np
from . import dsp, plot, wav


def softmax(z):
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def onehot(y, k):
    Y = np.zeros((len(y), k))
    Y[np.arange(len(y)), y] = 1.0
    return Y


def cross_entropy(p, Y):
    return -np.mean(np.sum(Y * np.log(p + 1e-12), axis=1))


def stratified_split(y, ratios=(0.6, 0.2, 0.2), seed=11):
    rng = np.random.default_rng(seed)
    tr, va, te = [], [], []
    for c in np.unique(y):
        idx = np.where(y == c)[0]
        rng.shuffle(idx)
        a = int(len(idx) * ratios[0])
        b = int(len(idx) * (ratios[0] + ratios[1]))
        tr += idx[:a].tolist()
        va += idx[a:b].tolist()
        te += idx[b:].tolist()
    return np.array(tr), np.array(va), np.array(te)


def confusion(y, pred, k):
    M = np.zeros((k, k), int)
    for a, b in zip(y, pred):
        M[a, b] += 1
    return M


def f1_scores(y, pred, k):
    out = []
    for c in range(k):
        tp = np.sum((y == c) & (pred == c))
        fp = np.sum((y != c) & (pred == c))
        fn = np.sum((y == c) & (pred != c))
        p = tp / (tp + fp + 1e-12)
        r = tp / (tp + fn + 1e-12)
        out.append(2 * p * r / (p + r + 1e-12))
    return np.asarray(out)


def roc(y_binary, score):
    order = np.argsort(-score)
    y = np.asarray(y_binary)[order]
    tp = np.cumsum(y == 1)
    fp = np.cumsum(y == 0)
    tpr = np.r_[0, tp / (tp[-1] + 1e-12)]
    fpr = np.r_[0, fp / (fp[-1] + 1e-12)]
    tpr = np.r_[tpr, 1.0]
    fpr = np.r_[fpr, 1.0]
    auc = float(np.trapezoid(tpr, fpr))
    return fpr, tpr, auc


# ------------------------------------------------------------------ BPNN

class BPNN:
    """误差反向传播网络：z1=XW1+b1, a1=tanh(z1), z2=a1W2+b2, p=softmax(z2)。"""

    def __init__(self, n_in, n_hidden=48, n_out=6, seed=3):
        rng = np.random.default_rng(seed)
        self.W1 = rng.normal(0, np.sqrt(2.0 / (n_in + n_hidden)), (n_in, n_hidden))
        self.b1 = np.zeros(n_hidden)
        self.W2 = rng.normal(0, np.sqrt(2.0 / (n_hidden + n_out)), (n_hidden, n_out))
        self.b2 = np.zeros(n_out)

    def params(self):
        return [self.W1, self.b1, self.W2, self.b2]

    def forward(self, X):
        z1 = X @ self.W1 + self.b1
        a1 = np.tanh(z1)
        z2 = a1 @ self.W2 + self.b2
        return softmax(z2), (X, a1)

    def loss_grad(self, X, Y):
        p, (Xc, a1) = self.forward(X)
        loss = cross_entropy(p, Y)
        dZ2 = (p - Y) / len(X)
        dW2 = a1.T @ dZ2
        db2 = dZ2.sum(axis=0)
        dA1 = dZ2 @ self.W2.T
        dZ1 = dA1 * (1 - a1 ** 2)
        dW1 = Xc.T @ dZ1
        db1 = dZ1.sum(axis=0)
        return loss, [dW1, db1, dW2, db2]

    def predict_proba(self, X):
        return self.forward(X)[0]


# ------------------------------------------------------------------ CNN

def im2col(X, kh, kw, pad=1):
    N, C, H, W = X.shape
    Xp = np.pad(X, ((0, 0), (0, 0), (pad, pad), (pad, pad)))
    oh, ow = H + 2 * pad - kh + 1, W + 2 * pad - kw + 1
    i0 = np.repeat(np.arange(kh), kw)
    j0 = np.tile(np.arange(kw), kh)
    i1 = np.repeat(np.arange(oh), ow)
    j1 = np.tile(np.arange(ow), oh)
    i = i0[:, None] + i1[None, :]
    j = j0[:, None] + j1[None, :]
    cols = Xp[:, :, i, j].transpose(0, 3, 1, 2).reshape(N * oh * ow, -1)
    return cols, (X.shape, Xp, i, j, oh, ow, pad)


def col2im(dcol, cache):
    (N, C, H, W), Xp, i, j, oh, ow, pad = cache
    K = i.shape[0]
    d = dcol.reshape(N, oh * ow, C, K).transpose(0, 2, 3, 1)
    dxp = np.zeros_like(Xp)
    for a in range(K):
        ii = i[a].reshape(oh, ow)
        jj = j[a].reshape(oh, ow)
        np.add.at(dxp, (slice(None), slice(None), ii, jj), d[:, :, a, :].reshape(N, C, oh, ow))
    return dxp[:, :, pad:pad + H, pad:pad + W] if pad else dxp


def maxpool(X, p=2):
    N, C, H, W = X.shape
    oh, ow = H // p, W // p
    Xr = X.reshape(N, C, oh, p, ow, p)
    out = Xr.max(axis=(3, 5))
    mask = (Xr == out[:, :, :, None, :, None])
    return out, (Xr, mask, X.shape)


def maxpool_back(dout, cache):
    Xr, mask, shape = cache
    cnt = mask.sum(axis=(3, 5), keepdims=True)
    dXr = dout[:, :, :, None, :, None] * mask / (cnt + 1e-12)
    return dXr.reshape(shape)


class CNN:
    def __init__(self, n_class=6, n_filter=4, size=32, seed=5):
        rng = np.random.default_rng(seed)
        self.Wc = rng.normal(0, np.sqrt(2.0 / 9), (n_filter, 1, 3, 3))
        self.bc = np.zeros(n_filter)
        flat = n_filter * (size // 2) ** 2
        self.Wf = rng.normal(0, np.sqrt(2.0 / (flat + n_class)), (flat, n_class))
        self.bf = np.zeros(n_class)
        self.size = size

    def params(self):
        return [self.Wc, self.bc, self.Wf, self.bf]

    def forward(self, X):
        cols, cache = im2col(X, 3, 3, 1)
        oh, ow = cache[4], cache[5]
        conv = (cols @ self.Wc.reshape(len(self.Wc), -1).T + self.bc).reshape(
            len(X), oh, ow, len(self.Wc)).transpose(0, 3, 1, 2)
        relu = np.maximum(conv, 0)
        pool, pcache = maxpool(relu, 2)
        flat = pool.reshape(len(X), -1)
        z = flat @ self.Wf + self.bf
        return softmax(z), (cols, cache, conv, relu, pool, pcache, flat)

    def loss_grad(self, X, Y):
        p, (cols, cache, conv, relu, pool, pcache, flat) = self.forward(X)
        loss = cross_entropy(p, Y)
        dZ = (p - Y) / len(X)
        dWf = flat.T @ dZ
        dbf = dZ.sum(axis=0)
        dflat = dZ @ self.Wf.T
        dpool = dflat.reshape(pool.shape)
        drelu = maxpool_back(dpool, pcache)
        dconv = drelu * (conv > 0)
        F = len(self.Wc)
        dout = dconv.transpose(0, 2, 3, 1).reshape(-1, F)
        dWc = (dout.T @ cols).reshape(self.Wc.shape)
        dbc = dout.sum(axis=0)
        dcols = dout @ self.Wc.reshape(F, -1)
        dX = col2im(dcols, cache)
        return loss, [dWc, dbc, dWf, dbf]

    def predict_proba(self, X):
        return self.forward(X)[0]


# ------------------------------------------------------------------ 训练

def _adam(params, grads, state, t, lr):
    if not state:
        for p in params:
            state.append([np.zeros_like(p), np.zeros_like(p)])
    b1, b2, eps = 0.9, 0.999, 1e-8
    for i, (p, g) in enumerate(zip(params, grads)):
        m, v = state[i]
        m *= b1
        m += (1 - b1) * g
        v *= b2
        v += (1 - b2) * (g * g)
        mh = m / (1 - b1 ** t)
        vh = v / (1 - b2 ** t)
        p -= lr * mh / (np.sqrt(vh) + eps)


def train(model, X, y, Xv, yv, epochs=60, lr=3e-3, batch=16, verbose=False, tag=""):
    k = int(max(np.max(y), np.max(yv))) + 1
    Ytr = onehot(y, k)
    Yv = onehot(yv, k)
    state = []
    rng = np.random.default_rng(17)
    hist = {"loss": [], "val_loss": [], "acc": [], "val_acc": []}
    t = 0
    t0 = time.perf_counter()
    for ep in range(epochs):
        order = rng.permutation(len(X))
        for s in range(0, len(order), batch):
            idx = order[s:s + batch]
            t += 1
            loss, grads = model.loss_grad(X[idx], Ytr[idx])
            _adam(model.params(), grads, state, t, lr)
        p = model.predict_proba(X)
        pv = model.predict_proba(Xv)
        hist["loss"].append(cross_entropy(p, Ytr))
        hist["val_loss"].append(cross_entropy(pv, Yv))
        hist["acc"].append(float(np.mean(p.argmax(1) == y)))
        hist["val_acc"].append(float(np.mean(pv.argmax(1) == yv)))
        if verbose and ((ep + 1) % 10 == 0 or ep == 0):
            print(f"  {tag} epoch {ep + 1:3d}/{epochs}  loss={hist['loss'][-1]:.4f}  "
                  f"val_acc={hist['val_acc'][-1]:.3f}", flush=True)
    hist["seconds"] = time.perf_counter() - t0
    return hist


def grad_check(model, X, Y, n_probe=8, eps=1e-5, seed=0):
    """数值梯度 vs 解析梯度：返回最大相对误差，验证反向传播正确性。"""
    rng = np.random.default_rng(seed)
    _, grads = model.loss_grad(X, Y)
    params = model.params()
    errs, abs_errs = [], []
    for pi, (p, g) in enumerate(zip(params, grads)):
        flat = np.arange(p.size)
        rng.shuffle(flat)
        for j in flat[: max(2, n_probe // len(params))]:
            old = p.flat[j]
            p.flat[j] = old + eps
            lp = model.loss_grad(X, Y)[0]
            p.flat[j] = old - eps
            lm = model.loss_grad(X, Y)[0]
            p.flat[j] = old
            ng = (lp - lm) / (2 * eps)
            rel = abs(ng - g.flat[j]) / (abs(ng) + abs(g.flat[j]) + 1e-8)
            errs.append(rel)
            abs_errs.append(abs(ng - g.flat[j]))
    # 第三个值很关键：相对误差会被"梯度≈0"的元素放大，绝对误差才是实现是否正确的硬判据
    return float(np.max(errs)), float(np.mean(errs)), float(np.max(abs_errs))


def make_maps(signals, fs=wav.FS, gamma=0.4, size=32, verbose=True):
    """每个信号 -> (1,size,size) 的 Gamma 校正 log-Mel 谱图。"""
    out = np.empty((len(signals), 1, size, size), np.float32)
    for i, s in enumerate(signals):
        _, lm = dsp.mfcc(s, fs, return_logmel=True)
        M = dsp.gamma_correct(lm, gamma)
        # 手写双线性缩放：先按行插值，再按列插值
        y0 = np.linspace(0, M.shape[0] - 1, size)
        tmp = np.array([np.interp(y0, np.arange(M.shape[0]), M[:, c]) for c in range(M.shape[1])]).T
        x0 = np.linspace(0, tmp.shape[1] - 1, size)
        R = np.array([np.interp(x0, np.arange(tmp.shape[1]), tmp[r]) for r in range(size)])
        out[i, 0] = R
        if verbose and (i + 1) % 60 == 0:
            print(f"  谱图构建 {i + 1}/{len(signals)}", flush=True)
    return out


def write_csv(path, headers, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(headers)
        for r in rows:
            w.writerow([f"{v:.4f}" if isinstance(v, (float, np.floating)) else v for v in r])
    return path


def run_experiments(X, y, maps, out_dir, epochs_bp=90, epochs_cnn=45):
    """训练 + 全部分类曲线，返回指标 dict。"""
    os.makedirs(out_dir, exist_ok=True)
    k = len(wav.CLASSES)
    tr, va, te = stratified_split(y)

    # --- 标准化（只用训练集统计量，避免数据泄漏）
    mean, std = X[tr].mean(0), X[tr].std(0) + 1e-8
    Xs = (X - mean) / std
    Ms = maps

    print("  BPNN 训练中…", flush=True)
    bp = BPNN(X.shape[1], 48, k)
    g_bp = grad_check(bp, Xs[tr[:4]], onehot(y[tr[:4]], k))
    hb = train(bp, Xs[tr], y[tr], Xs[va], y[va], epochs_bp, lr=4e-3, batch=16, tag="BPNN")

    print("  CNN 训练中…", flush=True)
    cn = CNN(k, 4, Ms.shape[-1])
    g_cn = grad_check(cn, Ms[tr[:2]], onehot(y[tr[:2]], k))
    hc = train(cn, Ms[tr], y[tr], Ms[va], y[va], epochs_cnn, lr=2e-3, batch=16, tag="CNN ")

    results = {}
    probs = {}
    for name, hist, model, data in [("BPNN", hb, bp, Xs[te]), ("CNN", hc, cn, Ms[te])]:
        p = model.predict_proba(data)
        pred = p.argmax(1)
        f1 = f1_scores(y[te], pred, k)
        M = confusion(y[te], pred, k)
        aucs = [roc((y[te] == c).astype(int), p[:, c])[2] for c in range(k)]
        results[name] = {
            "acc": float(np.mean(pred == y[te])),
            "macro_f1": float(f1.mean()),
            "macro_auc": float(np.mean(aucs)),
            "epochs": len(hist["loss"]),
            "seconds": hist["seconds"],
            "params": int(sum(q.size for q in model.params())),
            "final_val_acc": hist["val_acc"][-1],
        }
        probs[name] = (p, pred, f1, M, aucs, hist)

        ep = np.arange(1, len(hist["loss"]) + 1)
        plot.line_chart(os.path.join(out_dir, f"curve_{name.lower()}_loss.png"),
                        [(ep, hist["loss"], "训练损失", None), (ep, hist["val_loss"], "验证损失", None)],
                        "epoch", "交叉熵损失", f"{name} 训练/验证损失曲线")
        plot.line_chart(os.path.join(out_dir, f"curve_{name.lower()}_acc.png"),
                        [(ep, hist["acc"], "训练准确率", None), (ep, hist["val_acc"], "验证准确率", None)],
                        "epoch", "准确率", f"{name} 分类准确率曲线", ylim=(0, 1.02),
                        hlines=[1 / k])
        plot.heatmap_chart(os.path.join(out_dir, f"confusion_{name.lower()}.png"), M,
                           f"{name} 测试集混淆矩阵（计数）", "预测类别", "真实类别",
                           w=720, h=580, vmin=0, vmax=M.max())

    # --- ROC / AUC
    roc_series, pr_series = [], []
    for name, (p, pred, f1, M, aucs, hist) in probs.items():
        for c in range(k):
            fpr, tpr, auc = roc((y[te] == c).astype(int), p[:, c])
            if name == "CNN":
                roc_series.append((fpr, tpr, f"{wav.CLASSES[c]} AUC={aucs[c]:.2f}", None))
    roc_series.append(([0, 1], [0, 1], "随机基线", plot.GRAY))
    plot.line_chart(os.path.join(out_dir, "roc_curves.png"), roc_series,
                    "FPR（假阳性率）", "TPR（真阳性率）", "CNN 多分类 ROC（One-vs-Rest）",
                    xlim=(0, 1), ylim=(0, 1.02), w=800, h=560, legend_pos="br")

    # --- 噪声鲁棒性：给特征/谱图逐级注入高斯噪声，看准确率怎么掉
    noise_x = [0.0, 0.1, 0.2, 0.4, 0.7, 1.0, 1.5, 2.0]
    noise_series, noise_acc = [], {}
    for name, model, data in [("BPNN", bp, Xs[te]), ("CNN", cn, Ms[te])]:
        rng2 = np.random.default_rng(2026)
        scale = float(data.std())
        accs = []
        for s in noise_x:
            d = data + rng2.normal(0, s * scale, data.shape)
            accs.append(float(np.mean(model.predict_proba(d).argmax(1) == y[te])))
        noise_acc[name] = accs
        noise_series.append((noise_x, accs, name, None))
    plot.line_chart(os.path.join(out_dir, "noise_robustness.png"), noise_series,
                    "噪声标准差 / 数据标准差", "测试准确率",
                    "噪声鲁棒性：输入受扰时分类准确率的衰减",
                    xlim=(0, 2.05), ylim=(0, 1.02), hlines=[1 / k])
    write_csv(os.path.join(out_dir, "noise_robustness.csv"),
              ["noise_ratio"] + list(noise_acc.keys()),
              [[noise_x[i]] + [noise_acc[n][i] for n in noise_acc] for i in range(len(noise_x))])

    # --- 逐类 F1 对比 + 模型对比表
    f1b, f1c = probs["BPNN"][2], probs["CNN"][2]
    plot.bar_chart(os.path.join(out_dir, "f1_by_class.png"), wav.CLASSES, f1c,
                   "CNN 逐类 F1 分数（测试集）", "F1", colors=wav.CLASS_COLORS, hline=f1c.mean())
    rows = [[wav.CLASSES[c], f"{f1b[c]:.3f}", f"{f1c[c]:.3f}"] for c in range(k)]
    plot.table_image(os.path.join(out_dir, "f1_table.png"), ["故障类别", "BPNN F1", "CNN F1"],
                     rows, "逐类 F1 对比（测试集）")
    cmp_rows = [[name, f"{r['acc']:.4f}", f"{r['macro_f1']:.4f}", f"{r['macro_auc']:.4f}",
                 f"{r['params']}", f"{r['seconds']:.1f}s", f"{r['final_val_acc']:.4f}"]
                for name, r in results.items()]
    plot.table_image(os.path.join(out_dir, "model_compare.png"),
                     ["模型", "测试准确率", "宏平均 F1", "宏平均 AUC", "参数量", "训练耗时", "最终验证准确率"],
                     cmp_rows, "手写 BPNN vs 手写 CNN（同一批 6 类声纹）")
    write_csv(os.path.join(out_dir, "model_compare.csv"),
              ["model", "test_acc", "macro_f1", "macro_auc", "params", "seconds", "final_val_acc"],
              [[name] + [r[q] for q in ["acc", "macro_f1", "macro_auc", "params", "seconds", "final_val_acc"]]
               for name, r in results.items()])

    # --- 混淆矩阵表（CNN）
    Mc = probs["CNN"][3]
    plot.table_image(os.path.join(out_dir, "confusion_table.png"),
                     ["真实\\预测"] + wav.CLASSES,
                     [[wav.CLASSES[i]] + list(Mc[i]) for i in range(k)],
                     "CNN 混淆矩阵（测试集计数）")

    # --- 学习曲线（BPNN，训练量递增）
    lc_x, lc_y = [], []
    for frac in [0.2, 0.4, 0.6, 0.8, 1.0]:
        sub = np.concatenate([idxc[: max(1, int(len(idxc) * frac))]
                              for c in np.unique(y[tr])
                              for idxc in [tr[y[tr] == c]]])
        m = BPNN(8, 24, k, seed=3)  # 只用 8 维时域特征，任务变难才能看出样本量的影响
        train(m, Xs[sub, :8], y[sub], Xs[va, :8], y[va], epochs=max(20, epochs_bp // 2), lr=4e-3, batch=16)
        lc_x.append(frac * 100)
        lc_y.append(float(np.mean(m.predict_proba(Xs[te, :8]).argmax(1) == y[te])))
    plot.line_chart(os.path.join(out_dir, "learning_curve.png"),
                    [(lc_x, lc_y, "BPNN 测试准确率（仅时域 8 维）", plot.BLUE)],
                    "训练样本比例 / %", "测试准确率", "学习曲线：仅用时域特征时，训练样本量对泛化的影响",
                    xlim=(15, 105), ylim=(0, 1.02))
    write_csv(os.path.join(out_dir, "learning_curve.csv"), ["train_pct", "test_acc"],
              [[a, b] for a, b in zip(lc_x, lc_y)])

    return {
        "models": results, "grad_bpnn": g_bp, "grad_cnn": g_cn,
        "noise": {"levels": noise_x, **noise_acc},
        "split": {"train": len(tr), "val": len(va), "test": len(te)},
        "learning": [[a, b] for a, b in zip(lc_x, lc_y)],
        "f1_by_class": {wav.CLASSES[c]: [float(f1b[c]), float(f1c[c])] for c in range(k)},
    }
