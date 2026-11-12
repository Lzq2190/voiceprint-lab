# -*- coding: utf-8 -*-
"""推导详解扩展内容：第 1–6 讲。每块插在该讲「误区与注意事项」之前。"""

EXP_A = {}

EXP_A["s1"] = r"""
<div class="derive">
<div class="dtitle">推导详解 · 第 1 讲　声音、分贝与复指数</div>

<h4>1. 符号对照表</h4>
<table class="sym"><tr><th>符号</th><th>含义</th><th>单位</th><th>本讲义典型值</th></tr>
<tr><td>\(x(t)\)</td><td>瞬时声压</td><td>Pa</td><td>\(10^{-3}\sim1\)</td></tr>
<tr><td>\(p_0\)</td><td>听阈参考声压</td><td>Pa</td><td>\(2\times10^{-5}\)</td></tr>
<tr><td>\(A\)</td><td>峰值振幅</td><td>Pa</td><td>1（归一化信号）</td></tr>
<tr><td>\(f_0\)</td><td>基频</td><td>Hz</td><td>100（变压器）、80–300（人声）</td></tr>
<tr><td>\(\omega\)</td><td>角频率</td><td>rad/s</td><td>\(2\pi f\)</td></tr>
<tr><td>\(c\)</td><td>声速</td><td>m/s</td><td>343（20 ℃ 空气）</td></tr>
</table>

<h4>2. 为什么分贝前面是 20 而不是 10</h4>
<p>声压是<b>幅度量</b>，声强（单位面积功率）正比于声压的平方：\(I=p^2/(\rho c)\)，其中 \(\rho\) 为空气密度、\(\rho c\) 为声阻抗。分贝的定义针对的是<b>功率比</b>：</p>
<div class="math sub">\[ L=10\log_{10}\frac{I}{I_0}=10\log_{10}\frac{p^2}{p_0^2}=10\log_{10}\left(\frac{p}{p_0}\right)^2=20\log_{10}\frac{p}{p_0} \tag{1-4} \]</div>
<p>所以「20」来自平方，不是另一个约定。同理，幅度谱画 dB 时也是 \(20\log_{10}|X|\)，而功率谱画 dB 时用 \(10\log_{10}P\)——因为 \(P=|X|^2\) 已经是功率量。<b>混用这两者是频谱图最常见的标定错误</b>。</p>
<p>数值例：把幅值降到原来的 \(1/10\) → \(20\log_{10}(0.1)=-20\,\mathrm{dB}\)；降到 \(1/\sqrt2\) → \(-3.01\,\mathrm{dB}\)（这就是 −3 dB 半功率点的来历）。</p>

<h4>3. 为什么一定要引入复数：欧拉公式把两个实数合成一个</h4>
<div class="math sub">\[ e^{j\theta}=\cos\theta+j\sin\theta,\qquad \cos\theta=\frac{e^{j\theta}+e^{-j\theta}}{2},\qquad \sin\theta=\frac{e^{j\theta}-e^{-j\theta}}{2j} \tag{1-5} \]</div>
<p>一个实正弦需要<b>振幅 + 相位</b>两个实数描述，或用<b>一个复数</b> \(X=|X|e^{j\varphi}\) 描述。用复指数的好处是：求导、相乘、平移都变成指数运算，不必反复套三角恒等式。例如把信号延迟 \(n_0\) 点：</p>
<div class="math sub">\[ x[n-n_0]\;\xleftrightarrow{\ \mathrm{DFT}\ }\;X[k]\,e^{-j2\pi kn_0/N},\qquad \big|e^{-j2\pi kn_0/N}\big|=1 \tag{1-6} \]</div>
<p>即时延<b>只改相位、不改幅度谱</b>。这条性质解释了为什么声纹特征常丢掉相位：录音起点不同、麦克风距离不同，相位全变，但幅度谱稳。</p>

<h4>4. 谐波叠加：一个算到底的例子</h4>
<p>设 \(f_0=100\,\mathrm{Hz}\)、\(A_1=1\)、\(A_2=0.5\)、\(A_3=0.2\)，相位全为 0。在 \(t=2.5\,\mathrm{ms}\)（即 \(2\pi f_0t=\pi/2\)）处：</p>
<div class="math sub">\[ \begin{aligned}
x(t)&=\sin(\pi/2)+0.5\sin(\pi)+0.2\sin(3\pi/2)\\
&=1+0-0.2=0.8
\end{aligned} \tag{1-7} \]</div>
<p>把 \(\varphi_2\) 从 0 改成 \(\pi/2\)，第二项变成 \(0.5\sin(\pi+\pi/2)=-0.5\)，于是 \(x(t)=1-0.5-0.2=0.3\)。<b>三个振幅没变、功率谱没变，波形却明显不同</b>——这就是「相位决定波形形状、幅度谱决定能量分布」的具体含义，也是后面 MFCC 只用幅度谱的代价与理由。</p>

<h4>5. 公式 ↔ 代码</h4>
<pre><code># 式(1-2)：单频正弦
t = np.arange(N) / fs
x = A * np.sin(2 * np.pi * f * t + phi)

# 式(1-3)：谐波叠加（K 次）
x = sum(A[k] * np.sin(2*np.pi*(k+1)*f0*t + ph[k]) for k in range(K))

# 式(1-4)：声压级
Lp = 20 * np.log10(np.sqrt(np.mean(x**2)) / 2e-5 + 1e-12)</code></pre>
<p><code>acoustic-lab/src/dsp.py</code> 里的 <code>make_signal()</code> 就是上面三行，六类故障信号的差别只在 \(A_k\) 的取值（正常以 100 Hz 为主；直流偏磁额外加 150/250/350 Hz 的奇次倍频）。</p>

<h4>6. 边界与失效条件</h4>
<ul><li>\(A\) 超过 ADC 满量程 → <b>削波</b>，波形被削平，凭空产生大量高次谐波，频谱里出现本不存在的峰。任何后续分析都救不回来。</li>
<li>叠加只是<b>线性</b>模型；声压很大、传播距离很远时会出现非线性失真，此时 \(A_k\) 不再独立。</li>
<li>「相位听不出来」只对<b>单个稳态纯音</b>成立；多分量叠加、瞬态、双耳定位时相位是可听的。</li></ul>
</div>
"""

