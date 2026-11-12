# -*- coding: utf-8 -*-
"""理论桥接块：把郑君里《信号与系统》（第三版，上下册）的定理逐讲钉到现有各讲末尾。

每块追加在该讲「推导详解」之后、成为独立的 .bridge 区块，公式编号用 Z<讲号>-<序>，
与正文的「讲-序」、专题的 A/B/C/D/E-序 均不冲突。
"""

BRIDGES = {}

BRIDGES["s1"] = r"""
<div class="bridge">
<div class="btitle">理论桥接 · 郑君里《信号与系统》上册 §1.2–§1.4、§3.2</div>
<p>第 1 讲说「任何复杂声音都能拆成正弦波之和」，这句话的严格版本是傅里叶级数，而它能成立的根本原因只有一条：<strong>复指数是 LTI 系统的特征函数</strong>。把 \(e^{j\omega t}\) 送进冲激响应为 \(h\) 的系统：</p>
<div class="mathbox">
  <div class="math">\[ \int h(\tau)e^{j\omega(t-\tau)}\mathrm{d}\tau=e^{j\omega t}\underbrace{\int h(\tau)e^{-j\omega\tau}\mathrm{d}\tau}_{H(\omega)} \tag{Z1-1} \]</div>
  <div class="mathnote"><p>输出仍是 \(e^{j\omega t}\)，只被乘了一个复数 \(H(\omega)\)——<b>形状不变，只改幅度和相位</b>。这就是为什么「用正弦分解信号」在 LTI 世界里不是一种选择，而是唯一自然的坐标系：每个谐波各自独立通过系统，互不干扰。反过来，任何非线性环节（整流、限幅、AGC）都会立刻破坏这条性质，产生新的频率成分。</p></div>
</div>
<p>教材 §1.4 用 \(\delta(t)\) 与 \(u(t)\) 建立「基本单元」，§3.2 再把它展开成 FS：\(x(t)=\sum_n C_n e^{jn\omega_1 t}\)，系数 \(C_n=\frac{1}{T}\int_{-T/2}^{T/2}x(t)e^{-jn\omega_1t}\mathrm{d}t\) 就是「信号与第 \(n\) 次谐波的内积」。<b>专题 A 里变压器 100 / 200 / 300 Hz 的谐波串，正是这个式子的物理实例</b>：磁致伸缩的平方非线性决定了哪些 \(C_n\) 非零，而不是随便出现的峰。</p>
</div>
"""

BRIDGES["s2"] = r"""
<div class="bridge">
<div class="btitle">理论桥接 · 郑君里《信号与系统》上册 §3.10–§3.11、§5.9–§5.10</div>
<p>第 2 讲的核心结论「\(F_s\gt2f_m\) 才能无失真」在这里有完整证明链：抽样 = 乘冲激串 → 频域周期复制 (D-12) → 不重叠条件 (D-13) → 理想低通取出原谱 → sinc 内插 (D-16)。补一个常被忽略的点：<strong>整个采样–量化链条里，只有量化是非线性、不可逆的</strong>。</p>
<div class="mathbox">
  <div class="math">\[ x_q[n]=Q\big(x(nT_s)\big)=x(nT_s)+e[n],\qquad e[n]\sim U\Big(-\frac{\Delta}{2},\frac{\Delta}{2}\Big) \tag{Z2-1} \]</div>
  <div class="mathnote"><p>把量化误差建模成与信号<strong>不相关</strong>的均匀白噪声，才有第 2 讲那条 \(\mathrm{SNR}=6.02B+1.76\) dB。这个假设成立需要三个条件：信号跨越多个量化级、采样点之间足够「去相关」、无过载削顶。<b>失效场景很具体</b>：小信号（只用到 2–3 个量化级）时误差与信号强相关，会出现谐波失真；信号接近满量程时削顶产生大量高次谐波——两者都会让实测 SNR 明显低于公式值。</p></div>
</div>
<p>教材 §5.10 的 PCM 把这条链补全：抽样 → 量化 → 编码 → 传输 → 解码 → 内插。工程上 8 kHz / 16 bit 的电话语音，理论上限 4 kHz、实际可用 3.4 kHz，就是因为抗混叠与重建滤波器都需要过渡带（见 D.8 的佩利–维纳准则）。</p>
</div>
"""

