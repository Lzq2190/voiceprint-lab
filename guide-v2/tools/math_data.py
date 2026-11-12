# -*- coding: utf-8 -*-
"""
讲义公式数据层（第 3 版改造）。

FORMULAS[i] 对应 index.html 中第 i 个 <div class="eq">（1-based）。
每一项是 (latex, note)：
  latex 不为空 → 渲染成 KaTeX 展示公式，自动加 \tag{讲-序}
  latex 为 None → 这是「定义 / 流程 / 算例」而非公式，排成 .defbox

note 是公式下方的中文解释（HTML），保留原有信息并适当补全。
"""
import io, os, re

# 公式编号：按讲归组，(起始序号, 结束序号, 讲号)
GROUPS = [
    (1, 3, "1"), (4, 10, "2"), (11, 15, "3"), (16, 21, "4"),
    (22, 24, "5"), (25, 31, "6"), (32, 36, "7"), (37, 43, "8"),
    (44, 50, "9"), (51, 54, "10"), (55, 56, "11"), (57, 62, "12"),
    (63, 67, "13"), (68, 69, "14"), (70, 70, "15"),
]


def tag_for(i):
    for a, b, ch in GROUPS:
        if a <= i <= b:
            return "%s-%d" % (ch, i - a + 1)
    return "A-%d" % i


FORMULAS = {}

# ---------------------------------------------------------------- 第 1 讲 声音是什么
FORMULAS[1] = (
    None,
    r"""<div class="defbox"><div class="dh">符号约定</div>
<table class="sym"><tr><th>符号</th><th>含义</th><th>单位 / 取值</th></tr>
<tr><td>\(x(t)\)</td><td>时刻 \(t\) 的瞬时声压（相对大气压的微小起伏）</td><td>Pa（帕）</td></tr>
<tr><td>\(p_0\)</td><td>听阈参考声压，人耳 1 kHz 处刚能听见</td><td>\(2\times10^{-5}\,\mathrm{Pa}=20\,\mu\mathrm{Pa}\)</td></tr>
<tr><td>\(L_p\)</td><td>声压级（分贝表示法）</td><td>dB SPL</td></tr>
</table>
<p>工程上几乎不直接用 Pa，而是用 <b>声压级</b>：\(L_p=20\log_{10}\big(x_{\mathrm{rms}}/p_0\big)\)。之所以是 20 而不是 10，见本讲「推导详解」。</p></div>""")

FORMULAS[2] = (
    r"x(t)=A\sin\!\big(2\pi f t+\varphi\big)=A\sin\!\big(\tfrac{2\pi}{T}t+\varphi\big),\qquad T=\frac{1}{f}",
    r"""<div class="symgrid">
<div><b>\(A\)</b> 振幅（Pa）→ 决定<b>响度</b>；有效值 \(x_{\mathrm{rms}}=A/\sqrt{2}\)</div>
<div><b>\(f\)</b> 频率（Hz）→ 决定<b>音高</b>；角频率 \(\omega=2\pi f\)</div>
<div><b>\(\varphi\)</b> 初相位（rad）→ 单听纯音听不出，但多频率叠加时决定波形形状</div>
<div><b>\(T\)</b> 周期（s），一个完整振荡所需时间</div>
</div>""")

FORMULAS[3] = (
    r"x(t)=\sum_{k=1}^{K}A_k\sin\!\big(2\pi k f_0 t+\varphi_k\big)=A_1\sin(2\pi f_0t+\varphi_1)+A_2\sin(4\pi f_0t+\varphi_2)+\cdots",
    r"""<p>其中 \(f_0\) 是<b>基频</b>，\(kf_0\) 是第 \(k\) 次<b>谐波</b>，\(A_k,\varphi_k\) 是它的振幅与相位。
这就是<b>傅里叶级数</b>的思想：任何周期信号都能拆成一组整数倍频率的正弦。变压器本体振动以
\(f_0=100\,\mathrm{Hz}\)（工频 50 Hz 的两倍，因为磁致伸缩与电动势平方成正比）为基频，
故障会改变 \(A_2,A_3,\dots\) 的分布——这正是频域能诊断故障的物理依据。</p>""")

# ---------------------------------------------------------------- 第 2 讲 数字化
FORMULAS[4] = (
    r"x[n]\;\equiv\;x(nT_s)=x\!\left(\frac{n}{F_s}\right),\qquad T_s=\frac{1}{F_s},\quad n=0,1,\dots,N-1",
    r"""<p>\(F_s\) 是采样率（Hz），\(T_s\) 是采样间隔（s），\(N\) 是总点数，观测时长 \(T_{\mathrm{obs}}=NT_s=N/F_s\)。
例：\(F_s=8000\,\mathrm{Hz}\)、时长 \(0.5\,\mathrm{s}\) → \(N=F_sT=8000\times0.5=4000\) 点，\(T_s=0.125\,\mathrm{ms}\)。</p>""")

FORMULAS[5] = (
    r"F_s>2f_{\max}\quad\Longleftrightarrow\quad f_{\max}<\frac{F_s}{2}=f_{\mathrm{Nyq}}",
    r"""<p>\(f_{\mathrm{Nyq}}=F_s/2\) 称<b>奈奎斯特频率</b>。<b>本讲义 \(F_s=8\,\mathrm{kHz}\)，
所以有效期率上限是 \(4000\,\mathrm{Hz}\)</b>；再扣掉抗混叠滤波器的过渡带，工程可用带宽约 \(3.4\,\mathrm{kHz}\)。
注意这是「严格大于」：等号成立时若采样相位恰好落在过零点，信号会整体消失。</p>""")

FORMULAS[6] = (
    r"f_{\mathrm{alias}}=\min_{k\in\mathbb{Z}}\big|f-kF_s\big|\;\in\;[0,F_s/2]",
    r"""<p>取 \(k=1\) 的例子：\(f=1000\,\mathrm{Hz}\)、\(F_s=800\,\mathrm{Hz}\) →
\(|1000-800|=200\,\mathrm{Hz}\)，落在 \([0,400]\) 内，于是这个 1000 Hz 的信号被<b>永久误认</b>成 200 Hz。
关键是：<b>采样完成后信息已经丢失，增加采样点数、换更好的算法都救不回来</b>。
所以抗混叠必须是采样<b>之前</b>的模拟低通滤波，这是硬件责任，不是软件责任。</p>""")

FORMULAS[7] = (
    r"\mathrm{SNR}_{\mathrm{dB}}=10\log_{10}\frac{P_x}{P_q}\approx6.02\,B+1.76\quad(\text{满幅正弦输入})",
    r"""<p>\(B=16\) → \(6.02\times16+1.76\approx98\,\mathrm{dB}\)；\(B=8\) → \(\approx50\,\mathrm{dB}\)。
每多 1 bit 提高约 6 dB，这就是「一个比特 6 dB」的来历。完整推导见本讲「推导详解」。</p>""")

FORMULAS[8] = (
    None,
    r"""<div class="defbox"><div class="dh">分帧三参数</div>
<table class="sym"><tr><th>参数</th><th>定义</th><th>常用值</th></tr>
<tr><td>帧长 \(L\)</td><td>一帧包含的采样点数</td><td>20–30 ms（准平稳假设的窗口）</td></tr>
<tr><td>帧移 \(S\)</td><td>相邻两帧起点的间隔（hop）</td><td>10 ms</td></tr>
<tr><td>重叠 \(L-S\)</td><td>相邻帧共用的点数</td><td>50%–66%，即 \(S=L/2\sim L/3\)</td></tr>
</table>
<p>为什么必须分帧：语音/设备声的频谱随时间变化，但在一个短窗口内近似不变（<b>短时平稳</b>）。
窗太长会跨过变化点，窗太短则频率分辨率不够（见第 5 讲的不确定关系）。</p></div>""")

