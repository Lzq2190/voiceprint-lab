"""特征提取与特征分析：时域 / 频域 / 时频域 / MFCC / 小波 / EMD。

输出 CSV 表格、类间可分性(Fisher)、相关热力图、PCA 散点、表格 PNG。
"""
from __future__ import annotations
import os
import csv
import numpy as np
from . import dsp, plot, wav

TD_NAMES = ["rms", "energy_std", "peak", "kurtosis", "skewness",
            "zcr", "crest_factor", "impulse_factor"]
FD_NAMES = ["spec_centroid", "spec_bandwidth", "spec_flatness", "ratio_100hz",
            "odd_harm_ratio", "high_freq_ratio", "peak_freq"]
MFCC_NAMES = [f"mfcc{i}_mean" for i in range(1, 14)] + [f"mfcc{i}_std" for i in range(1, 14)]
TF_NAMES = ["haar_energy_entropy", "db4_detail_ratio", "cwt_energy_centroid",
            "emd_imf1", "emd_imf2", "emd_imf3", "emd_imf4", "emd_sampen"]
FEATURE_NAMES = TD_NAMES + FD_NAMES + MFCC_NAMES + TF_NAMES


def sample_entropy(x, m: int = 2, r: float | None = None) -> float:
    """样本熵 SampEn(m,r)：衡量序列不可预测性，故障冲击会抬高它。"""
    x = np.asarray(x, float)
    n = len(x)
    if n < m + 2:
        return 0.0
    if r is None:
        r = 0.2 * np.std(x) + 1e-12
    tmpl = np.lib.stride_tricks.sliding_window_view(x, m)
    B = 0
    for i in range(len(tmpl) - 1):
        B += np.sum(np.max(np.abs(tmpl[i + 1:] - tmpl[i]), axis=1) <= r)
    tmpl2 = np.lib.stride_tricks.sliding_window_view(x, m + 1)
    A = 0
    for i in range(len(tmpl2) - 1):
        A += np.sum(np.max(np.abs(tmpl2[i + 1:] - tmpl2[i]), axis=1) <= r)
    if B == 0 or A == 0:
        return 0.0
    return float(-np.log(A / B))


def _band(f, P, lo, hi) -> float:
    m = (f >= lo) & (f < hi)
    return float(P[m].sum() / (P.sum() + 1e-12))


def extract(x, fs: int = wav.FS) -> np.ndarray:
    """单条声纹 → 46 维特征向量。"""
    x = np.asarray(x, float)
    n = len(x)
    v = []

    # --- 时域（8）
    rms = np.sqrt(np.mean(x ** 2))
    fr = dsp.frames(x, 200, 100)
    e = np.sqrt(np.mean(fr ** 2, axis=1) + 1e-12)
    mu, sd = x.mean(), x.std() + 1e-12
    v += [rms, e.std(), np.max(np.abs(x)),
          float(np.mean(((x - mu) / sd) ** 4) - 3), float(np.mean(((x - mu) / sd) ** 3)),
          float(np.mean(np.abs(np.diff(np.sign(x))) > 0)),
          float(np.max(np.abs(x)) / (rms + 1e-12)),
          float(np.max(np.abs(x)) / (np.mean(np.abs(x)) + 1e-12))]

    # --- 频域（7）
    f, S = dsp.spectrum(x, fs, n_fft=4096)
    P = S ** 2
    pt = P / (P.sum() + 1e-12)
    cent = float((f * pt).sum())
    v += [cent, float(np.sqrt(((f - cent) ** 2 * pt).sum())),
          float(np.exp(np.mean(np.log(P + 1e-12))) / (np.mean(P) + 1e-12)),
          _band(f, P, 90, 110),
          float((_band(f, P, 140, 160) + _band(f, P, 240, 260) + _band(f, P, 340, 360))
                / (_band(f, P, 90, 410) + 1e-12)),
          _band(f, P, 1500, 4000), float(f[np.argmax(P)])]

    # --- MFCC 统计（26）
    cc = dsp.mfcc(x, fs)
    v += list(cc.mean(axis=0)) + list(cc.std(axis=0))

    # --- 时频（8）
    hc = dsp.haar_dwt(x, 4)
    he = np.array([np.sum(cD ** 2) for cA, cD in hc] + [np.sum(hc[-1][0] ** 2)])
    hp = he / (he.sum() + 1e-12)
    v.append(float(-np.sum(hp * np.log(hp + 1e-12))))

    dc = dsp.db4_dwt(x, 3)
    de = np.array([np.sum(cD ** 2) for cA, cD in dc])
    v.append(float(de.sum() / (de.sum() + np.sum(dc[-1][0] ** 2) + 1e-12)))

    xs = x[::2]
    W, fr_c = dsp.cwt_morlet(xs, fs / 2, freqs=np.geomspace(50, 1800, 24))
    we = (W ** 2).sum(axis=1)
    wp = we / (we.sum() + 1e-12)
    v.append(float((fr_c * wp).sum()))

    imfs, res = dsp.emd(x[::4], max_imf=4, max_sift=12)
    ie = np.array([np.sum(im ** 2) for im in imfs] + [np.sum(res ** 2)])
    ip = ie / (ie.sum() + 1e-12)
    for i in range(4):
        v.append(float(ip[i]) if i < len(ip) else 0.0)
    v.append(sample_entropy(imfs[0] if len(imfs) else x[::4]))
    return np.asarray(v, float)