BRIDGES["s3"] = r"""
<div class="bridge">
<div class="btitle">理论桥接 · 郑君里《信号与系统》上册 §6.6–§6.8</div>
<p>第 3 讲的三个时域特征，在理论上其实只依赖两个量：<strong>能量</strong>与<strong>自相关</strong>。教材 §6.7 的维纳–辛钦定理把后者与功率谱连成一对傅里叶变换：</p>
<div class="mathbox">
  <div class="math">\[ R_x[m]=\sum_n x[n]x[n-m]\ \longleftrightarrow\ S_x(\omega)=\big|X(e^{j\omega})\big|^2 \tag{Z3-1} \]</div>
  <div class="mathnote"><p>于是「时域测周期」与「频域看谐波」是同一件事的两种算法：自相关在基音周期处出现峰，等价于功率谱在谐波处出现梳状结构。<b>这也解释了为什么自相关比直接找峰值稳健</b>：它把整段信号的能量都用来投票，而不是只看某一个峰。</p></div>
</div>
<p>过零率则对应功率谱的<strong>二阶矩</strong>。对零均值高斯过程，\(\mathbb{E}[\text{ZCR}]=2\sqrt{m_2/m_0}\)（式 D-29），离散计算时把积分换成求和：\(m_0=\sum_k S[k]\)、\(m_2=\sum_k (kF_s/N)^2S[k]\)。这意味着：<b>过零率不是「高频含量的粗糙指标」，而是一个有明确量纲的谱矩估计</b>；当信号被宽带噪声污染时，\(m_2\) 被抬高，过零率虚高，双门限端点检测就会把噪声段判成语音——这正是第 3 讲「误区」里那条的定量解释。</p>
</div>
"""

BRIDGES["s4"] = r"""
<div class="bridge">
<div class="btitle">理论桥接 · 郑君里《信号与系统》上册 §3.8，下册 §9.3、§9.5</div>
<p>第 4 讲从「DFT 定义」直接开算，容易让人以为它是凭空规定的。真实的逻辑链是：<strong>FS → DFS → DFT</strong>，而 DFT 只是 z 变换在单位圆上的 \(N\) 点等间隔采样 (E-10)：</p>
<div class="mathbox">
  <div class="math">\[ X[k]=X(z)\Big|_{z=e^{j2\pi k/N}},\qquad k=0,1,\dots,N-1 \tag{Z4-1} \]</div>
  <div class="mathnote"><p><b>这一条解释了三件常被误解的事：</b>① 补零不提高分辨率——它只是让你在同样的连续谱上多采几个点；② 频谱以 \(2\pi\) 为周期——因为 \(e^{j\omega}\) 本身以 \(2\pi\) 为周期；③ 实序列共轭对称——\(X[N-k]=X^*[k]\)，所以单边谱只取前 \(N/2+1\) 点，且要乘 \(2/N\) 补偿被丢掉的一半能量。</p></div>
</div>
<p><b>把本讲义的参数代进去算一次：</b>帧长 200 点、补零到 \(N=512\)、\(F_s=8000\)。频率栅格间隔是 \(8000/512=15.625\) Hz，但<strong>真实分辨能力</strong>由窗长决定：矩形窗主瓣宽 \(2F_s/N_{\text{frame}}=2\times8000/200=80\) Hz。所以「能分辨两个相隔 20 Hz 的峰」是错觉——那只是栅格密，不是分辨率高。这条区分，是第 4 讲与专题 E.5 的交汇点。</p>
</div>
"""

