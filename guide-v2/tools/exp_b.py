# -*- coding: utf-8 -*-
"""推导详解扩展内容：第 7–11 讲。"""

EXP_B = {}

EXP_B["s7"] = r"""
<div class="derive">
<div class="dtitle">推导详解 · 第 7 讲　小波、Mallat 算法与 EMD 筛分</div>

<h4>1. 符号对照表</h4>
<table class="sym"><tr><th>符号</th><th>含义</th><th>与 STFT 的对应</th></tr>
<tr><td>\(a\)</td><td>尺度参数，&gt;0；拉宽小波</td><td>相当于「窗长」，但随频率自适应</td></tr>
<tr><td>\(b\)</td><td>平移参数，时间位置</td><td>相当于帧起点 \(mS\)</td></tr>
<tr><td>\(\psi\)</td><td>母小波，零均值、有限能量</td><td>相当于窗，但必须振荡且均值为 0</td></tr>
<tr><td>\(h,g\)</td><td>分解低通 / 高通滤波器</td><td>—</td></tr>
<tr><td>\(\tilde h,\tilde g\)</td><td>重构（综合）滤波器</td><td>—</td></tr>
<tr><td>\(cA_j,cD_j\)</td><td>第 \(j\) 层近似 / 细节系数</td><td>—</td></tr>
</table>

<h4>2. 为什么母小波必须零均值：容许条件</h4>
<p>由 \(\int\psi(t)\,\mathrm{d}t=\hat\psi(0)\)，若要能从 \(W(a,b)\) 反演原信号，需要</p>
<div class="math sub">\[ C_\psi=\int_{-\infty}^{\infty}\frac{\big|\hat\psi(\omega)\big|^2}{|\omega|}\,\mathrm{d}\omega<\infty
\quad\Longrightarrow\quad \hat\psi(0)=0\ \Leftrightarrow\ \int\psi(t)\,\mathrm{d}t=0 \tag{7-6} \]</div>
<p>否则 \(\omega\to0\) 时被积函数 \(\sim|\hat\psi(0)|^2/|\omega|\) 发散。零均值意味着 \(\psi\) 必须有正有负、呈振荡状——
这就是「小波（wavelet）」名字的由来。有了它，连续小波反变换为</p>
<div class="math sub">\[ x(t)=\frac{1}{C_\psi}\int_0^{\infty}\!\!\int_{-\infty}^{\infty}
W(a,b)\,\frac{1}{\sqrt a}\psi\!\left(\frac{t-b}{a}\right)\frac{\mathrm{d}b\,\mathrm{d}a}{a^2} \tag{7-7} \]</div>

<h4>3. 尺度 → 频率：把 1/a 关系推清楚</h4>
<p>Morlet 母小波 \(\psi(t)=\pi^{-1/4}e^{j\omega_0t}e^{-t^2/2}\)（\(\omega_0\approx6\) 使容许条件近似成立）。
尺度 \(a\) 下小波为 \(\psi(t/a)\)，其傅里叶中心频率由尺度性质得 \(\omega=\omega_0/a\)（rad/sample），换算成物理频率：</p>
<div class="math sub">\[ f=\frac{\omega_0}{2\pi a}\,F_s\approx\frac{0.9549}{a}F_s
\quad(\omega_0=6),\qquad a=\frac{\omega_0 F_s}{2\pi f} \tag{7-8} \]</div>
<p>配套实现用 \(f_c\approx0.8125\)（Morlet 的实测中心频率，取决于采样与归一化约定），
于是 \(F_s=8000\)、\(a=8\Rightarrow f\approx812\,\mathrm{Hz}\)；\(a=80\Rightarrow f\approx81\,\mathrm{Hz}\)。
<b>关键陷阱</b>：若把尺度按对数取样（常见做法 \(a_j=a_02^{j\Delta}\)），得到的频率轴是<b>指数分布</b>的；
直接拿线性刻度去标，会把 100 Hz 标成 900 Hz。正确做法是先按式 (7-8) 算出每个尺度对应的频率，
再重采样插值到均匀线性频率轴——配套项目 <code>cwt_morlet()</code> 的修复正是这一步。</p>

<h4>4. 与 STFT 的分辨率对比（定量）</h4>
<p>小波在尺度 \(a\) 下的等效窗宽 \(\Delta t_a=a\,\Delta t_\psi\)，等效带宽 \(\Delta f_a=\Delta f_\psi/a\)，故</p>
<div class="math sub">\[ \Delta t_a\cdot\Delta f_a=\Delta t_\psi\,\Delta f_\psi=\text{常数}
\quad\text{但}\quad \frac{\Delta f_a}{f}=\frac{\Delta f_\psi}{\omega_0}=\text{常数} \tag{7-9} \]</div>
<p>即 <b>恒 Q（恒定相对带宽）分析</b>：高频处时间分辨率好、频率分辨率差；低频处反过来。
STFT 则是恒绝对带宽。对「100 Hz 嗡鸣 + 3 kHz 瞬态放电」这类信号，小波更合适：
低频要分开 100/150 Hz（需好频率分辨），高频要定位放电时刻（需好时间分辨）。</p>

<h4>5. DWT：把 Mallat 算法写成矩阵，顺便解释那个 1.40 的 bug</h4>
<p>单层分解可以写成矩阵形式 \(\mathbf y=A\mathbf x\)，其中 \(A\) 的每行是 \(h\) 或 \(g\) 平移 2 点后的滤波器（\(\downarrow2\)）。
对<b>正交小波</b>（Haar、dbN）有 \(A^{\mathsf T}A=I\)，因此</p>
<div class="math sub">\[ \mathbf x=A^{\mathsf T}\mathbf y=A^{\mathsf T}\!\begin{bmatrix}cA_1\\cD_1\end{bmatrix}
=\underbrace{A_h^{\mathsf T}cA_1}_{\text{低通支路}}+\underbrace{A_g^{\mathsf T}cD_1}_{\text{高通支路}} \tag{7-10} \]</div>
<p>这就是式 (7-3) 第二行的矩阵写法。它说明<b>重构就是分析算子的转置</b>，不需要另推一套公式。</p>
<p>配套项目里 db4 最初的重构误差达 <b>1.40</b>，原因正是把 \(A^{\mathsf T}\) 误写成「另一套卷积 + 相位偏移」：
分析用的是 \(\sum_k h[k-2n]x[k]\)，转置后应为 \(x[n]=\sum_j h[n-2j]cA[j]\)（<b>先上采样再卷积，且索引是 \(n-2j\)</b>），
而错误实现写成了普通相关卷积。改成显式构造 \(A\) 并取 \(A^{\mathsf T}\) 后，误差降到 \(10^{-12}\) 量级。
这个例子值得记住：<b>「看起来对称」不等于「是转置」，用矩阵写一遍最保险。</b></p>
<p>db4 的 8 个分解低通系数（归一化到 \(\sum h_k=\sqrt2\)）：</p>
<div class="math sub">\[ h=\tfrac{1}{4\sqrt2}\big[1+\sqrt3,\ 3+\sqrt3,\ 3-\sqrt3,\ 1-\sqrt3\big]\ \text{的 4 抽头推广}
\quad\Rightarrow\ g[k]=(-1)^k h[7-k] \tag{7-11} \]</div>
<p>高通由「低通反转 + 交替变号」得到（正交镜像滤波器 QMF），保证 \(A\) 正交。Haar 是最简单的特例：
\(h=[1/\sqrt2,1/\sqrt2]\)、\(g=[1/\sqrt2,-1/\sqrt2]\)，此时 \(cA_1[n]=\frac{x[2n]+x[2n+1]}{\sqrt2}\)、
\(cD_1[n]=\frac{x[2n]-x[2n+1]}{\sqrt2}\)，手工就能验证 \(x[2n]=(cA_1+cD_1)/\sqrt2\) ✓。</p>

<h4>6. EMD：筛分停止准则与端点效应</h4>
<p>第 \(k\) 次筛分的收敛判据用<b>标准差准则</b>：</p>
<div class="math sub">\[ \mathrm{SD}_k=\frac{\sum_{t}\big|h_{k-1}(t)-h_k(t)\big|^2}{\sum_t h_{k-1}^2(t)}<0.2\sim0.3 \tag{7-12} \]</div>
<p>太严（SD 要求极小）会过度筛分，把振幅调制也抹平，IMF 变成等幅的纯调频波；太松则 IMF 上下包络不对称，
瞬时频率失去意义。分解终止条件：残差 \(r\) 的极值点数 \(\le2\)，或 \(\max|r|\) 与 \(\sum|\mathrm{IMF}|\) 相比可忽略。</p>
<p><b>端点效应</b>：三次样条在序列两端没有约束，包络会「飞出去」，且误差随筛分逐层向内传播。
标准补救是<b>镜像延拓</b>：在左右各加一段关于端点对称翻转的极值点，筛完只取中间原长部分。</p>
<p>得到 IMF 后，对每个分量做 Hilbert 变换 \(\tilde c_j(t)=\frac{1}{\pi}\,\mathrm{p.v.}\!\int\frac{c_j(\tau)}{t-\tau}\mathrm d\tau\)，
构造解析信号 \(z_j(t)=c_j+j\tilde c_j=a_j(t)e^{j\phi_j(t)}\)，瞬时频率 \(f_j(t)=\frac{1}{2\pi}\frac{\mathrm d\phi_j}{\mathrm dt}\)，
于是得到时间–频率–能量三维的 <b>Hilbert 谱</b> \(H(f,t)=\sum_j a_j^2(t)\delta(f-f_j(t))\)。
与语谱图不同，它不受窗长约束，能同时给出高频瞬态的精确定位与低频的精细频率。</p>

<h4>7. 公式 ↔ 代码</h4>
<pre><code># 式(7-1) CWT：逐尺度与信号做卷积
for a in scales:
    psi = morlet(np.arange(-4*a, 4*a) / a) / np.sqrt(a)
    W[i] = np.convolve(x, psi, 'same')

# 式(7-3) DWT 单层（分析）
cA = conv_down(x, h, 2); cD = conv_down(x, g, 2)

# 式(7-10) 重构：显式用分析算子的转置（这是修 bug 后的写法）
A = build_analysis_matrix(len(x), h, g)     # 每行是平移 2 点的 h / g
y = np.concatenate([cA, cD])
x_hat = A.T @ y                              # 误差 ~1e-12

# 式(7-12) EMD 筛分
while True:
    env_hi = spline(maxima); env_lo = spline(minima)
    m = (env_hi + env_lo) / 2
    h_new = h - m
    if sd(h, h_new) < 0.25: break
    h = h_new</code></pre>

<h4>8. 边界与失效条件</h4>
<ul><li><b>模态混叠</b>：一个 IMF 里混入尺度差异极大的成分，或同一尺度被拆到多个 IMF。噪声最容易诱发；EEMD/CEEMDAN 通过加噪集合平均缓解。</li>
<li>信号长度必须远大于最大小波尺度，否则 \(a\) 大的尺度卷积边界占满整段，系数全是端点伪影（画 CWT 图时应标出「影响锥」cone of influence 并裁掉）。</li>
<li>DWT 每层降采样使长度减半，长度非 2 的幂时需做对称延拓（<code>mode='symmetric'</code>），否则重构长度对不上。</li>
<li>EMD 没有正交性保证，各 IMF 能量之和不必等于原信号能量，做能量特征时要先验证。</li></ul>
</div>
"""