EXP_A["s2"] = r"""
<div class="derive">
<div class="dtitle">推导详解 · 第 2 讲　采样定理、混叠与量化噪声</div>

<h4>1. 符号对照表</h4>
<table class="sym"><tr><th>符号</th><th>含义</th><th>单位</th><th>本讲义取值</th></tr>
<tr><td>\(F_s\)</td><td>采样率</td><td>Hz</td><td>8000</td></tr>
<tr><td>\(T_s\)</td><td>采样间隔 \(1/F_s\)</td><td>s</td><td>0.000125</td></tr>
<tr><td>\(f_{\mathrm{Nyq}}\)</td><td>奈奎斯特频率</td><td>Hz</td><td>4000</td></tr>
<tr><td>\(B\)</td><td>量化位数</td><td>bit</td><td>16</td></tr>
<tr><td>\(L/S\)</td><td>帧长 / 帧移</td><td>点</td><td>200 / 80</td></tr>
<tr><td>\(q\)</td><td>量化步长 \(\Delta=2A_{\max}/2^B\)</td><td>—</td><td>\(2/65536\)</td></tr>
</table>

<h4>2. 采样定理的完整推导（不跳步）</h4>
<p><b>第 1 步：把采样建模成与冲激串相乘。</b>定义周期冲激串 \(s(t)=\sum_{n=-\infty}^{\infty}\delta(t-nT_s)\)，采样信号为</p>
<div class="math sub">\[ x_s(t)=x(t)\,s(t)=\sum_n x(nT_s)\,\delta(t-nT_s) \tag{2-5} \]</div>
<p><b>第 2 步：求 \(s(t)\) 的傅里叶变换。</b>它是周期函数，展开成傅里叶级数 \(s(t)=\frac{1}{T_s}\sum_{k}e^{j2\pi k t/T_s}\)，于是</p>
<div class="math sub">\[ S(f)=\frac{1}{T_s}\sum_{k=-\infty}^{\infty}\delta\!\left(f-\frac{k}{T_s}\right)=\frac{1}{T_s}\sum_k\delta(f-kF_s) \tag{2-6} \]</div>
<p><b>第 3 步：时域相乘 = 频域卷积。</b></p>
<div class="math sub">\[ X_s(f)=X(f)*S(f)=\frac{1}{T_s}\sum_{k=-\infty}^{\infty}X(f-kF_s) \tag{2-7} \]</div>
<p>这是整个采样定理的核心：<b>采样后频谱是原频谱以 \(F_s\) 为间隔的无限次平移复制</b>。</p>
<p><b>第 4 步：读出无混叠条件。</b>设原信号带限于 \(f_{\max}\)，即 \(X(f)=0\) 当 \(|f|>f_{\max}\)。相邻两份副本的中心相距 \(F_s\)，各自半宽 \(f_{\max}\)。要不重叠，必须</p>
<div class="math sub">\[ F_s-f_{\max}>f_{\max}\quad\Longrightarrow\quad F_s>2f_{\max} \tag{2-8} \]</div>
<p>满足时，用截止频率 \(F_s/2\) 的理想低通（增益 \(T_s\)）就能从 \(X_s(f)\) 中<b>完整取出</b> \(X(f)\)；时域上对应 Whittaker–Shannon 插值 \(x(t)=\sum_n x[n]\,\mathrm{sinc}\big((t-nT_s)/T_s\big)\)。<b>不满足时两份副本重叠，重叠区不可逆地相加，没有任何数学手段能拆开</b>。</p>

<h4>3. 混叠频率公式的来历</h4>
<p>一个频率 \(f>F_s/2\) 的复指数，在采样点上的值满足</p>
<div class="math sub">\[ e^{j2\pi f n/F_s}=e^{j2\pi (f-kF_s)n/F_s}\cdot e^{j2\pi k n}=e^{j2\pi (f-kF_s)n/F_s} \tag{2-9} \]</div>
<p>因为 \(e^{j2\pi kn}=1\)（\(k,n\) 都是整数）。<b>所有相差整数倍 \(F_s\) 的频率在采样点上完全相同</b>，这叫「频率混叠等价类」。选 \(k\) 使结果落进 \([0,F_s/2]\)，就是式 (2-3)。更一般地，还要关于 \(F_s/2\) 折叠（实信号的共轭对称）：</p>
<div class="math sub">\[ f_{\mathrm{alias}}=\Big|\big(f\bmod F_s\big)-\mathbb 1\big[f\bmod F_s>F_s/2\big]\cdot F_s\Big| \tag{2-10} \]</div>
<p>算例：\(F_s=8000\)，\(f=7500\,\mathrm{Hz}\) → \(7500\bmod8000=7500>4000\) → \(|7500-8000|=500\,\mathrm{Hz}\)。
所以 <b>7.5 kHz 的超声成分会伪装成 500 Hz 的正常振动</b>。这就是为什么抗混叠滤波器必须在 ADC <b>之前</b>用模拟电路实现——采样完成再滤波，500 Hz 处的假峰已经和数据融为一体了。</p>

<h4>4. 6.02B + 1.76 dB 的完整推导</h4>
<p>设满幅正弦 \(x(t)=A\sin(2\pi ft)\)，量化范围 \([-A,A]\) 被均分成 \(2^B\) 级，步长 \(\Delta=2A/2^B\)。</p>
<p><b>信号功率：</b>\(P_x=\dfrac{1}{T}\int_0^T A^2\sin^2(2\pi ft)\,\mathrm{d}t=\dfrac{A^2}{2}\)。</p>
<p><b>量化噪声功率：</b>把量化误差 \(e=x_q-x\) 近似成 \([-\Delta/2,\Delta/2]\) 上均匀分布的白噪声（在步长足够小、信号足够复杂时成立），则 \(P_q=\mathbb E[e^2]=\dfrac{1}{\Delta}\int_{-\Delta/2}^{\Delta/2}e^2\,\mathrm{d}e=\dfrac{\Delta^2}{12}\)。</p>
<p><b>代入并化简：</b></p>
<div class="math sub">\[ \begin{aligned}
\mathrm{SNR}&=\frac{P_x}{P_q}=\frac{A^2/2}{\Delta^2/12}=\frac{6A^2}{\Delta^2}
=\frac{6A^2}{(2A/2^B)^2}=\frac{6}{4}\,2^{2B}=\frac{3}{2}\,2^{2B}\\[4pt]
\mathrm{SNR}_{\mathrm{dB}}&=10\log_{10}\!\left(\tfrac32\right)+20B\log_{10}2
=1.7609+6.0206\,B
\end{aligned} \tag{2-11} \]</div>
<p>「1.76」来自 \(10\log_{10}(3/2)\)（满幅正弦的波形因子），「6.02」来自 \(20\log_{10}2\)。若输入不是满幅正弦而是均匀分布信号，常数项会变；若信号幅度远小于满量程，有效位数下降，实际 SNR 是 \(6.02B+1.76-20\log_{10}(A/A_{\max})\)。<b>所以录音电平调到接近但不触及满幅，是提升有效精度的免费手段。</b></p>

<h4>5. 分帧与加窗的定量细节</h4>
<p>汉明窗定义（\(0\le n\le L-1\)）：</p>
<div class="math sub">\[ w[n]=0.54-0.46\cos\frac{2\pi n}{L-1},\qquad
w_{\mathrm{Hann}}[n]=0.5-0.5\cos\frac{2\pi n}{L-1} \tag{2-12} \]</div>
<p>加窗在时域是逐点相乘，在频域是卷积，因此窗的频谱决定了泄漏形状：</p>
<table class="sym"><tr><th>窗</th><th>主瓣宽度（相对矩形窗）</th><th>最高旁瓣</th><th>适用</th></tr>
<tr><td>矩形</td><td>\(1\times\)</td><td>−13 dB</td><td>频率恰为 \(\Delta f\) 整数倍时才可用</td></tr>
<tr><td>汉宁</td><td>\(2\times\)</td><td>−31 dB</td><td>通用频谱分析</td></tr>
<tr><td>汉明</td><td>\(2\times\)</td><td>−43 dB</td><td><b>语音/MFCC 默认</b>，旁瓣最低</td></tr>
<tr><td>布莱克曼</td><td>\(3\times\)</td><td>−58 dB</td><td>强弱信号并存、需极高动态范围</td></tr>
</table>
<p>注意代价：主瓣变宽意味着<b>频率分辨率变差</b>。汉明窗主瓣约 \(4\pi/L\)（归一化角频率），对应约 2 个谱线间隔，所以「用汉明窗后能分开的最小频率间隔」约为 \(2F_s/L\)。这是选窗时必须算的一笔账。</p>
<p>帧数：\(N=16000\)、\(L=400\)、\(S=160\) → \(M=\lfloor(16000-400)/160\rfloor+1=98\) 帧，总覆盖时长 \((M-1)S+L=97\times160+400=15920\) 点，末尾 80 点被丢弃（不足一帧）。</p>

<h4>6. 公式 ↔ 代码</h4>
<pre><code># 式(2-1)：采样
t = np.arange(N) / fs                       # Ts = 1/fs 隐含在这里
x = np.sin(2*np.pi*f*t)

# 式(2-4)：量化（B bit，满幅 [-1,1]）
q = np.round((x + 1) * (2**B - 1) / 2)     # 量化到整数
xq = q * 2 / (2**B - 1) - 1                # 反量化回 [-1,1]

# 式(2-10) / (2-11)：分帧 + 汉明窗
L, S = int(0.025*fs), int(0.010*fs)
frames = np.array([x[i:i+L] for i in range(0, len(x)-L+1, S)])
win = 0.54 - 0.46*np.cos(2*np.pi*np.arange(L)/(L-1))
frames = frames * win</code></pre>

<h4>7. 边界与失效条件</h4>
<ul><li><b>等号不成立：</b>\(F_s=2f_{\max}\) 时，若采样相位恰好落在每个过零点，采到的全是 0。工程上留 10–20% 余量。</li>
<li><b>抗混叠过渡带：</b>实际滤波器不可能陡降到 0，所以 \(F_s=8\,\mathrm{kHz}\) 的<b>可用带宽约 3.4 kHz</b> 而非 4 kHz。</li>
<li><b>量化噪声白噪声假设失效：</b>信号幅度很小、或信号是纯正弦且频率与 \(F_s\) 成简单整数比时，误差与信号相关，会变成谐波失真而非白噪声，此时 SNR 公式偏乐观。</li>
<li><b>短时平稳假设：</b>25 ms 窗对稳态嗡鸣成立，对「敲击 / 放电脉冲」这类瞬态不成立，需要更短窗或小波（第 7 讲）。</li></ul>
</div>
"""