BRIDGES["s5"] = r"""
<div class="bridge">
<div class="btitle">理论桥接 · 郑君里《信号与系统》上册 §6.10、§5.4</div>
<p>第 5 讲用「傅里叶尺度性质」说明窗长与频率分辨率的矛盾，教材给的是更强的结论：由柯西–施瓦茨不等式与帕塞瓦尔定理可证</p>
<div class="mathbox">
  <div class="math">\[ \Delta t\cdot\Delta\omega\geq\frac12\quad\Longleftrightarrow\quad \Delta t\cdot\Delta f\geq\frac{1}{4\pi} \tag{Z5-1} \]</div>
  <div class="mathnote"><p>等号<strong>仅当</strong> \(x(t)\) 为高斯函数时成立。教材同时给出工程版本：理想低通的阶跃响应上升时间 \(t_r\) 与带宽 \(B\) 满足 \(t_rB=1\)——注意这是「响应速度 vs 带宽」的另一种说法，与 (Z5-1) 同源。<b>算到账：</b>25 ms 窗（\(\Delta t\approx12.5\) ms）给出 \(\Delta f\geq1/(4\pi\times0.0125)\approx6.4\) Hz 的理论下界；而矩形窗实际主瓣是 80 Hz，相差一个数量级——因为矩形窗远非高斯，且工程上还要压旁瓣。所以「理论下界」与「实际窗的主瓣」是两回事，不能混着引用。</p></div>
</div>
<p>教材 §5.4 还指出理想低通不可实现（(D-23) 非因果）。这直接说明：<strong>STFT 不可能有「既无限窄又无限短」的分析窗</strong>，因为那要求一个理想的分频器。Gabor 变换选高斯窗，就是在给定 \(\Delta t\) 下取到 (Z5-1) 等号的最优解。</p>
</div>
"""

BRIDGES["s6"] = r"""
<div class="bridge">
<div class="btitle">理论桥接 · 郑君里《信号与系统》下册 §8.9、§9.10、§10.7</div>
<p>MFCC 常被当成一串「工程配方」背下来。用系统语言看，它的每一步都有明确身份：</p>
<table class="sym">
  <tr><th>步骤</th><th>系统语言</th><th>教材</th></tr>
  <tr><td>预加重</td><td>一阶 FIR 高通，零点 \(z=0.97\)</td><td>§10.7、§8.8</td></tr>
  <tr><td>分帧加窗</td><td>时域相乘 ⇒ 频域与窗谱卷积（<b>这一步破坏 LTI</b>）</td><td>§3.8</td></tr>
  <tr><td>FFT</td><td>z 变换单位圆上 \(N\) 点采样</td><td>§9.5</td></tr>
  <tr><td>Mel 滤波器组</td><td>并联带通组，中心频率按 Mel 分布</td><td>§10.2</td></tr>
  <tr><td>取 log</td><td>同态变换，把卷积变成加法（<b>非线性</b>）</td><td>—</td></tr>
  <tr><td>DCT</td><td>偶延拓后的正交变换，去相关</td><td>§9.10</td></tr>
</table>
<div class="mathbox">
  <div class="math">\[ \underbrace{x[n]\ast h[n]}_{\text{声道}\,\times\,\text{激励}}\ \xrightarrow{\ \log\ }\ \log X+\log H\ \xrightarrow{\ \text{DCT}\ }\ \text{倒谱} \tag{Z6-1} \]</div>
  <div class="mathnote"><p><b>关键洞察：</b>整条链路只有「加窗」和「取 log」两处<strong>不是 LTI</strong>。加窗把长信号切成短段，用「短时平稳」近似时变系统；取 log 则是同态解卷积的核心，把两个相乘的频谱变成相加，从而能用低通（DCT 截断）把慢变的声道包络 \(H\) 与快变的激励谐波 \(X\) 分开。<b>所以 MFCC 不是「随便设计的特征」，而是「在短时平稳假设下，用同态变换做一次近似解卷积」。</b>这也解释了它为什么对信道/麦克风差异有一定鲁棒性——信道是乘性的，取 log 后变成加性偏置，DCT 后集中在低阶，丢掉 c0 就削掉了一大半。</p></div>
</div>
</div>
"""