EXP_B["s8"] = r"""
<div class="derive">
<div class="dtitle">推导详解 · 第 8 讲　反向传播的每一项都算出来</div>

<h4>1. 网络结构与维度表</h4>
<table class="sym"><tr><th>量</th><th>形状</th><th>本讲义取值</th><th>说明</th></tr>
<tr><td>\(\mathbf x\)</td><td>\((d,1)\)</td><td>\(d=39\)</td><td>MFCC 统计特征</td></tr>
<tr><td>\(W_1,\mathbf b_1\)</td><td>\((H,d),(H,1)\)</td><td>\(H=32\)</td><td>隐层</td></tr>
<tr><td>\(\mathbf h\)</td><td>\((H,1)\)</td><td>32</td><td>隐层激活</td></tr>
<tr><td>\(W_2,\mathbf b_2\)</td><td>\((C,H),(C,1)\)</td><td>\(C=6\)</td><td>六类工况</td></tr>
<tr><td>\(\mathbf p\)</td><td>\((C,1)\)</td><td>6</td><td>softmax 概率</td></tr>
</table>

<h4>2. softmax 的导数：δ₂ = p − y 的完整推导</h4>
<p>记 \(p_c=e^{z_c}/\sum_j e^{z_j}=e^{z_c}/Z\)。先求雅可比，对 \(i\neq c\) 与 \(i=c\) 分别用商法则：</p>
<div class="math sub">\[ \frac{\partial p_c}{\partial z_i}=
\begin{cases}
\dfrac{e^{z_i}Z-e^{z_c}e^{z_i}}{Z^2}=p_i(1-p_c)=p_c(\delta_{ci}-p_i),&i=c\\[8pt]
\dfrac{-e^{z_c}e^{z_i}}{Z^2}=-p_c p_i=p_c(\delta_{ci}-p_i),&i\neq c
\end{cases} \tag{8-8} \]</div>
<p>两种情况可统一写成 \(\partial p_c/\partial z_i=p_c(\delta_{ci}-p_i)\)。代入 \(L=-\sum_c y_c\ln p_c\)：</p>
<div class="math sub">\[ \begin{aligned}
\frac{\partial L}{\partial z_i}&=-\sum_c\frac{y_c}{p_c}\frac{\partial p_c}{\partial z_i}
=-\sum_c\frac{y_c}{p_c}\,p_c(\delta_{ci}-p_i)\\
&=-\sum_c y_c\delta_{ci}+p_i\sum_c y_c=-y_i+p_i
\end{aligned} \tag{8-9} \]</div>
<p>最后一步用了 one-hot 标签 \(\sum_c y_c=1\)。<b>结论：softmax 的雅可比与交叉熵的导数恰好抵消，
梯度退化成极简的 \(p-y\)</b>。这就是「分类任务用交叉熵而不用 MSE」的数学理由：MSE 的梯度里会多出
\(p_c(1-p_c)\) 因子，在预测错得离谱（\(p\approx0\) 或 1）时梯度趋零，训练直接卡死。</p>

<h4>3. 逐层回传：链式法则的每一步</h4>
<p><b>输出层权重</b>：由 \(z_{2,c}=\sum_j W_{2,cj}h_j+b_{2,c}\) 得 \(\partial z_{2,c}/\partial W_{2,ij}=\delta_{ci}h_j\)，于是</p>
<div class="math sub">\[ \frac{\partial L}{\partial W_{2,ij}}=\frac{\partial L}{\partial z_{2,i}}\,h_j=\delta_{2,i}h_j
\quad\Longrightarrow\quad \frac{\partial L}{\partial W_2}=\boldsymbol\delta_2\mathbf h^{\mathsf T} \tag{8-10} \]</div>
<p><b>传到隐层</b>：\(\mathbf z_2=W_2\mathbf h+\mathbf b_2\)，故 \(\partial L/\partial\mathbf h=W_2^{\mathsf T}\boldsymbol\delta_2\)；
再由 \(\mathbf h=\sigma(\mathbf z_1)\) 逐元素求导 \(\partial h_j/\partial z_{1,j}=\sigma'(z_{1,j})=h_j(1-h_j)\)：</p>
<div class="math sub">\[ \boldsymbol\delta_1=\frac{\partial L}{\partial\mathbf z_1}
=\big(W_2^{\mathsf T}\boldsymbol\delta_2\big)\odot\sigma'(\mathbf z_1),\qquad
\frac{\partial L}{\partial W_1}=\boldsymbol\delta_1\mathbf x^{\mathsf T} \tag{8-11} \]</div>
<p><b>偏置</b>：\(\partial z/\partial b=1\)，故 \(\partial L/\partial\mathbf b_2=\boldsymbol\delta_2\)、\(\partial L/\partial\mathbf b_1=\boldsymbol\delta_1\)。</p>
<p>统一规律：<b>每层的权重梯度 = 该层的误差向量 ⊗ 该层的输入向量</b>。
检查形状是最快的自检：\(\boldsymbol\delta_2\) 是 \((C,1)\)、\(\mathbf h^{\mathsf T}\) 是 \((1,H)\) → 外积 \((C,H)\)，与 \(W_2\) 一致 ✓。</p>

<h4>4. 数值梯度：为什么中心差分是 O(ε²)</h4>
<p>对 \(L(w)\) 在 \(w\) 处做泰勒展开：</p>
<div class="math sub">\[ \begin{aligned}
L(w+\varepsilon)&=L(w)+\varepsilon L'(w)+\tfrac{\varepsilon^2}{2}L''(w)+\tfrac{\varepsilon^3}{6}L'''(w)+O(\varepsilon^4)\\
L(w-\varepsilon)&=L(w)-\varepsilon L'(w)+\tfrac{\varepsilon^2}{2}L''(w)-\tfrac{\varepsilon^3}{6}L'''(w)+O(\varepsilon^4)
\end{aligned} \tag{8-12} \]</div>
<p>两式相减，偶次项全消：\(\dfrac{L(w+\varepsilon)-L(w-\varepsilon)}{2\varepsilon}=L'(w)+\dfrac{\varepsilon^2}{6}L'''(w)+O(\varepsilon^4)\)，
误差 \(O(\varepsilon^2)\)。而前向差分 \(\frac{L(w+\varepsilon)-L(w)}{\varepsilon}=L'(w)+\frac{\varepsilon}{2}L''(w)+\cdots\) 只有 \(O(\varepsilon)\)。</p>
<p><b>ε 不能无限小</b>：\(\varepsilon<10^{-8}\) 时两个相近的 \(L\) 值相减会发生灾难性抵消（双精度约 16 位有效数字），
舍入误差反超截断误差。经验值 \(\varepsilon=10^{-5}\sim10^{-4}\)（\(\sqrt[3]{\epsilon_{\mathrm{mach}}}\) 量级）。
判据建议用<b>相对误差</b> \(\dfrac{\|g_{\mathrm{analytic}}-g_{\mathrm{numeric}}\|}{\|g_{\mathrm{analytic}}\|+\|g_{\mathrm{numeric}}\|}<10^{-7}\)，
避免逐元素比较时被近零元素放大。</p>

<h4>5. 完整手算一轮（带所有中间数）</h4>
<div class="math sub">\[ \begin{aligned}
&x=[1,2],\ w=[0.5,-0.5],\ b=0,\ y=1,\ \eta=0.1\\
&z=0.5(1)-0.5(2)=-0.5,\quad p=\frac{1}{1+e^{0.5}}=0.3775407\\
&L=-\ln p=0.9740770,\quad \delta=p-y=-0.6224593\\
&\nabla_w=\delta x=[-0.6224593,\,-1.2449187],\quad \nabla_b=-0.6224593\\
&w'=[0.5+0.0622459,\,-0.5+0.1244919]=[0.5622459,\,-0.3755081]
\end{aligned} \tag{8-13} \]</div>
<p>验证：\(z'=0.5622459(1)-0.3755081(2)=-0.1887703\)，\(p'=\sigma(-0.1887703)=0.4529549\)，
\(L'=-\ln 0.4529549=0.7920007\)。损失从 0.9741 降到 0.7920 ✓。
一阶近似预测的下降量是 \(\eta\|\nabla\|^2=0.1(0.6225^2+1.2449^2+0.6225^2)=0.2326\)，
实际下降 0.1821，小于预测——因为步长偏大、二阶项把它拉回来了，这正是<b>学习率不能太大</b>的定量体现。</p>

<h4>6. 梯度消失的定量说明</h4>
<p>若把 sigmoid 换成 \(L\) 层全 sigmoid 网络，\(\boldsymbol\delta_1\) 中含 \(\prod_{l}\sigma'(z_l)\)，
而 \(\sigma'(z)\le0.25\)，于是 5 层之后梯度上界为 \(0.25^5\approx10^{-3}\)，10 层后 \(10^{-6}\)。
ReLU 在正区导数恒为 1，连乘不衰减，这是它能训深网络的原因。代价是「死 ReLU」：
\(z<0\) 时导数恒 0，该神经元永久不再更新，需靠 Leaky ReLU 或小学习率缓解。</p>

<h4>7. 公式 ↔ 代码</h4>
<pre><code># 式(8-2) 前向（softmax 减 max 防溢出）
z1 = W1 @ x + b1; h = sigmoid(z1)
z2 = W2 @ h + b2
e = np.exp(z2 - z2.max()); p = e / e.sum()

# 式(8-9) 反向：四行全部与公式一一对应
d2 = p - onehot(y)                       # delta_2
gW2 = d2 @ h.T; gb2 = d2                 # 式(8-10)
d1 = (W2.T @ d2) * (h * (1 - h))         # 式(8-11) sigma'=h(1-h)
gW1 = d1 @ x.T;  gb1 = d1

# 式(8-12) 梯度检查（中心差分）
for i in range(W.size):
    Wp = W.copy(); Wp.flat[i] += eps
    Wm = W.copy(); Wm.flat[i] -= eps
    gn = (loss(Wp) - loss(Wm)) / (2*eps)
    assert abs(gn - g.flat[i]) < 1e-8</code></pre>
<p>配套 <code>acoustic-lab/src/nn.py</code> 的 <code>grad_check()</code> 实测绝对误差 \(<10^{-10}\)。
若某元素相对误差显示为 \(5\times10^{-6}\)，先查它是不是量级 \(10^{-6}\) 的近零梯度——
那个例子里绝对误差只有 \(10^{-11}\)，属正常浮点噪声。</p>

<h4>8. 边界与失效条件</h4>
<ul><li>权重初始化不能全为 0（对称破缺失败，所有隐单元学到同一东西）；用 He/Xavier：\(\mathrm{Var}(w)=2/d_{\mathrm{in}}\)。</li>
<li>特征未标准化时，量级大的维度主导梯度，损失曲面狭长，SGD 会来回震荡——MFCC 各维量纲差异大，务必先标准化。</li>
<li>交叉熵里 \(\ln p_c\) 在 \(p_c\to0\) 时爆炸，实现要加 \(\varepsilon\) 或直接用 log-sum-exp 形式 \(L=-z_{c^*}+\ln\sum_j e^{z_j}\)。</li>
<li>数值梯度检查要关掉 dropout、固定 batch，否则两次前向的随机性会污染差分。</li></ul>
</div>
"""

