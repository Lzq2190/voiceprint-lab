"""一键复现入口。

    python run.py                    # 全流程（合成 6 类声纹 + 全部图/表/训练）
    python run.py --n 20             # 减小数据量，快速复跑
    python run.py --wav path/a.wav   # 只分析一个真实 WAV（波形/频谱/MFCC/特征表）
    python run.py --check            # 只跑算法数值验证

输出：index.html 讲义、outputs/*.png、outputs/*.csv、data/*.wav
零第三方依赖：numpy + Pillow（标准库 wave/csv/json）。
"""
from __future__ import annotations
import os
import re
import sys
import json
import argparse
import numpy as np

from src import wav, dsp, features, nn, viz

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "outputs")


def _js(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        f.write("window.METRICS = " + json.dumps(obj, ensure_ascii=False, indent=2) + ";\n")


def _inline(html_path, obj):
    """把指标内联进讲义，保证 file:// 直接打开也能看到全部表格（幂等）。"""
    with open(html_path, encoding="utf-8") as f:
        h = f.read()
    block = '<script id="metrics">window.METRICS = ' + json.dumps(obj, ensure_ascii=False) + ";</script>"
    h2, n = re.subn(r'<script id="metrics">.*?</script>', lambda _: block, h, count=1, flags=re.S)
    if n != 1:
        print("  [warn] 讲义里未找到内联占位，跳过（表格可能显示旧数据）")
        return
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(h2)


def real_wav(path):
    """单文件分析模式：不做训练，只做可视化与特征表。"""
    x, fs = wav.read_wav(path)
    print(f"[wav] {path}  fs={fs} Hz  样本数={len(x)}  时长={len(x) / fs:.3f} s")
    d = os.path.join(OUT, "real_wav")
    os.makedirs(d, exist_ok=True)
    n = min(len(x), int(fs * 0.08))
    t = np.arange(n) / fs * 1000
    from src import plot
    plot.line_chart(os.path.join(d, "waveform.png"), [(t, x[:n], "x[n]", None)],
                    "时间 / ms", "幅值", os.path.basename(path) + "：时域波形", legend=False)
    f, S = dsp.spectrum(x, fs, 8192)
    m = f <= min(4000, fs / 2)
    plot.line_chart(os.path.join(d, "spectrum.png"), [(f[m], S[m], "幅度谱", None)],
                    "频率 / Hz", "幅度", "FFT 幅度谱", legend=False)
    cc, lm = dsp.mfcc(x, fs, return_logmel=True)
    plot.heatmap_chart(os.path.join(d, "logmel.png"), lm[::-1],
                       "log-Mel 时频谱", "帧", "Mel 通道", w=820, h=380)
    plot.heatmap_chart(os.path.join(d, "mfcc.png"), cc.T[::-1],
                       "MFCC（13 维）", "帧", "系数", w=820, h=380)
    v = features.extract(x, fs)
    rows = [[features.FEATURE_NAMES[i], f"{v[i]:.6f}"] for i in range(len(v))]
    features.write_csv(os.path.join(d, "features.csv"), ["feature", "value"], rows)
    plot.table_image(os.path.join(d, "feature_table.png"), ["特征", "数值"],
                     rows[:18], f"{os.path.basename(path)} 特征向量（前 18 / {len(v)} 维）")
    print(f"[wav] 已输出 {d}（waveform / spectrum / logmel / mfcc / features.csv）")
    print("[wav] 前 8 维特征：")
    for i in range(8):
        print(f"       {features.FEATURE_NAMES[i]:<20} {v[i]:.6f}")


def main():
    ap = argparse.ArgumentParser(description="变压器声纹信号处理教学复现")
    ap.add_argument("--n", type=int, default=40, help="每类合成样本数（默认 40）")
    ap.add_argument("--epochs-bp", type=int, default=90, help="BPNN 训练轮数")
    ap.add_argument("--epochs-cnn", type=int, default=70, help="CNN 训练轮数")
    ap.add_argument("--wav", type=str, default="", help="真实 WAV 路径（单文件分析模式）")
    ap.add_argument("--check", action="store_true", help="只跑数值验证")
    args = ap.parse_args()

    if args.wav:
        real_wav(args.wav)
        return

    os.makedirs(OUT, exist_ok=True)
    print("=" * 62)
    print("变压器声纹信号处理 · 全流程复现（零第三方算法依赖）")
    print("=" * 62)

    v = dsp.verify(x=wav.synth(3, 42))
    print("[1/7] 算法数值验证")
    for k, val in v.items():
        print(f"       {k:<24} {val:.4g}")
    if args.check:
        return

    print(f"[2/7] 合成 6 类声纹 × {args.n} 条（fs={wav.FS} Hz, {wav.DUR}s）")
    signals, y = wav.build_dataset(args.n)
    wav.save_examples(os.path.join(ROOT, "data"))
    ex = viz.examples(signals, y)

    print("[3/7] WAV 可视化：波形 / 采样表 / 频谱 / STFT")
    viz.waveforms(ex, OUT, wav.FS)
    viz.fourier_plots(ex, OUT, wav.FS)

    print("[4/7] Gamma 校正 / Mel / MFCC / Gammatone")
    ginfo = viz.gamma_plots(ex, OUT, wav.FS)
    ainfo = viz.auditory_plots(ex, OUT, wav.FS)

    print("[5/7] 小波（Haar / db4 / Morlet CWT）与 EMD")
    winfo = viz.wavelet_plots(ex, OUT, wav.FS)
    einfo = viz.emd_plots(ex, OUT, wav.FS)

    print(f"[6/7] 提取 {len(features.FEATURE_NAMES)} 维特征并做特征分析")
    X, _ = features.build_matrix(signals, y, wav.FS)
    finfo = features.analyze(X, y, OUT)

    print("[7/7] 手写 BPNN / CNN 训练与分类曲线")
    maps = nn.make_maps(signals, wav.FS)
    ninfo = nn.run_experiments(X, y, maps, OUT, args.epochs_bp, args.epochs_cnn)

    metrics = {
        "dataset": {"n_per_class": args.n, "total": len(y), "fs": wav.FS,
                    "duration_s": wav.DUR, "classes": wav.CLASSES,
                    "n_fft": 512, "frame_ms": 25, "hop_ms": 10, "n_mels": 26},
        "verify": {k: float(x) for k, x in v.items()},
        "gamma": ginfo, "auditory": ainfo, "wavelet": winfo, "emd": einfo,
        "features": finfo, "nn": ninfo,
    }
    _js(os.path.join(OUT, "metrics.js"), metrics)
    with open(os.path.join(OUT, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    _inline(os.path.join(ROOT, "index.html"), metrics)

    print("-" * 62)
    print("验证表（关键结果）")
    print(f"  DFT/FFT/STFT 与 numpy 偏差      {v['dft_vs_numpy']:.2e} / {v['fft_vs_numpy']:.2e} / {v['stft_vs_numpy']:.2e}")
    print(f"  Haar / db4 重构 RMSE            {v['haar_recon_rmse']:.2e} / {v['db4_recon_rmse']:.2e}")
    print(f"  EMD 重构 RMSE / 正交指数       {v['emd_recon_rmse']:.2e} / {v['emd_orthogonality']:.4f}")
    print(f"  反向传播梯度检查 BPNN / CNN     {ninfo['grad_bpnn'][0]:.2e} / {ninfo['grad_cnn'][0]:.2e}")
    for name, r in ninfo["models"].items():
        print(f"  {name:<5} 测试准确率 {r['acc']:.3f}  宏F1 {r['macro_f1']:.3f}  宏AUC {r['macro_auc']:.3f}")
    print("-" * 62)
    print("完成：打开 index.html 查看讲义；outputs/ 为全部图与 CSV；data/ 为 6 个示例 WAV。")


if __name__ == "__main__":
    main()