BRIDGES["s7"] = r"""
<div class="bridge">
<div class="btitle">理论桥接 · 郑君里《信号与系统》上册 §5.6、§6.3–§6.4</div>
<p>第 7 讲讲小波与 EMD「用另一组基看信号」，教材 §6.3 的正交函数分解给了统一框架：任何信号都可以在一组<strong>完备正交函数集</strong>上展开，\(x=\sum_n c_n\varphi_n\)，\(c_n=\langle x,\varphi_n\rangle/\|\varphi_n\|^2\)。傅里叶用复指数，小波用伸缩平移的母小波，EMD 则用<strong>数据驱动</strong>的 IMF——它不是预先给定的基，这也是 EMD 难以做严格正交性证明的原因。</p>
<div class="mathbox">
  <div class="math">\[ z(t)=x(t)+j\hat{x}(t),\qquad \hat{x}(t)=x(t)\ast\frac{1}{\pi t},\qquad a(t)=|z(t)|,\ \ f_i(t)=\frac{1}{2\pi}\frac{\mathrm{d}}{\mathrm{d}t}\arg z(t) \tag{Z7-1} \]</div>
  <div class="mathnote"><p>教材 §5.6 的希尔伯特变换正是 EMD 最后一步「Hilbert 谱」的数学基础：对每个 IMF 构造解析信号，得到<strong>包络</strong> \(a(t)\) 与<strong>瞬时频率</strong> \(f_i(t)\)，才能画出「时间–频率–能量」三维图。<b>边界提醒</b>：瞬时频率只对<strong>单分量、窄带</strong>信号有物理意义；直接把原始多分量信号送进希尔伯特变换会得到负频率等无意义结果——这正是 EMD 必须先分解、再对每个 IMF 单独做希尔伯特变换的原因。</p></div>
</div>
<p>教材 §6.4 的帕塞瓦尔定理还保证了小波/EMD 分解不「漏能量」：只要基是完备的，各尺度系数平方和就等于总能量。诊断里用「小波包能量谱」做特征（专题 A），前提正是这一条。</p>
</div>
"""

BRIDGES["s8"] = r"""
<div class="bridge">
<div class="btitle">理论桥接 · 郑君里《信号与系统》上册 §2.7，下册 §7.6</div>
<p>第 8 讲的 BPNN 看上去与信号与系统无关，其实它的<strong>前向计算就是一个多层复合函数</strong>，而反向传播是链式法则——两者都不满足 LTI。这一点必须说清，否则很容易把「卷积定理」「频域滤波」误用到神经网络上。</p>
<div class="mathbox">
  <div class="math">\[ \mathbf{h}^{(l)}=\sigma\big(W^{(l)}\mathbf{h}^{(l-1)}+\mathbf{b}^{(l)}\big)\ \Longrightarrow\ \frac{\partial L}{\partial W^{(l)}}=\boldsymbol{\delta}^{(l)}\big(\mathbf{h}^{(l-1)}\big)^{\mathsf T} \tag{Z8-1} \]</div>
  <div class="mathnote"><p><b>哪里破坏了 LTI：</b>① \(\sigma(\cdot)\) 是非线性（ReLU、sigmoid）；② 权重随训练变化，是时变的。所以神经网络<strong>没有</strong>一个固定的 \(H(\omega)\)，也不能用卷积定理分析。但仍有一条与 LTI 相通的直觉：<b>反向传播是把误差信号「反向通过」一层层线性系统（\(W^{\mathsf T}\)）并逐层乘上局部增益 \(\sigma'\)</b>；若这些增益的乘积长期小于 1 就梯度消失，大于 1 就梯度爆炸——这与 E.8 的反馈稳定性判据是同构的。</p></div>
</div>
<p>教材 §2.7 与 §7.6 的卷积表示在这里还有一个用处：<strong>梯度检查</strong>本质是数值微分 \(\big(L(\theta+\epsilon)-L(\theta-\epsilon)\big)/2\epsilon\)，它是线性近似，与解析梯度在 \(\epsilon\to0\) 时一致。所以第 8 讲强调「同时报相对误差与绝对误差」——近零梯度处相对误差会被放大，这是数值微分的固有性质，不是反向传播写错了。</p>
</div>
"""

