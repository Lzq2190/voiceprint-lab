# -*- coding: utf-8 -*-
"""专题 D：信号与系统（上册）——连续时间 LTI 系统与变换域（完整 <section>）。

资料来源：郑君里、应启珩、杨为理《信号与系统》第三版 上册（第 1–6 章）。
该 PDF 为扫描版、无文本层，只有 88 条书签目录；本专题按目录给出的章节框架，
用讲义自身的符号体系重写标准结论与推导，未照抄原文。
书中记法 Sa(x)=sin(x)/x、omega_s=2*pi/T_s 予以保留并注明。
"""

TOPIC_D = r"""
<section id="sD">
  <h2><span class="no">专题 D</span>信号与系统（上）：连续时间 LTI 与变换域</h2>

  <div class="goal">
    <div class="g">目标</div>
    <ul>
      <li>能把讲义里所有「滤波器、加窗、分帧、频谱」操作，追溯到一条统一的定理：LTI 系统的卷积表示与卷积定理。</li>
      <li>能自己推出抽样定理与 sinc 内插恢复，说清 8 kHz 为什么对应 4 kHz 上限、3.4 kHz 又是从哪来的。</li>
      <li>会用零极点几何法读频率响应，理解共振峰、最小相位、稳定性这些词在声纹特征里到底指什么。</li>
      <li>能用帕塞瓦尔定理和柯西–施瓦茨不等式，推出匹配滤波器与测不准原理，不再把「窗长不能两全」当口号。</li>
    </ul>
  </div>
  <div class="goal">
    <div class="g">产出</div>
    <ul><li>一张「讲义操作 → 信号与系统定理 → 教材章节」映射表；三组手算到底的数值例（卷积和、帕塞瓦尔、预加重频响）；一份可自己复算的定理清单。</li></ul>
  </div>

  <div class="note"><span class="t">这本教材怎么读</span>郑君里《信号与系统》第三版分上下两册，共 12 章、160 条目录条目。上册（第 1–6 章）讲<strong>连续时间</strong>：LTI 系统、傅里叶变换、拉普拉斯变换、通信系统、信号矢量空间；下册（第 7–12 章）讲<strong>离散时间</strong>：差分方程、z 变换、DFT、数字滤波器、反馈与状态变量，见专题 E。本讲义原先是「从声音出发往特征走」的工程顺序，这两个专题是<strong>回头补地基</strong>：不是另起炉灶，而是把第 1–14 讲用到的每一个结论都挂回严格的理论出处。教材是扫描版（无文本层），所以下面的推导是按目录框架、用本讲义的符号重写标准结论，<b>不是原文转录</b>；书页里的记法 \(\operatorname{Sa}(x)=\sin x/x\) 与 \(\omega_s=2\pi/T_s\) 予以保留。</div>

  <h3>D.1　一张地图：讲义的每个动作，背后是哪条定理</h3>
  <p>先建立对应关系，后面每一节都是把这张表里的某一行展开成推导。看懂这张表，就能明白「信号与系统」不是另一门课，而是本讲义所有公式的语法。</p>
  <table class="sym">
    <tr><th>讲义里在做的事</th><th>背后真正的定理</th><th>郑君里章节</th><th>本专题</th></tr>
    <tr><td>预加重 \(y[n]=x[n]-0.97x[n-1]\)</td><td>一阶 FIR 差分方程 / 系统函数零点</td><td>§2.2, §4.6, §8.8</td><td>D.2, D.7, E.4</td></tr>
    <tr><td>分帧后乘汉明窗</td><td>时域相乘 \(\leftrightarrow\) 频域卷积（泄漏的根源）</td><td>§3.8, §5.4</td><td>D.4</td></tr>
    <tr><td>加窗后做 FFT 得频谱</td><td>DFT 是 z 变换单位圆上的等间隔采样</td><td>§9.3, §9.5</td><td>E.5</td></tr>
    <tr><td>8 kHz 采样、4 kHz 上限</td><td>抽样信号的傅里叶变换 + 抽样定理</td><td>§3.10, §3.11, §5.9</td><td>D.6</td></tr>
    <tr><td>Mel / Gammatone 滤波器组</td><td>带通滤波、二阶谐振系统、物理可实现性</td><td>§4.9, §5.5, §10.2</td><td>D.7, D.8, E.7</td></tr>
    <tr><td>短时能量、自相关、过零率</td><td>相关函数 \(\leftrightarrow\) 功率谱（维纳–辛钦）、谱矩</td><td>§6.6–§6.8</td><td>D.9</td></tr>
    <tr><td>STFT 窗长不能同时兼顾时频</td><td>测不准原理（柯西–施瓦茨 + 帕塞瓦尔）</td><td>§6.10</td><td>D.9</td></tr>
    <tr><td>模板匹配 / 余弦打分 / DTW</td><td>匹配滤波器使输出信噪比最大</td><td>§6.9</td><td>D.9</td></tr>
    <tr><td>共振峰、LPC、倒谱</td><td>二阶谐振极点 / 全极点模型 / 最小相位</td><td>§4.9, §4.10, §8.8</td><td>D.7, E.4</td></tr>
    <tr><td>EMD 的瞬时频率、包络</td><td>希尔伯特变换与解析信号</td><td>§5.6</td><td>D.8</td></tr>
    <tr><td>CNN 的卷积层</td><td>卷积和（严格说是互相关，差一个翻转）</td><td>§2.7, §7.6</td><td>D.3, E.1</td></tr>
    <tr><td>训练发散 / IIR 递归爆炸</td><td>稳定性判据（极点位置、奈奎斯特）</td><td>§4.11, §11.5</td><td>E.8</td></tr>
  </table>

  <h3>D.2　冲激信号与 LTI：卷积表示是「推」出来的，不是「定义」出来的</h3>
  <h4>1. 符号对照表</h4>
  <table class="sym"><tr><th>符号</th><th>含义</th><th>本讲义对应</th></tr>
  <tr><td>\(\delta(t)\)</td><td>单位冲激（狄拉克函数）</td><td>单位样值 \(\delta[n]\)</td></tr>
  <tr><td>\(u(t)\)</td><td>单位阶跃</td><td>窗的起点</td></tr>
  <tr><td>\(h(t)\)</td><td>冲激响应：\(\delta(t)\) 通过系统后的输出</td><td>滤波器系数向量</td></tr>
  <tr><td>\(x(t),y(t)\)</td><td>输入、输出</td><td>波形、滤波后波形</td></tr>
  <tr><td>\(H(\omega)\), \(H(s)\)</td><td>频率响应、系统函数</td><td>预加重、Mel 滤波器</td></tr>
  <tr><td>\(\ast\)</td><td>卷积运算</td><td><code>np.convolve</code></td></tr>
  </table>

  <h4>2. 从 δ 的筛选性质到卷积积分（四步，一步都不跳）</h4>
  <p>狄拉克函数不是普通函数，而是由它的<strong>筛选性质</strong>定义的广义函数：\(\delta(t)=0\ (t\neq0)\)、\(\int_{-\infty}^{\infty}\delta(t)\,\mathrm{d}t=1\)，于是对任意在 \(t\) 处连续的 \(x\)：</p>
  <div class="mathbox">
    <div class="math">\[ \int_{-\infty}^{\infty}x(\tau)\,\delta(t-\tau)\,\mathrm{d}\tau=x(t) \tag{D-1} \]</div>
    <div class="mathnote"><p>把 \(x\) 拆成「无穷多个加权的移位冲激」——这是全部 LTI 理论的第一块砖。离散版更直观：\(x[n]=\sum_k x[k]\,\delta[n-k]\)，就是把每个样点单独拎出来。</p></div>
  </div>
  <p><b>第 1 步（分解）</b>：由 (D-1)，输入可写成 \(x(t)=\int x(\tau)\delta(t-\tau)\mathrm{d}\tau\)。<br>
  <b>第 2 步（时不变）</b>：系统对 \(\delta(t)\) 的响应是 \(h(t)\)；时不变性保证对 \(\delta(t-\tau)\) 的响应就是 \(h(t-\tau)\)，形状不变、只平移。<br>
  <b>第 3 步（齐次性）</b>：分量 \(x(\tau)\delta(t-\tau)\mathrm{d}\tau\) 的响应是 \(x(\tau)h(t-\tau)\mathrm{d}\tau\)。<br>
  <b>第 4 步（可加性 / 叠加积分）</b>：把所有分量的响应加起来：</p>
  <div class="mathbox">
    <div class="math">\[ y(t)=\int_{-\infty}^{\infty}x(\tau)\,h(t-\tau)\,\mathrm{d}\tau=(x\ast h)(t) \tag{D-2} \]</div>
    <div class="mathnote"><p><b>结论：</b>「线性 + 时不变」这两条看似朴素的性质，<strong>唯一地</strong>决定了系统只能是卷积。所以只要你在讲义里看到「滤波器」，它背后一定有一个 \(h\)；只要 \(h\) 有限长，就是 FIR；只要反馈递归，就是 IIR。反过来，<b>任何非线性或时变操作都不再能用一次卷积描述</b>——例如取绝对值、取 \(\log\)（MFCC 第 5 步）、ReLU、批归一化，这也是为什么神经网络不能简单套用频域分析。</p></div>
  </div>
  <p>两个必须记住的附加条件：<strong>因果性</strong>要求 \(h(t)=0\ (t<0)\)（响应不能早于激励）；<strong>BIBO 稳定</strong>要求 \(\int_{-\infty}^{\infty}|h(t)|\,\mathrm{d}t<\infty\)（§4.11）。后者在离散域变成 \(\sum_n|h[n]|<\infty\)，是 IIR 是否会炸的判据。</p>

  <h4>3. 零输入响应与零状态响应：为什么微分方程要分两半解</h4>
  <p>§2.5 把全响应拆成两部分，这个拆法在声纹里对应「设备本底噪声 / 由激励产生的信号」：</p>
  <div class="mathbox">
    <div class="math">\[ y(t)=\underbrace{y_{zi}(t)}_{\text{零输入：由初始状态产生}}+\underbrace{y_{zs}(t)}_{\text{零状态：}x\ast h} \tag{D-3} \]</div>
    <div class="mathnote"><p>零输入响应满足齐次微分方程（由系统极点决定，与输入无关）；零状态响应才是 (D-2) 的卷积。§2.4 专门处理「起始点跳变」：电容电压、电感电流不能突变，所以要从 \(0^-\) 状态换算出 \(0^+\) 状态。工程含义：<b>一段录音开头几个样点的异常，往往是滤波器初始状态没清零</b>，与信号本身无关。</p></div>
  </div>

  <h4>4. 手算例：预加重其实是一个零点在 \(z=0.97\) 的一阶高通</h4>
  <p>第 6 讲第 1 步用 \(y[n]=x[n]-0.97\,x[n-1]\)。写成卷积形式，冲激响应只有两个抽头：</p>
  <div class="mathbox">
    <div class="math">\[ h[n]=\delta[n]-0.97\,\delta[n-1],\qquad H(e^{j\omega})=1-0.97e^{-j\omega} \tag{D-4} \]</div>
    <div class="mathnote"><p>\(\omega=2\pi f/F_s\)，\(F_s=8000\) Hz。幅度的平方可直接展开：\(|H|^2=1+0.97^2-2\cdot0.97\cos\omega=1.9409-1.94\cos\omega\)。代四个频率算到底：</p>
    <table class="sym compact">
      <tr><th>\(f\) (Hz)</th><th>\(\omega\)</th><th>\(\cos\omega\)</th><th>\(|H|^2\)</th><th>\(|H|\)</th><th>dB</th></tr>
      <tr><td>0</td><td>0</td><td>1.0000</td><td>0.0009</td><td>0.0300</td><td>−30.5</td></tr>
      <tr><td>1000</td><td>\(\pi/4\)</td><td>0.7071</td><td>0.5691</td><td>0.7544</td><td>−2.45</td></tr>
      <tr><td>2000</td><td>\(\pi/2\)</td><td>0</td><td>1.9409</td><td>1.3932</td><td>+2.88</td></tr>
      <tr><td>4000</td><td>\(\pi\)</td><td>−1</td><td>3.8809</td><td>1.9700</td><td>+5.89</td></tr>
    </table>
    <p>直流被压掉 30 dB，高频抬起约 6 dB，正是「补偿声门激励 −6 dB/oct 的频谱倾斜」所需。对照代码 <code>mfcc()</code> 里的 <code>x[1:] - preemph*x[:-1]</code>：它就是这个 \(h\) 的逐点实现，没有任何额外魔法。</p></div>
  </div>

  <h3>D.3　卷积怎么算：图解法、性质与一次手算对拍</h3>
  <p>§2.7 给出的图解四步是：<b>换元</b>（把 \(x(\tau),h(\tau)\) 都画成 \(\tau\) 的函数）→ <b>翻转</b>（\(h(-\tau)\)）→ <b>平移</b>（\(h(t-\tau)\)）→ <b>相乘积分</b>（重叠面积）。离散版就是卷积和：</p>
  <div class="mathbox">
    <div class="math">\[ y[n]=\sum_{k=-\infty}^{\infty}x[k]\,h[n-k],\qquad \operatorname{len}(y)=\operatorname{len}(x)+\operatorname{len}(h)-1 \tag{D-5} \]</div>
    <div class="mathnote"><p><b>手算到底：</b>取 \(x=[1,2,3]\)、\(h=[1,-1]\)（即一阶差分）。长度应为 \(3+2-1=4\)。</p>
    <table class="sym compact">
      <tr><th>\(n\)</th><th>参与求和的项</th><th>\(y[n]\)</th></tr>
      <tr><td>0</td><td>\(x[0]h[0]=1\cdot1\)</td><td>1</td></tr>
      <tr><td>1</td><td>\(x[0]h[1]+x[1]h[0]=1\cdot(-1)+2\cdot1\)</td><td>1</td></tr>
      <tr><td>2</td><td>\(x[1]h[1]+x[2]h[0]=2\cdot(-1)+3\cdot1\)</td><td>1</td></tr>
      <tr><td>3</td><td>\(x[2]h[1]=3\cdot(-1)\)</td><td>−3</td></tr>
    </table>
    <p>得 \(y=[1,1,1,-3]\)。用 <code>np.convolve([1,2,3],[1,-1])</code> 可一行验证。<b>注意长度</b>：卷积会「长出」\(L_h-1\) 个点，这正是 CNN 需要 <code>pad</code>、以及 STFT 分帧必须截断/补零的原因之一。</p></div>
  </div>
  <p>§2.8 的性质每一条都有工程后果：</p>
  <table class="sym">
    <tr><th>性质</th><th>公式</th><th>在讲义里的用处</th></tr>
    <tr><td>交换律</td><td>\(x\ast h=h\ast x\)</td><td>级联滤波器可以换顺序，预加重与抗混叠的先后不影响结果</td></tr>
    <tr><td>结合律</td><td>\((x\ast h_1)\ast h_2=x\ast(h_1\ast h_2)\)</td><td>多级滤波器可合并成一个等效 \(h\)，省一次循环</td></tr>
    <tr><td>分配律</td><td>\(x\ast(h_1+h_2)=x\ast h_1+x\ast h_2\)</td><td>Mel 滤波器组的输出可看作一组并联子带之和</td></tr>
    <tr><td>与 \(\delta\) 卷积</td><td>\(x\ast\delta(t-t_0)=x(t-t_0)\)</td><td>纯延时系统 \(h(t)=\delta(t-t_0)\)，只改相位不改幅度</td></tr>
    <tr><td>微分性质</td><td>\((x\ast h)'=x'\ast h=x\ast h'\)</td><td>差分与平滑可交换顺序；过零率对高频噪声敏感的理论解释</td></tr>
  </table>
  <div class="defbox"><div class="dh">一个容易混的点：卷积 vs 互相关</div>
  <p>互相关 \(R_{xh}[\ell]=\sum_n x[n]\,h[n+\ell]\) <strong>不翻转</strong>核，卷积 \(y[n]=\sum_k x[k]h[n-k]\) <strong>要翻转</strong>。CNN 里所谓「卷积」实际算的是互相关（核不翻转），但因为核是可学习参数，翻转与否只是参数重标号，不影响表达能力。若要用 FFT 加速真正的卷积，记得先把核翻转；这也是 §7.7「解卷积（反卷积）」要处理的问题：已知 \(y\) 和 \(h\) 反求 \(x\)，在频域是 \(X=Y/H\)，一旦 \(H\) 有小值就会把噪声放大，必须正则化。</p></div>

  <h3>D.4　卷积定理：整个频域处理的地基</h3>
  <p>§3.8 称它是「通信系统和信号处理研究领域中应用最广的傅里叶变换性质之一」，这个评价不为过。采用本讲义的变换约定：</p>
  <div class="mathbox">
    <div class="math">\[ X(\omega)=\int_{-\infty}^{\infty}x(t)e^{-j\omega t}\mathrm{d}t,\qquad x(t)=\frac{1}{2\pi}\int_{-\infty}^{\infty}X(\omega)e^{j\omega t}\mathrm{d}\omega \tag{D-6} \]</div>
  </div>
  <h4>1. 时域卷积 \(\leftrightarrow\) 频域相乘（不跳步的证明）</h4>
  <div class="mathbox">
    <div class="math">\[ \begin{aligned} \mathcal{F}\{x\ast h\} &amp;=\int_{-\infty}^{\infty}\Big[\int_{-\infty}^{\infty}x(\tau)h(t-\tau)\mathrm{d}\tau\Big]e^{-j\omega t}\mathrm{d}t \\ &amp;\overset{u=t-\tau}{=}\int_{-\infty}^{\infty}x(\tau)\Big[\int_{-\infty}^{\infty}h(u)e^{-j\omega(u+\tau)}\mathrm{d}u\Big]\mathrm{d}\tau \\ &amp;=\Big[\int x(\tau)e^{-j\omega\tau}\mathrm{d}\tau\Big]\Big[\int h(u)e^{-j\omega u}\mathrm{d}u\Big]=X(\omega)\,H(\omega) \end{aligned} \tag{D-7} \]</div>
    <div class="mathnote"><p>只用了「交换积分次序 + 变量代换」。物理含义：<b>复指数 \(e^{j\omega t}\) 是 LTI 系统的特征函数</b>——送进一个正弦，出来还是同频正弦，只被乘上复数 \(H(\omega)\)。所以「滤波」在时域是卷积，在频域只是逐点乘法。这就是 STFT、Mel 滤波、频域去噪能够成立的全部理由。</p></div>
  </div>
  <h4>2. 时域相乘 \(\leftrightarrow\) 频域卷积（以及 \(1/2\pi\) 从哪来）</h4>
  <div class="mathbox">
    <div class="math">\[ \mathcal{F}\{x(t)\cdot w(t)\}=\frac{1}{2\pi}\,(X\ast W)(\omega)=\frac{1}{2\pi}\int_{-\infty}^{\infty}X(\theta)W(\omega-\theta)\mathrm{d}\theta \tag{D-8} \]</div>
    <div class="mathnote"><p>系数 \(1/2\pi\) 来自 (D-6) 里逆变换的归一化：把 \(x,w\) 都写成逆变换再相乘，对两个频率变量做卷积时会多出一次 \((1/2\pi)^2\)，与外层正变换的 \(2\pi\) 抵消后剩一个 \(1/2\pi\)。<b>离散周期版</b>则变成 \((1/N)\) 的圆周卷积（见 E.5）。</p></div>
  </div>
  <p><b>直接后果（这条最重要）：</b>分帧加窗 \(x_w[n]=x[n]\cdot w[n]\) 的频谱不是 \(X\)，而是 \(X\) 与窗谱 \(W\) 的卷积。哪怕 \(x\) 是纯净单频（\(X\) 是一根 \(\delta\) 谱线），加窗后也会变成「\(\delta\) 被 \(W\) 抹开」的形状——这就是第 4 讲反复强调的<strong>频谱泄漏</strong>。窗谱的主瓣宽度与旁瓣电平决定了分辨率和动态范围的一对矛盾：</p>
  <div class="mathbox">
    <div class="math">\[ W(\omega)=e^{-j\omega(N-1)/2}\,\frac{\sin(N\omega/2)}{\sin(\omega/2)},\qquad \Delta\omega_{\text{主瓣}}=\frac{4\pi}{N} \tag{D-9} \]</div>
    <div class="mathnote"><p><b>算到底：</b>本讲义 <code>stft(frame=200, n_fft=512, Fs=8000)</code>。矩形窗主瓣宽 \(4\pi/200=0.0628\) rad，占一个 \(2\pi\) 周期的比例是 \(0.0628/(2\pi)=0.01\)，换算成频率 \(0.01\times8000=80\) Hz；第一旁瓣约 −13.2 dB。换汉明窗，主瓣加倍到 \(8\pi/N\) 即 160 Hz，但第一旁瓣压到约 −42.7 dB。所以<b>选窗不是选「更好」，是选「要分辨率还是要动态范围」</b>。第 5 讲的窗长账在这里得到严格解释。</p></div>
  </div>

  <h3>D.5　傅里叶的四种形态：为什么教材要用一整章讲「离散性与周期性」</h3>
  <p>§9.2 用一张四象限表把四种变换统一起来，规律只有一句：<strong>时域周期性 \(\leftrightarrow\) 频域离散性；时域离散性 \(\leftrightarrow\) 频域周期性</strong>。</p>
  <table class="sym">
    <tr><th>时域</th><th>频域</th><th>变换</th><th>谱的样子</th><th>本讲义用在哪</th></tr>
    <tr><td>连续、周期</td><td>离散、非周期</td><td>傅里叶级数 FS</td><td>一根根谱线 \(n\omega_1\)</td><td>第 1 讲谐波叠加、变压器 100 Hz 谐波串</td></tr>
    <tr><td>连续、非周期</td><td>连续、非周期</td><td>傅里叶变换 FT</td><td>连续谱密度</td><td>D.4 全部推导</td></tr>
    <tr><td>离散、周期</td><td>离散、周期</td><td>离散傅里叶级数 DFS</td><td>周期谱线</td><td>E.5 引出 DFT</td></tr>
    <tr><td>离散、非周期</td><td>连续、周期</td><td>序列傅里叶变换 DTFT</td><td>以 \(2\pi\) 为周期</td><td>§8.9、补零为什么只改显示密度</td></tr>
    <tr><td>离散、有限长</td><td>离散、有限长</td><td>DFT（DFS 取主值）</td><td>\(N\) 个频点</td><td>第 4 讲 <code>fft()</code></td></tr>
  </table>
  <h4>1. 从 FS 到 FT：谱线怎么变成谱密度</h4>
  <div class="mathbox">
    <div class="math">\[ C_n=\frac{1}{T}\int_{-T/2}^{T/2}x(t)e^{-jn\omega_1 t}\mathrm{d}t=\frac{1}{T}X(n\omega_1),\quad \omega_1=\frac{2\pi}{T} \tag{D-10} \]</div>
    <div class="mathnote"><p>令 \(T\to\infty\)：谱线间隔 \(\omega_1\to0\)，\(C_n\to0\)，但 \(T C_n=X(n\omega_1)\) 保持有限。于是「离散谱线」稠密成「连续谱密度」，\(x(t)=\sum_n C_n e^{jn\omega_1t}\) 的求和变成 (D-6) 的积分。<b>所以 FT 不是另一套公式，而是 FS 在周期趋于无穷时的极限。</b>这解释了第 4 讲里「DFT 的频率分辨率 \(\Delta f=F_s/N\)」的来历：\(N\) 点 DFT 等价于把信号当成一个周期 \(T=N/F_s\) 的周期序列，基频就是 \(F_s/N\)。</p></div>
  </div>
  <h4>2. 常用变换对（沿用教材附录二、附录三的记法）</h4>
  <table class="sym">
    <tr><th>时域</th><th>频域</th><th>为什么在讲义里重要</th></tr>
    <tr><td>\(\operatorname{rect}(t/\tau)\)</td><td>\(\tau\operatorname{Sa}(\omega\tau/2)\)</td><td>矩形窗的频谱，泄漏的形状由它决定</td></tr>
    <tr><td>\(\delta(t)\)</td><td>1</td><td>冲激含全部频率，白噪声的理论原型</td></tr>
    <tr><td>\(u(t)\)</td><td>\(\dfrac{1}{j\omega}+\pi\delta(\omega)\)</td><td>教材式 (3-49)；积分环节的 \(\delta\) 项不能漏</td></tr>
    <tr><td>\(e^{-at}u(t),\ a>0\)</td><td>\(\dfrac{1}{a+j\omega}\)</td><td>一阶低通，单极点系统的原型</td></tr>
    <tr><td>\(\cos\omega_0t\)</td><td>\(\pi[\delta(\omega-\omega_0)+\delta(\omega+\omega_0)]\)</td><td>第 1 讲纯音、第 2 讲混叠验证</td></tr>
    <tr><td>\(e^{-\alpha t^2}\)</td><td>\(\sqrt{\pi/\alpha}\,e^{-\omega^2/(4\alpha)}\)</td><td>高斯是唯一取到测不准下界的波形</td></tr>
  </table>
  <h4>3. §3.10 抽样信号的傅里叶变换：一个双重求和</h4>
  <p>教材上册书页 162（PDF 第 178 页）用周期矩形脉冲抽样做例子，先对时域周期延拓、再对频域周期延拓，得到双重求和。一般结论更简洁：抽样脉冲串 \(\delta_T(t)=\sum_n\delta(t-nT_s)\) 本身是周期的，其 FS 系数全为 \(1/T_s\)：</p>
  <div class="mathbox">
    <div class="math">\[ \delta_T(t)=\frac{1}{T_s}\sum_{m=-\infty}^{\infty}e^{jm\omega_s t},\quad \omega_s=\frac{2\pi}{T_s}=2\pi F_s \tag{D-11} \]</div>
  </div>
  <p>把它乘上 \(x(t)\) 再取傅里叶变换，每个复指数分量只造成一次频移：</p>
  <div class="mathbox">
    <div class="math">\[ X_s(\omega)=\mathcal{F}\{x(t)\delta_T(t)\}=\frac{1}{T_s}\sum_{m=-\infty}^{\infty}X(\omega-m\omega_s) \tag{D-12} \]</div>
    <div class="mathnote"><p><b>这就是第 2 讲采样定理那张「频谱被周期性复制」图的严格版本。</b>注意三个细节：① 幅度被统一缩放 \(1/T_s\)；② 复制间隔是 \(\omega_s\)（对应 \(F_s\)）；③ 复制的是完整双边谱，正负频率各一份。教材 §3.10 的双重求和只是把它作用在「先周期延拓过的 \(f_1(t)\)」上，多了一层 \(n\) 的求和，本质相同。</p></div>
  </div>

  <h3>D.6　抽样定理与理想恢复：sinc 内插不是「插值技巧」，是唯一正确解</h3>
  <p>§3.11 开门见山地提出两个问题：<b>如何从抽样信号恢复原连续信号？在什么条件下才能无失真地恢复？</b>答复就是抽样定理。设 \(X(\omega)=0\) 当 \(|\omega|>\omega_m\)（带限），由 (D-12)：</p>
  <div class="mathbox">
    <div class="math">\[ \omega_s\geq 2\omega_m\quad\Longleftrightarrow\quad F_s\geq 2f_m \tag{D-13} \]</div>
    <div class="mathnote"><p>相邻两份复制谱刚好不重叠。取等号时称<strong>奈奎斯特率</strong> \(F_s=2f_m\)。此时只要用一个理想低通把中间那一份切出来，就能无失真恢复——注意「无失真」是<b>数学上精确相等</b>，不是「听起来差不多」。</p></div>
  </div>
  <h4>1. 恢复滤波器的冲激响应与内插公式（完整推导）</h4>
  <div class="mathbox">
    <div class="math">\[ H_r(\omega)=\begin{cases}T_s,&amp;|\omega|\lt\omega_m\\ 0,&amp;\text{otherwise}\end{cases} \tag{D-14} \]</div>
  </div>
  <p>取逆变换（用 \(\operatorname{Sa}(x)=\sin x/x\)）：</p>
  <div class="mathbox">
    <div class="math">\[ \begin{aligned} h_r(t)&amp;=\frac{1}{2\pi}\int_{-\omega_m}^{\omega_m}T_s e^{j\omega t}\mathrm{d}\omega=\frac{T_s}{\pi t}\sin(\omega_m t)=\frac{T_s\omega_m}{\pi}\operatorname{Sa}(\omega_m t) \end{aligned} \tag{D-15} \]</div>
  </div>
  <p>抽样信号是 \(x_s(t)=\sum_n x(nT_s)\delta(t-nT_s)\)，与 \(h_r\) 卷积即得<strong>惠特克–香农内插公式</strong>：</p>
  <div class="mathbox">
    <div class="math">\[ x(t)=\sum_{n=-\infty}^{\infty}x(nT_s)\,\frac{T_s\omega_m}{\pi}\,\operatorname{Sa}\big(\omega_m(t-nT_s)\big) \overset{F_s=2f_m}{=}\sum_n x(nT_s)\,\operatorname{sinc}\Big(\frac{t-nT_s}{T_s}\Big) \tag{D-16} \]</div>
    <div class="mathnote"><p>其中 \(\operatorname{sinc}(u)=\sin(\pi u)/(\pi u)\)。取等号时 \(T_s=\pi/\omega_m\)，系数 \(T_s\omega_m/\pi=1\)，且 \(\operatorname{Sa}(\omega_m(t-nT_s))=\operatorname{sinc}((t-nT_s)/T_s)\)。<b>关键性质：</b>在第 \(k\) 个样点处，\(\operatorname{sinc}(k-n)=\delta[k-n]\)，所以内插曲线精确穿过所有样点，而样点之间由全体样点共同决定——这是「采样值含有完整信息」的构造性证明，不只是存在性断言。</p></div>
  </div>
  <h4>2. 算到账：8 kHz / 4 kHz / 3.4 kHz 三个数字的关系</h4>
  <table class="sym">
    <tr><th>量</th><th>数值</th><th>来历</th></tr>
    <tr><td>\(F_s\)</td><td>8000 Hz</td><td>本讲义 <code>wav.FS</code>，也是电话语音标准</td></tr>
    <tr><td>\(T_s=1/F_s\)</td><td>0.125 ms</td><td>样点间隔</td></tr>
    <tr><td>奈奎斯特频率 \(F_s/2\)</td><td><b>4000 Hz</b></td><td>(D-13)，任何 4000 Hz 以上成分都会折叠回来</td></tr>
    <tr><td>工程可用带宽</td><td>约 3400 Hz</td><td>抗混叠滤波器必须留 600 Hz 过渡带，见 D.8</td></tr>
    <tr><td>DFT 分辨率 \(\Delta f=F_s/N\)</td><td>15.625 Hz（\(N=512\)）</td><td>(D-10) 的离散版</td></tr>
  </table>
  <p>混叠的定量式：输入 \(f_{in}>F_s/2\) 时，观测到的频率是把它按 \(F_s\) 折叠回 \([0,F_s/2]\) 的结果：</p>
  <div class="mathbox">
    <div class="math">\[ f_{\text{alias}}=\big|f_{in}-kF_s\big|,\quad k=\operatorname{round}(f_{in}/F_s),\qquad f_{\text{alias}}\in[0,F_s/2] \tag{D-17} \]</div>
    <div class="mathnote"><p><b>手算：</b>6000 Hz → \(k=1\) → \(|6000-8000|=2000\) Hz；9000 Hz → \(k=1\) → 1000 Hz；13000 Hz → \(k=2\) → \(|13000-16000|=3000\) Hz。第 2 讲的混叠实验、以及「8 kHz 下 2000 Hz 以上成分注定是假的」那句被纠正过的话，都以此式为准（正确上限是 4000 Hz）。</p></div>
  </div>
  <h4>3. 三条失效边界（比背定理更重要）</h4>
  <div class="defbox"><div class="dh">抽样定理在什么情况下「不成立」</div>
  <ol>
    <li><b>非带限信号</b>：真实声压总有高于 \(F_s/2\) 的成分（开关瞬态、摩擦、局部放电脉冲）。所以 ADC 前<strong>必须有模拟抗混叠低通</strong>，否则采样后再用数字滤波也救不回来——折叠已经发生了。</li>
    <li><b>理想低通不可实现</b>：(D-15) 的 \(h_r(t)\) 在 \(t<0\) 处非零（非因果），且 \(\operatorname{Sa}\) 衰减仅 \(1/t\)，无穷长。真实恢复用零阶保持 + 补偿，或过采样 + 短 FIR。</li>
    <li><b>采样时刻抖动</b>：定理假设严格等间隔。时钟抖动 \(\sigma_t\) 引入的噪声功率约 \(\sigma_t^2\int\omega^2|X|^2\mathrm{d}\omega\)，对高频成分伤害更大；变压器在线监测的长线缆、低成本 ADC 尤其要注意。</li>
  </ol></div>
  <p>§5.9「从抽样信号恢复连续时间信号」与 §5.10「PCM」把这条链条接到工程：抽样 → 量化 → 编码 → 传输 → 解码 → 内插恢复。第 2 讲已推过量化 SNR 的 \(6.02B+1.76\) dB，这里补上的是它两端（抽样与内插）的严格依据。</p>

  <h3>D.7　s 域：系统函数、零极点与共振峰的物理来源</h3>
  <h4>1. 拉普拉斯变换与收敛域（§4.2）</h4>
  <div class="mathbox">
    <div class="math">\[ X(s)=\int_{-\infty}^{\infty}x(t)e^{-st}\mathrm{d}t,\qquad s=\sigma+j\omega \tag{D-18} \]</div>
    <div class="mathnote"><p>比 FT 多了一个实部 \(\sigma\)，相当于给 \(x(t)\) 先乘 \(e^{-\sigma t}\) 再变换。好处：许多 FT 不收敛的信号（如 \(e^{at}u(t),\ a>0\)）只要选合适的 \(\sigma\) 就能收敛。<b>ROC（收敛域）不是附带说明，而是变换的一部分</b>：同一个代数式 \(1/(s-a)\) 配不同 ROC 代表完全不同的时域信号（右边序列 / 左边序列），见 E.2。</p></div>
  </div>
  <h4>2. 系统函数与零极点（§4.6–§4.8）</h4>
  <div class="mathbox">
    <div class="math">\[ H(s)=\frac{Y(s)}{X(s)}=K\,\frac{\prod_{i=1}^{M}(s-z_i)}{\prod_{k=1}^{N}(s-p_k)},\qquad Y(s)=H(s)X(s) \tag{D-19} \]</div>
    <div class="mathnote"><p>这是 (D-7) 在 s 域的写法：卷积仍变乘法。<b>零点</b> \(z_i\) 是让 \(H=0\) 的 \(s\)，<b>极点</b> \(p_k\) 是让 \(H\to\infty\) 的 \(s\)。教材 §4.7 用部分分式说明：每个极点 \(p_k=\sigma_k+j\omega_k\) 对应时域的一个模态 \(e^{p_k t}=e^{\sigma_k t}e^{j\omega_k t}\)。</p></div>
  </div>
  <table class="sym">
    <tr><th>极点位置</th><th>时域模态</th><th>系统行为</th><th>声纹里的例子</th></tr>
    <tr><td>\(\operatorname{Re}p<0\)（左半平面）</td><td>\(e^{\sigma t}\) 衰减振荡</td><td>稳定、有阻尼</td><td>声道共振峰、机械阻尼振动</td></tr>
    <tr><td>\(\operatorname{Re}p=0\)（虚轴）</td><td>等幅振荡</td><td>临界稳定（边界稳定系统）</td><td>理想正弦、无阻尼谐振</td></tr>
    <tr><td>\(\operatorname{Re}p>0\)（右半平面）</td><td>指数增长</td><td>不稳定</td><td>自激振荡、递归滤波器爆炸</td></tr>
  </table>
  <h4>3. 零极点几何法读频响（§4.8，教材上册书页 228）</h4>
  <p>令 \(s=j\omega\)（前提：ROC 包含虚轴，§4.13），把每个因子看成从零点/极点指向 \(j\omega\) 的向量：</p>
  <div class="mathbox">
    <div class="math">\[ |H(j\omega)|=|K|\,\frac{\prod_i|j\omega-z_i|}{\prod_k|j\omega-p_k|},\qquad \angle H(j\omega)=\angle K+\sum_i\arg(j\omega-z_i)-\sum_k\arg(j\omega-p_k) \tag{D-20} \]</div>
    <div class="mathnote"><p><b>一句话读图：</b>当 \(j\omega\) 扫过虚轴、路过某个极点附近时，分母向量变短 → 幅度出现<strong>峰</strong>；路过零点附近时分子变短 → 出现<strong>陷波</strong>。极点越贴近虚轴，峰越尖越高。教材 §4.8 从正弦激励 \(e(t)=E_m\sin\omega_0t\) 出发，用部分分式（式 4-103~4-105）严格导出 \(H(j\omega_0)=H_0e^{j\varphi_0}\)，结论与几何法一致。</p></div>
  </div>
  <h4>4. 二阶谐振系统：共振峰就是一对靠近虚轴的极点（§4.9）</h4>
  <div class="mathbox">
    <div class="math">\[ H(s)=\frac{\omega_n^2}{s^2+2\zeta\omega_n s+\omega_n^2},\qquad p_{1,2}=-\zeta\omega_n\pm j\omega_n\sqrt{1-\zeta^2},\qquad Q=\frac{1}{2\zeta} \tag{D-21} \]</div>
    <div class="mathnote"><p>当 \(j\omega\) 走到 \(\omega_n\sqrt{1-2\zeta^2}\) 附近出现谐振峰，3 dB 带宽 \(B\approx\omega_n/Q=2\zeta\omega_n\)。<b>手算例：</b>共振峰 \(f_n=1000\) Hz（\(\omega_n=2\pi\cdot1000\approx6283\) rad/s）、\(\zeta=0.05\) ⇒ \(Q=10\)、\(B=2\cdot0.05\cdot1000=100\) Hz、极点实部 \(-\zeta\omega_n\approx-314\) s\(^{-1}\)、包络衰减时间常数 \(1/314\approx3.18\) ms。<b>这正是第 6 讲 MFCC 能捕捉「共振峰」、专题 B 的 LPC 用全极点模型描述声道的物理原因</b>：声道就是若干组这样的二阶谐振并联。变压器铁芯/绕组的机械谐振也用同一个式子描述，只是 \(f_n\) 换成 100 Hz 及其谐波。</p></div>
  </div>
  <h4>5. 全通、最小相位与稳定性（§4.10–§4.11）</h4>
  <table class="sym">
    <tr><th>概念</th><th>零极点条件</th><th>性质</th><th>讲义里的位置</th></tr>
    <tr><td>稳定（因果连续系统）</td><td>全部极点在左半平面</td><td>\(\int|h|<\infty\)，BIBO</td><td>§4.11、E.8</td></tr>
    <tr><td>最小相位</td><td>零点与极点都在左半平面</td><td>逆系统也稳定因果；同幅频下相位滞后最小</td><td>倒谱、同态解卷积（第 6 讲）</td></tr>
    <tr><td>全通函数</td><td>零点与极点关于虚轴镜像</td><td>\(|H(j\omega)|\equiv1\)，只改相位</td><td>相位均衡、混响模拟</td></tr>
    <tr><td>拉氏 ↔ 傅氏</td><td>ROC 含虚轴</td><td>\(X(j\omega)=X(s)|_{s=j\omega}\)</td><td>§4.13；否则 FT 会出现 \(\delta\) 项，如 \(u(t)\)</td></tr>
  </table>
  <p><b>回到预加重：</b>(D-4) 的 \(H(z)=1-0.97z^{-1}=(z-0.97)/z\)，零点 \(z=0.97\)、极点 \(z=0\)，两者都在单位圆内（离散域），所以它是<strong>最小相位</strong>系统，逆系统 \(1/(1-0.97z^{-1})\) 稳定——这就是为什么 MFCC 流程里预加重可以无损反变换，而第 6 讲「同态解卷积」要求信号满足最小相位假设才有意义。</p>

  <h3>D.8　无失真传输、物理可实现性与希尔伯特变换</h3>
  <h4>1. 无失真传输条件（§5.3）</h4>
  <div class="mathbox">
    <div class="math">\[ y(t)=K\,x(t-t_0)\ \Longleftrightarrow\ H(j\omega)=K\,e^{-j\omega t_0}\ \Longleftrightarrow\ |H|=\text{const},\ \ \varphi(\omega)=-\omega t_0 \tag{D-22} \]</div>
    <div class="mathnote"><p>幅度必须<strong>对所有频率一视同仁</strong>，相位必须是<strong>过原点的直线</strong>（斜率即群延时 \(t_0=-d\varphi/d\omega\)）。幅频不平坦叫<em>幅度失真</em>，相频非线性叫<em>相位/群延时失真</em>。工程含义：一个「好听/好用」的采集通道，比一个「频响范围很宽」的通道更重要；变压器在线监测换麦克风后特征漂移，往往就是幅频不平坦导致的。</p></div>
  </div>
  <h4>2. 理想低通为什么造不出来（§5.4–§5.5）</h4>
  <div class="mathbox">
    <div class="math">\[ H_{LP}(j\omega)=\begin{cases}1,&amp;|\omega|\lt\omega_c\\0,&amp;|\omega|>\omega_c\end{cases}\ \Longrightarrow\ h_{LP}(t)=\frac{\omega_c}{\pi}\operatorname{Sa}(\omega_c t),\quad t\in(-\infty,\infty) \tag{D-23} \]</div>
  </div>
  <p>§5.5 的佩利–维纳（Paley–Wiener）准则给出物理可实现性的严格判据：</p>
  <div class="mathbox">
    <div class="math">\[ \int_{-\infty}^{\infty}\frac{\big|\ln|H(j\omega)|\big|}{1+\omega^2}\,\mathrm{d}\omega<\infty \tag{D-24} \]</div>
    <div class="mathnote"><p>若 \(|H|\) 在任一有限频带上<strong>严格等于 0</strong>，则 \(\ln|H|\to-\infty\) 使积分发散。结论极为实用：<b>理想低通、理想带阻、理想「砖墙」抗混叠滤波器在物理上都不存在</b>，任何实际滤波器都必须有过渡带。这就把 D.6 里「4 kHz 是理论上限、3.4 kHz 才是工程带宽」补成了闭环：600 Hz 是留给过渡带的价格。同理，Mel 滤波器组若做成完全不重叠的矩形，也违背此准则。</p></div>
  </div>
  <h4>3. 希尔伯特变换与解析信号（§5.6）</h4>
  <div class="mathbox">
    <div class="math">\[ \hat{x}(t)=x(t)\ast\frac{1}{\pi t},\qquad \mathcal{F}\{\hat{x}\}=-j\,\operatorname{sgn}(\omega)\,X(\omega),\qquad z(t)=x(t)+j\hat{x}(t) \tag{D-25} \]</div>
    <div class="mathnote"><p>希尔伯特变换就是「正频率移相 \(-90^\circ\)、负频率移相 \(+90^\circ\)」的全通移相器。解析信号的频谱 \(Z(\omega)=2X(\omega)u(\omega)\) 只保留正频率，于是可以定义<b>包络</b> \(a(t)=|z(t)|\)、<b>瞬时相位</b> \(\phi(t)=\arg z(t)\)、<b>瞬时频率</b> \(f_i(t)=\frac{1}{2\pi}\frac{\mathrm{d}\phi}{\mathrm{d}t}\)。这正是第 7 讲 EMD 做 Hilbert 谱、以及 Gammatone 滤波器提取包络的理论依据。§5.6 还指出：因果稳定系统的幅频与相频不是独立的，二者由希尔伯特变换互相约束（Kramers–Kronig 关系）——所以「只改幅度不改相位」的滤波器同样造不出来。</p></div>
  </div>

  <h3>D.9　矢量空间视角：正交、帕塞瓦尔、相关、匹配滤波与测不准</h3>
  <p>§6 把信号看成<strong>矢量</strong>，前 5 章的所有变换都变成「换一组正交基」。这是理解 DFT / DCT / 小波 / Gammatone 为什么能互相替代的统一语言。</p>
  <h4>1. 内积、正交分解与帕塞瓦尔定理（§6.2–§6.4）</h4>
  <div class="mathbox">
    <div class="math">\[ \langle x,y\rangle=\int_{-\infty}^{\infty}x(t)y^*(t)\mathrm{d}t,\quad \|x\|^2=E_x=\langle x,x\rangle,\quad c_n=\frac{\langle x,\varphi_n\rangle}{\|\varphi_n\|^2} \tag{D-26} \]</div>
  </div>
  <div class="mathbox">
    <div class="math">\[ E_x=\int_{-\infty}^{\infty}|x(t)|^2\mathrm{d}t=\frac{1}{2\pi}\int_{-\infty}^{\infty}|X(\omega)|^2\mathrm{d}\omega=\sum_n|c_n|^2\|\varphi_n\|^2 \tag{D-27} \]</div>
    <div class="mathnote"><p><b>帕塞瓦尔定理 = 能量守恒</b>：换基不改变矢量长度。所以「时域能量」与「频域能量」必然相等，第 3 讲短时能量与第 4 讲频谱能量是同一个量的两种算法。<b>DFT 版手算对拍</b>（第 4 讲的 \(X[k]=\sum_{n=0}^{N-1}x[n]e^{-j2\pi kn/N}\)）：取 \(x=[1,2,3,4]\)，\(N=4\)。</p>
    <table class="sym compact">
      <tr><th>量</th><th>计算</th><th>结果</th></tr>
      <tr><td>时域 \(\sum|x[n]|^2\)</td><td>\(1+4+9+16\)</td><td><b>30</b></td></tr>
      <tr><td>\(X[0]\)</td><td>\(1+2+3+4\)</td><td>10 → \(|X|^2=100\)</td></tr>
      <tr><td>\(X[1]\)</td><td>\(1-2j-3+4j=-2+2j\)</td><td>\(|X|^2=8\)</td></tr>
      <tr><td>\(X[2]\)</td><td>\(1-2+3-4=-2\)</td><td>\(|X|^2=4\)</td></tr>
      <tr><td>\(X[3]\)</td><td>\(-2-2j\)</td><td>\(|X|^2=8\)</td></tr>
      <tr><td>频域 \(\frac{1}{N}\sum|X[k]|^2\)</td><td>\((100+8+4+8)/4\)</td><td><b>30</b> ✓</td></tr>
    </table>
    <p>这个 \(1/N\) 就是第 4 讲「单边谱要乘 \(2/N\)」里那个 \(1/N\) 的正式出处；可用 <code>fft()</code> 与 <code>dft()</code> 直接对拍。</p></div>
  </div>
  <h4>2. 相关函数与功率谱（§6.6–§6.8，维纳–辛钦）</h4>
  <div class="mathbox">
    <div class="math">\[ R_x(\tau)=\int_{-\infty}^{\infty}x(t)x^*(t-\tau)\mathrm{d}t\ \longleftrightarrow\ S_x(\omega)=|X(\omega)|^2 \tag{D-28} \]</div>
    <div class="mathnote"><p><b>自相关与能量谱是一对傅里叶变换</b>。第 3 讲用自相关测基音周期，第 4 讲用频谱看谐波，原来算的是同一件事的两面。对功率信号，§6.8 进一步给出「信号通过 LTI 系统后 \(S_y(\omega)=|H(\omega)|^2S_x(\omega)\)」——<b>滤波器只改功率谱的形状，不改它的随机性结构</b>，这是维纳滤波（专题 B）与谱减法（专题 A）共用的出发点。</p></div>
  </div>
  <p>一个常被跳过但很有用的推论：对零均值平稳高斯信号，<strong>过零率的期望由功率谱的二阶矩决定</strong>（Rice 公式）：</p>
  <div class="mathbox">
    <div class="math">\[ \mathbb{E}[\text{ZCR}]=2\sqrt{\frac{m_2}{m_0}},\qquad m_0=\int_0^{\infty}S(f)\mathrm{d}f,\ \ m_2=\int_0^{\infty}f^2S(f)\mathrm{d}f \tag{D-29} \]</div>
    <div class="mathnote"><p><b>验算：</b>纯正弦 \(f_0\) 的 \(S(f)\) 是一根 \(\delta\)，\(m_2/m_0=f_0^2\) ⇒ ZCR \(=2f_0\)，与「每周期过零两次」一致。白噪声的 \(m_2/m_0\) 由带宽决定，带宽越宽过零越密。<b>所以第 3 讲「过零率反映高频成分」不是经验，是可以定量预测的结论</b>；也解释了为什么高频噪声会让端点检测的双门限失效。</p></div>
  </div>
  <h4>3. 匹配滤波器（§6.9）：模板打分为什么是最优的</h4>
  <p>教材上册书页 375 把问题说得很清楚：已知信号波形 \(s(t)\)，要设计一个滤波器，使某一判决时刻 \(t_m\) 的<strong>输出信噪比</strong> \(\rho=s_o^2(t_m)/\mathbb{E}[n_o^2(t_m)]\)（式 6-166）最大。设噪声为白噪声、双边功率谱密度 \(N_0/2\)：</p>
  <div class="mathbox">
    <div class="math">\[ \rho=\frac{\Big|\frac{1}{2\pi}\int H(\omega)S(\omega)e^{j\omega t_m}\mathrm{d}\omega\Big|^2}{\frac{N_0}{2}\cdot\frac{1}{2\pi}\int|H(\omega)|^2\mathrm{d}\omega}\ \overset{\text{C-S}}{\leq}\ \frac{2E}{N_0},\qquad E=\frac{1}{2\pi}\int|S(\omega)|^2\mathrm{d}\omega \tag{D-30} \]</div>
    <div class="mathnote"><p>分子用柯西–施瓦茨不等式放缩：\(|\int AB|^2\leq\int|A|^2\int|B|^2\)，取 \(A=H\)、\(B=S e^{j\omega t_m}\)。等号成立当且仅当两者成比例，即</p>
    <p style="text-align:center">\(H(\omega)=K\,S^*(\omega)e^{-j\omega t_m}\ \Longleftrightarrow\ h(t)=K\,s^*(t_m-t)\)（因果化要求 \(t_m\geq\) 信号时长）。</p>
    <p><b>物理含义：</b>把模板<strong>时间反转并取共轭</strong>当冲激响应，在 \(t=t_m\) 时刻所有频率分量同相叠加，输出瞬时功率达到最大；与信号能量 \(E\) 成正比、与噪声谱密度成反比，<b>与波形具体形状无关</b>。声纹里的模板匹配、余弦打分、DTW 对齐后求相似，都是这个结论在「离散 / 非白噪声 / 波形不完全已知」条件下的近似；也解释了为什么第 12 讲的分数归一化（ZT/AT-norm）必须做——不同模板的 \(E\) 不同，\(\rho\) 的量纲就不同。</p></div>
  </div>
  <h4>4. 测不准原理（§6.10）：第 5 讲那句话的严格证明</h4>
  <p>教材明确说：证明测不准原理所需的依据就是本章「反复运用的<strong>柯西–施瓦茨不等式</strong>和<strong>帕塞瓦尔定理</strong>」，物理本质是能量受限与能量守恒；书中还给出工程版 \(t_r B=1\)（理想低通阶跃响应上升时间与带宽之积）。标准推导如下。</p>
  <p>定义能量归一化下的时宽与带宽（设 \(\bar{t}=\bar{\omega}=0\)，不失一般性）：</p>
  <div class="mathbox">
    <div class="math">\[ (\Delta t)^2=\frac{1}{E}\int t^2|x(t)|^2\mathrm{d}t,\qquad (\Delta\omega)^2=\frac{1}{2\pi E}\int\omega^2|X(\omega)|^2\mathrm{d}\omega \tag{D-31} \]</div>
  </div>
  <p>由帕塞瓦尔与 \(\mathcal{F}\{x'(t)\}=j\omega X(\omega)\)，有 \(\frac{1}{2\pi}\int\omega^2|X|^2\mathrm{d}\omega=\int|x'(t)|^2\mathrm{d}t\)。对 \(t\,x(t)\) 与 \(x'(t)\) 用柯西–施瓦茨：</p>
  <div class="mathbox">
    <div class="math">\[ \Big|\int t\,x(t)\,x'^*(t)\mathrm{d}t\Big|^2\leq\Big(\int t^2|x|^2\mathrm{d}t\Big)\Big(\int|x'|^2\mathrm{d}t\Big)=E^2(\Delta t)^2(\Delta\omega)^2 \tag{D-32} \]</div>
  </div>
  <p>左边取实部：\(\operatorname{Re}\int t x x'^*\mathrm{d}t=\frac{1}{2}\int t\frac{\mathrm{d}}{\mathrm{d}t}|x|^2\mathrm{d}t=-\frac{1}{2}\int|x|^2\mathrm{d}t=-E/2\)（分部积分，边界项为 0），故 \(E^2/4\leq E^2(\Delta t)^2(\Delta\omega)^2\)：</p>
  <div class="mathbox">
    <div class="math">\[ \Delta t\cdot\Delta\omega\ \geq\ \frac{1}{2}\qquad\Longleftrightarrow\qquad \Delta t\cdot\Delta f\ \geq\ \frac{1}{4\pi} \tag{D-33} \]</div>
    <div class="mathnote"><p>等号当且仅当 \(x'(t)=-\alpha t\,x(t)\)，解为<strong>高斯函数</strong> \(x(t)=Ce^{-\alpha t^2/2}\)，与 D.5 表中「高斯 ↔ 高斯」一致。<b>算到账：</b>取 STFT 窗长 25 ms（\(\Delta t\approx12.5\) ms 量级），则 \(\Delta f\geq1/(4\pi\cdot0.0125)\approx6.4\) Hz——这只是理论下界；实际矩形窗主瓣 80 Hz（D.9 前算过），因为矩形窗远非高斯，且工程上还要顾及旁瓣。<b>结论：</b>第 5 讲「窗长不能同时兼顾时间和频率」不是妥协，是 (D-33) 的硬下界；Gabor 变换选高斯窗，正是为了取到等号。</p></div>
  </div>

  <h3>D.10　公式 ↔ 代码：这些定理落在 acoustic-lab 的哪一行</h3>
  <table class="sym">
    <tr><th>定理</th><th>公式</th><th>代码位置</th><th>可做的对拍实验</th></tr>
    <tr><td>卷积表示</td><td>(D-2), (D-5)</td><td><code>mfcc()</code> 的预加重；<code>db4_dwt()</code> 的滤波抽取</td><td>手算 \([1,2,3]\ast[1,-1]\) 与 <code>np.convolve</code> 比较</td></tr>
    <tr><td>卷积定理</td><td>(D-7), (D-8)</td><td><code>stft()</code> 的 <code>fr * hamming</code></td><td>纯音加矩形窗，观察旁瓣 −13.2 dB；换汉明看 −42.7 dB</td></tr>
    <tr><td>帕塞瓦尔</td><td>(D-27)</td><td><code>fft()</code> / <code>dft()</code></td><td>验证 \(\sum|x|^2=\frac{1}{N}\sum|X|^2\)，用 <code>--check</code></td></tr>
    <tr><td>抽样定理</td><td>(D-12), (D-13), (D-17)</td><td><code>wav.FS=8000</code>，合成信号</td><td>注入 6000 Hz，看谱峰落在 2000 Hz</td></tr>
    <tr><td>零极点 / 谐振</td><td>(D-20), (D-21)</td><td><code>mel_filterbank()</code>、<code>gammatone_filters()</code></td><td>改中心频率，看子带峰值位置线性移动</td></tr>
    <tr><td>正交分解</td><td>(D-26), (D-27)</td><td><code>dct_matrix()</code>、<code>haar_dwt()</code></td><td>检查 \(D D^{\mathsf T}=I\)、小波重构 RMSE</td></tr>
    <tr><td>解析信号</td><td>(D-25)</td><td><code>emd()</code> 之后的 Hilbert 谱</td><td>对单个 IMF 求包络，看是否等于调幅包络</td></tr>
  </table>

  <h3>D.11　边界与失效条件</h3>
  <div class="defbox"><div class="dh">把这套理论用错，通常错在这六处</div>
  <ol>
    <li><b>对非线性/时变系统套卷积定理</b>：MFCC 里的 \(\log\)、神经网络里的 ReLU、AGC 自动增益，都不满足 LTI，(D-7) 不成立。</li>
    <li><b>忘记 ROC</b>：看到 \(1/(s-a)\) 就写 \(e^{at}u(t)\)，但配左边 ROC 时是 \(-e^{at}u(-t)\)。离散域见 E.2。</li>
    <li><b>把奈奎斯特率当「可用带宽」</b>：4000 Hz 是折叠边界，不是可分辨带宽；抗混叠过渡带必须留（D.8）。</li>
    <li><b>认为加窗只是「防止边界不连续」</b>：加窗在频域是卷积 (D-8)，会抹开所有谱线，包括本来干净的那些。</li>
    <li><b>用零极点几何法时忽略 ROC 是否含虚轴</b>：不满足时 \(H(j\omega)\) 根本不存在（系统不稳定），几何法给出的是发散解。</li>
    <li><b>把匹配滤波器的 \(2E/N_0\) 直接套到声纹打分</b>：它假设白噪声、波形已知、单次判决；真实声纹是信道失配 + 非白噪声，所以要channel补偿与分数归一化。</li>
  </ol></div>

  <h3>自检</h3>
  <div class="checklist">
    <label><input type="checkbox" data-k="qD-1"> 我能不看讲义，从 δ 的筛选性质四步推出卷积积分 (D-2)，并说出「线性」「时不变」各用在哪一步。</label>
    <label><input type="checkbox" data-k="qD-2"> 我能推出卷积定理 (D-7)，并解释为什么分帧加窗必然导致频谱泄漏、以及 \(1/2\pi\) 系数的来历。</label>
    <label><input type="checkbox" data-k="qD-3"> 我能用 (D-12) 推出抽样定理，写出 sinc 内插公式，并算清 8 kHz / 4 kHz / 3.4 kHz 三者的关系。</label>
    <label><input type="checkbox" data-k="qD-4"> 我能在 s 平面上画出二阶谐振系统的极点，说明 \(Q\)、带宽、衰减时间常数怎么算，并联系共振峰。</label>
    <label><input type="checkbox" data-k="qD-5"> 我能用帕塞瓦尔定理手算验证 \(N=4\) 的 DFT 能量守恒，并说清 \(1/N\) 与单边谱 \(2/N\) 的关系。</label>
    <label><input type="checkbox" data-k="qD-6"> 我能说出匹配滤波器的最优冲激响应和最大输出信噪比，以及测不准原理取等号时为什么一定是高斯窗。</label>
  </div>
</section>
"""