EXP_A["s3"] = r"""
<div class="derive">
<div class="dtitle">推导详解 · 第 3 讲　时域特征的完整推导</div>

<h4>1. 从连续能量到短时能量</h4>
<p>连续信号的总能量是 \(E=\int_{-\infty}^{\infty}x^2(t)\,\mathrm{d}t\)。对离散、加窗后的第 \(m\) 帧，积分换成求和：</p>
<div class="math sub">\[ E_m=\sum_{n=0}^{N-1}\big(x[n]\,w[n-mS]\big)^2=\sum_{n=0}^{N-1}x_m^2[n] \tag{3-6} \]</div>
<p>注意<b>窗函数平方也进来了</b>：汉明窗两端接近 0.08，平方后仅 0.0064，意味着帧两端的样本对能量贡献被压掉 99%。这是加窗的必然代价，也是帧与帧要重叠 50% 以上的原因——否则边界信息会周期性丢失。</p>
<p>归一化到「平均功率」要除以 \(\sum_n w^2[n]\) 而不是 \(N\)：\(\bar P_m=\dfrac{E_m}{\sum_n w^2[n]}\)。对汉明窗，\(\sum w^2\approx0.397L\)，除以 \(L\) 会低估约 2.5 倍（约 4 dB）。</p>

<h4>2. 过零率公式为什么有系数 2</h4>
<p>纯正弦 \(x(t)=A\sin(2\pi ft)\) 在一个周期 \(T=1/f\) 内穿越零点 2 次（上升沿、下降沿各一次）。一帧时长 \(T_{\mathrm{frame}}=N/F_s\)，包含 \(T_{\mathrm{frame}}/T=fN/F_s\) 个周期，故</p>
<div class="math sub">\[ Z=2\cdot\frac{fN}{F_s},\qquad \frac{Z}{N}=\frac{2f}{F_s},\qquad f=\frac{Z\,F_s}{2N} \tag{3-7} \]</div>
<p>代入数字：\(F_s=8000\)、\(N=200\)、\(f=500\) → \(Z=2(500)(200)/8000=25\)。
反过来 \(f=25\times8000/(2\times200)=500\,\mathrm{Hz}\) ✓。</p>
<p><b>这个反推的适用条件很窄</b>：只对单频、无直流、无噪声的正弦成立。真实信号里谐波也会过零，噪声更会制造大量虚假过零，所以过零率只能当「高频成分多不多」的粗指标，<b>不能当基频估计器</b>——基频要靠自相关（下式）。</p>

<h4>3. 自相关为什么能测周期：一步不跳的证明</h4>
<p>设 \(x[n]\) 周期为 \(P\)，即 \(x[n+P]=x[n]\)。把它代入自相关定义：</p>
<div class="math sub">\[ R(P)=\sum_n x[n]\,x[n+P]=\sum_n x^2[n]=R(0)=E,\qquad
\rho(P)=\frac{R(P)}{R(0)}=1 \tag{3-8} \]</div>
<p>即周期整数倍处的归一化自相关恒为 1；而非周期倍数处，乘积正负相消，\(\rho(k)\) 明显小于 1。
有偏估计 \(R(k)=\sum_{n=0}^{N-1-k}x[n]x[n+k]\) 的求和项随 \(k\) 增大而减少，所以峰值会随 \(k\) 缓慢下降——
这反而有助于抑制大 \(k\) 处的伪峰。若改用无偏估计（除以 \(N-k\)），在 \(k\to N\) 时只剩极少数样本，方差爆炸，反而更容易选错峰。<b>「有偏」在这里是特性不是缺陷。</b></p>
<p>峰值搜索必须避开 \(k=0\)：\(\rho(0)\equiv1\) 是全局最大值。按目标基频范围设区间：</p>
<div class="math sub">\[ k\in\left[\left\lfloor\frac{F_s}{f_{\max}}\right\rfloor,\ \left\lceil\frac{F_s}{f_{\min}}\right\rceil\right]
\;\xrightarrow{\;F_s=8000,\ f\in[80,400]\mathrm{Hz}\;}\;k\in[20,\,100] \tag{3-9} \]</div>
<p>例：在 \(k_0=80\) 处取到峰 → \(f_0=8000/80=100\,\mathrm{Hz}\)，周期 \(T=1/100=10\,\mathrm{ms}\) = 80 点 ✓。</p>

<h4>4. 双门限端点检测：把两个特征合起来用</h4>
<p>单靠能量会把强噪声当语音，单靠过零率会把静音段的微弱直流漂移当清音。工程做法是<b>三级状态机</b>：</p>
<div class="math sub">\[ \begin{cases}
E_m>\tau_{\mathrm{high}} &\Rightarrow \text{进入「有效段」}\\
\tau_{\mathrm{low}}<E_m\le\tau_{\mathrm{high}}\ \text{且}\ Z_m<\tau_{Z} &\Rightarrow \text{暂留（可能是尾部）}\\
E_m\le\tau_{\mathrm{low}} &\Rightarrow \text{判为静音，回退到高门限越过的起点}
\end{cases} \tag{3-10} \]</div>
<p>门限常按背景噪声自适应：\(\tau_{\mathrm{low}}=\mu_E+2\sigma_E\)、\(\tau_{\mathrm{high}}=4\tau_{\mathrm{low}}\)（前 100 ms 假定为静音用于估计 \(\mu_E,\sigma_E\)）。低门限负责「不切掉弱起音」，高门限负责「不被噪声骗开」，两者缺一不可。</p>

<h4>5. 公式 ↔ 代码</h4>
<pre><code># 式(3-1) 能量 / 式(3-2) 过零率
E = np.sum(frames**2, axis=1)
Z = 0.5*np.sum(np.abs(np.diff(np.sign(frames), axis=1)), axis=1)

# 式(3-4)(3-5) 归一化自相关 + 限定区间找峰
def pitch(x, fs, fmin=80, fmax=400):
    x = x - x.mean()
    r = np.correlate(x, x, 'full')[len(x)-1:]      # R(k), k=0..N-1
    lo, hi = int(fs/fmax), min(int(fs/fmin), len(r)-1)
    k0 = lo + np.argmax(r[lo:hi+1] / (r[0] + 1e-12))
    return fs / k0, k0</code></pre>
<p>注意 <code>np.correlate(x,x,'full')</code> 取后半段才是 \(k\ge0\) 的部分；写成 <code>[:len(x)]</code> 会得到反向序列，峰位置全错。配套项目的 <code>autocorr_pitch()</code> 已按上式实现并做了去直流。</p>

<h4>6. 边界与失效条件</h4>
<ul><li><b>直流偏置</b>：哪怕只有 0.01 的直流，也会让过零率几乎归零。必须先去均值或预加重。</li>
<li><b>倍周期 / 半周期错误</b>：自相关在 \(2P,3P\) 处同样有峰，在 \(P/2\) 处对某些波形也有较强峰。取「第一个超过阈值的峰」比取全局最大更稳。</li>
<li><b>帧长不够</b>：要可靠看到 \(f_{\min}=80\,\mathrm{Hz}\) 的一个周期，帧长至少 \(F_s/f_{\min}=100\) 点（12.5 ms @8 kHz），实务上取 2–3 个周期以上。</li></ul>
</div>
"""