BRIDGES["s9"] = r"""
<div class="bridge">
<div class="btitle">理论桥接 · 郑君里《信号与系统》下册 §7.6、§9.4</div>
<p>第 9 讲说 CNN 的卷积层「在做一个可学习的滤波器」。严格说，深度学习框架实现的是<strong>互相关</strong>而不是卷积：</p>
<div class="mathbox">
  <div class="math">\[ y[i,j]=\sum_{u,v}w[u,v]\,x[i+u,j+v]\quad(\text{互相关})\ \ \text{vs}\ \ \sum_{u,v}w[u,v]\,x[i-u,j-v]\quad(\text{卷积}) \tag{Z9-1} \]</div>
  <div class="mathnote"><p>只差一个核翻转。因为核是学习出来的，翻转与否等价于参数重命名，不影响表达能力——但如果你要用 FFT 加速、或把训练好的核当「滤波器」去做频域分析，就必须先翻转，否则相位全错。<b>与教材 (E-11) 的联系：</b>把多通道、多核的求和展开，CNN 一层就是若干组「卷积和 + 偏置 + 非线性」；<code>im2col</code> 只是把这一步改写成矩阵乘法，数学上没变。</p></div>
</div>
<p>另一个精确的对应是<strong>感受野与卷积长度</strong>：第 \(l\) 层的等效核长度是前几层的组合，\(L_l=L_{l-1}+(k_l-1)\)（无空洞、stride=1）。这与 D.3 的「卷积输出长度 = 输入 + 核 − 1」是同一个加法。所以深层堆叠相当于一个很长的 FIR，只是中间插了非线性——这也是为什么 CNN 能同时看到「局部纹理（底层）」和「全局结构（深层）」。</p>
</div>
"""

BRIDGES["s10"] = r"""
<div class="bridge">
<div class="btitle">理论桥接 · 郑君里《信号与系统》下册 §11.4–§11.5</div>
<p>第 10 讲讲「学习率太大 loss 会炸」，教材第 11 章的反馈稳定性给出了严格解释。把梯度下降写成闭环递推并在极小点附近线性化：</p>
<div class="mathbox">
  <div class="math">\[ w_{t+1}-w^*=(I-\eta H)(w_t-w^*)\ \Longrightarrow\ \text{收敛}\iff \big|1-\eta\lambda_i\big|\lt1\ \ \forall i\ \iff\ 0\lt\eta\lt\frac{2}{\lambda_{\max}} \tag{Z10-1} \]</div>
  <div class="mathnote"><p>这就是教材 §11.4 根轨迹的离散版：增益 \(\eta\) 增大时，「闭环极点」\(1-\eta\lambda_i\) 从 1 向 −1 移动，越过 −1 就进入单位圆外，开始振荡发散。<b>三个可直接用的推论：</b>① 学习率上限由<strong>最大曲率</strong>决定，与平均曲率无关——所以数据里只要有一小撮「陡方向」就会限制步长；② 条件数 \(\lambda_{\max}/\lambda_{\min}\) 越大，收敛越慢（病态）；③ 动量/Adam 相当于给闭环加阻尼与自适应增益，本质是在改极点位置。第 10 讲的「学习率预热」「梯度裁剪」都能在这条式子里找到位置。</p></div>
</div>
</div>
"""

BRIDGES["s11"] = r"""
<div class="bridge">
<div class="btitle">理论桥接 · 郑君里《信号与系统》上册 §6.9</div>
<p>第 11 讲把声纹确认描述成「注册模板 vs 测试语音，算一个相似度再比阈值」。教材 §6.9 的匹配滤波器证明了这个做法在什么意义下最优：在加性白噪声中，使判决时刻输出信噪比最大的滤波器是</p>
<div class="mathbox">
  <div class="math">\[ h(t)=K\,s^*(t_m-t),\qquad \rho_{\max}=\frac{2E}{N_0} \tag{Z11-1} \]</div>
  <div class="mathnote"><p>也就是说，<strong>「与模板做相关」不是一种启发式，而是白噪声下的最优检测器</strong>；它与模板的能量成正比、与噪声谱密度成反比，且与波形细节无关。这给声纹工程三个直接结论：① 打分要对<strong>能量归一化</strong>，否则模板能量不同会让分数不可比（对应第 12 讲的分数归一化 ZT-norm）；② 噪声不是白的（信道、背景人声），所以匹配滤波只是上界，真实系统要靠 Channel 补偿；③ 多模板/多条件注册，相当于用多个 \(s_k\) 分别匹配再融合，逼近「未知波形」下的广义似然比检验。</p></div>
</div>
</div>
"""