def build_matrix(signals, labels, fs=wav.FS, verbose=True):
    X = np.empty((len(signals), len(FEATURE_NAMES)), float)
    for i, s in enumerate(signals):
        X[i] = extract(s, fs)
        if verbose and (i + 1) % 30 == 0:
            print(f"  特征提取 {i + 1}/{len(signals)} ({(i + 1) / len(signals) * 100:.0f}%)", flush=True)
    return X, np.asarray(labels, int)


def standardize(X, mean=None, std=None):
    if mean is None:
        mean = X.mean(axis=0)
    if std is None:
        std = X.std(axis=0) + 1e-8
    return (X - mean) / std, mean, std


def fisher_scores(X, y) -> np.ndarray:
    """Fisher 类间/类内方差比，越大越可分。"""
    overall = X.mean(axis=0)
    sb = np.zeros(X.shape[1])
    sw = np.zeros(X.shape[1])
    for c in np.unique(y):
        Xc = X[y == c]
        sb += len(Xc) * (Xc.mean(axis=0) - overall) ** 2
        sw += ((Xc - Xc.mean(axis=0)) ** 2).sum(axis=0)
    return sb / (sw + 1e-8)


def pca2(X, y=None):
    Xc = X - X.mean(axis=0)
    _, s, vt = np.linalg.svd(Xc, full_matrices=False)
    Z = Xc @ vt[:2].T
    return Z, float(s[0] ** 2 / np.sum(s ** 2)), float(s[1] ** 2 / np.sum(s ** 2)), vt


def write_csv(path, headers, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(headers)
        for r in rows:
            w.writerow([f"{v:.6f}" if isinstance(v, (float, np.floating)) else v for v in r])
    return path


def analyze(X, y, out_dir: str, top: int = 15) -> dict:
    """生成全部特征分析产物，返回关键数值。"""
    os.makedirs(out_dir, exist_ok=True)
    classes = wav.CLASSES
    write_csv(os.path.join(out_dir, "features.csv"), ["label", "class"] + FEATURE_NAMES,
              [[int(y[i]), classes[y[i]]] + list(X[i]) for i in range(len(y))])

    # 每类均值 ± 标准差表（取前 12 个特征）
    show = FEATURE_NAMES[:12]
    idx = [FEATURE_NAMES.index(s) for s in show]
    stat_rows = []
    for c, name in enumerate(classes):
        Xc = X[y == c]
        stat_rows.append([name] + [f"{Xc[:, j].mean():.3f}±{Xc[:, j].std():.3f}" for j in idx])
    write_csv(os.path.join(out_dir, "feature_stats.csv"), ["类别"] + show, stat_rows)
    plot.table_image(os.path.join(out_dir, "feature_table.png"),
                     ["类别"] + show[:7],
                     [[r[0]] + r[1:8] for r in stat_rows],
                     "各工况时域/频域特征统计（均值 ± 标准差，前 7 维）")

    # Fisher 可分性
    fs = fisher_scores(X, y)
    order = np.argsort(fs)[::-1]
    write_csv(os.path.join(out_dir, "fisher_scores.csv"), ["rank", "feature", "fisher_ratio"],
              [[i + 1, FEATURE_NAMES[order[i]], fs[order[i]]] for i in range(len(fs))])
    plot.bar_chart(os.path.join(out_dir, "fisher_top.png"),
                   [FEATURE_NAMES[order[i]] for i in range(top)],
                   [fs[order[i]] for i in range(top)],
                   "类间可分性 Fisher 比（Top 15）", "Fisher 比（越大越可分）", w=1100, h=470)

    # 特征相关热力图（前 24 维）
    sub = X[:, :24]
    C = np.corrcoef(sub.T)
    plot.heatmap_chart(os.path.join(out_dir, "feature_corr.png"), C,
                       "特征相关系数矩阵（前 24 维）", "特征序号", "特征序号",
                       w=800, h=620, vmin=-1, vmax=1)

    # PCA 散点
    Z, e1, e2, _ = pca2(standardize(X)[0])
    groups = [(Z[y == c, 0], Z[y == c, 1], classes[c], wav.CLASS_COLORS[c])
              for c in range(len(classes))]
    plot.scatter_chart(os.path.join(out_dir, "pca_scatter.png"), groups,
                       "PC1", "PC2",
                       f"特征空间 PCA 投影（手写 SVD，累计解释方差 {(e1 + e2) * 100:.1f}%）")

    # Top-1 特征的各类均值
    j = int(order[0])
    means = [X[y == c, j].mean() for c in range(len(classes))]
    plot.bar_chart(os.path.join(out_dir, "top_feature_by_class.png"), classes, means,
                   f"最具可分性特征：{FEATURE_NAMES[j]}（各类均值）", FEATURE_NAMES[j],
                   colors=wav.CLASS_COLORS)

    return {
        "n_features": len(FEATURE_NAMES),
        "fisher_top": [(FEATURE_NAMES[order[i]], float(fs[order[i]])) for i in range(5)],
        "pca_var1": float(e1), "pca_var2": float(e2),
        "corr_max_offdiag": float(np.max(np.abs(C - np.eye(len(C))))),
    }