EXP_A["s4"] = r"""
<div class="derive">
<div class="dtitle">推导详解 · 第 4 讲　DFT 正交性、归一化与 FFT 蝶形</div>

<h4>1. 符号对照表</h4>
<table class="sym"><tr><th>符号</th><th>含义</th><th>备注</th></tr>
<tr><td>\(N\)</td><td>DFT 点数</td><td>本讲义 256 / 1024</td></tr>
<tr><td>\(W_N\)</td><td>旋转因子 \(e^{-j2\pi/N}\)</td><td>\(W_N^N=1\)</td></tr>
<tr><td>\(X[k]\)</td><td>频域第 \(k\) 点</td><td>复数，\(k=0..N-1\)</td></tr>
<tr><td>\(\Delta f\)</td><td>谱线间隔 \(F_s/N\)</td><td>31.25 Hz @8000/256</td></tr>
<tr><td>\(T_{\mathrm{obs}}\)</td><td>观测时长 \(N/F_s\)</td><td>决定真实分辨率</td></tr>
</table>

<h4>2. 离散正交性：用几何级数算出来</h4>
<p>把基函数列成向量 \(\mathbf u_k=\big[W_N^{-kn}\big]_{n=0}^{N-1}\)。两个不同基的内积为</p>
<div class="math sub">\[ \langle\mathbf u_p,\mathbf u_q\rangle=\sum_{n=0}^{N-1}e^{j2\pi(p-q)n/N}
=\sum_{n=0}^{N-1}r^{n},\qquad r=e^{j2\pi(p-q)/N} \tag{4-7} \]</div>
<p>若 \(p=q\)，则 \(r=1\)，和为 \(N\)。若 \(p\neq q\) 且 \(|p-q|<N\)，由等比级数求和</p>
<div class="math sub">\[ \sum_{n=0}^{N-1}r^n=\frac{1-r^N}{1-r}
=\frac{1-e^{j2\pi(p-q)}}{1-e^{j2\pi(p-q)/N}}=\frac{1-1}{1-r}=0 \tag{4-8} \]</div>
<p>合并得 \(\langle\mathbf u_p,\mathbf u_q\rangle=N\delta_{pq}\)。<b>正交性不是公理，是「整数个周期求和为零」的直接结果</b>。这也解释了为什么 DFT 点数必须正好覆盖整数个基函数周期：一旦 \(k\) 不是整数（信号频率不落在谱线上），式 (4-8) 的分子不再为 0，能量就漏到相邻谱线——这就是<b>频谱泄漏</b>的数学来源。</p>

<h4>3. 逆变换里的 1/N 是怎么定出来的</h4>
<p>把 DFT 写成矩阵 \(X=F x\)，其中 \(F_{kn}=W_N^{kn}\)。由上式 \(F^{\mathsf H}F=N I\)（共轭转置），故 \(F^{-1}=\frac{1}{N}F^{\mathsf H}\)，于是</p>
<div class="math sub">\[ x[n]=\frac{1}{N}\sum_{k=0}^{N-1}X[k]\,e^{j2\pi kn/N} \tag{4-9} \]</div>
<p>把 DFT 正变换代进去可验证：\(\frac{1}{N}\sum_k\sum_m x[m]e^{-j2\pi km/N}e^{j2\pi kn/N}
=\sum_m x[m]\,\frac{1}{N}\sum_k e^{j2\pi k(n-m)/N}=\sum_m x[m]\delta_{nm}=x[n]\) ✓。
<b>归一化的位置是约定问题</b>：有的库把 \(1/\sqrt N\) 平分给正反变换（对称约定），numpy 采用「正变换不除、逆变换除 \(N\)」。
写成代码对拍时，必须先确认用的是哪一套，否则结果会差 \(N\) 倍。</p>

<h4>4. 共轭对称与 2/N 的完整来历</h4>
<p>实信号 \(x[n]\in\mathbb R\) 时：</p>
<div class="math sub">\[ X[N-k]=\sum_n x[n]e^{-j2\pi(N-k)n/N}
=\sum_n x[n]e^{j2\pi kn/N}\underbrace{e^{-j2\pi n}}_{=1}
=\overline{X[k]} \tag{4-10} \]</div>
<p>再看幅度为 \(A\) 的实正弦，用欧拉公式展开：</p>
<div class="math sub">\[ x[n]=A\sin\frac{2\pi k_0n}{N}=\frac{A}{2j}\left(e^{j2\pi k_0n/N}-e^{-j2\pi k_0n/N}\right) \tag{4-11} \]</div>
<p>正频率 \(k_0\) 那一支与 DFT 基相消后求和得 \(N\) 个 1，故 \(X[k_0]=\frac{A}{2j}N\)，模长 \(|X[k_0]|=AN/2\)；
负频率 \(N-k_0\) 处同样有 \(AN/2\)。<b>能量被正负频率各分一半</b>，只看单边就要补回 2 倍，再除以 \(N\) 消掉求和积累：</p>
<div class="math sub">\[ A[k]=\frac{2|X[k]|}{N},\qquad A[0]=\frac{|X[0]|}{N}=\frac{1}{N}\left|\sum_n x[n]\right|=|\bar x| \tag{4-12} \]</div>
<p>直流不乘 2，因为它没有「负频率伙伴」，\(X[0]=\sum_n x[n]=N\bar x\) 本身就直接给出均值。</p>

<h4>5. 补零为什么只改显示密度：从 DTFT 看</h4>
<p>把 \(N_0\) 点信号 \(x[n]\) 补零到 \(M\) 点，其 \(M\) 点 DFT 为</p>
<div class="math sub">\[ X_M[k]=\sum_{n=0}^{N_0-1}x[n]e^{-j2\pi kn/M}=X_{\mathrm{DTFT}}\!\left(\omega=\frac{2\pi k}{M}\right) \tag{4-13} \]</div>
<p>注意求和上限仍是 \(N_0\)：<b>补零没有增加任何新信息</b>，只是把同一条连续频谱 \(X_{\mathrm{DTFT}}(\omega)\) 在更密的频率网格上采样。
两个频率能否分开，取决于这条连续曲线的主瓣宽度 \(\approx2\pi/N_0\)，与采样网格密度 \(2\pi/M\) 无关。
这就是「\(\Delta f_{\mathrm{true}}=F_s/N_0\)，\(\Delta f_{\mathrm{display}}=F_s/M\)」的严格表述。</p>

<h4>6. FFT：Cooley–Tukey 按时间抽取的完整分解</h4>
<p><b>第 1 步：把求和按 \(n\) 的奇偶拆开</b>（设 \(N\) 为偶数，\(n=2r\) 与 \(n=2r+1\)，\(r=0..N/2-1\)）：</p>
<div class="math sub">\[ \begin{aligned}
X[k]&=\sum_{r=0}^{N/2-1}x[2r]W_N^{k(2r)}+\sum_{r=0}^{N/2-1}x[2r+1]W_N^{k(2r+1)}\\
&=\underbrace{\sum_r x[2r]W_{N/2}^{kr}}_{E[k]}+W_N^{k}\underbrace{\sum_r x[2r+1]W_{N/2}^{kr}}_{O[k]}
=E[k]+W_N^{k}O[k]
\end{aligned} \tag{4-14} \]</div>
<p>用了 \(W_N^{2kr}=e^{-j2\pi(2kr)/N}=e^{-j2\pi kr/(N/2)}=W_{N/2}^{kr}\)。\(E,O\) 恰是两个 \(N/2\) 点 DFT。</p>
<p><b>第 2 步：利用周期性与对称性省掉一半计算。</b>因为 \(E,O\) 以 \(N/2\) 为周期，且</p>
<div class="math sub">\[ W_N^{k+N/2}=e^{-j2\pi(k+N/2)/N}=W_N^{k}\,e^{-j\pi}=-W_N^{k} \tag{4-15} \]</div>
<p>于是对 \(k=0..N/2-1\) 配对计算（这就是<b>蝶形运算</b>）：</p>
<div class="math sub">\[ \begin{cases}X[k]=E[k]+W_N^{k}O[k]\\ X[k+N/2]=E[k]-W_N^{k}O[k]\end{cases} \tag{4-16} \]</div>
<p>一次蝶形 = 1 次复乘 + 2 次复加，同时产出两个输出。</p>
<p><b>第 3 步：复杂度递推。</b>\(T(N)=2T(N/2)+\frac{N}{2}\)（每层 \(N/2\) 个蝶形），共 \(\log_2N\) 层：</p>
<div class="math sub">\[ T(N)=\frac{N}{2}\log_2N,\qquad
\frac{T(N)}{N^2}=\frac{\log_2N}{2N}\xrightarrow{N=1024}\frac{1}{205} \tag{4-17} \]</div>
<p>与式 (4-6) 的表格完全一致。递归到最后是 2 点 DFT，输入需按<b>位反转顺序</b>重排（或递归时自动完成）。</p>

<h4>7. 频谱泄漏的定量描述</h4>
<p>对长度为 \(N\) 的矩形窗，其 DTFT 是 Dirichlet 核：</p>
<div class="math sub">\[ W(\omega)=e^{-j\omega(N-1)/2}\,\frac{\sin(N\omega/2)}{\sin(\omega/2)} \tag{4-18} \]</div>
<p>主瓣零点在 \(\omega=\pm2\pi/N\)，第一旁瓣约 −13 dB。若信号频率落在两根谱线中间（\(k_0+0.5\)），
相邻谱线恰好采在旁瓣上，会出现「主峰降低约 3.9 dB（扇形损失）+ 两侧一串旁瓣」。
汉明窗把旁瓣压到 −43 dB，代价是主瓣展宽 2 倍。这就是第 2 讲那张窗函数表的定量依据。</p>

<h4>8. 公式 ↔ 代码</h4>
<pre><code># 式(4-2)：DFT 基矩阵（每一行是一个频率）
def dft(x):
    N = len(x); n = np.arange(N); k = n.reshape(-1, 1)
    W = np.exp(-2j*np.pi*k*n/N)      # W_N^{kn}
    return W @ x

# 式(4-9)：逆变换，注意 1/N
def idft(X):
    N = len(X); n = np.arange(N); k = n.reshape(-1, 1)
    return np.exp(2j*np.pi*k*n/N) @ X / N

# 式(4-12)：单边幅度谱
A = np.abs(X[:N//2+1]) * 2 / N
A[0] /= 2                            # 直流不乘 2

# 式(4-16)：一个 2 点蝶形（递归 FFT 的核心）
Xe, Xo = fft(x[0::2]), fft(x[1::2])
T = np.exp(-2j*np.pi*np.arange(N//2)/N) * Xo
X = np.concatenate([Xe + T, Xe - T])</code></pre>

<h4>9. 边界与失效条件</h4>
<ul><li>\(N\) 不是 2 的幂时上述二分不成立，需 Bluestein / 混合基算法；numpy 会变慢但不报错。</li>
<li>信号含 \(>F_s/2\) 成分时 DFT 结果本身已是混叠后的，<b>频域无法补救</b>（回到第 2 讲）。</li>
<li>相位谱在 \(|X[k]|\approx0\) 处数值不稳定，取 \(\arg X[k]\) 前应先设幅度阈值。</li>
<li>浮点误差：DFT 基矩阵是 \(O(N^2)\) 内存，\(N=8192\) 时约 1 GB（complex128），大点数必须走 FFT。</li></ul>
</div>
"""