EXP_B["s9"] = r"""
<div class="derive">
<div class="dtitle">推导详解 · 第 9 讲　CNN 的尺寸、参数与反向传播</div>

<h4>1. 输出尺寸公式的逐步推导</h4>
<p>输入高 \(H_{\mathrm{in}}\)，上下各补 \(P\) 圈零 → 有效高 \(H'=H_{\mathrm{in}}+2P\)。
大小为 \(F\) 的核，其左上角能放的位置满足「右下角不越界」，即起点 \(i\) 从 0 取到 \(H'-F\)。
步长 \(S\) 时能取到的起点数为 \(\lfloor(H'-F)/S\rfloor+1\)，于是</p>
<div class="math sub">\[ H_{\mathrm{out}}=\left\lfloor\frac{H_{\mathrm{in}}+2P-F}{S}\right\rfloor+1 \tag{9-8} \]</div>
<p>算例：\(H=32,F=3,P=1,S=1\to32\)；\(P=0,S=2\to\lfloor29/2\rfloor+1=15\)。
若希望「same」保持尺寸且 \(S=1\)，解得 \(P=(F-1)/2\)，所以 \(F\) 取奇数——这就是卷积核几乎都是 3、5、7 的原因。</p>

<h4>2. im2col 的维度为什么是 \((CF^2)\times(H_{\mathrm{out}}W_{\mathrm{out}})\)</h4>
<p>每个输出位置需要一块 \(F\times F\times C\) 的数据，拉平成长度 \(CF^2\) 的列；共 \(H_{\mathrm{out}}W_{\mathrm{out}}\) 个输出位置。
把 \(C_{\mathrm{out}}\) 个核各拉成一行，卷积就变成</p>
<div class="math sub">\[ Y_{[C_{\mathrm{out}}\times H_{\mathrm{out}}W_{\mathrm{out}}]}
=W_{\mathrm{col}}\,[C_{\mathrm{out}}\times CF^2]\;\cdot\;X_{\mathrm{col}}\,[CF^2\times H_{\mathrm{out}}W_{\mathrm{out}}] \tag{9-9} \]</div>
<p>例：输入 \((1,32,32)\)、\(F=3\)、\(P=1\)、\(C_{\mathrm{out}}=4\) → \(X_{\mathrm{col}}\) 是 \(9\times1024\)，
\(W_{\mathrm{col}}\) 是 \(4\times9\)，一次 \(4\times9\times1024=36\,864\) 次乘加即得全部输出。
内存代价：原输入 1024 个数 → 展开后 9216 个，放大 9 倍（\(F^2\)）。</p>

<h4>3. 反向传播三条公式从矩阵乘直接得到</h4>
<p>由 \(Y=W_{\mathrm{col}}X_{\mathrm{col}}\)，记上游梯度 \(G=\partial L/\partial Y\)（形状同 \(Y\)），套用第 8 讲式 (8-10)：</p>
<div class="math sub">\[ \frac{\partial L}{\partial W_{\mathrm{col}}}=G\,X_{\mathrm{col}}^{\mathsf T},\qquad
\frac{\partial L}{\partial X_{\mathrm{col}}}=W_{\mathrm{col}}^{\mathsf T}G \tag{9-10} \]</div>
<p>验证形状：\(G\) 是 \((C_{\mathrm{out}},N_{\mathrm{pos}})\)、\(X_{\mathrm{col}}^{\mathsf T}\) 是 \((N_{\mathrm{pos}},CF^2)\) →
结果 \((C_{\mathrm{out}},CF^2)\) 与 \(W_{\mathrm{col}}\) 一致 ✓。</p>
<p><b>col2im 必须累加</b>：同一个输入像素会出现在多个重叠窗口里，因此 \(\partial L/\partial X\) 的每一处是
若干个 \(\partial L/\partial X_{\mathrm{col}}\) 元素的<b>和</b>。写成覆盖赋值会让梯度检查在窗口重叠区失败，且失败位置呈周期性——
这是最容易忽略的实现细节。</p>
<p><b>池化回传</b>：最大池化前向保存 argmax 掩码 \(M\)，反向 \(\partial L/\partial X=M\odot\mathrm{up}(G)\)（只回传最大值位置）；
平均池化则把 \(G\) 除以池化窗口面积后广播回全部位置。</p>

<h4>4. 参数量与感受野的两笔账</h4>
<div class="math sub">\[ N_{\mathrm{param}}=(F^2C_{\mathrm{in}}+1)C_{\mathrm{out}},\qquad
\mathrm{RF}_k=\mathrm{RF}_{k-1}+(F_k-1)\prod_{j<k}S_j \tag{9-11} \]</div>
<p>三层 \(3\times3\)、步长全 1：RF = 3 → 5 → 7，参数量 \(3\times(9C_{\mathrm{in}}+1)C_{\mathrm{out}}\)；
若用一层 \(7\times7\) 达到同样感受野，参数量是 \((49C_{\mathrm{in}}+1)C_{\mathrm{out}}\)，约多 1.8 倍，
而且少两层非线性。<b>「多层小核优于单层大核」</b>就是这么算出来的。</p>
<p>把感受野换算到物理时间：8 kHz 下 RF=80 点 = 10 ms，恰是 100 Hz 基频的一个周期；
若网络只有 3 层 \(3\times3\)（RF=7 点 = 0.875 ms），它<b>根本看不到一个完整周期</b>，
再深的全连接也补不回这个信息。设计网络前先算这笔账，比盲目调层数有用得多。</p>

<h4>5. 公式 ↔ 代码</h4>
<pre><code># 式(9-8) 尺寸
Hout = (Hin + 2*P - F)//S + 1

# 式(9-9) im2col（单通道示意）
cols = np.array([x[i:i+F, j:j+F].ravel()
                 for i in range(Hout) for j in range(Wout)]).T   # (F*F, Npos)
out = (W_col @ cols).reshape(Cout, Hout, Wout)

# 式(9-10) 反向 + col2im（注意 += 累加）
dW_col = dout.reshape(Cout, -1) @ cols.T
dX_col = W_col.T @ dout.reshape(Cout, -1)
dx = np.zeros_like(x)
for idx, (i, j) in enumerate(positions):
    dx[i:i+F, j:j+F] += dX_col[:, idx].reshape(F, F)   # 累加！</code></pre>

<h4>6. 边界与失效条件</h4>
<ul><li>边界像素参与的输出位置更少，梯度天然偏小；若不做 padding，输出逐层缩小，几层后就没了。声纹图谱常用 <code>same</code> padding 保持时间轴。</li>
<li>im2col 在大输入上内存爆炸：\(F=5\)、输入 \(512\times512\) 时放大 25 倍；生产库改用隐式 GEMM 或 Winograd。</li>
<li>把「语谱图」当普通图像做二维卷积时，两个轴的物理含义不同（时间 vs 频率），平移不变性在时间轴成立、在频率轴<b>不成立</b>（100 Hz 的峰挪到 3 kHz 是完全不同的故障）。因此更严谨的做法是频率轴不共享权重，或只用一维时间卷积。</li></ul>
</div>
"""

