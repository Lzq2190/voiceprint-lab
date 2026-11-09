"""DSP 教学可视化：x(t) 采样、频谱、STFT、Gamma、Mel/MFCC、小波、EMD。"""
from __future__ import annotations
import os
import csv
import numpy as np
from . import dsp, plot, wav


def examples(signals, labels):
    """每类取第一个样本作为代表波形。"""
    return {c: signals[int(np.where(np.asarray(labels) == c)[0][0])]
            for c in range(len(wav.CLASSES))}


def stacked(path, waves, labels, title, colors=None, w=940, panel=88):
    """垂直堆叠多条波形（每条独立归一化），用于 IMF / 小波系数展示。"""
    n = len(waves)
    h = panel * n + 96
    f = plot.Fig(w, h, title, pad=(72, 54, 20, 36))
    hp = (f.y1 - f.y0) / n
    for i, s in enumerate(waves):
        s = np.asarray(s, float)
        yc = f.y0 + hp * (i + 0.5)
        c = (colors[i] if colors else plot.PALETTE[i % len(plot.PALETTE)])
        f.d.line((f.x0, yc + hp / 2 - 3, f.x1, yc + hp / 2 - 3), fill=plot.GRID, width=1)
        amp = hp * 0.40 / (np.max(np.abs(s)) + 1e-12)
        step = max(1, len(s) // 1800)
        pts = [(f.x0 + (f.x1 - f.x0) * j / (len(s) - 1), yc - s[j] * amp)
               for j in range(0, len(s), step)]
        f.d.line(pts, fill=c, width=1)
        f.d.text((f.x0 + 6, yc - hp / 2 + 4), labels[i], font=plot.font(12), fill=plot.MUTED)
    return f.save(path)


def waveforms(ex, out_dir, fs=wav.FS):
    os.makedirs(out_dir, exist_ok=True)
    rep = [ex[c] for c in range(len(wav.CLASSES))]
    n = min(640, len(rep[0]))
    t = np.arange(n) / fs * 1000
    for c, s in enumerate(rep):
        plot.line_chart(os.path.join(out_dir, f"wave_c{c}.png"),
                        [(t, s[:n], wav.CLASSES[c], wav.CLASS_COLORS[c])],
                        "时间 / ms", "幅值（归一化）",
                        f"{wav.CLASSES[c]}：时域波形 x[n]（前 {n / fs * 1000:.0f} ms）",
                        ylim=(-1.05, 1.05), legend=False, w=820, h=300)
    # 正常 vs 局部放电，突出脉冲
    n2 = min(400, len(rep[0]))
    t2 = np.arange(n2) / fs * 1000
    plot.line_chart(os.path.join(out_dir, "wave_compare.png"),
                    [(t2, rep[0][:n2], "正常", wav.CLASS_COLORS[0]),
                     (t2, rep[3][:n2], "局部放电（高频脉冲）", wav.CLASS_COLORS[3])],
                    "时间 / ms", "幅值", "时域对比：局部放电的稀疏瞬态脉冲",
                    ylim=(-1.1, 1.1))
    stacked(os.path.join(out_dir, "wave_all6.png"),
            [s[:1200] for s in rep], wav.CLASSES,
            "六类工况时域波形对照（各 150 ms）", wav.CLASS_COLORS, panel=76)

    # 采样表格 + 完整波形数据 CSV
    s0 = rep[0]
    q16 = (np.clip(s0, -1, 1) * 32767).astype(int)
    rows = [[i, f"{i / fs * 1000:.4f}", f"{s0[i]:.6f}", q16[i]] for i in range(14)]
    plot.table_image(os.path.join(out_dir, "sampling_table.png"),
                     ["n", "t = n·Ts / ms", "x[n]（浮点）", "int16 量化"],
                     rows, "连续 x(t) 的离散化：采样与 16 bit 量化（fs = 8000 Hz, Ts = 0.125 ms）")
    with open(os.path.join(out_dir, "waveform_data.csv"), "w", newline="", encoding="utf-8-sig") as f:
        wr = csv.writer(f)
        wr.writerow(["n", "t_ms", "x_n", "int16"])
        for i in range(min(len(s0), 4000)):
            wr.writerow([i, f"{i / fs * 1000:.4f}", f"{s0[i]:.8f}", q16[i]])
    return rep


def fourier_plots(ex, out_dir, fs=wav.FS):
    rep = [ex[c] for c in range(len(wav.CLASSES))]
    # DFT 基函数示意
    N = 64
    k = np.arange(N)
    plot.line_chart(os.path.join(out_dir, "dft_basis.png"),
                    [(k, np.sin(2 * np.pi * q * k / N), f"基函数 k={q}", None)
                     for q in (1, 2, 4)],
                    "样点 n", "Re{exp(-j2πkn/N)}",
                    "DFT 的本质：用不同频率的复正弦基与 x[n] 做内积", ylim=(-1.15, 1.15))

    for c, s in enumerate(rep):
        f, S = dsp.spectrum(s, fs, 4096)
        m = f <= 1200
        plot.line_chart(os.path.join(out_dir, f"spectrum_c{c}.png"),
                        [(f[m], S[m] / (S[m].max() + 1e-12), wav.CLASSES[c], wav.CLASS_COLORS[c])],
                        "频率 / Hz", "归一化幅度", f"{wav.CLASSES[c]}：FFT 幅度谱（0–1200 Hz）",
                        ylim=(0, 1.05), legend=False, w=820, h=320)
    # 正常 vs 直流偏磁（奇次谐波）
    f, A = dsp.spectrum(rep[0], fs, 4096)
    _, B = dsp.spectrum(rep[2], fs, 4096)
    m = f <= 600
    plot.line_chart(os.path.join(out_dir, "spectrum_compare.png"),
                    [(f[m], A[m] / (A[m].max() + 1e-12), "正常", wav.CLASS_COLORS[0]),
                     (f[m], B[m] / (B[m].max() + 1e-12), "直流偏磁（奇次谐波抬升）", wav.CLASS_COLORS[2])],
                    "频率 / Hz", "归一化幅度", "频谱对比：直流偏磁在 150/250/350 Hz 出现奇次谐波",
                    ylim=(0, 1.05))

    # STFT / log-Mel 谱图（每类一张）
    for c, s in enumerate(rep):
        _, lm = dsp.mfcc(s, fs, return_logmel=True)
        plot.heatmap_chart(os.path.join(out_dir, f"stft_c{c}.png"), lm[::-1],
                           f"{wav.CLASSES[c]}：log-Mel 时频谱（STFT → Mel 滤波）",
                           "时间 / ms", "Mel 通道（低频在下）", w=760, h=380,
                           extent=(0, len(s) / fs * 1000, 4000, 80))
    return rep


def gamma_plots(ex, out_dir, fs=wav.FS):
    s = ex[3]  # 局部放电，动态范围最大
    _, lm = dsp.mfcc(s, fs, return_logmel=True)
    for g in (0.3, 0.6, 1.0, 2.0):
        G = dsp.gamma_correct(lm, g)
        plot.heatmap_chart(os.path.join(out_dir, f"gamma_{str(g).replace('.', '')}.png"), G[::-1],
                           f"Gamma 校正 γ = {g}（同一段局放声纹）", "时间 / ms", "Mel 通道",
                           w=640, h=330, extent=(0, len(s) / fs * 1000, 4000, 80), vmin=0, vmax=1)
    u = np.linspace(0, 1, 200)
    plot.line_chart(os.path.join(out_dir, "gamma_curve.png"),
                    [(u, u ** g, f"γ = {g}", None) for g in (0.3, 0.6, 1.0, 2.0)],
                    "归一化谱能量 s", "s^γ", "Gamma 校正的非线性压缩曲线",
                    xlim=(0, 1), ylim=(0, 1.02), w=760, h=420)
    # 动态范围压缩量化
    raw = (lm - lm.min()) / (lm.max() - lm.min() + 1e-10)
    out = {}
    for g in (0.3, 0.6, 1.0, 2.0):
        G = raw ** g
        out[g] = {"p10": float(np.percentile(G, 10)), "p90": float(np.percentile(G, 90)),
                  "contrast": float(np.percentile(G, 90) - np.percentile(G, 10))}
    return out


def auditory_plots(ex, out_dir, fs=wav.FS):
    s = ex[0]
    fb = dsp.mel_filterbank(fs, 512, 26)
    f = np.arange(257) * fs / 512
    m = f <= 4000
    plot.line_chart(os.path.join(out_dir, "mel_filters.png"),
                    [(f[m], fb[j][m], f"Mel 滤波器 {j + 1}", None) for j in range(0, 10, 2)],
                    "频率 / Hz", "滤波器增益", "Mel 三角滤波器组（低频分辨细，高频分辨粗）",
                    ylim=(0, 0.32), w=900, h=360)

    cc, lm = dsp.mfcc(s, fs, return_logmel=True)
    d1, d2 = dsp.delta(cc), dsp.delta(dsp.delta(cc))
    plot.heatmap_chart(os.path.join(out_dir, "mfcc_heatmap.png"), cc.T[::-1],
                       "MFCC 倒谱系数（13 维 × 48 帧）", "帧序号", "倒谱系数序号",
                       w=820, h=380, extent=(0, cc.shape[0], 13, 0))
    stacked(os.path.join(out_dir, "mfcc_39.png"),
            [cc[:, 0], d1[:, 0], d2[:, 0], cc[:, 1], d1[:, 1], d2[:, 1]],
            ["C1 静态", "ΔC1", "ΔΔC1", "C2 静态", "ΔC2", "ΔΔC2"],
            "39 维 MFCC 的构成：13 静态 + 13 一阶差分 + 13 二阶差分（此处示意前 2 维）",
            panel=72)
    G, cfs = dsp.gammatonegram(s, fs)
    plot.heatmap_chart(os.path.join(out_dir, "gammatonegram.png"), G[::-1],
                       "Gammatonegram：听觉滤波器组时频表示", "时间 / ms",
                       f"中心频率 {cfs[-1]:.0f} Hz（上）→ {cfs[0]:.0f} Hz（下）",
                       w=820, h=380, extent=(0, len(s) / fs * 1000, 4000, 80))
    return {"cfs_first": float(cfs[0]), "cfs_last": float(cfs[-1]),
            "mfcc_shape": list(cc.shape), "n_mels": int(lm.shape[0])}


def wavelet_plots(ex, out_dir, fs=wav.FS):
    s = ex[3]  # 局放：瞬态脉冲最适合展示时频定位
    hc = dsp.haar_dwt(s, 4)
    waves = [s] + [hc[i][1] for i in range(4)] + [hc[-1][0]]
    labels = ["原始 x[n]"] + [f"Haar D{i+1} 细节" for i in range(4)] + ["A4 近似"]
    stacked(os.path.join(out_dir, "haar_decomposition.png"), waves, labels,
            "Haar 离散小波多层分解：x = A4 + D1 + D2 + D3 + D4", panel=78)

    dc = dsp.db4_dwt(s, 3)
    stacked(os.path.join(out_dir, "db4_decomposition.png"),
            [s] + [dc[i][1] for i in range(3)] + [dc[-1][0]],
            ["原始 x[n]"] + [f"db4 D{i+1}" for i in range(3)] + ["db4 A3"],
            "db4（Daubechies D8）正交小波分解", panel=88)

    W, fr = dsp.cwt_morlet(s, fs)
    Wd = W[:, ::8]
    # 尺度原本是对数分布的，必须重采样到线性频率轴，否则 y 轴刻度会错位
    lin_fr = np.linspace(fr[0], fr[-1], 64)
    Wl = np.array([np.interp(lin_fr, fr, Wd[:, j]) for j in range(Wd.shape[1])]).T
    # 减去每个频率带的时间中位数，只保留"瞬态增强"，稳态谐波带自然变暗
    med = np.median(Wl, axis=1, keepdims=True)
    p95 = np.percentile(Wl, 95, axis=1, keepdims=True)
    Wn = np.clip((Wl - med) / (p95 - med + 1e-12), 0, 1.5)
    plot.heatmap_chart(os.path.join(out_dir, "cwt_scalogram.png"), Wn[::-1],
                       "连续小波尺度图（复 Morlet，线性频率轴 + 稳态抑制）",
                       "时间 / ms", "频率 / Hz（上高下低）", w=940, h=430,
                       extent=(0, len(s) / fs * 1000, lin_fr[-1], lin_fr[0]), vmin=0, vmax=1.3)

    # 滤波器系数与频响
    h0, h1 = dsp.DB4_H, (-1.0) ** np.arange(8) * dsp.DB4_H[::-1]
    plot.bar_chart(os.path.join(out_dir, "db4_coeffs.png"),
                   [f"h[{i}]" for i in range(8)], h0,
                   "db4 分解低通系数 h0（正交镜像滤波器组）", "系数值", w=820, h=360)
    Hf = np.abs(np.fft.rfft(h0, 512))
    Gf = np.abs(np.fft.rfft(h1, 512))
    ff = np.arange(257) * fs / 512
    plot.line_chart(os.path.join(out_dir, "db4_response.png"),
                    [(ff, Hf, "低通 h0", plot.BLUE), (ff, Gf, "高通 h1", plot.AMBER)],
                    "频率 / Hz", "幅频响应", "db4 双通道 QMF 幅频响应（二抽取滤波器组）")
    return {"haar_levels": len(hc), "db4_levels": len(dc), "cwt_scales": len(fr)}


def emd_plots(ex, out_dir, fs=wav.FS):
    s = ex[1]   # 铁芯松动：调幅 + 敲击，IMF 层次清晰
    xs = s[::2]
    imfs, res = dsp.emd(xs, max_imf=5, max_sift=25)
    waves = [xs] + list(imfs) + [res]
    labels = ["原始 x(t)"] + [f"IMF {i + 1}" for i in range(len(imfs))] + ["残差 r(t)"]
    stacked(os.path.join(out_dir, "emd_imfs.png"), waves, labels,
            "EMD 经验模态分解：按特征尺度自适应筛分（非预设基）", panel=74)
    e = np.array([np.sum(a ** 2) for a in imfs] + [np.sum(res ** 2)])
    p = e / e.sum()
    plot.bar_chart(os.path.join(out_dir, "emd_energy.png"),
                   [f"IMF{i + 1}" for i in range(len(imfs))] + ["残差"],
                   p, "各 IMF 能量占比（故障冲击集中在高频 IMF）", "能量占比", w=860, h=380)
    return {"n_imf": int(len(imfs)), "energy": [float(v) for v in p],
            "recon_rmse": float(np.sqrt(np.mean((np.sum(imfs, axis=0) + res - xs) ** 2)))}