FORMULAS[9] = (
    r"L=\frac{t_{\mathrm{ms}}\,F_s}{1000},\qquad S=\frac{s_{\mathrm{ms}}\,F_s}{1000}",
    r"""<table class="sym compact"><tr><th>\(F_s\)</th><th>25 ms 帧长</th><th>10 ms 帧移</th></tr>
<tr><td>16000 Hz</td><td>\(25\times16000/1000=400\) 点</td><td>160 点</td></tr>
<tr><td>8000 Hz</td><td>\(25\times8000/1000=200\) 点</td><td>80 点</td></tr></table>""")

FORMULAS[10] = (
    r"M=\left\lfloor\frac{N-L}{S}\right\rfloor+1",
    r"""<p>例：\(N=16000\)（1 s @ 16 kHz）、\(L=400\)、\(S=160\) →
\(\lfloor(16000-400)/160\rfloor+1=\lfloor97.5\rfloor+1=97+1=98\) 帧。
最后一帧若不足 \(L\) 点，通常补零或丢弃；本讲义的 <code>frame_signal</code> 采用「丢弃不足帧」，
所以实际帧数会随实现略有差异，写代码时务必打印形状确认。</p>""")

# ---------------------------------------------------------------- 第 3 讲 时域特征
FORMULAS[11] = (
    r"E_m=\sum_{n=0}^{N-1}x_m^2[n],\qquad E_m^{\log}=\log\!\left(1+\frac{E_m}{a}\right)",
    r"""<p>第 \(m\) 帧、帧长 \(N\)。取对数是为了压缩动态范围：强信号与弱信号在同一个坐标里都看得见。
\(a\) 是防 \(\log 0\) 的小常数。注意能量对幅值增益敏感（幅度翻倍 → 能量变 4 倍），
所以跨设备比较前必须做幅度归一化。</p>""")

FORMULAS[12] = (
    r"Z_m=\frac{1}{2}\sum_{n=1}^{N-1}\big|\operatorname{sgn}(x_m[n])-\operatorname{sgn}(x_m[n-1])\big|",
    r"""<p>\(\operatorname{sgn}\) 为符号函数（正取 1、负取 −1、零取 0）。每穿越零点一次，
相邻两项之差的绝对值为 2，乘 \(1/2\) 恰好记一次过零。它是<b>区分清音/浊音、判断高频成分强弱</b>的粗指标，
对直流偏置和低频漂移敏感，因此通常只在预加重与去均值之后使用。</p>""")

FORMULAS[13] = (
    r"Z=2f\cdot\frac{N}{F_s}\quad\Longleftrightarrow\quad f=\frac{Z\,F_s}{2N},\qquad \frac{Z}{N}=\frac{2f}{F_s}",
    r"""<p>一个周期穿越零点两次，一帧时长 \(N/F_s\) 内包含 \(fN/F_s\) 个周期，故过零 \(2fN/F_s\) 次。
例：\(F_s=8000\)、\(N=200\)（25 ms）、\(f=500\,\mathrm{Hz}\) → \(Z=2\times500\times200/8000=25\) 次；
反推 \(f=25\times8000/(2\times200)=500\,\mathrm{Hz}\) ✓。归一化过零率 \(Z/N\) 直接正比于 \(f/F_s\)。</p>""")

FORMULAS[14] = (
    r"R_m(k)=\sum_{n=0}^{N-1-k}x_m[n]\,x_m[n+k],\qquad k=0,1,\dots,K",
    r"""<p>自相关衡量「信号与它自己平移 \(k\) 点之后有多像」。周期信号在 \(k\) 等于周期（及其整数倍）处出现峰值。
无偏版本会再除以 \(N-k\)，但那样在 \(k\) 大时噪声被放大，工程上常用上式（有偏估计）并配归一化
\(\rho(k)=R_m(k)/R_m(0)\)。</p>""")

FORMULAS[15] = (
    r"k_0=\mathop{\arg\max}_{k\in[k_{\min},k_{\max}]}\rho(k),\qquad f_0=\frac{F_s}{k_0}",
    r"""<p>例：\(F_s=8000\)，自相关在 \(k_0=80\) 处出现峰 → \(f_0=8000/80=100\,\mathrm{Hz}\) ✓（变压器基频）。
搜索区间要按目标基频范围设定：找 80–400 Hz 对应 \(k\in[20,100]\)；不设下界容易把 \(k=0\) 的
全局最大值（\(R(0)\) 恒等于能量）当成答案——这是最常见的实现 bug。</p>""")

# ---------------------------------------------------------------- 第 4 讲 傅里叶
FORMULAS[16] = (
    r"\left\langle e^{j2\pi f_1t},\,e^{j2\pi f_2t}\right\rangle=\int_{0}^{T}e^{j2\pi f_1t}\,\overline{e^{j2\pi f_2t}}\,\mathrm{d}t=0\quad(f_1\neq f_2)",
    r"""<p>复指数 \(e^{j2\pi ft}=\cos(2\pi ft)+j\sin(2\pi ft)\)（欧拉公式）就是「频率轴上的单位向量」，
不同频率彼此正交，所以「信号在频率 \(f\) 上的分量」＝信号与该频率复指数的内积。
离散情形下正交性由几何级数保证，完整推导见本讲「推导详解」。</p>""")

FORMULAS[17] = (
    r"""X[k]=\sum_{n=0}^{N-1}x[n]\,e^{-j\frac{2\pi kn}{N}}
=\sum_{n=0}^{N-1}x[n]\,W_N^{kn},\qquad W_N\;\equiv\;e^{-j2\pi/N},\quad k=0,\dots,N-1""",
    r"""<table class="sym"><tr><th>符号</th><th>含义</th></tr>
<tr><td>\(x[n]\)</td><td>第 \(n\) 个采样点（时域，实数或复数）</td></tr>
<tr><td>\(X[k]\)</td><td>第 \(k\) 个频率分量（频域，<b>复数</b>）；模长＝强度，辐角＝相位</td></tr>
<tr><td>\(W_N^{kn}\)</td><td>旋转因子（twiddle factor），第 \(k\) 个基函数在 \(n\) 处的值</td></tr>
<tr><td>\(f_k\)</td><td>第 \(k\) 根谱线的物理频率 \(f_k=kF_s/N\)，间隔 \(\Delta f=F_s/N\)</td></tr>
</table>
<p>逐项翻译：对每个 \(k\)，把整段信号与第 \(k\) 个复正弦<b>逐点相乘再求和</b>。含该频率则同号居多、求和结果大；
不含则正负相消、结果近 0。逆变换为 \(x[n]=\frac{1}{N}\sum_{k=0}^{N-1}X[k]e^{j2\pi kn/N}\)——
注意 \(1/N\) 只在逆变换一侧，这个约定决定了后面幅度谱要乘 \(2/N\)。</p>""")

FORMULAS[18] = (
    r"""\begin{aligned}
X[0]&=1+0+1+0=2\\
X[1]&=1\cdot1+0\cdot(-j)+1\cdot(-1)+0\cdot j=1-1=0\\
X[2]&=1\cdot1+0\cdot(-1)+1\cdot1+0\cdot(-1)=2\\
X[3]&=1\cdot1+0\cdot j+1\cdot(-1)+0\cdot(-j)=0
\end{aligned}\quad\Rightarrow\quad X=[2,\,0,\,2,\,0]""",
    r"""<p>取 \(x=[1,0,1,0]\)、\(N=4\)，基函数在 4 个点上的取值只有 \(1,-j,-1,j\)。
怎么读：\(X[0]=2\) 是直流（均值 \(\times N=0.5\times4=2\) ✓）；\(X[2]=2\) 对应
\(f=2F_s/4=F_s/2\)，正是「1,0,1,0」的交替频率；\(X[1]=X[3]=0\) 说明没有其他成分。
<b>DFT 只是把信号往每个频率上射一次影</b>。</p>""")