BRIDGES["s12"] = r"""
<div class="bridge">
<div class="btitle">理论桥接 · 郑君里《信号与系统》上册 §6.9，下册 §9.4</div>
<p>第 12 讲的 EER、DCF 是「判决层」的指标，而它们的可分性来自「表示层」的信噪比。把 (Z11-1) 接过来：匹配滤波输出的信噪比 \(\rho_{\max}=2E/N_0\) 决定了两个分布（同人 / 异人）的重叠程度。若把两个得分分布近似为等方差高斯，均值间隔 \(d\)、标准差 \(\sigma\)，则</p>
<div class="mathbox">
  <div class="math">\[ \mathrm{EER}=\Phi\!\Big(-\frac{d}{2\sigma}\Big),\qquad d'=\frac{d}{\sigma}\ \text{（可分性）} \tag{Z12-1} \]</div>
  <div class="mathnote"><p>\(\Phi\) 是标准正态分布函数。这条式子把「EER 1%」翻译成一个可操作的物理量：<b>\(d'=2\Phi^{-1}(0.99)\approx4.65\)</b>，即同人/异人均值要拉开近 5 个标准差。它同时解释了为什么「换信道后 EER 暴涨」——信道失配让同人分布的方差 \(\sigma\) 变大（而不是均值 \(d\) 变小），所以补偿手段（CMVN、PLDA 自适应）主要是在<strong>压方差</strong>。第 12 讲的 DCF 加权（\(C_{\text{miss}}\) 与 \(C_{\text{fa}}\) 不等）则是在这条 ROC 上按代价选工作点，数学上是贝叶斯风险最小化，与教材 §6.9 的「最小错误概率判决」同一逻辑。</p></div>
</div>
</div>
"""

BRIDGES["s13"] = r"""
<div class="bridge">
<div class="btitle">理论桥接 · 郑君里《信号与系统》上册 §4.9–§4.10、§5.6</div>
<p>第 13 讲的 GMM-UBM 用一堆高斯分量描述声纹，每个分量的协方差矩阵刻画「能量在频谱上怎么分布」。这在系统语言里就是<strong>一组二阶谐振系统</strong>：</p>
<div class="mathbox">
  <div class="math">\[ H_k(s)=\frac{\omega_{n,k}^2}{s^2+2\zeta_k\omega_{n,k}s+\omega_{n,k}^2},\qquad Q_k=\frac{1}{2\zeta_k},\ \ B_k\approx\frac{\omega_{n,k}}{Q_k} \tag{Z13-1} \]</div>
  <div class="mathnote"><p>共振峰越窄（\(Q\) 越高、阻尼越小），在频谱上越是尖峰；GMM 的一个分量若在某个频带方差很小，就相当于一个高 \(Q\) 的谐振。所以「GMM 分量数」与「能分辨多少个共振峰」是相关的——分量太少，相邻共振峰会被一个宽高斯糊在一起。<b>i-vector 的 Total Variability 空间</b>则相当于给这组谐振器加了一个低维的「全局调节旋钮」，用几十维描述「这个人的声道整体偏长还是偏短」。</p></div>
</div>
<p>倒谱（第 6 讲）与教材 §4.10 的最小相位也有直接关系：只有当声道系统是最小相位（零极点都在单位圆内），倒谱的因果部分才完整携带声道信息，且逆滤波稳定。这就是为什么 MFCC 用 DCT 取前 13 维（低阶倒谱）就能近似还原声道包络——高阶项对应激励的快速变化，丢掉它们相当于做了一次低通平滑。</p>
</div>
"""

