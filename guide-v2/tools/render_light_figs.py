# -*- coding: utf-8 -*-
"""
把讲义引用的 11 张图用「印刷浅色主题」重绘，输出到 guide-v2/assets-print/。
深色网页版仍用 assets/，两者互不覆盖。

用法：python tools/render_light_figs.py
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GUIDE = os.path.dirname(HERE)
ROOT = os.path.dirname(GUIDE)
ACOUSTIC = os.path.join(ROOT, "acoustic-lab")
sys.path.insert(0, ACOUSTIC)

import numpy as np  # noqa: E402
from src import plot, wav, viz, features, nn  # noqa: E402

OUT = os.path.join(GUIDE, "assets-print")
STAGE = os.path.join(GUIDE, "_figs_stage")

NEEDED = [
    "sampling_table.png", "spectrum_compare.png", "stft_c3.png",
    "mel_filters.png", "mfcc_39.png", "cwt_scalogram.png", "emd_imfs.png",
    "curve_bpnn_loss.png", "curve_cnn_acc.png", "model_compare.png",
    "noise_robustness.png", "learning_curve.png", "pca_scatter.png",
    "roc_curves.png", "wave_compare.png",
]


def main():
    plot.set_theme("light")
    plot.set_font_scale(1.3, pad=1.18)   # 印刷版：字号放大，缩到 A4 后仍清晰
    plot.set_font_scale(1.3, pad=1.18)   # 印刷版：字号放大，缩到 A4 后仍清晰
    # 类别配色跟随主题（viz 直接读 wav.CLASS_COLORS）
    wav.CLASS_COLORS = [plot.BLUE, plot.TEAL, plot.AMBER, plot.RED, plot.PURPLE, plot.GRAY]

    os.makedirs(STAGE, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)

    print("合成数据 ...")
    s, y = wav.build_dataset(40)
    ex = viz.examples(s, y)

    print("波形 / 采样表 ...")
    viz.waveforms(ex, STAGE, wav.FS)
    print("频谱 ...")
    viz.fourier_plots(ex, STAGE, wav.FS)
    print("听觉 / MFCC ...")
    viz.auditory_plots(ex, STAGE, wav.FS)
    print("小波 ...")
    viz.wavelet_plots(ex, STAGE, wav.FS)
    print("EMD ...")
    viz.emd_plots(ex, STAGE, wav.FS)

    print("训练网络并出分类曲线 ...")
    X, _ = features.build_matrix(s, y, verbose=False)
    M = nn.make_maps(s, verbose=False)
    r = nn.run_experiments(X, y, M, STAGE, epochs_bp=90, epochs_cnn=70)
    for name, m in r["models"].items():
        print("  %-5s acc=%.4f  macroF1=%.4f" % (name, m["acc"], m["macro_f1"]))

    missing = []
    for f in NEEDED:
        src = os.path.join(STAGE, f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(OUT, f))
        else:
            missing.append(f)
    print("复制 %d 张到 %s" % (len(NEEDED) - len(missing), OUT))
    if missing:
        print("缺失：", missing)

    # 校验：图必须接近白底（抽四角像素）
    from PIL import Image
    bad = []
    for f in NEEDED:
        p = os.path.join(OUT, f)
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert("RGB")
        w, h = im.size
        corners = [im.getpixel((2, 2)), im.getpixel((w - 3, 2)),
                   im.getpixel((2, h - 3)), im.getpixel((w - 3, h - 3))]
        mean = np.mean(corners)
        if mean < 200:
            bad.append((f, round(float(mean), 1)))
    print("非白底图：", bad if bad else "无，全部为浅色背景")
    shutil.rmtree(STAGE, ignore_errors=True)


if __name__ == "__main__":
    main()