FORMULAS[19] = (
    r"A[k]=\begin{cases}\dfrac{|X[0]|}{N},&k=0\\[6pt]\dfrac{2\,|X[k]|}{N},&1\le k<N/2\end{cases}",
    r"""<p>实信号的频谱共轭对称：\(X[N-k]=\overline{X[k]}\)，负频率没有独立信息，只看前 \(N/2+1\) 根谱线。
幅度为 \(A\) 的实正弦 \(A\sin(2\pi f t)\) 由 \(\pm f\) 两个复指数各分到 \(A/2\)，
DFT 求和后每侧模长为 \(AN/2\)，因此乘 \(2/N\) 才还原成 \(A\)。
例：幅值 1.0、\(N=1024\) → \(|X[k]|\approx512\) → \(A=2\times512/1024=1.0\) ✓。
忘了这个归一化就会得出「信号幅值 512 Pa」的荒谬结论。</p>""")

FORMULAS[20] = (
    r"""\Delta f_{\mathrm{true}}=\frac{1}{T_{\mathrm{obs}}}=\frac{F_s}{N_{\text{original}}},\qquad
\Delta f_{\mathrm{display}}=\frac{F_s}{M}\;\;(M\ge N_{\text{original}})""",
    r"""<p>把 256 点补零到 1024 点，谱线从 31.25 Hz 变「密」到 7.8 Hz，但<b>分辨能力没变</b>：
补零只是对同一条连续频谱曲线做更细的插值采样。本来糊在一起的两个峰，补零后仍糊在一起，只是多画了几个点。
要分辨间隔 5 Hz 的两个成分，观测时长至少 \(1/5=0.2\,\mathrm{s}\)——这就是声纹分析用
0.2–1 s 片段而不是单帧 25 ms 的原因。</p>""")

FORMULAS[21] = (
    r"C_{\mathrm{DFT}}=N^2,\qquad C_{\mathrm{FFT}}=\frac{N}{2}\log_2 N",
    r"""<table class="sym compact"><tr><th>\(N\)</th><th>DFT 复数乘法</th><th>FFT</th><th>加速比</th></tr>
<tr><td>1024</td><td>\(1\,048\,576\)</td><td>\(5\,120\)</td><td>≈ 205×</td></tr>
<tr><td>8192</td><td>\(6.7\times10^{7}\)</td><td>\(5.3\times10^{4}\)</td><td>≈ 1260×</td></tr></table>
<p>实时系统要求 FFT 长度取 2 的幂，不是数学要求，而是 Cooley–Tukey 分治要能一直二分下去。</p>""")

# ---------------------------------------------------------------- 第 5 讲 时频
FORMULAS[22] = (
    r"X[m,k]=\sum_{n=-\infty}^{\infty}x[n]\,w[n-mS]\,e^{-j\frac{2\pi kn}{N}}",
    r"""<p>\(m\)：帧号（时间轴）；\(k\)：谱线号（频率轴）；\(w[\cdot]\)：窗函数；\(S\)：帧移。
输出是二维复数矩阵，尺寸 \(M\times(N/2+1)\)。取模后取对数就是<b>语谱图</b>。
与 DFT 的唯一差别是多了 \(w[n-mS]\)：把无限长信号截成局部，代价是频谱泄漏（窗的频域旁瓣）。</p>""")

FORMULAS[23] = (
    r"""\Delta t\approx\frac{L}{F_s},\qquad \Delta f\approx\frac{F_s}{L},\qquad
\Delta t\cdot\Delta f\approx1\;\;\left(\text{严格界：}\Delta t\,\Delta f\ge\frac{1}{4\pi}\right)""",
    r"""<p>这是海森堡不确定原理在工程上的形态：窗长 \(L\) 同时决定时间分辨率和频率分辨率，
<b>不可能同时变小</b>。\(L=200\) 点 @8 kHz → \(\Delta t=25\,\mathrm{ms}\)、\(\Delta f=40\,\mathrm{Hz}\)；
\(L=800\) 点 → \(\Delta t=100\,\mathrm{ms}\)、\(\Delta f=10\,\mathrm{Hz}\)。
选窗就是选一个折中：要抓「敲击的瞬间」用短窗，要分辨「100 Hz 与 120 Hz」用长窗。</p>""")

FORMULAS[24] = (
    r"S_{\mathrm{dB}}[m,k]=20\log_{10}\!\big(|X[m,k]|+\varepsilon\big)",
    r"""<p>线性幅度下，强基频会把弱谐波完全压成一条平线；取 20 log 后动态范围被压缩，
40 dB 的差距在图上变成「一格半」的灰度差，弱结构才看得见。
为什么是 20 log：功率 \(\propto\) 幅度平方，\(10\log_{10}(A^2)=20\log_{10}A\)。
\(\varepsilon\) 取 \(10^{-10}\) 量级，防止 \(\log 0=-\infty\)。</p>""")

# ---------------------------------------------------------------- 第 6 讲 MFCC
FORMULAS[25] = (
    r"""y[n]=x[n]-\alpha\,x[n-1],\qquad H(z)=1-\alpha z^{-1},\quad
\big|H(e^{j\omega})\big|^2=(1-\alpha)^2+4\alpha\sin^2\!\frac{\omega}{2}""",
    r"""<p>\(\alpha\) 通常取 0.95–0.97。这是<b>一阶高通</b>，约 6 dB/倍频程，
用来抵消口唇辐射造成的高频衰减（语音）。<b>但设备声纹要慎用</b>：变压器判别信息集中在
100 Hz 基频及其低次谐波，预加重会把这一段相对压低，等于扔掉主要特征。
本讲义流程中默认 \(\alpha=0.95\) 仅用于演示，实际设备诊断建议 \(\alpha=0\) 或 0.5 以下。</p>""")

FORMULAS[26] = (
    r"P[k]=\frac{\big|X[k]\big|^2}{N},\qquad k=0,1,\dots,\frac{N}{2}",
    r"""<p>流程：帧长 25 ms、帧移 10 ms、汉明窗（第 2 讲）→ 每帧做 \(N\) 点 FFT
（\(N=256\) 或 512，补零到 2 的幂）→ 取模平方并除以 \(N\) 得功率谱。
以 8 kHz、25 ms（200 点）、补零到 256 为例，得 129 根谱线，间隔 \(8000/256=31.25\,\mathrm{Hz}\)。</p>""")

FORMULAS[27] = (
    r"""m(f)=2595\log_{10}\!\left(1+\frac{f}{700}\right),\qquad
f(m)=700\left(10^{m/2595}-1\right)""",
    r"""<p>例：\(f=0\to0\) mel；\(f=1000\,\mathrm{Hz}\to2595\log_{10}(2.4286)\approx1000\) mel（巧合）；
\(f=4000\,\mathrm{Hz}\to2595\log_{10}(6.714)\approx2146\) mel。
700 Hz 是经验折点：低于它对频率近似线性，高于它近似对数。
在 Mel 轴上等间隔放 \(M\) 个三角滤波器，映射回 Hz 后<b>低频窄而密、高频宽而疏</b>，正好模仿人耳。</p>""")

FORMULAS[28] = (
    r"""E_m=\sum_{k=0}^{N/2}P[k]\,H_m[k],\qquad
H_m(k)=\begin{cases}
0,&k< f_{m-1}\\[3pt]
\dfrac{k-f_{m-1}}{f_m-f_{m-1}},&f_{m-1}\le k<f_m\\[9pt]
\dfrac{f_{m+1}-k}{f_{m+1}-f_m},&f_m\le k\le f_{m+1}\\[9pt]
0,&k>f_{m+1}
\end{cases}""",
    r"""<p>\(f_{m-1},f_m,f_{m+1}\) 是第 \(m\) 个三角滤波器的左端点、中心、右端点（已换算到 FFT 谱线索引），
且相邻滤波器重叠 50%，保证 \(\sum_m H_m[k]=1\)（能量不凭空增减）。
这一步把 129 根谱线压成 26 个数，同时完成「降维 + 按听觉加权」。
频率到谱线索引的换算是 \(k=fN/F_s\)，写错这个是最常见的 off-by-one 来源。</p>""")

