"""零依赖绘图引擎：只使用 numpy + Pillow，深色主题，中文用微软雅黑，绝不乱码。

提供 line / heatmap / bar / scatter / table 五类图，全部输出 PNG。
"""
from __future__ import annotations
import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BG = (15, 19, 27)
PANEL = (22, 28, 38)
HEADER = (34, 46, 62)
GRID = (42, 52, 66)
BORDER = (60, 72, 88)
TEXT = (230, 237, 243)
MUTED = (150, 165, 182)

BLUE = (76, 155, 232)
TEAL = (45, 212, 167)
AMBER = (245, 165, 36)
RED = (242, 109, 109)
PURPLE = (167, 139, 250)
GRAY = (136, 148, 164)
PALETTE = [BLUE, TEAL, AMBER, RED, PURPLE, GRAY, (94, 201, 240), (214, 143, 92)]

CMAP = "inferno"   # 深色主题用 inferno；浅色主题切到 viridis，白纸上更易分辨

_DARK = {
    "BG": (15, 19, 27), "PANEL": (22, 28, 38), "HEADER": (34, 46, 62),
    "GRID": (42, 52, 66), "BORDER": (60, 72, 88),
    "TEXT": (230, 237, 243), "MUTED": (150, 165, 182),
    "BLUE": (76, 155, 232), "TEAL": (45, 212, 167), "AMBER": (245, 165, 36),
    "RED": (242, 109, 109), "PURPLE": (167, 139, 250), "GRAY": (136, 148, 164),
    "CMAP": "inferno",
}

# 浅色 / 印刷主题：白底、深色墨线，颜色加饱和以便打印后仍可区分
_LIGHT = {
    "BG": (255, 255, 255), "PANEL": (244, 247, 250), "HEADER": (228, 235, 243),
    "GRID": (208, 216, 226), "BORDER": (150, 163, 178),
    "TEXT": (26, 34, 46), "MUTED": (92, 105, 122),
    "BLUE": (31, 90, 186), "TEAL": (11, 122, 116), "AMBER": (176, 102, 6),
    "RED": (190, 42, 42), "PURPLE": (104, 55, 182), "GRAY": (104, 116, 132),
    "CMAP": "viridis",
}


def set_theme(name: str = "dark"):
    """切换配色主题：'dark'（网页/深色讲义）或 'light'（白底印刷）。"""
    g = _LIGHT if name == "light" else _DARK
    global BG, PANEL, HEADER, GRID, BORDER, TEXT, MUTED, CMAP
    global BLUE, TEAL, AMBER, RED, PURPLE, GRAY, PALETTE
    BG, PANEL, HEADER = g["BG"], g["PANEL"], g["HEADER"]
    GRID, BORDER = g["GRID"], g["BORDER"]
    TEXT, MUTED = g["TEXT"], g["MUTED"]
    BLUE, TEAL, AMBER = g["BLUE"], g["TEAL"], g["AMBER"]
    RED, PURPLE, GRAY = g["RED"], g["PURPLE"], g["GRAY"]
    PALETTE = [BLUE, TEAL, AMBER, RED, PURPLE, GRAY]
    CMAP = g["CMAP"]

_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\msyhbd.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
]
_FONT_PATH = next((p for p in _FONT_CANDIDATES if os.path.exists(p)), None)
_FONT_CACHE: dict[int, ImageFont.FreeTypeFont] = {}


FONT_SCALE = 1.0     # 全局字号比例：印刷版插图设为 1.3，缩到 A4 后字号才够大
PAD_SCALE = 1.0      # 边距补偿，避免放大字号后与刻度/边缘相撞


def set_font_scale(s: float = 1.0, pad: float = 1.0):
    global FONT_SCALE, PAD_SCALE
    FONT_SCALE, PAD_SCALE = float(s), float(pad)


def font(size: int):
    size = max(6, int(round(size * FONT_SCALE)))
    if size not in _FONT_CACHE:
        _FONT_CACHE[size] = (
            ImageFont.truetype(_FONT_PATH, size) if _FONT_PATH else ImageFont.load_default()
        )
    return _FONT_CACHE[size]