EXP_A["s5"] = r"""
<div class="derive">
<div class="dtitle">推导详解 · 第 5 讲　STFT、不确定关系与语谱图</div>

<h4>1. STFT 的定义与反变换</h4>
<p>STFT 就是「加窗 + DFT」在每一帧上重复：</p>
<div class="math sub">\[ X[m,k]=\sum_{n}x[n]\,w[n-mS]\,e^{-j2\pi kn/N}
=\big\langle \mathbf x,\ \underbrace{w[\cdot-mS]e^{j2\pi k\cdot/N}}_{g_{m,k}}\big\rangle \tag{5-4} \]</div>
<p>\(g_{m,k}\) 叫 <b>Gabor 原子</b>：平移 \(mS\) 选时间、调制 \(k\) 选频率。反变换（重叠相加 OLA）为</p>
<div class="math sub">\[ x[n]=\frac{\sum_m\sum_k X[m,k]\,e^{j2\pi kn/N}}{\sum_m w[n-mS]},\qquad
\text{需满足}\ \sum_m w[n-mS]\neq0 \tag{5-5} \]</div>
<p>分母是各帧窗的和。汉明窗取 \(S=L/2\) 时 \(\sum_m w[n-mS]\approx1.08\) 近似常数，满足 <b>COLAs</b>（常数重叠相加）条件，因此可以无损重构；若取 \(S=L\)（无重叠），汉明窗之和在帧边界处起伏，重构会失真。<b>这就是「帧移不能随便取大」的硬理由。</b></p>

<h4>2. 时频不确定关系：从傅里叶尺度性质推出来</h4>
<p>把窗 \(w(t)\) 看作一个「波形包」，定义其能量归一化的一、二阶矩：</p>
<div class="math sub">\[ \Delta t^2=\frac{\int(t-\mu_t)^2|w(t)|^2\mathrm{d}t}{\int|w|^2\mathrm{d}t},\qquad
\Delta f^2=\frac{\int(f-\mu_f)^2|W(f)|^2\mathrm{d}f}{\int|W|^2\mathrm{d}f} \tag{5-6} \]</div>
<p>由傅里叶变换的尺度性质 \(w(at)\leftrightarrow\frac{1}{|a|}W(f/a)\)：把窗在时间上压窄 \(a\) 倍，频谱必然展宽 \(a\) 倍。
用柯西–施瓦茨不等式可严格证明 \(\Delta t\,\Delta f\ge\dfrac{1}{4\pi}\)，等号仅当 \(w\) 是<b>高斯函数</b>时取到（Gabor 变换用高斯窗的原因）。</p>
<p>对长度 \(L\) 的矩形窗，\(\Delta t\approx L/F_s\)、\(\Delta f\approx F_s/L\)，乘积约 1——比理论下界大 \(4\pi\) 倍，因为矩形窗远非高斯。<b>工程上的结论是：乘积是个常数，只能换，不能双赢。</b></p>

<h4>3. 选窗的一笔定量账</h4>
<table class="sym"><tr><th>窗长 \(L\)（@8 kHz）</th><th>\(\Delta t\)</th><th>\(\Delta f=F_s/L\)</th><th>能分辨的最小频率间隔</th><th>适用</th></tr>
<tr><td>80 点（10 ms）</td><td>10 ms</td><td>100 Hz</td><td>约 200 Hz（含汉明主瓣）</td><td>瞬态、敲击起点</td></tr>
<tr><td>200 点（25 ms）</td><td>25 ms</td><td>40 Hz</td><td>约 80 Hz</td><td><b>语音 MFCC 默认</b></td></tr>
<tr><td>800 点（100 ms）</td><td>100 ms</td><td>10 Hz</td><td>约 20 Hz</td><td>分辨 100/120 Hz 谐波</td></tr>
<tr><td>1600 点（200 ms）</td><td>200 ms</td><td>5 Hz</td><td>约 10 Hz</td><td>稳态嗡鸣精细谱</td></tr>
</table>
<p>变压器诊断要看 50 Hz 间隔的谐波（100/150/200 Hz），25 ms 窗的 80 Hz 分辨力不够，所以配套项目在画「精细谱」时用的是整段 0.5 s 加长窗，而 MFCC 仍用 25 ms 短窗——<b>同一个系统里可以并存两套时频尺度，各管一件事</b>。</p>

<h4>4. dB 换算与动态范围</h4>
<div class="math sub">\[ S_{\mathrm{dB}}=20\log_{10}(|X|+\varepsilon),\qquad
P_{\mathrm{dB}}=10\log_{10}(P+\varepsilon),\qquad P=|X|^2/N \tag{5-7} \]</div>
<p>验证二者一致：\(10\log_{10}(|X|^2)=20\log_{10}|X|\) ✓。取 20 log 后，幅值比 \(10^3\)（60 dB）在灰度上映射成 60 dB 的跨度；
若用线性幅度，最大值 1.0 之下 0.001 的成分只有 1/1000 像素亮度，肉眼完全看不见。
显示时通常再设 <b>下限钳位</b>：\(S_{\mathrm{show}}=\max(S_{\mathrm{dB}},\,S_{\max}-D)\)，\(D=60\sim80\,\mathrm{dB}\)，
把低于最大值 60 dB 以下的全部涂成背景色，避免底噪把图糊满。</p>

<h4>5. 公式 ↔ 代码</h4>
<pre><code># 式(5-1) STFT：分帧 + 窗 + rfft
F = frame_signal(x, L=200, S=80) * np.hamming(200)
X = np.fft.rfft(F, n=256, axis=1)          # (M, 129) 复数

# 式(5-7) 语谱图（含下限钳位）
S = 20*np.log10(np.abs(X) + 1e-10)
S = np.maximum(S, S.max() - 70)

# 式(5-5) OLA 重构需要的窗和
wsum = np.zeros(len(x))
for i in range(0, len(x)-L+1, S): wsum[i:i+L] += np.hamming(L)
print(wsum.min(), wsum.max())              # 应近似常数、且 > 0</code></pre>

<h4>6. 边界与失效条件</h4>
<ul><li>帧移 \(S>L\) → 窗和中出现 0，式 (5-5) 分母为零，重构出现周期性空洞。</li>
<li>补零到 \(N>L\) 只让频率轴变密，<b>不改变本讲的 \(\Delta f\)</b>（回到式 4-13）。</li>
<li>STFT 是<b>线性</b>时频表示，多分量交叉项不会像 Wigner–Ville 分布那样产生伪影，但也换来分辨率受限。</li>
<li>对数显示会压缩强弱差异，做定量幅值比较时必须回到线性域。</li></ul>
</div>
"""