FORMULAS[29] = (
    r"L_m=\ln\!\big(E_m+\varepsilon\big)",
    r"""<p>两个理由。<b>感知上</b>：人耳对响度的响应近似对数（这正是 dB 存在的原因）。
<b>工程上</b>：声源与信道在时域是卷积 \(x*h\)，频域变相乘 \(X\cdot H\)，取对数后变<b>相加</b>
\(\log|X\cdot H|=\log|X|+\log|H|\)，信道影响退化成一个加性常量，
后面的倒谱均值归一化（CMN）可以直接把它减掉。这一步是「倒谱」名称的由来
（cepstrum = spectrum 前四个字母倒过来），也是<b>同态信号处理</b>的核心。</p>""")

FORMULAS[30] = (
    r"""c_i=\sqrt{\frac{2}{M}}\sum_{m=1}^{M}L_m\cos\!\left[\frac{\pi i}{M}\left(m-\tfrac12\right)\right],
\qquad i=0,1,\dots,M-1""",
    r"""<p>这是 DCT-II 型（正交归一化版本）。\(c_0\) 反映总能量（对增益敏感，常丢弃或单独用），
\(c_1\dots c_{12}\) 反映频谱包络的形状，通常保留前 13 个系数。
为什么有效：Mel 对数谱是一条平滑曲线，能量集中在「倒频率」低的系数上——
前几个系数就描述了整条包络，后面的对应快速起伏（多为噪声）。丢掉后面的既降维又降噪。
DCT 与 PCA 目的一样（去相关 + 能量集中），但基是固定余弦、不需从数据里学，所以极快且换数据集不用重算。</p>""")

FORMULAS[31] = (
    r"""d_t=\frac{\displaystyle\sum_{n=1}^{N}n\big(c_{t+n}-c_{t-n}\big)}
{2\displaystyle\sum_{n=1}^{N}n^2}
\;\xrightarrow{\;N=2\;}\;
\frac{(c_{t+1}-c_{t-1})+2(c_{t+2}-c_{t-2})}{10}""",
    r"""<p>这不是简单相减，而是对局部窗口做<b>最小二乘直线拟合后的斜率</b>：
用 \(\pm n\) 对称的样本估计 \(\partial c/\partial t\)，分母 \(2\sum n^2\) 正是正规方程的解。
\(N=2\) 时分母 \(2(1^2+2^2)=10\)。二阶差分 \(dd_t\) 即对 \(d_t\) 再做一次同样运算。
维度：13 静态 + 13 一阶 \(\Delta\) + 13 二阶 \(\Delta\Delta\) = <b>39 维</b>。</p>""")

# ---------------------------------------------------------------- 第 7 讲 小波与 EMD
FORMULAS[32] = (
    r"""W(a,b)=\int_{-\infty}^{\infty}x(t)\,\frac{1}{\sqrt{a}}\,
\overline{\psi\!\left(\frac{t-b}{a}\right)}\,\mathrm{d}t,\qquad a>0""",
    r"""<p>\(\psi\) 是<b>母小波</b>：一小段振荡、两端衰减到 0、且均值为零
（容许条件 \(C_\psi=\int|\hat\psi(\omega)|^2/|\omega|\,\mathrm{d}\omega<\infty\)）。
\(a\) 是<b>尺度</b>：\(a\) 大 → 小波被拉宽 → 看低频；\(b\) 是<b>平移</b>：直接对应时间位置。
前面的 \(1/\sqrt a\) 是能量归一化，保证不同尺度下的系数可直接比较。
与 STFT 的根本差别：STFT 窗宽固定，CWT 的窗宽随 \(a\) 自动变——<b>低频用长窗、高频用短窗</b>。</p>""")

FORMULAS[33] = (
    r"f\approx\frac{f_c\,F_s}{a},\qquad f_c=\frac{\text{母小波中心频率(归一化)}}{T_s}",
    r"""<p>例：\(F_s=8000\)、Morlet 的 \(f_c\approx0.8125\) →
\(a=8\Rightarrow f\approx812\,\mathrm{Hz}\)；\(a=80\Rightarrow f\approx81\,\mathrm{Hz}\)。
尺度轴是 \(1/f\) 关系，所以画 CWT 图时若把 \(a\) 当线性频率轴标注，会把 100 Hz 错标成 900 Hz——
本讲义配套代码曾踩过这个坑，修法是先把尺度对应的频率算出来，再重采样到线性频率轴。</p>""")

FORMULAS[34] = (
    r"""\begin{aligned}
cA_{j+1}[n]&=\sum_{k}h[k-2n]\,cA_j[k],&
cD_{j+1}[n]&=\sum_{k}g[k-2n]\,cA_j[k]\\
x[n]&=\sum_{k}\tilde h[n-2k]\,cA_J[k]+\sum_{j=1}^{J}\sum_{k}\tilde g[n-2k]\,cD_j[k]
\end{aligned}""",
    r"""<p>这是 <b>Mallat 塔式算法</b>：\(h\) 低通、\(g\) 高通，两者后跟 \(\downarrow2\) 降采样。
第 1 层 \(x\to cA_1\)（近似）+ \(cD_1\)（细节），第 2 层再分解 \(cA_1\)，
3 层后得到 \(cA_3+cD_3+cD_2+cD_1\)，可以<b>无损重构</b>回原信号。
正交/双正交小波满足 \(A^{\mathsf T}A=I\)，所以重构就是分析算子的转置 \(A^{\mathsf T}\)。
配套项目里 db4 的重构曾因把 \(A^{\mathsf T}\) 误写成另一套卷积相位而产生 1.40 的误差，
改成显式转置后降到 \(10^{-12}\) 量级——这正是「公式要落到代码」的反面教材。</p>""")

FORMULAS[35] = (
    None,
    r"""<div class="defbox"><div class="dh">本征模态函数（IMF）的两个判定条件</div>
<ol><li>极值点个数与过零点个数相差不超过 1（保证没有叠加的骑行波）；</li>
<li>上包络（局部极大值拟合）与下包络（局部极小值拟合）的<b>均值为 0</b>（局部对称）。</li></ol>
<p>满足这两条的分量才有明确的瞬时频率，才能做 Hilbert 谱。EMD 不需要预设基函数，
是<b>数据驱动</b>的自适应分解，适合非线性、非平稳信号；代价是没有正交性保证、且对噪声敏感（模态混叠）。</p></div>""")

FORMULAS[36] = (
    None,
    r"""<div class="defbox"><div class="dh">EMD 筛分（sifting）流程</div>
<ol><li>找出 \(x\) 的所有局部极大值、极小值；</li>
<li>用三次样条插值连成上包络 \(e_{\max}\) 与下包络 \(e_{\min}\)；</li>
<li>求均值包络 \(m=(e_{\max}+e_{\min})/2\)；</li>
<li>令 \(h=x-m\)，判断 \(h\) 是否满足 IMF 两条件；不满足则把 \(h\) 当作新的 \(x\) 回到 ①；</li>
<li>满足则记为一个 IMF，令残差 \(r=x-\mathrm{IMF}\)，对 \(r\) 继续下一轮；</li>
<li>残差变单调、或极值点少于 2 个时停止，最后得到 \(x=\sum_j \mathrm{IMF}_j+r\)。</li></ol>
<p>停止准则常用「连续两次筛分的标准差 \(\mathrm{SD}=\sum_t|h_{k-1}(t)-h_k(t)|^2/\sum_t h_{k-1}^2(t)<0.2\sim0.3\)」，
过筛会抹掉振幅调制信息，欠筛则 IMF 不够对称。端点效应需用镜像延拓抑制。</p></div>""")