def tw(draw, s: str, size: int) -> float:
    box = draw.textbbox((0, 0), s, font=font(size))
    return box[2] - box[0]


def _fmt(v: float) -> str:
    if v == 0:
        return "0"
    a = abs(v)
    if a >= 1e5 or a < 1e-3:
        return f"{v:.1e}"
    if a >= 100:
        return f"{v:.0f}"
    if a >= 10:
        return f"{v:.1f}"
    if a >= 1:
        return f"{v:.2f}"
    return f"{v:.3f}"


def _inferno(v: float):
    stops = [
        (0.00, (8, 10, 26)), (0.15, (40, 16, 82)), (0.32, (96, 24, 110)),
        (0.50, (156, 42, 100)), (0.68, (214, 84, 62)), (0.84, (246, 152, 52)),
        (1.00, (252, 240, 168)),
    ]
    v = min(1.0, max(0.0, v))
    for (a, ca), (b, cb) in zip(stops[:-1], stops[1:]):
        if a <= v <= b:
            r = (v - a) / (b - a)
            return tuple(int(ca[i] + r * (cb[i] - ca[i])) for i in range(3))
    return stops[-1][1]


def _viridis(v: float):
    """印刷友好的顺序色标：深紫 → 蓝 → 青 → 绿 → 黄，白纸上层次清楚。"""
    stops = [
        (0.00, (68, 1, 84)), (0.25, (59, 82, 139)), (0.50, (33, 145, 140)),
        (0.75, (94, 201, 98)), (1.00, (253, 231, 37)),
    ]
    v = min(1.0, max(0.0, v))
    for (a, ca), (b, cb) in zip(stops[:-1], stops[1:]):
        if a <= v <= b:
            r = (v - a) / (b - a)
            return tuple(int(ca[i] + r * (cb[i] - ca[i])) for i in range(3))
    return stops[-1][1]


def _cmap_lut(n: int = 256) -> np.ndarray:
    f = _viridis if CMAP == "viridis" else _inferno
    return np.array([f(v) for v in np.linspace(0, 1, n)], np.uint8)