EXP_A["s6"] = r"""
<div class="derive">
<div class="dtitle">推导详解 · 第 6 讲　MFCC 七步，每一步都推到底</div>

<h4>1. 全局符号对照表</h4>
<table class="sym"><tr><th>符号</th><th>含义</th><th>本讲义取值</th><th>形状</th></tr>
<tr><td>\(x[n]\)</td><td>原始采样序列</td><td>0.5 s @8 kHz</td><td>(4000,)</td></tr>
<tr><td>\(F\)</td><td>分帧矩阵</td><td>25 ms / 10 ms</td><td>(T, 200)</td></tr>
<tr><td>\(P[k]\)</td><td>功率谱</td><td>256 点 rfft</td><td>(T, 129)</td></tr>
<tr><td>\(H_m[k]\)</td><td>第 \(m\) 个三角滤波器</td><td>\(M=26\)</td><td>(26, 129)</td></tr>
<tr><td>\(E_m\)</td><td>Mel 通道能量</td><td>—</td><td>(T, 26)</td></tr>
<tr><td>\(c_i\)</td><td>倒谱系数</td><td>取前 13</td><td>(T, 13)</td></tr>
<tr><td>\(d_t,dd_t\)</td><td>一阶 / 二阶差分</td><td>窗宽 \(N=2\)</td><td>(T, 13)</td></tr>
</table>

<h4>2. 第 1 步：预加重的传递函数与频率响应</h4>
<p>差分方程 \(y[n]=x[n]-\alpha x[n-1]\) 取 Z 变换：\(Y(z)=X(z)-\alpha z^{-1}X(z)\)，故</p>
<div class="math sub">\[ H(z)=1-\alpha z^{-1},\qquad
H(e^{j\omega})=1-\alpha e^{-j\omega}=(1-\alpha\cos\omega)+j\alpha\sin\omega \tag{6-8} \]</div>
<div class="math sub">\[ |H(e^{j\omega})|^2=(1-\alpha\cos\omega)^2+(\alpha\sin\omega)^2
=1-2\alpha\cos\omega+\alpha^2=(1-\alpha)^2+4\alpha\sin^2\frac{\omega}{2} \tag{6-9} \]</div>
<p>代入 \(\alpha=0.95\)：\(\omega=0\) 时 \(|H|^2=0.0025\)（−26 dB）；\(\omega=\pi\) 时 \(|H|^2=3.8025\)（+5.8 dB）。
<b>低频被压掉近 30 dB</b>。对语音（判别信息在 1–3 kHz 共振峰）这是好事；对变压器（判别信息在 100–500 Hz）这是灾难。
定量结论：若要保留 100 Hz，需 \(20\log_{10}|H(e^{j2\pi100/8000})|\ge-3\,\mathrm{dB}\)，反解要求 \(\alpha\lesssim0.45\)。</p>

<h4>3. 第 4 步：Mel 滤波器边界的完整计算</h4>
<p>给定 \(F_s=8000\)、\(N=256\)、\(M=26\)，把 Hz 上下限换成 mel：\(m_{\mathrm{low}}=m(0)=0\)，
\(m_{\mathrm{high}}=m(4000)=2595\log_{10}(1+4000/700)=2146.1\) mel。在 mel 轴等分 \(M+2=28\) 个点：</p>
<div class="math sub">\[ m_j=m_{\mathrm{low}}+j\cdot\frac{m_{\mathrm{high}}-m_{\mathrm{low}}}{M+1}
= j\cdot\frac{2146.1}{27}=j\cdot79.49\ \mathrm{mel},\quad j=0,\dots,27 \tag{6-10} \]</div>
<p>再反变换回 Hz：\(f_j=700(10^{m_j/2595}-1)\)，最后换成 FFT 谱线索引 \(k_j=\left\lfloor\dfrac{(N+1)f_j}{F_s}\right\rfloor\)。
前几个结果：\(f_0=0\)、\(f_1=700(10^{79.49/2595}-1)=51.0\,\mathrm{Hz}\)、\(f_2=106.1\,\mathrm{Hz}\)、\(f_3=165.2\,\mathrm{Hz}\)……
与讲义正文「前 10 个中心频率」表完全一致。<b>注意分母是 \(M+1\) 而不是 \(M\)：因为有 \(M\) 个三角形，
需要 \(M+2\) 个边界点（每个三角形用左、中、右三个相邻点），相邻滤波器因此自然重叠 50%。</b></p>
<p>验证归一化：对任意谱线 \(k\)，落在它上面的只有相邻两个非零三角形，且二者在该点的值之和为 1，故 \(\sum_m H_m[k]=1\)。
这保证「滤波组不放大也不衰减总能量」，只是重新分配。</p>

<h4>4. 第 5 步：同态解卷积，取 log 到底在解什么</h4>
<p>真实录音是声源 \(s\) 经过信道 \(h\)（麦克风频响、房间反射、距离）：\(x=s*h\)。取傅里叶变换：</p>
<div class="math sub">\[ X(f)=S(f)\,H(f)\ \xrightarrow{\ \log|\cdot|\ }\
\log|X|=\log|S|+\underbrace{\log|H|}_{\text{与说话人无关}} \tag{6-11} \]</div>
<p>卷积 → 乘积 → 求和，这三步叫<b>同态解卷积</b>。若信道在一段录音内不变，\(\log|H|\) 是一个沿时间轴恒定的偏置；
CMN（每维减去整段的均值）恰好把它消掉：</p>
<div class="math sub">\[ \tilde c_i[t]=c_i[t]-\frac{1}{T}\sum_{t'=1}^{T}c_i[t']
\;\Rightarrow\; \log|H|\ \text{项被抵消} \tag{6-12} \]</div>
<p>因为 DCT 是线性变换，减均值的操作在 Mel 域和倒谱域等价。<b>这就是「为什么 MFCC 要取 log」的完整答案</b>：
不取 log，信道是乘性的，减均值消不掉；取了 log，信道变加性，一步减法就解决。
另外人耳响度感知近似对数（Weber–Fechner 定律），与工程动机正好一致。</p>

<h4>5. 第 6 步：DCT-II 的正交性验证</h4>
<p>取基向量 \(\phi_i[m]=\cos\!\big[\frac{\pi i}{M}(m-\tfrac12)\big]\)，\(m=1..M\)。用积化和差可证</p>
<div class="math sub">\[ \sum_{m=1}^{M}\phi_i[m]\phi_{j}[m]=
\begin{cases}M,&i=j=0\\ M/2,&i=j>0\\ 0,&i\neq j\end{cases} \tag{6-13} \]</div>
<p>所以归一化的正交 DCT 系数是 \(c_i=\sqrt{2/M}\,\lambda_i\sum_m L_m\phi_i[m]\)（\(\lambda_0=1/\sqrt2\)，其余为 1），
逆变换为 \(L_m=\sqrt{2/M}\sum_i\lambda_i c_i\phi_i[m]\)。
<b>只保留前 13 个系数等价于把 Mel 对数谱投影到「变化最慢」的 13 个余弦基上</b>——
低频基描述包络总体形状，高频基描述细节起伏。若把 26 个系数全留下，逆变换能精确还原 \(L_m\)；
截断到 13 相当于做了一次低通平滑，正好滤掉了通道间噪声。</p>

<h4>6. 第 7 步：差分系数是最小二乘斜率，不是随便相减</h4>
<p>假设在 \(t\) 附近，第 \(i\) 维倒谱随时间近似线性：\(c_{t+n}^{(i)}\approx a+b\,n\)，其中 \(b\) 就是想要的斜率 \(d_t\)。
对 \(n=-N,\dots,N\) 最小化 \(\sum_n\big(c_{t+n}-a-bn\big)^2\)。对 \(a,b\) 求偏导置零：</p>
<div class="math sub">\[ \begin{aligned}
\frac{\partial}{\partial a}&:\ \sum_n(c_{t+n}-a-bn)=0\ \Rightarrow\ a=\frac{1}{2N+1}\sum_n c_{t+n}\quad(\text{因}\ \textstyle\sum n=0)\\
\frac{\partial}{\partial b}&:\ \sum_n n(c_{t+n}-a-bn)=0\ \Rightarrow\
b=\frac{\sum_n n\,c_{t+n}}{\sum_n n^2}
\end{aligned} \tag{6-14} \]</div>
<p>把正负 \(n\) 配对：\(\sum_{n=-N}^{N}n\,c_{t+n}=\sum_{n=1}^{N}n(c_{t+n}-c_{t-n})\)，
\(\sum_{n=-N}^{N}n^2=2\sum_{n=1}^{N}n^2\)，于是</p>
<div class="math sub">\[ d_t=b=\frac{\sum_{n=1}^{N}n(c_{t+n}-c_{t-n})}{2\sum_{n=1}^{N}n^2},
\qquad N=2:\ \frac{1(c_{t+1}-c_{t-1})+2(c_{t+2}-c_{t-2})}{2(1+4)}=\frac{\cdots}{10} \tag{6-15} \]</div>
<p>分母 10 就是这么来的。这个推导说明差分特征<b>对噪声有一定抑制</b>（用了 2N+1 帧拟合而非相邻两帧相减），
且窗口越宽越平滑、时间分辨率越差。<b>边界处理</b>：首尾不足 \(N\) 帧时通常复制边缘帧，否则前 2 帧的差分恒为 0。</p>

<h4>7. 全流程维度账（算到底）</h4>
<div class="math sub">\[ \begin{aligned}
&0.5\,\mathrm{s}\times8000=4000\ \text{点}\ \xrightarrow{L=200,S=80}\
T=\left\lfloor\frac{4000-200}{80}\right\rfloor+1=48\ \text{帧}\\
&4000\ \text{点}\ \to\ (48,200)\ \to\ (48,129)\ \to\ (48,26)\ \to\ (48,13)\\
&\xrightarrow{+\Delta+\Delta\Delta}\ (48,39)=1872\ \text{个数}
\end{aligned} \tag{6-16} \]</div>
<p>压缩比 \(4000/1872\approx2.1\)。若再做时间上的统计池化（各维取均值与标准差）得 78 维，
压缩比约 51——这就是第 14 讲 x-vector 之前「手工特征 + 统计量」路线的终点。</p>

<h4>8. 公式 ↔ 代码（逐行对应）</h4>
<pre><code>def mfcc(x, fs, n_mels=26, n_ceps=13, N=256, L=200, S=80, alpha=0.0):
    # 式(6-1) 预加重：y[n]=x[n]-alpha*x[n-1]
    y = np.append(x[0], x[1:] - alpha*x[:-1])
    # 式(2-11) 分帧 + (2-12) 汉明窗
    F = frame_signal(y, L, S) * (0.54-0.46*np.cos(2*np.pi*np.arange(L)/(L-1)))
    # 式(6-2) 功率谱：|X|^2/N
    P = np.abs(np.fft.rfft(F, n=N, axis=1))**2 / N        # (T,129)
    # 式(6-3)(6-4) Mel 滤波器组 → 式(6-5) 能量
    fb = mel_filterbank(n_mels, N, fs)                     # (26,129)
    E = P @ fb.T + 1e-10                                  # (T,26)
    # 式(6-6) 取 log  L_m
    Lm = np.log(E)
    # 式(6-7) DCT-II，取前 n_ceps 列
    C = dct(Lm, type=2, norm='ortho')[:, :n_ceps]           # (T,13)
    # 式(6-15) 一阶/二阶差分
    D, DD = delta(C, N=2), delta(delta(C, N=2), N=2)
    feat = np.hstack([C, D, DD])                            # (T,39)
    # 式(6-12) CMN
    return feat - feat.mean(axis=0)</code></pre>
<p>对照 <code>acoustic-lab/src/dsp.py</code>：<code>mel_filterbank()</code> 里的 <code>points = np.linspace(mel_low, mel_high, n_mels+2)</code>
对应式 (6-10) 的 28 个边界点；<code>delta()</code> 的分母 <code>2*sum(n**2)</code> 对应式 (6-15)。</p>

<h4>9. 边界与失效条件</h4>
<ul><li>\(E_m=0\) 时 \(\log\) 发散 → 必须加 \(\varepsilon\)（\(10^{-10}\)）；也可对功率谱设下限。</li>
<li>频率上限必须用 \(F_s/2\)：把 8000 Hz 采样的数据按 16000 Hz 建滤波器组，高频通道全空，特征后半段恒为 0。</li>
<li>Mel 滤波器数 \(M\) 与倒谱维数要匹配：\(n_{\mathrm{ceps}}>M\) 没有意义（后面系数恒为 0）。</li>
<li>CMN 要求同一段内信道不变；若录音中途换了设备，分段做 CMN 才有效。</li>
<li>设备声纹的 \(f_0=100\,\mathrm{Hz}\) 落在第 2–3 个 Mel 滤波器里，而语音的判别信息多在上千 Hz；
<b>照搬语音的 26 通道配置会把最关键的频带只分到 2–3 个通道</b>。可改用线性滤波器组、或把 Mel 下限抬到 50 Hz 后加密低频通道。</li></ul>
</div>
"""