# ---------------------------------------------------------------- 第 8 讲 BPNN
FORMULAS[37] = (
    r"""z=\sum_{i=1}^{d}w_i x_i+b=\mathbf w^{\mathsf T}\mathbf x+b,\qquad
a=\sigma(z)=\frac{1}{1+e^{-z}},\qquad \sigma'(z)=a(1-a)""",
    r"""<p>sigmoid 输出 \((0,1)\)，可解释为概率；其导数能直接用输出值算，这是它早年流行的原因。
但 \(|z|\) 大时 \(\sigma'\to0\)，多层连乘会造成<b>梯度消失</b>，所以现代隐含层多用 ReLU
\(\sigma_{\mathrm{ReLU}}(z)=\max(0,z)\)。</p>""")

FORMULAS[38] = (
    r"""\begin{aligned}
\mathbf z_1&=W_1\mathbf x+\mathbf b_1,& \mathbf h&=\sigma(\mathbf z_1)\\
\mathbf z_2&=W_2\mathbf h+\mathbf b_2,&
p_c&=\frac{e^{z_{2,c}}}{\sum_{j}e^{z_{2,j}}}\quad(\mathrm{softmax})
\end{aligned}""",
    r"""<p>输入 \(\mathbf x\) 是 39 维 MFCC 统计量（对整段语音各维取均值/标准差），
\(W_1\in\mathbb R^{H\times39}\)、\(W_2\in\mathbb R^{C\times H}\)。
softmax 把任意实数得分压成和为 1 的概率分布；实现时要减去 \(\max_j z_{2,j}\) 防溢出，
因为 \(e^{z-\max}\) 不会超过 1（平移不改变 softmax 结果）。</p>""")

FORMULAS[39] = (
    r"""L(\mathbf p,\mathbf y)=-\sum_{c=1}^{C}y_c\ln p_c=-\ln p_{c^*}
\quad(\mathbf y\ \text{为 one-hot})""",
    r"""<p>交叉熵来自极大似然：把标签看成真实分布，最小化 \(-\ln p_{c^*}\) 等价于最大化正确类的似然。
用交叉熵配 softmax 的关键好处是梯度里<b>不含 \(\sigma'\)</b>（见下式），
不会像「均方误差 + sigmoid」那样在错得很离谱时反而梯度趋零、学不动。</p>""")

FORMULAS[40] = (
    r"""\boldsymbol\delta_2\equiv\frac{\partial L}{\partial\mathbf z_2}=\mathbf p-\mathbf y,
\qquad \frac{\partial L}{\partial z_{2,c}}=p_c-y_c""",
    r"""<p>推导：\(\frac{\partial L}{\partial z_{2,i}}=
\sum_c\frac{\partial L}{\partial p_c}\frac{\partial p_c}{\partial z_{2,i}}\)，
其中 \(\frac{\partial p_c}{\partial z_{2,i}}=p_c(\delta_{ci}-p_i)\)，
代入 \(L=-\sum_c y_c\ln p_c\) 并用 \(\sum_c y_c=1\) 即得 \(p_i-y_i\)。
例：三类 \(p=[0.7,0.2,0.1]\)、\(y=[0,1,0]\) → \(\delta_2=[0.7,-0.8,0.1]\)：
预测比标签大的往下压（正梯度），比标签小的往上抬（负梯度）。</p>""")

FORMULAS[41] = (
    r"""\begin{aligned}
\frac{\partial L}{\partial W_2}&=\boldsymbol\delta_2\,\mathbf h^{\mathsf T},&
\frac{\partial L}{\partial\mathbf b_2}&=\boldsymbol\delta_2\\
\boldsymbol\delta_1&=\big(W_2^{\mathsf T}\boldsymbol\delta_2\big)\odot\sigma'(\mathbf z_1),&
\frac{\partial L}{\partial W_1}&=\boldsymbol\delta_1\,\mathbf x^{\mathsf T},\quad
\frac{\partial L}{\partial\mathbf b_1}=\boldsymbol\delta_1
\end{aligned}""",
    r"""<p>\(\odot\) 是逐元素乘（Hadamard 积）。每个梯度都是「<b>上游误差 × 本层输入</b>」的外积，
形状自动与权重矩阵一致——这是检查反向传播写对没有的第一道关。
\(\sigma'(\mathbf z_1)=\mathbf h\odot(1-\mathbf h)\) 可复用前向缓存，不必重算指数。
参数更新：\(W\leftarrow W-\eta\,\partial L/\partial W\)，\(\eta\) 为学习率。</p>""")

FORMULAS[42] = (
    r"""\begin{aligned}
z&=0.5(1)-0.5(2)+0=-0.5,& p&=\sigma(-0.5)=0.3775\\
L&=-\ln 0.3775=0.9741,& \delta&=p-y=-0.6225\\
\partial L/\partial\mathbf w&=\delta\mathbf x=[-0.6225,\,-1.2450],&
\partial L/\partial b&=-0.6225\\
\mathbf w_{\text{new}}&=\mathbf w-\eta\,\partial L/\partial\mathbf w=[0.5623,\,-0.3755]
\end{aligned}""",
    r"""<p>输入 \(\mathbf x=[1,2]\)、\(\mathbf w=[0.5,-0.5]\)、\(b=0\)、\(y=1\)、\(\eta=0.1\)。
再前向一次：\(z'=0.5623\times1-0.3755\times2=-0.1887\)，\(p'=\sigma(-0.1887)=0.4530\)，
\(L'=0.7919<0.9741\) ✓ <b>损失确实下降了</b>。
这个「手算一轮、确认损失变小」的习惯，比跑通十次训练更能建立对反向传播的信任。</p>""")

FORMULAS[43] = (
    r"""\frac{\partial L}{\partial w_i}\approx
\frac{L(\mathbf w+\varepsilon\mathbf e_i)-L(\mathbf w-\varepsilon\mathbf e_i)}{2\varepsilon},
\qquad \varepsilon\sim10^{-5},\ \text{截断误差 }O(\varepsilon^2)""",
    r"""<p>中心差分由泰勒展开 \(L(w\pm\varepsilon)=L(w)\pm\varepsilon L'(w)+\frac{\varepsilon^2}{2}L''(w)\pm
\frac{\varepsilon^3}{6}L'''(w)+\cdots\) 相减得到，偶次项自动抵消，所以误差是 \(O(\varepsilon^2)\)，
而前向差分只有 \(O(\varepsilon)\)。<b>梯度检查</b>：把解析梯度与上式逐元素比较。
配套项目实测绝对误差 \(<10^{-10}\)；若某元素相对误差看着大，先检查它是不是接近 0 的极小量
（例如 \(-2.03\times10^{-6}\) 会把相对误差放大到 \(5\times10^{-6}\)，但绝对误差只有 \(10^{-11}\)，不是 bug）。</p>""")

# ---------------------------------------------------------------- 第 9 讲 CNN
FORMULAS[44] = (
    r"y[i,j]=\sum_{p=0}^{F-1}\sum_{q=0}^{F-1}x[i+p,\,j+q]\,K[p,q]+b",
    r"""<p>\(K\) 是 \(F\times F\) 卷积核，\(b\) 是偏置。严格说深度学习里做的是<b>互相关</b>而非数学卷积
（少了核翻转），但因为 \(K\) 是学出来的，翻转与否不影响表达能力。
两个归纳偏置：<b>局部连接</b>（只看邻域）与<b>权值共享</b>（同一核扫全图）。</p>""")