BRIDGES["s14"] = r"""
<div class="bridge">
<div class="btitle">理论桥接 · 郑君里《信号与系统》下册 §12.2–§12.5</div>
<p>第 14 讲的 x-vector 用 TDNN + 统计池化把变长帧序列压成一个定长嵌入。用状态变量的语言，这就是一个<strong>离散状态空间模型</strong>在跑：</p>
<div class="mathbox">
  <div class="math">\[ \mathbf{x}[n+1]=A\mathbf{x}[n]+B\mathbf{u}[n],\qquad \mathbf{y}=C\mathbf{x}[n]+D\mathbf{u}[n],\qquad \mathbf{e}=\text{Pool}\big(\{\mathbf{x}[n]\}\big) \tag{Z14-1} \]</div>
  <div class="mathnote"><p>TDNN 的膨胀卷积相当于让 \(A\) 具有稀疏的、跨多帧的结构（感受野变大）；统计池化则把整段轨迹的均值与标准差汇总——用教材的话说，是在<strong>估计状态的充分统计量</strong>。教材 §12.6–§12.7 的可控性/可观性在这里有直观对应：如果某维状态对输入完全不敏感（不可控），它对嵌入就没有贡献，等于白占维度；如果它对输出不可见（不可观），训练信号传不回去，梯度会很小。<b>这正是「嵌入维度不是越大越好」的理论解释。</b></p></div>
</div>
<p>再往远看一步：RNN 就是 (Z14-1) 加非线性激活，LSTM 的门控是在给 \(A\) 加可学习的遗忘因子，Kalman 滤波是线性高斯下的最优状态估计，而 S4/Mamba 这类状态空间模型直接把 \(A\) 参数化成结构化矩阵、用卷积形式并行训练。<strong>声纹里的「帧 → 句」聚合，与这些模型做的是同一件事：从一条状态轨迹里提取一个定长摘要。</strong></p>
</div>
"""