EXP_B["s10"] = r"""
<div class="derive">
<div class="dtitle">推导详解 · 第 10 讲　优化器、正则化与训练动力学</div>

<h4>1. 从 SGD 到 Adam：每个更新式在做什么</h4>
<div class="math sub">\[ \begin{aligned}
\text{SGD:}\quad &\theta_{t+1}=\theta_t-\eta\,\nabla_\theta L(\theta_t)\\
\text{Momentum:}\quad &v_t=\gamma v_{t-1}+\eta\nabla L,\quad \theta_{t+1}=\theta_t-v_t\\
\text{Adam:}\quad &m_t=\beta_1m_{t-1}+(1-\beta_1)g_t,\quad v_t=\beta_2v_{t-1}+(1-\beta_2)g_t^2\\
&\hat m_t=\frac{m_t}{1-\beta_1^t},\quad \hat v_t=\frac{v_t}{1-\beta_2^t},\quad
\theta_{t+1}=\theta_t-\frac{\eta\,\hat m_t}{\sqrt{\hat v_t}+\epsilon}
\end{aligned}\tag{10-4} \]</div>
<p>动量 \(v_t\) 是梯度的指数移动平均，等价于给损失曲面加「惯性」：在狭长谷地里抵消横向震荡、累积纵向推进。
Adam 的 \(m_t\) 是一阶矩（方向），\(v_t\) 是二阶矩（每维的尺度），相除相当于<b>给每个参数自动配一个学习率</b>——
梯度长期大的维度步长被压小，梯度小的维度被放大。\(\hat m,\hat v\) 的除项是<b>偏差修正</b>：
初始 \(m_0=v_0=0\)，前几步估计会系统性偏小，除以 \(1-\beta^t\) 后无偏。常用 \(\beta_1=0.9,\beta_2=0.999,\epsilon=10^{-8}\)。</p>

<h4>2. L2、dropout、BN 的数学形式</h4>
<div class="math sub">\[ L_{\mathrm{reg}}=L+\frac{\lambda}{2}\|\theta\|_2^2,\qquad
\nabla L_{\mathrm{reg}}=\nabla L+\lambda\theta,\qquad
\theta\leftarrow(1-\eta\lambda)\theta-\eta\nabla L \tag{10-5} \]</div>
<p>可见 L2 每次更新都把权重乘一个 \(<1\) 的因子（权重衰减）。<b>注意</b>：Adam 下 L2 与权重衰减并不等价
（自适应学习率会把惩罚项也缩放），要严格解耦应使用 AdamW。</p>
<div class="math sub">\[ \text{dropout:}\quad \tilde h=\frac{m\odot h}{1-p},\ m_i\sim\mathrm{Bernoulli}(1-p),\qquad
\text{BN:}\quad \hat h=\frac{h-\mu_B}{\sqrt{\sigma_B^2+\epsilon}},\ h'=\gamma\hat h+\beta \tag{10-6} \]</div>
<p>dropout 除以 \(1-p\) 是<b>反向 dropout</b>，保证训练时激活的期望与推理时一致；忘了除会导致训练/推理输出差 \(1/(1-p)\) 倍。
BN 在训练时用 batch 内统计量、推理时用滑动平均的全局统计量，两个模式混用是常见线上事故。</p>

<h4>3. 过拟合的偏差–方差分解</h4>
<div class="math sub">\[ \mathbb E\big[(y-\hat f)^2\big]
=\underbrace{\big(\mathbb E[\hat f]-f\big)^2}_{\text{偏差}^2}
+\underbrace{\mathbb E\big[(\hat f-\mathbb E\hat f)^2\big]}_{\text{方差}}
+\underbrace{\sigma^2}_{\text{不可约噪声}} \tag{10-7} \]</div>
<p>模型太小 → 偏差大（训练/验证损失都高）；模型太大且数据少 → 方差大（训练损失低、验证损失高）。
早停、正则化、增数据都在压方差；加容量、加特征、训更久在压偏差。<b>看两条曲线的相对位置</b>就能判断该往哪边走，
比盲目调参有效。</p>

<h4>4. 学习率的定量选择</h4>
<p>损失沿某方向的曲率由 Hessian 特征值 \(\lambda_{\max}\) 决定，SGD 稳定条件是 \(\eta<2/\lambda_{\max}\)；
超过就震荡甚至发散。实用做法：<b>学习率范围测试</b>——从 \(10^{-6}\) 起每个 batch 按指数增大 \(\eta\)，
记录损失，取「损失开始稳定下降」到「开始上扬」之间偏左一个数量级的值。
配合余弦退火 \(\eta_t=\eta_{\min}+\frac{\eta_0-\eta_{\min}}{2}\big(1+\cos(\pi t/T)\big)\) 可兼顾前期快速与后期收敛。</p>

<h4>5. 数据划分的正确姿势（对声纹尤其重要）</h4>
<p>设某设备有 10 段录音、每段 48 帧，共 480 个样本。若按帧随机切 60/20/20，
同一段录音的相邻帧会同时出现在训练和测试里，它们的相似度接近 1，测试准确率虚高到接近 100%。
正确做法是<b>按录音段（或按说话人/设备编号）分组切分</b>，保证测试集中的段在训练时完全没出现过。
更进一步，评估「未知设备」泛化能力时要用 leave-one-device-out。</p>

<h4>6. 公式 ↔ 代码</h4>
<pre><code># 式(10-4) Adam（含偏差修正）
m = b1*m + (1-b1)*g; v = b2*v + (1-b2)*g*g
mhat = m/(1-b1**t); vhat = v/(1-b2**t)
theta -= lr*mhat/(np.sqrt(vhat) + 1e-8)

# 式(10-5) L2 / 式(10-6) 反向 dropout
g += lam*theta
h = (h * (np.random.rand(*h.shape) > p)) / (1-p)

# 早停：验证损失连续 patience 轮不降即停
if val_loss < best - 1e-4: best, wait = val_loss, 0
else: wait += 1
if wait >= patience: break</code></pre>

<h4>7. 边界与失效条件</h4>
<ul><li>类别极不平衡时，交叉熵会被多数类主导；改用加权 CE（权重 \(\propto1/n_c\)）或 focal loss。</li>
<li>小 batch 下 BN 的 \(\mu_B,\sigma_B^2\) 估计噪声大，可换 LayerNorm / GroupNorm。</li>
<li>验证集被反复用于调参，本质上也会「过拟合到验证集」；超参数调得多时，应再留一个最终测试集。</li></ul>
</div>
"""