FORMULAS[45] = (
    r"""H_{\mathrm{out}}=\left\lfloor\frac{H_{\mathrm{in}}-F+2P}{S}\right\rfloor+1,\qquad
W_{\mathrm{out}}=\left\lfloor\frac{W_{\mathrm{in}}-F+2P}{S}\right\rfloor+1""",
    r"""<p>核最后一个位置是 \(H_{\mathrm{in}}-F+2P\)，从 0 出发每次走 \(S\)，故位置数为
\(\lfloor(H_{\mathrm{in}}-F+2P)/S\rfloor+1\)。
例：\(32\times32\)、\(F=3\)、\(P=1\)、\(S=1\) → 32（尺寸不变，称 <code>same</code> padding）；
\(P=0,S=2\) → \(\lfloor29/2\rfloor+1=15\)（下采样）。</p>""")

FORMULAS[46] = (
    r"N_{\mathrm{param}}=\big(F\times F\times C_{\mathrm{in}}+1\big)\times C_{\mathrm{out}}",
    r"""<p>每个核有 \(F^2C_{\mathrm{in}}\) 个权重 + 1 个偏置，共 \(C_{\mathrm{out}}\) 个核。
例：1 通道、4 个 \(3\times3\) 核 → \((9+1)\times4=40\) 个参数。
对比全连接 \(1024\to1000\) 需 \(1\,025\,000\) 个参数，相差约 25000 倍——
这就是 CNN 在小样本上不容易过拟合的根本原因。</p>""")

FORMULAS[47] = (
    r"""y^{\max}_{i,j}=\max_{0\le p,q<2}x[2i+p,\,2j+q],\qquad
y^{\mathrm{avg}}_{i,j}=\frac{1}{4}\sum_{p,q}x[2i+p,\,2j+q]""",
    r"""<p>\(2\times2\)、步长 2 → 空间尺寸减半。池化<b>没有可学参数</b>，作用是降维并获得一定的平移不变性。
反向传播时最大池化要把梯度<b>只回传给前向取到最大值的那个位置</b>（需保存 argmax 掩码），
平均池化则把梯度均分给 4 个位置。</p>""")

FORMULAS[48] = (
    r"\mathrm{RF}_k=\mathrm{RF}_{k-1}+(F_k-1)\prod_{j=1}^{k-1}S_j,\qquad \mathrm{RF}_1=F_1",
    r"""<p>逐层：1 层 \(3\times3\) → 3；2 层 → \(3+(3-1)=5\)；3 层 → \(5+(3-1)=7\)。
若中间有步长 2，前面各层的步长要乘进增量。感受野决定「一个输出神经元能看到多长的时间/多大的图」，
必须覆盖目标模式的尺度：想让网络看见 100 Hz 基频的一个完整周期（10 ms），
在 8 kHz 下至少要覆盖 80 个采样点。</p>""")

FORMULAS[49] = (
    r"""X_{\mathrm{col}}\in\mathbb R^{(C F^2)\times(H_{\mathrm{out}}W_{\mathrm{out}})},\qquad
W_{\mathrm{col}}\in\mathbb R^{C_{\mathrm{out}}\times(C F^2)},\qquad
Y=W_{\mathrm{col}}X_{\mathrm{col}}""",
    r"""<p><b>im2col</b>：把输入 \((C,H,W)\) 中所有 \(F\times F\) 小块拉成列，拼成大矩阵；
卷积核展开成行。于是「滑动卷积」变成<b>一次 GEMM 矩阵乘法</b>，可以直接吃 BLAS 优化。
输出 reshape 回 \((C_{\mathrm{out}},H_{\mathrm{out}},W_{\mathrm{out}})\)。
代价是内存放大约 \(F^2\) 倍（重叠块被复制），这是典型的「以空间换时间」。</p>""")

FORMULAS[50] = (
    r"""\frac{\partial L}{\partial W_{\mathrm{col}}}=\frac{\partial L}{\partial Y}\,X_{\mathrm{col}}^{\mathsf T},
\qquad
\frac{\partial L}{\partial X_{\mathrm{col}}}=W_{\mathrm{col}}^{\mathsf T}\frac{\partial L}{\partial Y}
\;\xrightarrow{\ \mathrm{col2im}\ }\;\frac{\partial L}{\partial X}""",
    r"""<p>既然前向是一次矩阵乘，反向就是第 8 讲那套「上游误差 × 本层输入」的外积公式。
唯一额外工作是 <code>col2im</code>：把列的梯度<b>累加</b>回原位置（重叠处要相加，不能覆盖）。
配套项目的 <code>col2im</code> 若忘记累加，梯度检查会在重叠区域先出错——这类 bug 用数值梯度一测就现形。</p>""")

# ---------------------------------------------------------------- 第 10 讲 训练
FORMULAS[51] = (
    None,
    r"""<div class="defbox"><div class="dh">三集合划分（严格隔离）</div>
<table class="sym"><tr><th>集合</th><th>占比</th><th>唯一用途</th></tr>
<tr><td>训练集</td><td>60%</td><td>计算梯度、更新参数</td></tr>
<tr><td>验证集</td><td>20%</td><td>选超参数（学习率、层数、早停轮数）</td></tr>
<tr><td>测试集</td><td>20%</td><td><b>只在最后用一次</b>，报告最终性能</td></tr>
</table>
<p>划分必须在提取特征<b>之前</b>按「说话人 / 设备编号」分组做，不能按帧随机切：
同一段录音的相邻帧高度相关，随机切会让测试集里混进训练集的近似副本，指标虚高。</p></div>""")

FORMULAS[52] = (
    None,
    r"""<div class="defbox"><div class="dh">从损失曲线读诊断</div>
<table class="sym"><tr><th>现象</th><th>结论</th><th>对策</th></tr>
<tr><td>训练损失持续下降，验证损失先降后升</td><td><b>过拟合</b></td><td>早停、L2、dropout、增数据</td></tr>
<tr><td>训练与验证损失都很高</td><td><b>欠拟合</b></td><td>加大模型、多训几轮、查特征与学习率</td></tr>
<tr><td>损失震荡不降甚至 NaN</td><td>学习率过大 / 梯度爆炸</td><td>降 \(\eta\)、梯度裁剪、检查归一化</td></tr>
</table></div>""")

FORMULAS[53] = (
    r"""\mathrm{Acc}=\frac{TP+TN}{TP+TN+FP+FN},\quad
P=\frac{TP}{TP+FP},\quad R=\frac{TP}{TP+FN},\quad
F_1=\frac{2PR}{P+R}""",
    r"""<p>精确率 \(P\) 回答「报了警的里面有多少是真故障」（少误报）；召回率 \(R\) 回答
「真故障里抓到了多少」（少漏报）。\(F_1\) 是两者调和平均，比算术平均更惩罚偏科：
\(P=1,R=0.1\) 时算术平均 0.55，\(F_1\) 只有 0.18。
类别不平衡时（故障样本远少于正常）准确率会骗人：全判「正常」也能有 95% 准确率，
所以必须同时看 \(P,R,F_1\)。</p>""")

FORMULAS[54] = (
    r"""\mathrm{FPR}=\frac{FP}{FP+TN},\qquad
\mathrm{TPR}=\frac{TP}{TP+FN}=R,\qquad
\mathrm{AUC}=\int_0^1\mathrm{TPR}(\mathrm{FPR})\,\mathrm{d}\,\mathrm{FPR}""",
    r"""<p>ROC 曲线：横轴 FPR、纵轴 TPR，扫阈值得到；\(\mathrm{AUC}=0.5\) 是随机猜，\(1.0\) 是完美，<b>越大越好</b>。
<div class="warn inline"><span class="t">注意这是陷阱</span>上面是<b>机器学习教材</b>的画法。
声纹领域传统用 DET 曲线（横轴 FA、纵轴 FR 的递减曲线，常用正态偏差刻度），AUC <b>越小越好</b>；
第 12 讲会专门讲这套评价体系和阈值的代价模型。</div></p>""")

