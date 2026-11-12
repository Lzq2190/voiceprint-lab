# -*- coding: utf-8 -*-
r"""
重建 guide-v2/index.html（第 3 版：公式用 KaTeX 排版 + 每讲推导详解）。

用法：python tools/rebuild_guide.py
  · 先把当前 index.html 备份到 tools/backup/index_v2.html（只备份一次）
  · 把 70 个 <div class="eq"> 换成 .mathbox / .defbox
  · 在每讲「误区与注意事项」前插入「推导详解」区块
  · 把正文里残留的 ASCII 行内公式换成 \(...\)
  · 注入本地 KaTeX 的 CSS/JS 与 auto-render
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GUIDE = os.path.dirname(HERE)
SRC = os.path.join(GUIDE, "index.html")
BACKUP_DIR = os.path.join(HERE, "backup")
BACKUP = os.path.join(BACKUP_DIR, "index_v2.html")

sys.path.insert(0, HERE)
from math_data import FORMULAS, tag_for          # noqa: E402
from exp_a import EXP_A                           # noqa: E402
from exp_b import EXP_B                           # noqa: E402
from exp_c import EXP_C                           # noqa: E402

EXPANSIONS = {}
EXPANSIONS.update(EXP_A)
EXPANSIONS.update(EXP_B)
EXPANSIONS.update(EXP_C)

# ---------------------------------------------------------------- 新增样式
EXTRA_CSS = r"""
/* ============ 第 3 版：KaTeX 公式与推导详解 ============ */
.katex { color: var(--text); font-size: 1.06em; }
.mathbox{margin:18px 0 20px;border:1px solid var(--border);border-radius:10px;overflow:hidden;background:#141b28}
.mathbox .math{padding:16px 20px;text-align:center;overflow-x:auto;overflow-y:hidden;background:#111827;
  border-bottom:1px solid var(--border)}
.mathbox .math .katex-display{margin:.2em 0}
.mathbox .mathnote{padding:12px 20px;font-size:14px;color:var(--muted);line-height:1.75}
.mathbox .mathnote p{margin:6px 0}
.mathbox .mathnote strong,.mathbox .mathnote b{color:var(--text)}
.mathbox .mathnote .symgrid{margin:6px 0}
.defbox{background:#161f2e;border-left:3px solid var(--accent2);border-radius:8px;
  padding:12px 18px;margin:16px 0;font-size:14.5px}
.defbox .dh{font-weight:700;color:var(--accent2);margin-bottom:8px;font-size:15px}
.defbox p{margin:8px 0}
.defbox ol{margin:8px 0;padding-left:22px}
.defbox li{margin:5px 0}
.symgrid{display:grid;grid-template-columns:1fr 1fr;gap:6px 18px;margin:8px 0;font-size:14px}
.symgrid>div{background:var(--panel2);border-radius:6px;padding:7px 11px}
.symgrid b{color:var(--accent2)}
table.sym{border-collapse:collapse;width:100%;margin:10px 0;font-size:13.8px}
table.sym th,table.sym td{border:1px solid var(--border);padding:6px 10px;vertical-align:top}
table.sym th{background:#202a3a;color:#fff;font-size:13.2px}
table.sym td:first-child{white-space:nowrap;color:#ffd580;font-family:Consolas,monospace}
table.sym.compact td{text-align:center}
.warn.inline{background:#2a1d1d;border-left:3px solid var(--red);padding:9px 13px;
  border-radius:6px;margin:9px 0;font-size:13.8px}
.warn.inline .t{font-weight:700;color:var(--red);margin-right:5px}
/* 推导详解区 */
.derive{margin:28px 0 8px;border:1px solid #31507d;border-radius:12px;
  background:linear-gradient(180deg,#16223a 0,#141c2b 100%);padding:6px 24px 20px}
.derive .dtitle{font-size:16px;font-weight:700;color:#8fc0ff;letter-spacing:.02em;
  margin:18px 0 6px;padding-bottom:9px;border-bottom:1px solid #2c466c}
.derive h4{font-size:15px;color:var(--accent2);margin:22px 0 8px;
  padding-left:10px;border-left:3px solid var(--accent2)}
.derive p{font-size:14.6px;line-height:1.85;color:#d7e0ee}
.derive ul,.derive ol{font-size:14.6px;line-height:1.85;color:#d7e0ee;padding-left:22px}
.derive li{margin:7px 0}
.derive .math.sub{margin:13px 0;background:#0e1624;border:1px solid #2a3b57;
  border-radius:8px;padding:13px 16px;text-align:center;overflow-x:auto}
.derive .math.sub .katex-display{margin:.2em 0}
.derive pre{background:#0b0f16;font-size:12.8px}
.derive table.sym{margin:12px 0}
.derive .warn{font-size:14px}
.derive strong,.derive b{color:#fff}
.mathnote code,.derive code,.defbox code{background:#222d3f;color:#ffd580}
@media (max-width:900px){.symgrid{grid-template-columns:1fr}.derive{padding:4px 14px 16px}}
"""

# ---------------------------------------------------------------- head / body 注入
KATEX_HEAD = r"""<link rel="stylesheet" href="assets/katex/katex.min.css">
<script src="assets/katex/katex.min.js"></script>
<script src="assets/katex/contrib/auto-render.min.js"></script>
"""

KATEX_BODY = r"""<script>
document.addEventListener("DOMContentLoaded", function () {
  if (typeof renderMathInElement === "function") {
    renderMathInElement(document.body, {
      delimiters: [
        {left: "\\[", right: "\\]", display: true},
        {left: "\\(", right: "\\)", display: false}
      ],
      ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code", "option"],
      throwOnError: false
    });
  }
});
</script>
"""

# ---------------------------------------------------------------- 行内 ASCII 公式
INLINE = {
    r"<code>Δf = Fs/N</code>": r"\(\Delta f=F_s/N\)",
    r"<code>x(t)=A·sin(2πft+φ)</code>": r"\(x(t)=A\sin(2\pi ft+\varphi)\)",
    r"<code>2πf</code>": r"\(2\pi f\)",
    r"<code>T = 1/f</code>": r"\(T=1/f\)",
    r"<code>Ts = 1/Fs</code>": r"\(T_s=1/F_s\)",
    r"<code>ZCR = 2f/Fs</code>": r"\(Z/N=2f/F_s\)",
    r"<code>Z = 2fN/Fs</code>": r"\(Z=2fN/F_s\)",
    r"<code>e^(jθ) = cosθ + j·sinθ</code>": r"\(e^{j\theta}=\cos\theta+j\sin\theta\)",
    r"<code>e^(j2πft)</code>": r"\(e^{j2\pi ft}\)",
    r"<code>a=(1,0)</code>": r"\(\mathbf a=(1,0)\)",
    r"<code>b=(0,1)</code>": r"\(\mathbf b=(0,1)\)",
    r"<code>mel(f)=2595·log₁₀(1+f/700)</code>": r"\(m(f)=2595\log_{10}(1+f/700)\)",
    r"<code>x = Σ IMF_i + r</code>": r"\(x=\sum_i \mathrm{IMF}_i+r\)",
    r"<code>f ≈ Fs/a</code>": r"\(f\approx f_cF_s/a\)",
    r"<code>∂L/∂W = aᵀ·δ</code>": r"\(\partial L/\partial W=\mathbf a^{\mathsf T}\boldsymbol\delta\)",
    r"<code>W₂(W₁x) = (W₂W₁)x</code>": r"\(W_2(W_1\mathbf x)=(W_2W_1)\mathbf x\)",
    r"<code>δ₂ = ∂L/∂z₂ = p − y</code>": r"\(\boldsymbol\delta_2=\partial L/\partial\mathbf z_2=\mathbf p-\mathbf y\)",
    r"<code>∂L/∂W₁</code>": r"\(\partial L/\partial W_1\)",
    r"<code>∂L/∂W₂ = δ₂hᵀ</code>": r"\(\partial L/\partial W_2=\boldsymbol\delta_2\mathbf h^{\mathsf T}\)",
    r"<code>δ₁ = (W₂ᵀδ₂)⊙σ′(z₁)</code>": r"\(\boldsymbol\delta_1=(W_2^{\mathsf T}\boldsymbol\delta_2)\odot\sigma'(\mathbf z_1)\)",
    r"<code>C_det = C_FR·FR·P_T + C_FA·FA·P_I</code>": r"\(C_{\det}=C_{\mathrm{FR}}\mathrm{FRR}P_{\mathrm{tar}}+C_{\mathrm{FA}}\mathrm{FAR}P_{\mathrm{nontarget}}\)",
    r"<code>Σ_t log p(x_t|λ)</code>": r"\(\sum_t\ln p(\mathbf x_t\mid\lambda)\)",
    r"<code>512 × 39 = 19968</code>": r"\(512\times39=19968\)",
    r"<code>M = m + T·w</code>": r"\(\mathbf M=\mathbf m+T\mathbf w\)",
    r"<code>X[N−k] = conj(X[k])</code>": r"\(X[N-k]=\overline{X[k]}\)",
    r"<code>Fs / N</code>": r"\(F_s/N\)",
}

# 正文中不带 <code> 的裸公式（出现频率高、写法固定）
BARE = {
    r"<b>Δf = Fs / N</b>": r"<b>\(\Delta f=F_s/N\)</b>",
    r"<b>Δf = Fs/N</b>": r"<b>\(\Delta f=F_s/N\)</b>",
    r"<code>Δf_display = Fs / M</code>": r"\(\Delta f_{\mathrm{display}}=F_s/M\)",
}


# ---------------------------------------------------------------- 公式净化
def sanitize_tex(t):
    """LaTeX 里的裸 < > 必须换成 \\lt \\gt，否则 HTML 解析器会把 <f_m 当标签吃掉。"""
    # 后面必须留空格，否则 \gtf 会被解析成一条叫 "\gtf" 的命令
    return t.replace("<", r"\lt ").replace(">", r"\gt ")


_DISPLAY = re.compile(r"(\\\[ )(.*?)( \\\])", re.S)
_INLINE = re.compile(r"(\\\()(.*?)(\\\))", re.S)


def sanitize_block(html_str):
    """只净化 HTML 片段中数学定界符内部的内容，不动任何 HTML 标签。"""
    html_str = _DISPLAY.sub(lambda m: m.group(1) + sanitize_tex(m.group(2)) + m.group(3),
                            html_str)
    html_str = _INLINE.sub(lambda m: m.group(1) + sanitize_tex(m.group(2)) + m.group(3),
                           html_str)
    return html_str


# ---------------------------------------------------------------- 公式替换
def formula_html(i, latex, note):
    tag = tag_for(i)
    if latex is None:
        return sanitize_block(note.strip())
    return ('<div class="mathbox">\n'
            '<div class="math">\\[ %s \\tag{%s} \\]</div>\n'
            '<div class="mathnote">%s</div>\n'
            '</div>' % (sanitize_tex(latex.strip()), tag,
                        sanitize_block(note.strip())))


def replace_equations(src):
    counter = [0]

    def sub(m):
        counter[0] += 1
        i = counter[0]
        if i not in FORMULAS:
            raise RuntimeError("公式块 %d 缺少映射：%s" % (i, m.group(1)[:60]))
        latex, note = FORMULAS[i]
        return formula_html(i, latex, note)

    out = re.sub(r'<div class="eq">(.*?)</div>', sub, src, flags=re.S)
    if counter[0] != len(FORMULAS):
        raise RuntimeError("公式块数量不符：HTML 中 %d 个，映射表 %d 条"
                           % (counter[0], len(FORMULAS)))
    return out


# ---------------------------------------------------------------- 插入推导详解
def insert_derivations(src):
    pieces = re.split(r'(?=<section id="s\d+">)', src)
    out = []
    used = set()
    for seg in pieces:
        m = re.match(r'<section id="(s\d+)">', seg)
        if not m:
            out.append(seg)
            continue
        sid = m.group(1)
        raw_block = EXPANSIONS.get(sid)
        if not raw_block:
            out.append(seg)
            continue
        block = sanitize_block(raw_block)
        anchor = "<h3>误区与注意事项</h3>"
        if anchor in seg:
            seg = seg.replace(anchor, block.strip() + "\n\n  " + anchor, 1)
        else:
            # 没有误区标题：插在自检之前，再不行就插在 </section> 前
            for alt in ("<h3>自检</h3>", "</section>"):
                if alt in seg:
                    seg = seg.replace(alt, block.strip() + "\n\n  " + alt, 1)
                    break
        used.add(sid)
        out.append(seg)
    missing = set(EXPANSIONS) - used
    if missing:
        raise RuntimeError("未找到插入位置：%s" % sorted(missing))
    return "".join(out)


def main():
    # 幂等：始终从备份的原始 v2 版重建，避免二次运行重复注入
    if os.path.exists(BACKUP):
        src = io.open(BACKUP, encoding="utf-8").read()
        print("从备份读取原始讲义：tools/backup/index_v2.html")
    else:
        src = io.open(SRC, encoding="utf-8").read()
        os.makedirs(BACKUP_DIR, exist_ok=True)
        io.open(BACKUP, "w", encoding="utf-8").write(src)
        print("已备份 → tools/backup/index_v2.html")
    print("原始大小：%d 字符，%d 个公式块" % (len(src), src.count('class="eq"')))

    out = replace_equations(src)
    out = insert_derivations(out)

    for a, b in list(BARE.items()) + list(INLINE.items()):
        out = out.replace(a, b)

    out = out.replace("</style>", EXTRA_CSS + "\n</style>")
    out = out.replace("</head>", KATEX_HEAD + "</head>")
    out = out.replace("</body>", KATEX_BODY + "</body>")

    # 封面说明补充
    out = out.replace(
        "配套 <code>acoustic-lab</code> 复现项目",
        "全部公式由 KaTeX 排版并按「讲-序」编号，每讲末尾附<b>推导详解</b>（符号表、逐步推导、数值算例、代码对应、失效条件）。"
        "配套 <code>acoustic-lab</code> 复现项目")

    io.open(SRC, "w", encoding="utf-8").write(out)
    print("完成：%d 字符，mathbox %d 个，defbox %d 个，推导详解 %d 块" % (
        len(out), out.count('class="mathbox"'), out.count('class="defbox"'),
        out.count('class="derive"')))


if __name__ == "__main__":
    main()