class Fig:
    def __init__(self, w=940, h=460, title="", pad=(72, 58, 30, 58)):
        self.w, self.h = w, h
        pad = tuple(int(round(p * PAD_SCALE)) for p in pad)
        self.pad = pad
        self.img = Image.new("RGB", (w, h), BG)
        self.d = ImageDraw.Draw(self.img)
        if title:
            self.d.text((pad[0] - 46, 16), title, font=font(17), fill=TEXT)
        self.x0 = pad[0]
        self.y0 = pad[1]
        self.x1 = w - pad[2]
        self.y1 = h - pad[3]

    def vtext(self, x, y_center, text, size=13, fill=None):
        """竖排文字（自下而上），用于纵轴标题，避免长标签压到刻度。"""
        if not text:
            return
        fill = MUTED if fill is None else fill
        w_ = tw(self.d, text, size)
        canvas = Image.new("RGBA", (w_ + 14, size + 16), (0, 0, 0, 0))
        ImageDraw.Draw(canvas).text(
            ((w_ + 14) // 2, (size + 16) // 2), text,
            font=font(size), fill=fill, anchor="mm")
        canvas = canvas.rotate(90, expand=True)
        self.img.paste(canvas, (int(x), int(y_center - canvas.height / 2)), canvas)

    def frame(self, xlim, ylim, xlabel="", ylabel="", xticks=6, yticks=5, logx=False):
        x0, y0, x1, y1 = self.x0, self.y0, self.x1, self.y1
        self.d.rectangle((x0, y0, x1, y1), fill=PANEL, outline=BORDER, width=1)
        for i in range(yticks + 1):
            y = y1 - (y1 - y0) * i / yticks
            self.d.line((x0, y, x1, y), fill=GRID, width=1)
            val = ylim[0] + (ylim[1] - ylim[0]) * i / yticks
            s = _fmt(val)
            self.d.text((x0 - 8 - tw(self.d, s, 12), y - 8), s, font=font(12), fill=MUTED)
        for i in range(xticks + 1):
            if logx:
                val = 10 ** (math.log10(xlim[0]) + (math.log10(xlim[1]) - math.log10(xlim[0])) * i / xticks)
                x = x0 + (x1 - x0) * i / xticks
            else:
                val = xlim[0] + (xlim[1] - xlim[0]) * i / xticks
                x = x0 + (x1 - x0) * i / xticks
            self.d.line((x, y0, x, y1), fill=GRID, width=1)
            s = _fmt(val)
            self.d.text((x - tw(self.d, s, 12) / 2, y1 + 8), s, font=font(12), fill=MUTED)
        if xlabel:
            s = xlabel
            self.d.text(((x0 + x1) / 2 - tw(self.d, s, 13) / 2, self.h - 26), s, font=font(13), fill=MUTED)
        if ylabel:
            lab_max = max(tw(self.d, _fmt(ylim[0] + (ylim[1] - ylim[0]) * i / yticks), 12)
                          for i in range(yticks + 1))
            lx = max(4, x0 - 8 - lab_max - int(13 * FONT_SCALE) - 14)
            self.vtext(lx, (y0 + y1) / 2, ylabel)

    def _px(self, x, y, xlim, ylim, logx=False):
        if logx:
            u = (math.log10(max(x, xlim[0])) - math.log10(xlim[0])) / (math.log10(xlim[1]) - math.log10(xlim[0]))
        else:
            u = (x - xlim[0]) / (xlim[1] - xlim[0])
        v = (y - ylim[0]) / (ylim[1] - ylim[0])
        return self.x0 + u * (self.x1 - self.x0), self.y1 - v * (self.y1 - self.y0)

    def line(self, xs, ys, color=BLUE, width=2, xlim=None, ylim=None, logx=False):
        pts = [self._px(float(x), float(y), xlim, ylim, logx) for x, y in zip(xs, ys)]
        if len(pts) > 1:
            self.d.line(pts, fill=color, width=width, joint="curve")
        return pts

    def dots(self, xs, ys, color=BLUE, r=3, xlim=None, ylim=None, logx=False):
        for x, y in zip(xs, ys):
            px, py = self._px(float(x), float(y), xlim, ylim, logx)
            self.d.ellipse((px - r, py - r, px + r, py + r), fill=color)

    def legend(self, items, pos="tr"):
        # items: [(label, color)]；pos: tr / tl / br / bl
        x = self.x1 - 12 - max(tw(self.d, lab, 12) for lab, _ in items) - 34
        y = self.y0 + 10
        if pos in ("tl", "bl"):
            x = self.x0 + 12
        if pos in ("br", "bl"):
            y = self.y1 - 12 - 22 * len(items)
        for lab, col in items:
            self.d.rectangle((x, y + 3, x + 14, y + 9), fill=col)
            self.d.text((x + 20, y - 2), lab, font=font(12), fill=TEXT)
            y += 22

    def text(self, x, y, s, size=13, color=TEXT):
        self.d.text((x, y), s, font=font(size), fill=color)

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.img.save(path)
        return path


def line_chart(path, series, xlabel="", ylabel="", title="", xlim=None, ylim=None,
               legend=True, w=940, h=440, logx=False, xticks=6, yticks=5, hlines=None,
               legend_pos="tr"):
    """series: [(xs, ys, label, color)]"""
    all_x = np.concatenate([np.asarray(s[0], float) for s in series if len(s[0])])
    all_y = np.concatenate([np.asarray(s[1], float) for s in series if len(s[1])])
    if xlim is None:
        xlim = (float(all_x.min()), float(all_x.max()))
    if ylim is None:
        lo, hi = float(all_y.min()), float(all_y.max())
        gap = max(hi - lo, 1e-6) * 0.12
        ylim = (lo - gap, hi + gap)
    f = Fig(w, h, title)
    f.frame(xlim, ylim, xlabel, ylabel, xticks, yticks, logx)
    for hval in hlines or []:
        _, py = f._px(xlim[0], hval, xlim, ylim, logx)
        f.d.line((f.x0, py, f.x1, py), fill=AMBER, width=1)
    for i, (xs, ys, lab, col) in enumerate(series):
        f.line(xs, ys, PALETTE[i % len(PALETTE)] if col is None else col, 2, xlim, ylim, logx)
    if legend and len(series) > 1:
        f.legend([(s[2], PALETTE[i % len(PALETTE)] if s[3] is None else s[3]) for i, s in enumerate(series)],
                 legend_pos)
    return f.save(path)


def scatter_chart(path, groups, xlabel="", ylabel="", title="", w=760, h=560):
    """groups: [(xs, ys, label, color)]"""
    all_x = np.concatenate([np.asarray(g[0], float) for g in groups])
    all_y = np.concatenate([np.asarray(g[1], float) for g in groups])
    gx = (all_x.max() - all_x.min()) * 0.1 + 1e-6
    gy = (all_y.max() - all_y.min()) * 0.1 + 1e-6
    xlim = (float(all_x.min() - gx), float(all_x.max() + gx))
    ylim = (float(all_y.min() - gy), float(all_y.max() + gy))
    f = Fig(w, h, title, pad=(78, 58, 30, 62))
    f.frame(xlim, ylim, xlabel, ylabel, 6, 6)
    for i, (xs, ys, lab, col) in enumerate(groups):
        c = PALETTE[i % len(PALETTE)] if col is None else col
        f.dots(xs, ys, c, 4, xlim, ylim)
    f.legend([(g[2], PALETTE[i % len(PALETTE)] if g[3] is None else g[3]) for i, g in enumerate(groups)], "tl")
    return f.save(path)


def bar_chart(path, labels, values, title="", ylabel="", w=940, h=430, colors=None, hline=None):
    f = Fig(w, h, title, pad=(78, 58, 24, 78))
    vals = np.asarray(values, float)
    ylim = (min(0.0, float(vals.min()) * 1.1), float(vals.max()) * 1.18 + 1e-9)
    x0, y0, x1, y1 = f.x0, f.y0, f.x1, f.y1
    f.d.rectangle((x0, y0, x1, y1), fill=PANEL, outline=BORDER, width=1)
    for i in range(6):
        y = y1 - (y1 - y0) * i / 5
        f.d.line((x0, y, x1, y), fill=GRID, width=1)
        s = _fmt(ylim[0] + (ylim[1] - ylim[0]) * i / 5)
        f.d.text((x0 - 8 - tw(f.d, s, 12), y - 8), s, font=font(12), fill=MUTED)
    slot = (x1 - x0) / len(labels)
    bw = min(slot * 0.6, 64)
    for i, (lab, v) in enumerate(zip(labels, vals)):
        cx = x0 + slot * (i + 0.5)
        yt = y1 - (v - ylim[0]) / (ylim[1] - ylim[0]) * (y1 - y0)
        c = (PALETTE[i % len(PALETTE)] if colors is None else colors[i])
        f.d.rectangle((cx - bw / 2, min(yt, y1), cx + bw / 2, y1), fill=c)
        f.d.text((cx - tw(f.d, _fmt(v), 12) / 2, min(yt, y1) - 18), _fmt(v), font=font(12), fill=TEXT)
        f.d.text((cx - tw(f.d, lab, 12) / 2, y1 + 9), lab, font=font(12), fill=MUTED)
    if hline is not None:
        yt = y1 - (hline - ylim[0]) / (ylim[1] - ylim[0]) * (y1 - y0)
        f.d.line((x0, yt, x1, yt), fill=AMBER, width=2)
        f.d.text((x1 - 110, yt - 18), f"基线 {_fmt(hline)}", font=font(12), fill=AMBER)
    f.d.text(((x0 + x1) / 2 - tw(f.d, ylabel, 13) / 2, f.h - 26), ylabel, font=font(13), fill=MUTED)
    return f.save(path)


def heatmap_chart(path, mat, title="", xlabel="", ylabel="", w=880, h=470,
                  cmap="inferno", vmin=None, vmax=None, extent=None, colorbar=True):
    a = np.asarray(mat, float)
    vmin = float(a.min()) if vmin is None else vmin
    vmax = float(a.max()) if vmax is None else vmax
    if vmax - vmin < 1e-12:
        vmax = vmin + 1e-12
    norm = np.clip((a - vmin) / (vmax - vmin), 0, 1)
    lut = _cmap_lut()
    idx = (norm * 255).astype(np.uint8)
    rgb = lut[idx]
    im = Image.fromarray(rgb, "RGB")
    f = Fig(w, h, title, pad=(80, 58, (96 if colorbar else 30), 62))
    px0, py0, px1, py1 = f.x0, f.y0, f.x1, f.y1
    im = im.resize((px1 - px0, py1 - py0), Image.NEAREST)
    f.img.paste(im, (px0, py0))
    f.d.rectangle((px0, py0, px1, py1), outline=BORDER, width=1)
    if extent is None:
        extent = (0, a.shape[1], a.shape[0], 0)
    for i in range(6):
        x = px0 + (px1 - px0) * i / 5
        f.d.line((x, py0, x, py1), fill=GRID, width=1)
        s = _fmt(extent[0] + (extent[1] - extent[0]) * i / 5)
        f.d.text((x - tw(f.d, s, 12) / 2, py1 + 8), s, font=font(12), fill=MUTED)
    for i in range(5):
        y = py0 + (py1 - py0) * i / 4
        s = _fmt(extent[2] + (extent[3] - extent[2]) * i / 4)
        f.d.text((px0 - 8 - tw(f.d, s, 12), y - 8), s, font=font(12), fill=MUTED)
    f.d.text(((px0 + px1) / 2 - tw(f.d, xlabel, 13) / 2, f.h - 26), xlabel, font=font(13), fill=MUTED)
    lab_max = max(tw(f.d, _fmt(extent[2] + (extent[3] - extent[2]) * i / 4), 12) for i in range(5))
    f.vtext(max(4, px0 - 8 - lab_max - int(13 * FONT_SCALE) - 14), (py0 + py1) / 2, ylabel)
    if colorbar:
        bx0, by0, bx1, by1 = px1 + 18, py0, px1 + 34, py1
        for j in range(by1 - by0):
            v = 1 - j / max(1, by1 - by0 - 1)
            f.d.line((bx0, by0 + j, bx1, by0 + j), fill=_inferno(v), width=1)
        f.d.rectangle((bx0, by0, bx1, by1), outline=BORDER, width=1)
        f.d.text((bx0 + 4, by0 - 20), _fmt(vmax), font=font(11), fill=MUTED)
        f.d.text((bx0 + 4, by1 + 4), _fmt(vmin), font=font(11), fill=MUTED)
    return f.save(path)


def table_image(path, headers, rows, title="", w=None, row_h=30, font_size=13):
    """把表格渲染成 PNG（中文安全）。rows 中元素可为 str/float。"""
    fsz = font_size
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    def s(v):
        return v if isinstance(v, str) else (f"{v:.4g}" if isinstance(v, (float, np.floating)) else str(v))
    cells = [[s(c) for c in r] for r in rows]
    widths = []
    for j, hd in enumerate(headers):
        m = tw(probe, str(hd), fsz)
        for r in cells:
            m = max(m, tw(probe, r[j], fsz))
        widths.append(m + 26)
    W = int(sum(widths) + 40) if w is None else w
    # 标题可能比表格宽，宽度至少容纳标题文字，避免标题被右边缘裁切
    if title:
        W = max(W, int(tw(probe, title, 16)) + 44)
    H = 52 + row_h * (len(rows) + 1) + 26
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((20, 14), title, font=font(16), fill=TEXT)
    x = 20
    y = 52
    d.rectangle((x, y, x + sum(widths), y + row_h), fill=HEADER)
    for j, hd in enumerate(headers):
        d.text((x + 12, y + (row_h - fsz) / 2 - 2), str(hd), font=font(fsz), fill=TEXT)
        x += widths[j]
    y += row_h
    for i, r in enumerate(cells):
        x = 20
        if i % 2 == 0:
            d.rectangle((x, y, x + sum(widths), y + row_h), fill=PANEL)
        for j, c in enumerate(r):
            d.text((x + 12, y + (row_h - fsz) / 2 - 2), c, font=font(fsz), fill=TEXT if j == 0 else MUTED)
            x += widths[j]
        d.line((20, y + row_h, x, y + row_h), fill=GRID, width=1)
        y += row_h
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    return path