# ---------------------------------------------------------------- 第 11 讲 概览
FORMULAS[55] = (
    None,
    r"""<div class="defbox"><div class="dh">两个方向相反的任务</div>
<table class="sym"><tr><th>任务</th><th>想知道</th><th>要保留</th><th>要滤掉</th></tr>
<tr><td>语音识别 ASR</td><td>说了<b>什么</b></td><td>文本内容</td><td>说话人身份</td></tr>
<tr><td>声纹识别 SR</td><td><b>谁</b>说的</td><td>说话人身份</td><td>文本内容</td></tr>
</table>
<p>两者要抑制的变量恰好互为对方的信号，所以说它们「正交」。这也解释了为什么 MFCC 在两边都能用：
它保留的是声道的<b>形状</b>（共振峰），既承载音素也承载说话人生理特征，靠后续模型决定用哪部分。</p></div>""")

FORMULAS[56] = (
    None,
    r"""<div class="defbox"><div class="dh">一次完整验证的三段式</div>
<ol><li><b>注册 enrollment</b>：用户说几段话 → 提特征 → 训练/存储该用户的模型或一个 embedding 向量；</li>
<li><b>测试 test</b>：说一段话 → 提特征 → 与库中模型逐一比较 → 得到相似度分数 \(s\)；</li>
<li><b>判决 decision</b>：\(s>\theta\) 则接受，否则拒绝；\(\theta\) 由代价模型或目标 EER 选定。</li></ol>
<p>对应两种任务：<b>确认</b>（1:1，答案「是/否」，需要阈值）与<b>辨识</b>（1:N，取分数最高者，闭集无需阈值）。</p></div>""")

# ---------------------------------------------------------------- 第 12 讲 评价指标
FORMULAS[57] = (
    r"""\mathrm{FAR}(\theta)=\frac{N_{\mathrm{FA}}(\theta)}{N_{\mathrm{impostor}}},\qquad
\mathrm{FRR}(\theta)=\frac{N_{\mathrm{FR}}(\theta)}{N_{\mathrm{target}}}""",
    r"""<p><b>FA</b>（False Accept，误受）：把冒充者当成本人 → 安全风险；
<b>FR</b>（False Reject，误拒）：把本人拦在门外 → 体验问题。
两者都是阈值 \(\theta\) 的函数，且<b>单调方向相反</b>：\(\theta\) 调严 → FA↓ 但 FR↑。
这条此消彼长的关系决定了不存在「同时为零」的阈值，必须引入代价（见式 12-5）。</p>""")

FORMULAS[58] = (
    r"""\theta_{\mathrm{EER}}=\mathop{\arg\min}_{\theta}\big|\mathrm{FAR}(\theta)-\mathrm{FRR}(\theta)\big|,
\qquad \mathrm{EER}=\mathrm{FAR}(\theta_{\mathrm{EER}})=\mathrm{FRR}(\theta_{\mathrm{EER}})""",
    r"""<p>EER 越小系统越好。实际分数是离散的，两条阶梯曲线往往不严格相交，
工程做法是在交叉区间对 FAR、FRR 分别做<b>线性插值</b>再求交点，而不是取最接近的采样点。
EER 的优点是<b>与阈值无关</b>，可以跨系统比较；缺点是它默认 FA 与 FR 代价相等，
而真实门禁场景里放进一个冒充者往往比拒一次本人严重得多。</p>""")

FORMULAS[59] = (
    r"P_{\mathrm{err}}\big|_{\mathrm{EER}}=\tfrac12\mathrm{FAR}+\tfrac12\mathrm{FRR}=\mathrm{EER}",
    r"""<p>澄清一个常见误读：EER = 5% <b>不等于</b>「10% 的测试会判错」。
若真实试验与冒充试验数量相等，总错误率 \(=\tfrac12\mathrm{FAR}+\tfrac12\mathrm{FRR}=\mathrm{EER}=5\%\)。
但厂商常按「误识率 5%」宣传，用户在<b>先验不均衡</b>（冒充尝试远多于本人，或反之）时的实际感受会不同：
设 \(P_{\mathrm{target}}=0.01\)，则总错误率 \(=0.01\times0.05+0.99\times0.05=5\%\) 仍相同，
真正影响体感的是<b>错误落在哪一边</b>——1 次误放和 1 次误拒给人的代价完全不同，所以要 DCF。</p>""")

FORMULAS[60] = (
    r"""C_{\mathrm{det}}(\theta)=C_{\mathrm{FR}}\,\mathrm{FRR}(\theta)\,P_{\mathrm{target}}
+C_{\mathrm{FA}}\,\mathrm{FAR}(\theta)\,P_{\mathrm{nontarget}},\qquad
\mathrm{DCF}=\min_{\theta}\frac{C_{\mathrm{det}}(\theta)}{C_{\mathrm{default}}}""",
    r"""<p>\(C_{\mathrm{FR}}\)：漏掉一个真人的代价；\(C_{\mathrm{FA}}\)：放进一个冒充者的代价；
\(P_{\mathrm{target}}+P_{\mathrm{nontarget}}=1\) 是先验。
\(C_{\mathrm{default}}=\min(C_{\mathrm{FR}}P_{\mathrm{target}},\,C_{\mathrm{FA}}P_{\mathrm{nontarget}})\)
是「永远拒绝 / 永远接受」两种平凡策略中较好的那个，用它归一化后 \(\mathrm{DCF}\le1\)，
1 表示系统毫无价值。NIST SRE 常用 \(C_{\mathrm{FR}}=C_{\mathrm{FA}}=1\)、\(P_{\mathrm{target}}=0.01\)。</p>""")

FORMULAS[61] = (
    r"""\begin{aligned}
\theta_1 &: C_{\mathrm{det}}=1(0.02)(0.9)+10(0.05)(0.1)=0.018+0.050=0.068\\
\theta_2 &: C_{\mathrm{det}}=1(0.08)(0.9)+10(0.01)(0.1)=0.072+0.010=0.082
\end{aligned}""",
    r"""<p>设 \(C_{\mathrm{FR}}=1,\ C_{\mathrm{FA}}=10,\ P_{\mathrm{target}}=0.9\)。
阈值 \(\theta_1\)（FA=0.05, FR=0.02）得 0.068；更严格的 \(\theta_2\)（FA=0.01, FR=0.08）反而得 0.082，
<b>更差</b>。原因：本场景里真人占 90%，把 FR 从 2% 抬到 8% 带来的损失（0.054）
远大于把 FA 从 5% 压到 1% 省下的（0.040）。<b>阈值不是越严越好，是让代价最小才好。</b></p>""")

FORMULAS[62] = (
    r"""s'=\frac{s-\mu_{\mathrm{imp}}}{\sigma_{\mathrm{imp}}},\qquad
s''=\frac{s-\mu_{\mathrm{cohort}}(x)}{\sigma_{\mathrm{cohort}}(x)}""",
    r"""<p><b>z-norm</b>：用一批冒充者语音对该<b>目标模型</b>打分，估计 \(\mu,\sigma\) 后归一化，消除模型间的分数尺度差异；
<b>t-norm</b>：用该条<b>测试语音</b>对一批背景模型打分后归一化，消除测试语音本身的「难易」差异；
<b>zt-norm / s-norm</b>：两者串联或对称化，通常最稳，代价是需要额外的冒认/背景数据与约 2 倍计算量。
归一化的本质是把「绝对分数」变成「在同类分数分布中的相对位置」，从而让全局阈值 \(\theta\) 可用。</p>""")