EXP_B["s11"] = r"""
<div class="derive">
<div class="dtitle">推导详解 · 第 11 讲　声纹任务的数学定义</div>

<h4>1. 两种任务的严格表述</h4>
<p>设注册模型为 \(\lambda_{\mathrm{tar}}\)，测试语音特征为 \(X\)，打分函数 \(s(X,\lambda)\)。</p>
<div class="math sub">\[ \textbf{确认 (1:1)}:\quad s(X,\lambda_{\mathrm{tar}})\mathop{\gtrless}_{H_1}^{H_0}\theta,\qquad
\textbf{辨识 (1:N)}:\quad \hat c=\arg\max_{c}s(X,\lambda_c) \tag{11-1} \]</div>
<p>确认是<b>假设检验</b>：\(H_0\)「不是本人」、\(H_1\)「是本人」，必须设阈值，两类错误都可能出现。
闭集辨识是<b>分类</b>：只需比大小，无需阈值；但现实中存在「库里根本没有此人」的开集情形，
此时要加一个拒识门限，否则任何陌生人都会被强行匹配给最像的那个人。</p>

<h4>2. 似然比检验：为什么「比分数」在统计上是对的</h4>
<p>Neyman–Pearson 引理指出，在给定 FA 水平下使 FR 最小的最优检验是<b>似然比</b>：</p>
<div class="math sub">\[ \Lambda(X)=\frac{p(X\mid H_1)}{p(X\mid H_0)}\mathop{\gtrless}_{H_0}^{H_1}\theta',\qquad
\log\Lambda=\log p(X\mid\lambda_{\mathrm{tar}})-\log p(X\mid\lambda_{\mathrm{background}}) \tag{11-2} \]</div>
<p>GMM-UBM 的打分正是这个式子：目标模型与 UBM 的对数似然之差。
而「余弦相似度」可以看作在高斯先验、长度归一化 embedding 假设下对似然比的一种简化。
<b>理解了这个，就不会把打分值当成概率</b>——它只是似然比的单调函数，尺度随模型、数据而变，所以必须做 z/t-norm（第 12 讲）。</p>

<h4>3. 系统的四层数据流</h4>
<table class="sym"><tr><th>层</th><th>输入 → 输出</th><th>本讲义对应</th></tr>
<tr><td>① 采集</td><td>声波 → WAV</td><td>第 1–2 讲（\(F_s=8\) kHz、16 bit）</td></tr>
<tr><td>② 前端</td><td>WAV → 39 维 MFCC 序列</td><td>第 3–7 讲</td></tr>
<tr><td>③ 后端</td><td>特征序列 → 模型/embedding → 分数</td><td>第 8–10、13–14 讲</td></tr>
<tr><td>④ 判决</td><td>分数 → 是/否</td><td>第 12 讲（\(\theta\)、DCF、归一化）</td></tr>
</table>
<p>任何一层出错都会表现为「指标差」，但根因完全不同：① 混叠无法靠后端补救；② 参数错（如预加重压掉 100 Hz）后端再强也学不到；
③ 模型容量不足是欠拟合；④ 阈值选错则模型明明很好、用户却频繁被拒。<b>排查时按层从前往后走，别一上来就调网络。</b></p>

<h4>4. 边界与失效条件</h4>
<ul><li>注册数据太少 → 模型无法覆盖本人的音素/工况变化，FR 飙升。i-vector 与 x-vector 正是为解决少样本注册而生。</li>
<li>训练与部署的信道不一致（不同麦克风、不同距离、不同采样率）→ 分数分布整体平移，全局阈值失效，必须做分数归一化或域适配。</li>
<li>时间漂移：设备老化、麦克风灵敏度变化会让人几个月后「不像自己」，需要模板更新机制。</li></ul>
</div>
"""