# 附录：郑君里 12 章 → 讲义 17 讲的全映射（追加在附录 s16 的推导详解之后）
BRIDGES["s16"] = r"""
<div class="bridge">
<div class="btitle">资料补录 · 郑君里《信号与系统》第三版（上、下册）章节映射</div>
<p>本版新增的两册教材是<strong>理论根基</strong>，不按「讲」组织，因此单列一张映射表。上册 448 页、88 条书签；下册 416 页、72 条书签；均为扫描版（无文本层），讲义只依据其目录框架与标准结论重写，未转录原文。</p>
<table class="sym">
  <tr><th>教材位置</th><th>章节主题</th><th>本讲义对应</th><th>先读哪一段</th></tr>
  <tr><td>上册 §1.2–§1.8</td><td>信号分类、δ 与阶跃、LTI 定义</td><td>第 1 讲；专题 D.2</td><td>D.2「卷积表示是推出来的」</td></tr>
  <tr><td>上册 §2.2–§2.9</td><td>微分方程、零输入/零状态、卷积及性质</td><td>第 1、6 讲；专题 D.2–D.3</td><td>D.3 手算卷积 + 对拍</td></tr>
  <tr><td>上册 §3.2–§3.9</td><td>FS、FT、性质、卷积定理</td><td>第 1、4 讲；专题 D.4–D.5</td><td>D.4 泄漏的定量解释</td></tr>
  <tr><td>上册 §3.10–§3.11</td><td>抽样信号的 FT、抽样定理</td><td>第 2 讲；专题 D.6</td><td>D.6 sinc 内插推导</td></tr>
  <tr><td>上册 §4.2–§4.11</td><td>拉普拉斯、H(s)、零极点、稳定性</td><td>第 6 讲；专题 D.7</td><td>D.7 共振峰 = 一对极点</td></tr>
  <tr><td>上册 §4.12–§4.13</td><td>双边拉氏、拉氏与傅氏关系</td><td>专题 E.2（ROC 思想）</td><td>E.2 四种 ROC 形态</td></tr>
  <tr><td>上册 §5.2–§5.6</td><td>H(jω)、无失真、理想低通、可实现性、希尔伯特</td><td>第 2、7 讲；专题 D.8</td><td>D.8 佩利–维纳准则</td></tr>
  <tr><td>上册 §5.7–§5.11</td><td>调制解调、带通、抽样恢复、PCM、复用</td><td>第 2 讲；专题 D.6</td><td>D.6 三条失效边界</td></tr>
  <tr><td>上册 §6.2–§6.5</td><td>矢量空间、正交分解、帕塞瓦尔、沃尔什</td><td>第 4、6、7 讲；专题 D.9</td><td>D.9 帕塞瓦尔手算</td></tr>
  <tr><td>上册 §6.6–§6.8</td><td>相关、能量谱与功率谱</td><td>第 3 讲；专题 D.9</td><td>D.9 维纳–辛钦 + ZCR</td></tr>
  <tr><td>上册 §6.9</td><td>匹配滤波器</td><td>第 11、12 讲；专题 D.9</td><td>D.9 柯西–施瓦茨推导</td></tr>
  <tr><td>上册 §6.10</td><td>测不准原理及其证明</td><td>第 5 讲；专题 D.9</td><td>D.9 式 (D-31)~(D-33)</td></tr>
  <tr><td>下册 §7.2–§7.7</td><td>序列、差分方程、单位样值响应、卷积和、解卷积</td><td>第 3、6、9 讲；专题 E.1</td><td>E.1 解卷积为什么会炸</td></tr>
  <tr><td>下册 §8.2–§8.8</td><td>z 变换、ROC、逆 z、性质、系统函数</td><td>第 4、6 讲；专题 E.2–E.4</td><td>E.4 因果稳定判据</td></tr>
  <tr><td>下册 §8.9–§8.10</td><td>DTFT、离散系统频率响应</td><td>第 4 讲；专题 E.3</td><td>E.3 单位圆读图法</td></tr>
  <tr><td>下册 §9.2–§9.5</td><td>离散性与周期性、DFS→DFT、DFT 性质与 z 的关系</td><td>第 4 讲；专题 E.5</td><td>E.5 圆周卷积条件</td></tr>
  <tr><td>下册 §9.6–§9.10</td><td>FFT、DFT 应用（OFDM）、沃尔什变换、DCT</td><td>第 4、6 讲；专题 E.6</td><td>E.6 DCT = 偶延拓</td></tr>
  <tr><td>下册 §10.2–§10.5</td><td>模拟滤波器逼近、无源网络、频率变换</td><td>专题 E.7</td><td>E.7 巴特沃斯/切比雪夫</td></tr>
  <tr><td>下册 §10.6–§10.7</td><td>IIR、FIR 数字滤波器</td><td>第 6 讲；专题 E.7</td><td>E.7 双线性变换与窗函数法</td></tr>
  <tr><td>下册 §11.2–§11.6</td><td>反馈、自激、根轨迹、奈奎斯特、信号流图</td><td>第 10 讲；专题 E.8</td><td>E.8 学习率上限</td></tr>
  <tr><td>下册 §12.2–§12.7</td><td>状态方程、求解、线性变换、可控可观</td><td>第 14 讲；专题 E.9</td><td>E.9 RNN 与状态空间</td></tr>
</table>
<div class="note"><span class="t">怎么用这两册书</span>不建议从头读到尾。想搞清「为什么加窗会泄漏」读上册 §3.8 + 专题 D.4；想搞清「8 kHz 从哪来」读上册 §3.10–§3.11 + 专题 D.6；想搞清「共振峰是什么」读上册 §4.9 + 专题 D.7；想搞清「DFT 为什么有损」读下册 §9.2–§9.5 + 专题 E.5；想搞清「训练为什么炸」读下册 §11.4–§11.5 + 专题 E.8。<b>每一条都配了手算例与代码对拍，不必啃扫描版的原书也能走通。</b></div>
</div>
"""