# ---------------------------------------------------------------- 第 13 讲 经典方法
FORMULAS[63] = (
    r"""p(\mathbf x\mid\lambda)=\sum_{c=1}^{C}\pi_c\,\mathcal N(\mathbf x\mid\boldsymbol\mu_c,\Sigma_c),\qquad
\sum_c\pi_c=1""",
    r"""<p>\(\lambda=\{\pi_c,\boldsymbol\mu_c,\Sigma_c\}_{c=1}^{C}\)：混合权重、均值、协方差；
\(\mathcal N(\mathbf x\mid\boldsymbol\mu,\Sigma)=\dfrac{1}{\sqrt{(2\pi)^d|\Sigma|}}
\exp\!\left[-\tfrac12(\mathbf x-\boldsymbol\mu)^{\mathsf T}\Sigma^{-1}(\mathbf x-\boldsymbol\mu)\right]\)。
GMM 用多个高斯的加权和逼近任意形状的分布。声纹里通常取对角协方差（\(C=512\sim2048\)），
因为 39 维特征全协方差的参数量与过拟合风险都太高。</p>""")

FORMULAS[64] = (
    r"""\begin{aligned}
\text{E: }\;&\gamma_{tc}=\frac{\pi_c\mathcal N(\mathbf x_t\mid\boldsymbol\mu_c,\Sigma_c)}
{\sum_{j}\pi_j\mathcal N(\mathbf x_t\mid\boldsymbol\mu_j,\Sigma_j)}\\[5pt]
\text{M: }\;&\pi_c\leftarrow\frac{\sum_t\gamma_{tc}}{T},\quad
\boldsymbol\mu_c\leftarrow\frac{\sum_t\gamma_{tc}\mathbf x_t}{\sum_t\gamma_{tc}},\quad
\Sigma_c\leftarrow\frac{\sum_t\gamma_{tc}(\mathbf x_t-\boldsymbol\mu_c)(\mathbf x_t-\boldsymbol\mu_c)^{\mathsf T}}{\sum_t\gamma_{tc}}
\end{aligned}""",
    r"""<p>\(\gamma_{tc}\) 是「第 \(t\) 帧属于第 \(c\) 个高斯」的<b>责任度</b>（后验概率）。
EM 通过构造对数似然的下界（ELBO）并交替优化：E 步固定参数算责任度，M 步固定责任度做加权极大似然，
每轮保证似然不降，迭代到收敛。实现必须在<b>对数域</b>做（log-sum-exp 技巧），
否则 512 个高斯的密度连乘会直接下溢为 0。初始化用 k-means，否则易陷入局部最优。</p>""")

FORMULAS[65] = (
    r"""\hat{\boldsymbol\mu}_c=\alpha_c\,\boldsymbol\mu_c^{\mathrm{data}}+(1-\alpha_c)\,\boldsymbol\mu_c^{\mathrm{UBM}},
\qquad \alpha_c=\frac{n_c}{n_c+r},\quad n_c=\sum_t\gamma_{tc}""",
    r"""<p><b>UBM-MAP 自适应</b>：先用大量不同说话人的数据训一个通用背景模型（描述「人类语音的通用分布」），
再用目标说话人的少量数据把 UBM 的均值往数据方向拉。\(r\) 是相关性因子（常取 16）：
某高斯分到的帧数 \(n_c\) 少 → \(\alpha_c\) 小 → 更信任 UBM；数据多才敢偏离。
这解决了「每个说话人只有几秒数据、训不出 2048 个高斯」的根本困难，是 GMM-UBM 时代的基石。</p>""")

FORMULAS[66] = (
    r"""\mathbf M=\mathbf m+T\mathbf w,\qquad
\mathbf w\sim\mathcal N(\mathbf 0,I),\quad
\mathbf w=(I+T^{\mathsf T}\Sigma^{-1}T)^{-1}T^{\mathsf T}\Sigma^{-1}(\mathbf M-\mathbf m)""",
    r"""<p>\(\mathbf M\)：说话人的<b>超矢量</b>（把 UBM 所有高斯均值拼起来，\(2048\times39\approx 19968\) 维）；
\(\mathbf m\)：UBM 的超矢量（所有人共用）；\(T\)：<b>总变化空间</b>矩阵（约 \(19968\times400\)），从大量数据学出；
\(\mathbf w\)：<b>i-vector</b>（400 维），即新的说话人表示。
后验均值那一步是贝叶斯线性高斯模型的闭式解（\(400\times400\) 求逆，与超矢量维度无关，所以很快）。
i-vector 同时包含身份与信道信息，打分前要用 LDA/WCCN 去信道、再用 PLDA 或余弦打分。</p>""")

FORMULAS[67] = (
    r"\mathbf w=\boldsymbol\mu+V\mathbf y+U\mathbf x+\boldsymbol\varepsilon",
    r"""<p>这是 JFA（联合因子分析）的分解，也是 i-vector 的思想来源：\(\mathbf y\) 是<b>身份因子</b>
（同一人所有录音共享），\(\mathbf x\) 是<b>信道因子</b>（同一段录音内共享），\(V,U\) 是对应子空间，
\(\boldsymbol\varepsilon\) 是残差。i-vector 的简化在于：不再区分 \(V,U\)，用一个总变化空间 \(T\)
把两者一起建模，再用 LDA/PLDA 在后端把信道抹掉。<b>「先都装进来，再在打分时消掉」</b>是这一代方法的核心思路。</p>""")

# ---------------------------------------------------------------- 第 14 讲 深度学习
FORMULAS[68] = (
    r"""\boldsymbol\mu=\frac{1}{T}\sum_{t=1}^{T}\mathbf h_t,\qquad
\boldsymbol\sigma=\sqrt{\frac{1}{T}\sum_{t=1}^{T}(\mathbf h_t-\boldsymbol\mu)^2},\qquad
\mathbf e=[\boldsymbol\mu;\,\boldsymbol\sigma]""",
    r"""<p>输入是 MFCC \((\;T\text{ 帧}\times39\text{ 维}\;)\)，\(T\) 不固定。
TDNN 前几层逐帧变换并利用上下文（类似一维卷积、跨层连接）得到 \(\mathbf h_t\)；
<b>统计池化</b>把任意长度 \(T\) 压成固定长度的 \(\mathbf e\)（\(2\times\)隐层维），
这是整条流水线能处理变长语音的关键。标准差项不是装饰：它携带了「帧间离散程度」信息，
实测比只用均值明显更好。之后接全连接 → 512 维 embedding → softmax 分类。</p>""")

FORMULAS[69] = (
    r"""\text{A：}\;\hat c=\arg\max_c p_c,\qquad
\text{B：}\;s=\cos(\mathbf e_1,\mathbf e_2)=\frac{\mathbf e_1^{\mathsf T}\mathbf e_2}{\|\mathbf e_1\|\,\|\mathbf e_2\|},\;\;s>\theta?""",
    r"""<p><b>范式 A（分类）</b>：softmax 输出固定类别，适合「几种已知工况」；
<b>范式 B（度量）</b>：训练 embedding，测试时算余弦/PLDA 分数再比阈值，适合「类别会变」
（新用户注册、未知故障），也是声纹确认的标准做法。
训练 B 常用 AAM-Softmax：\(L=-\log\dfrac{e^{s(\cos(\theta_{y}+m)-\cdots)}}{\cdots}\)，
在角度上加 margin \(m\) 迫使同类更紧、异类更开。</p>""")

# ---------------------------------------------------------------- 第 15 讲 收尾
FORMULAS[70] = (
    None,
    r"""<div class="defbox"><div class="dh">三道出师关</div>
<ol><li><b>能讲</b>：合上讲义，向别人解释「为什么 MFCC 要取 log」。讲不清 = 只记住流程，没理解原因。</li>
<li><b>能写</b>：不看现成代码，写出能与 numpy 对拍到 \(10^{-10}\) 的 DFT。写不出 = 公式还停在纸面上。</li>
<li><b>能改</b>：给定新需求（如「要在 10 dB 噪声下识别局放」），能说出该改哪个环节、预期会怎样、怎么验证。
说不出 = 还不会用，只会复现。</li></ol></div>""")
