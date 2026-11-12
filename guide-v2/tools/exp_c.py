# -*- coding: utf-8 -*-
"""推导详解扩展内容：第 12–16 讲。"""

EXP_C = {}

EXP_C["s12"] = r"""
<div class="derive">
<div class="dtitle">推导详解 · 第 12 讲　阈值、DET、EER 与检测代价</div>

<h4>1. 符号对照表</h4>
<table class="sym"><tr><th>符号</th><th>含义</th><th>取值 / 范围</th></tr>
<tr><td>\(\theta\)</td><td>判决阈值</td><td>打分值域内</td></tr>
<tr><td>\(N_{\mathrm{tar}},N_{\mathrm{imp}}\)</td><td>真实试验 / 冒充试验次数</td><td>常不等</td></tr>
<tr><td>\(\mathrm{FAR},\mathrm{FRR}\)</td><td>误受率 / 误拒率</td><td>[0,1]</td></tr>
<tr><td>\(C_{\mathrm{FA}},C_{\mathrm{FR}}\)</td><td>两类错误的代价</td><td>常用 10 : 1</td></tr>
<tr><td>\(P_{\mathrm{tar}}\)</td><td>真实用户出现的先验</td><td>NIST 常用 0.01</td></tr>
</table>

<h4>2. FA/FR 随阈值单调变化：从分布图上读出来</h4>
<p>设本人分数分布密度 \(p(s\mid H_1)\)、冒充者分数分布 \(p(s\mid H_0)\)，则</p>
<div class="math sub">\[ \mathrm{FRR}(\theta)=\int_{-\infty}^{\theta}p(s\mid H_1)\,\mathrm ds,\qquad
\mathrm{FAR}(\theta)=\int_{\theta}^{\infty}p(s\mid H_0)\,\mathrm ds \tag{12-7} \]</div>
<p>对 \(\theta\) 求导：\(\dfrac{\mathrm d\,\mathrm{FRR}}{\mathrm d\theta}=p(\theta\mid H_1)>0\)、
\(\dfrac{\mathrm d\,\mathrm{FAR}}{\mathrm d\theta}=-p(\theta\mid H_0)<0\)。
<b>一个升、一个降，且都是密度积分，所以二者不可能同时变小</b>。这条严格单调性是所有阈值权衡的根据。
实践中不假设分布形状，而是把所有试验分数排序，逐个候选阈值统计 \(N_{\mathrm{FA}},N_{\mathrm{FR}}\) 得到经验阶梯曲线。</p>

<h4>3. EER 的插值算法（工程实现细节）</h4>
<p>分数是离散的，FAR 与 FRR 两条阶梯曲线通常不严格相交。做法是：</p>
<div class="math sub">\[ \begin{aligned}
&\text{(i) 在相邻阈值 }\theta_i,\theta_{i+1}\text{ 之间找 }d(\theta)=\mathrm{FAR}-\mathrm{FRR}\text{ 变号区间}\\
&\text{(ii) 线性插值：}\ \tau=\frac{d(\theta_i)}{d(\theta_i)-d(\theta_{i+1})}\\
&\text{(iii) }\mathrm{EER}=\mathrm{FAR}(\theta_i)+\tau\big[\mathrm{FAR}(\theta_{i+1})-\mathrm{FAR}(\theta_i)\big]
\end{aligned} \tag{12-8} \]</div>
<p>直接取「\(|d|\) 最小的那个采样点」在试验次数少时会高估 EER，因为阶梯宽度是 \(1/N_{\mathrm{imp}}\) 或 \(1/N_{\mathrm{tar}}\)。</p>

<h4>4. 检测代价函数的推导：从贝叶斯风险出发</h4>
<p>定义四种结果的风险：正确接受/正确拒绝代价为 0，误受代价 \(C_{\mathrm{FA}}\)、误拒代价 \(C_{\mathrm{FR}}\)。
期望风险（贝叶斯风险）为各错误概率按先验加权：</p>
<div class="math sub">\[ \begin{aligned}
\mathcal R(\theta)&=C_{\mathrm{FR}}\,P(H_1)\,\Pr(\text{拒}\mid H_1)
+C_{\mathrm{FA}}\,P(H_0)\,\Pr(\text{受}\mid H_0)\\
&=C_{\mathrm{FR}}P_{\mathrm{tar}}\,\mathrm{FRR}(\theta)+C_{\mathrm{FA}}P_{\mathrm{nontarget}}\,\mathrm{FAR}(\theta)
\end{aligned} \tag{12-9} \]</div>
<p>这正是式 (12-5) 的 \(C_{\mathrm{det}}\)。对 \(\theta\) 求导并令为 0：</p>
<div class="math sub">\[ C_{\mathrm{FR}}P_{\mathrm{tar}}\,p(\theta\mid H_1)-C_{\mathrm{FA}}P_{\mathrm{nontarget}}\,p(\theta\mid H_0)=0
\quad\Longrightarrow\quad
\Lambda(\theta)=\frac{p(\theta\mid H_1)}{p(\theta\mid H_0)}
=\frac{C_{\mathrm{FA}}P_{\mathrm{nontarget}}}{C_{\mathrm{FR}}P_{\mathrm{tar}}} \tag{12-10} \]</div>
<p><b>最优阈值就是似然比等于「代价×先验之比」的那个点</b>（呼应第 11 讲式 11-2）。
把 12-6 的算例代进去：右边 \(=\dfrac{10\times0.1}{1\times0.9}=1.11\)，即在该点两类密度相近，
阈值应偏「宽松」一侧——与算例结论（\(\theta_1\) 优于 \(\theta_2\)）一致。
归一化基准 \(C_{\mathrm{default}}=\min(C_{\mathrm{FR}}P_{\mathrm{tar}},\,C_{\mathrm{FA}}P_{\mathrm{nontarget}})\) 是
「永远拒绝 / 永远接受」两种平凡策略的风险，故 \(\mathrm{minDCF}\in[0,1]\)，越接近 0 越好。</p>

<h4>5. z-norm / t-norm 在消除什么</h4>
<p>不同目标模型的打分分布尺度不同（有的模型分数整体偏高），不同测试语音的难度也不同。设观测分数</p>
<div class="math sub">\[ s=a_{\mathrm{model}}+b_{\mathrm{test}}+s_{\mathrm{true}} \tag{12-11} \]</div>
<p>其中 \(a_{\mathrm{model}}\) 是模型偏置、\(b_{\mathrm{test}}\) 是测试语音偏置。
z-norm 用一批冒充语音估出该模型的 \((\mu_z,\sigma_z)\) 从而消掉 \(a_{\mathrm{model}}\)；
t-norm 用一批背景模型估出该测试语音的 \((\mu_t,\sigma_t)\) 消掉 \(b_{\mathrm{test}}\)。
两者串联（zt-norm）才把两个偏置都去掉。代价：需要额外的开发集，且每条测试要多算 \(N_{\mathrm{cohort}}\) 次打分。
<b>s-norm</b> 把两者对称平均，对队列选择更鲁棒。</p>

<h4>6. 公式 ↔ 代码</h4>
<pre><code># 式(12-7) 经验 FAR/FRR 曲线（无需假设分布）
ths = np.unique(np.concatenate([tar_scores, imp_scores]))
far = np.array([(imp_scores >= t).mean() for t in ths])
frr = np.array([(tar_scores <  t).mean() for t in ths])

# 式(12-8) 插值求 EER
d = far - frr
i = np.where(np.sign(d[:-1]) != np.sign(d[1:]))[0][0]
tau = d[i] / (d[i] - d[i+1])
eer = far[i] + tau*(far[i+1] - far[i])

# 式(12-9)(12-10) minDCF
cdet = C_FR*frr*P_tar + C_FA*far*(1-P_tar)
cd = cdet.min() / min(C_FR*P_tar, C_FA*(1-P_tar))

# 式(12-11) z-norm
s_norm = (s - imp_scores.mean()) / imp_scores.std()</code></pre>

<h4>7. 边界与失效条件</h4>
<ul><li>试验次数少时 EER 分辨率受限于 \(1/N\)：100 次冒充试验的最小非零 FAR 就是 1%，报「EER=0.3%」毫无意义。报告指标必须同时给出试验次数与置信区间。</li>
<li>DET 曲线常用正态偏差刻度 \(\Phi^{-1}(p)\) 拉伸低错误率区域，与 ROC 的线性刻度读法不同；<b>DET 越靠近左下角越好</b>，AUC 说法不适用。</li>
<li>阈值必须在<b>开发集</b>上选定，再在测试集上报结果；在测试集上调阈值等于作弊。</li>
<li>归一化队列要与目标模型同域，否则估计出的 \(\mu,\sigma\) 反而引入偏差。</li></ul>
</div>
"""

EXP_C["s13"] = r"""
<div class="derive">
<div class="dtitle">推导详解 · 第 13 讲　GMM–EM、MAP 自适应与 i-vector</div>

<h4>1. EM 算法从 ELBO 推出来（不跳步）</h4>
<p>目标是最大化对数似然 \(\ln p(X\mid\lambda)=\ln\sum_{\mathbf z}p(X,\mathbf z\mid\lambda)\)，
\(\mathbf z\) 是「每帧属于哪个高斯」的隐变量。引入任意分布 \(q(\mathbf z)\)，由 Jensen 不等式：</p>
<div class="math sub">\[ \begin{aligned}
\ln p(X\mid\lambda)&=\ln\sum_{\mathbf z}q(\mathbf z)\frac{p(X,\mathbf z\mid\lambda)}{q(\mathbf z)}
\ge\sum_{\mathbf z}q(\mathbf z)\ln\frac{p(X,\mathbf z\mid\lambda)}{q(\mathbf z)}\equiv\mathrm{ELBO}(q,\lambda)
\end{aligned}\tag{13-8} \]</div>
<p>两者之差恰是 \(\mathrm{KL}\big(q(\mathbf z)\,\|\,p(\mathbf z\mid X,\lambda)\big)\ge0\)。于是 EM 交替做两件事：</p>
<div class="math sub">\[ \begin{aligned}
\text{E 步：}&\ q\leftarrow p(\mathbf z\mid X,\lambda^{\mathrm{old}})\ \Rightarrow\ \text{KL}=0,\ \text{ELBO 紧贴似然}\\
\text{M 步：}&\ \lambda\leftarrow\arg\max_{\lambda}\mathrm{ELBO}(q,\lambda)
=\arg\max_\lambda\sum_{\mathbf z}q(\mathbf z)\ln p(X,\mathbf z\mid\lambda)
\end{aligned} \tag{13-9} \]</div>
<p>E 步算出的 \(q(z_t=c)\) 就是式 (13-2) 的责任度 \(\gamma_{tc}\)（贝叶斯公式展开即得）。
M 步在 \(q\) 固定下是带权极大似然：对 \(\boldsymbol\mu_c\) 求偏导</p>
<div class="math sub">\[ \frac{\partial}{\partial\boldsymbol\mu_c}\sum_{t,c}\gamma_{tc}
\Big[-\tfrac12(\mathbf x_t-\boldsymbol\mu_c)^{\mathsf T}\Sigma_c^{-1}(\mathbf x_t-\boldsymbol\mu_c)\Big]=0
\ \Longrightarrow\
\boldsymbol\mu_c=\frac{\sum_t\gamma_{tc}\mathbf x_t}{\sum_t\gamma_{tc}} \tag{13-10} \]</div>
<p>同理得 \(\Sigma_c\) 与 \(\pi_c\)（\(\pi_c\) 需加 \(\sum_c\pi_c=1\) 约束，用拉格朗日乘子）。
每轮「E 使下界贴合、M 使下界上升」，保证 \(\ln p(X\mid\lambda)\) 单调不降。</p>
<p><b>实现必须在对数域</b>：\(\ln\big[\pi_c\mathcal N(\mathbf x_t\mid\cdot)\big]
=\ln\pi_c-\tfrac12\big[d\ln2\pi+\ln|\Sigma_c|+(\mathbf x_t-\boldsymbol\mu_c)^{\mathsf T}\Sigma_c^{-1}(\mathbf x_t-\boldsymbol\mu_c)\big]\)，
再用 log-sum-exp 归一化 \(\ln\gamma_{tc}=\ell_{tc}-\ln\sum_j e^{\ell_{tj}}\)，
其中 \(\ln\sum_j e^{\ell_j}=m+\ln\sum_j e^{\ell_j-m}\)、\(m=\max_j\ell_j\)。不这么做，39 维 × 512 高斯的密度连乘会直接下溢为 0。</p>

<h4>2. UBM–MAP：为什么 \(\alpha_c=n_c/(n_c+r)\)</h4>
<p>把 UBM 均值当作先验：\(\boldsymbol\mu_c\sim\mathcal N(\boldsymbol\mu_c^{\mathrm{UBM}},\ \Sigma_c/r)\)。
观测到 \(n_c=\sum_t\gamma_{tc}\) 帧、样本均值 \(\boldsymbol\mu_c^{\mathrm{data}}\)，其似然为
\(\mathcal N(\boldsymbol\mu_c^{\mathrm{data}}\mid\boldsymbol\mu_c,\Sigma_c/n_c)\)。高斯先验 × 高斯似然后验均值是精度加权平均：</p>
<div class="math sub">\[ \hat{\boldsymbol\mu}_c=\frac{(r/\Sigma_c)\boldsymbol\mu_c^{\mathrm{UBM}}+(n_c/\Sigma_c)\boldsymbol\mu_c^{\mathrm{data}}}{r/\Sigma_c+n_c/\Sigma_c}
=\frac{n_c}{n_c+r}\boldsymbol\mu_c^{\mathrm{data}}+\frac{r}{n_c+r}\boldsymbol\mu_c^{\mathrm{UBM}} \tag{13-11} \]</div>
<p>正是式 (13-4)。\(r\) 是先验的「等效帧数」：数据少时先验占主导，数据多时才信任数据。
这一步把「每个说话人几秒数据」与「2048 个高斯」的矛盾化解掉，是 GMM-UBM 能实用的关键。</p>

<h4>3. i-vector 后验均值公式的来历</h4>
<p>模型 \(\mathbf M=\mathbf m+T\mathbf w+\boldsymbol\varepsilon\)，\(\mathbf w\sim\mathcal N(\mathbf 0,I)\)、
\(\boldsymbol\varepsilon\sim\mathcal N(\mathbf 0,\Sigma)\)。由线性高斯模型，后验 \(\mathbf w\mid\mathbf M\) 仍是高斯，其精度矩阵与均值为</p>
<div class="math sub">\[ \begin{aligned}
\mathrm{Cov}(\mathbf w\mid\mathbf M)&=\big(I+T^{\mathsf T}\Sigma^{-1}T\big)^{-1}\\
\mathbb E[\mathbf w\mid\mathbf M]&=\big(I+T^{\mathsf T}\Sigma^{-1}T\big)^{-1}T^{\mathsf T}\Sigma^{-1}(\mathbf M-\mathbf m)
\end{aligned}\tag{13-12} \]</div>
<p>矩阵求逆的维度是总变化空间维度（400×400），<b>与超矢量的 19968 维无关</b>，所以每条语音提 i-vector 很快。
\(\Sigma\) 由 UBM 的零阶/一阶 Baum–Welch 统计量按高斯块拼成分块对角阵，这是实现里最繁琐但最关键的一步。</p>

<h4>4. PLDA 打分：把「像不像」变成似然比</h4>
<p>对两条语音的 i-vector 建模（\(\mathbf w=\boldsymbol\mu+V\mathbf y+\boldsymbol\varepsilon\)，\(\mathbf y\) 身份隐变量、\(\boldsymbol\varepsilon\) 会话噪声），打分是</p>
<div class="math sub">\[ s(\mathbf w_1,\mathbf w_2)=\ln\frac{p(\mathbf w_1,\mathbf w_2\mid\text{同一人})}{p(\mathbf w_1\mid H_{\mathrm{ind}})p(\mathbf w_2\mid H_{\mathrm{ind}})} \tag{13-13} \]</div>
<p>两个高斯模型都有闭式协方差，代入即可算。PLDA 相比余弦相似度的优势是<b>显式建模了「同一人不同录音」的方差</b>，
能自动给受信道影响大的维度降权，因此在 SRE 任务上长期优于余弦。</p>

<h4>5. 三条技术路线的对照</h4>
<table class="sym"><tr><th>方法</th><th>说话人表示</th><th>打分</th><th>少样本注册</th><th>主要弱点</th></tr>
<tr><td>GMM-UBM</td><td>自适应后的 2048 高斯</td><td>对数似然比</td><td>尚可（MAP）</td><td>维度高、信道敏感</td></tr>
<tr><td>i-vector + PLDA</td><td>400 维低秩向量</td><td>PLDA 似然比</td><td>好</td><td>线性高斯假设</td></tr>
<tr><td>x-vector + PLDA</td><td>512 维 DNN embedding</td><td>PLDA / 余弦</td><td>很好</td><td>需大量训练数据</td></tr>
</table>

<h4>6. 边界与失效条件</h4>
<ul><li>GMM 用全协方差时参数量 \(\sim C d^2/2\)，几秒数据必然奇异；对角协方差是必需而非简化。</li>
<li>EM 只保证收敛到局部极大，k-means 初始化与多次重启影响明显。</li>
<li>i-vector 的 \(T\) 必须在与测试同域的大规模数据上训练；跨域（录音设备不同）时性能下降明显，需要域适配。</li></ul>
</div>
"""

EXP_C["s14"] = r"""
<div class="derive">
<div class="dtitle">推导详解 · 第 14 讲　统计池化与 margin 损失</div>

<h4>1. 为什么统计池化能处理变长输入</h4>
<p>设帧级输出 \(\mathbf h_t\in\mathbb R^{D}\)，\(t=1..T\)，\(T\) 随语音长度变化。统计池化</p>
<div class="math sub">\[ \boldsymbol\mu=\frac{1}{T}\sum_{t}\mathbf h_t,\qquad
\boldsymbol\sigma^2=\frac{1}{T}\sum_t(\mathbf h_t-\boldsymbol\mu)^2,\qquad
\mathbf e=[\boldsymbol\mu;\boldsymbol\sigma]\in\mathbb R^{2D} \tag{14-1} \]</div>
<p>把「集合」映射成固定维数的一、二阶矩，因此后续全连接层的输入维度与 \(T\) 无关。
从概率角度看，这是假设各帧独立同分布于某高斯、用充分统计量近似它；标准差项补充了「分散程度」，
实测比只用均值提升明显（x-vector 论文的关键设计之一）。</p>
<p><b>注意池化对 \(T\) 的偏置</b>：短语音的 \(\boldsymbol\sigma\) 估计方差大，长语音更稳，
所以训练时要做长度均衡（按时长分桶、或随机裁剪到固定长度），否则模型会学到「时长」而非身份。</p>

<h4>2. TDNN 与带上下文的逐帧变换</h4>
<div class="math sub">\[ \mathbf h_t=f\!\left(W\big[\mathbf x_{t-\tau_1};\mathbf x_t;\mathbf x_{t+\tau_2}\big]+\mathbf b\right),\qquad
\text{x-vector: }\tau\in\{-2,-1,0,1,2\}\ \text{的扩张卷积} \tag{14-2} \]</div>
<p>与 CNN 的差别是每个时间位置看的是「拼接的上下文帧」而非二维邻域，
且高层用<b>扩张（dilated）卷积</b>跳着取样：第 1 层看 \(\pm1\) 帧、第 2 层看 \(\pm2\)、第 3 层看 \(\pm3\)，
三层就覆盖 15 帧上下文而不增加参数。按 10 ms 帧移算约 150 ms，足以覆盖一个音节。</p>

<h4>3. AAM-Softmax：margin 加在哪里</h4>
<p>普通 softmax 只要求正确类分数最大，类内可以很松。把权重与特征都做长度归一化并令 \(\mathbf w_c^{\mathsf T}\mathbf e=\cos\theta_c\)，加性角度间隔损失为</p>
<div class="math sub">\[ L=-\ln\frac{e^{s\cos(\theta_{y}+m)}}{e^{s\cos(\theta_{y}+m)}+\sum_{c\neq y}e^{s\cos\theta_c}} \tag{14-3} \]</div>
<p>它强迫正确类的角度比原来再小 \(m\)（常用 \(m=0.2\) rad），等价于在球面上把类间拉开、类内压紧。
\(s\) 是尺度因子（常取 30），因为归一化后 \(\cos\theta\in[-1,1]\)，不放大则 softmax 太「软」、梯度太小。
训练完成后丢掉分类层，取倒数第二层的 \(\mathbf e\) 作为 embedding，即可用于开集声纹确认。</p>

<h4>4. embedding 打分的两种后端</h4>
<div class="math sub">\[ s_{\cos}=\frac{\mathbf e_1^{\mathsf T}\mathbf e_2}{\|\mathbf e_1\|\|\mathbf e_2\|},\qquad
s_{\mathrm{PLDA}}=\ln\frac{p(\mathbf e_1,\mathbf e_2\mid H_1)}{p(\mathbf e_1\mid H_0)p(\mathbf e_2\mid H_0)} \tag{14-4} \]</div>
<p>余弦简单、无需训练、适合数据量少；PLDA 需要一批开发数据估计类内/类间协方差，但能按维度加权，
在信道变化大时更稳。工程上常先做长度归一化 + LDA 降维去信道，再算余弦或 PLDA。</p>

<h4>5. 与「手工特征」路线的对比账</h4>
<table class="sym"><tr><th>环节</th><th>手工路线（第 6–10 讲）</th><th>x-vector 路线</th></tr>
<tr><td>特征</td><td>MFCC + Δ + ΔΔ（39 维，人工设计）</td><td>原始 MFCC / 频谱，逐帧由网络学变换</td></tr>
<tr><td>变长聚合</td><td>全局均值 / 统计量（人工）</td><td>统计池化（可学，且保留标准差）</td></tr>
<tr><td>说话人表示</td><td>GMM 超矢量 / i-vector</td><td>512 维 embedding</td></tr>
<tr><td>打分</td><td>对数似然比 / PLDA</td><td>余弦 / PLDA</td></tr>
</table>
<p>两条路线的<b>后半段其实一样</b>（都要定长向量 + 似然比/相似度 + 阈值），
差别在于「前面那段变换是人工设计还是学出来的」。理解这点，第 12 讲的评价体系就能无缝迁移到深度模型。</p>

<h4>6. 边界与失效条件</h4>
<ul><li>训练类别数太少时 margin softmax 的类间结构学不充分，embedding 泛化差；这类方法依赖成千上万个说话人。</li>
<li>短语音（&lt;2 s）时统计池化的二阶矩不可靠，性能明显下滑；可用注意力池化（给帧加权）缓解。</li>
<li>域不匹配（训练用 16 kHz 电话语音、测试用 8 kHz 设备声）影响远大于模型结构差异，优先做数据/前端对齐。</li></ul>
</div>
"""

EXP_C["s15"] = r"""
<div class="derive">
<div class="dtitle">推导详解 · 第 15 讲　从「能跑」到「能用」的检查清单</div>

<h4>1. 一条完整流水线的参数表（可直接照抄）</h4>
<table class="sym"><tr><th>环节</th><th>参数</th><th>取值</th><th>改错的后果</th></tr>
<tr><td>采集</td><td>\(F_s\)</td><td>8000 Hz / 16 bit</td><td>&lt;2×最高频率 → 混叠，不可恢复</td></tr>
<tr><td>抗混叠</td><td>模拟低通截止</td><td>3.4 kHz</td><td>缺失 → 高频伪装成低频峰</td></tr>
<tr><td>预加重</td><td>\(\alpha\)</td><td>设备声 0～0.45；语音 0.97</td><td>过大 → 100 Hz 基频被压 30 dB</td></tr>
<tr><td>分帧</td><td>\(L/S\)</td><td>200 / 80 点</td><td>无重叠 → OLA 重构失真</td></tr>
<tr><td>窗</td><td>汉明</td><td>0.54−0.46cos</td><td>矩形窗 → −13 dB 旁瓣、严重泄漏</td></tr>
<tr><td>FFT</td><td>\(N\)</td><td>256（2 的幂）</td><td>补零只改显示密度，不改分辨率</td></tr>
<tr><td>幅度谱</td><td>\(2/N\)</td><td>直流除外</td><td>漏乘 → 幅值虚高 \(N/2\) 倍</td></tr>
<tr><td>Mel</td><td>\(M\)</td><td>26</td><td>照搬语音配置 → 低频判别信息只占 2–3 通道</td></tr>
<tr><td>倒谱</td><td>\(n_{\mathrm{ceps}}\)</td><td>13 + Δ + ΔΔ = 39</td><td>只加维不加差分 → 误识别高约 20%</td></tr>
<tr><td>归一化</td><td>CMN</td><td>逐维减均值</td><td>漏做 → 换设备即崩</td></tr>
<tr><td>划分</td><td>按段分组</td><td>60/20/20</td><td>按帧随机切 → 指标虚高</td></tr>
<tr><td>判决</td><td>\(\theta\)</td><td>在开发集上按 minDCF 选</td><td>测试集上调阈值 → 作弊</td></tr>
</table>

<h4>2. 排查问题的固定顺序（从前往后，别跳）</h4>
<ol><li><b>时域</b>：画原始波形，确认没削波、没有直流偏置、长度与 \(F_s\) 对得上。</li>
<li><b>频域</b>：画纯正弦的谱，确认峰值落在正确频率、幅值经 \(2/N\) 后正确、旁瓣是加了窗的样子。</li>
<li><b>特征</b>：打印每一帧的形状与取值范围，确认 39 维、无 NaN、CMN 后各维均值≈0。</li>
<li><b>模型</b>：跑梯度检查（\(<10^{-8}\)），确认一轮更新后损失确实下降（式 8-13）。</li>
<li><b>划分</b>：确认训练集与测试集没有共享同一段录音。</li>
<li><b>评价</b>：同时报 FAR/FRR/EER/minDCF 与试验次数，别只报准确率。</li></ol>

<h4>3. 三个可自己动手的「破坏性实验」</h4>
<ul><li><b>把 \(F_s\) 改成 500 Hz</b>：看 100 Hz 基频附近凭空多出哪些峰，验证式 (2-10) 的混叠预测。</li>
<li><b>把汉明窗换成矩形窗</b>：比较纯正弦谱的旁瓣高度，量出约 30 dB 的差异。</li>
<li><b>把 \(\Delta/\Delta\Delta\) 去掉</b>：在同样数据上对比分类准确率，复现「加差分比加维数更有效」的结论。</li></ul>
</div>
"""

EXP_C["s16"] = r"""
<div class="derive">
<div class="dtitle">附录 · 全书符号总表与公式速查</div>

<h4>A. 符号总表</h4>
<table class="sym"><tr><th>符号</th><th>含义</th><th>首次出现</th></tr>
<tr><td>\(x(t),x[n]\)</td><td>连续 / 离散信号</td><td>第 1、2 讲</td></tr>
<tr><td>\(F_s,T_s,N\)</td><td>采样率、采样间隔、点数</td><td>第 2 讲</td></tr>
<tr><td>\(L,S,M\)</td><td>帧长、帧移、帧数 / 滤波器数</td><td>第 2、6 讲</td></tr>
<tr><td>\(w[n]\)</td><td>窗函数</td><td>第 2 讲</td></tr>
<tr><td>\(X[k],X[m,k]\)</td><td>DFT / STFT 系数</td><td>第 4、5 讲</td></tr>
<tr><td>\(W_N\)</td><td>旋转因子 \(e^{-j2\pi/N}\)</td><td>第 4 讲</td></tr>
<tr><td>\(P[k],H_m[k],E_m,L_m,c_i\)</td><td>功率谱、Mel 滤波器、通道能量、对数能量、倒谱系数</td><td>第 6 讲</td></tr>
<tr><td>\(a,b,\psi,cA_j,cD_j\)</td><td>尺度、平移、母小波、近似/细节系数</td><td>第 7 讲</td></tr>
<tr><td>\(W,\mathbf b,\mathbf z,\mathbf h,\boldsymbol\delta\)</td><td>权重、偏置、净输入、激活、误差信号</td><td>第 8 讲</td></tr>
<tr><td>\(\eta,\lambda,\gamma\)</td><td>学习率、正则系数、动量系数</td><td>第 8、10 讲</td></tr>
<tr><td>\(F,P,S,\mathrm{RF}\)</td><td>核大小、padding、步长、感受野</td><td>第 9 讲</td></tr>
<tr><td>\(\theta,\mathrm{FAR},\mathrm{FRR},\mathrm{EER},C_{\det}\)</td><td>阈值、两类错误率、等错误率、检测代价</td><td>第 12 讲</td></tr>
<tr><td>\(\pi_c,\boldsymbol\mu_c,\Sigma_c,\gamma_{tc}\)</td><td>GMM 权重/均值/协方差、责任度</td><td>第 13 讲</td></tr>
<tr><td>\(\mathbf M,\mathbf m,T,\mathbf w\)</td><td>超矢量、UBM 超矢量、总变化空间、i-vector</td><td>第 13 讲</td></tr>
<tr><td>\(\mathbf e,\boldsymbol\mu,\boldsymbol\sigma\)</td><td>embedding、统计池化均值/标准差</td><td>第 14 讲</td></tr>
</table>

<h4>B. 公式速查（按用途）</h4>
<table class="sym"><tr><th>用途</th><th>公式</th><th>编号</th></tr>
<tr><td>采样</td><td>\(x[n]=x(n/F_s)\)</td><td>2-1</td></tr>
<tr><td>奈奎斯特条件</td><td>\(F_s>2f_{\max}\)</td><td>2-2</td></tr>
<tr><td>混叠频率</td><td>\(f_{\mathrm{alias}}=\min_k|f-kF_s|\)</td><td>2-3</td></tr>
<tr><td>量化信噪比</td><td>\(\mathrm{SNR}_{\mathrm{dB}}=6.02B+1.76\)</td><td>2-4</td></tr>
<tr><td>DFT</td><td>\(X[k]=\sum_n x[n]W_N^{kn}\)</td><td>4-2</td></tr>
<tr><td>IDFT</td><td>\(x[n]=\frac1N\sum_kX[k]e^{j2\pi kn/N}\)</td><td>4-9</td></tr>
<tr><td>单边幅度谱</td><td>\(A[k]=2|X[k]|/N\)</td><td>4-5</td></tr>
<tr><td>真实分辨率</td><td>\(\Delta f=1/T_{\mathrm{obs}}=F_s/N_0\)</td><td>4-6</td></tr>
<tr><td>FFT 复杂度</td><td>\(\frac N2\log_2N\)</td><td>4-6</td></tr>
<tr><td>STFT</td><td>\(X[m,k]=\sum_nx[n]w[n-mS]e^{-j2\pi kn/N}\)</td><td>5-1</td></tr>
<tr><td>时频不确定</td><td>\(\Delta t\,\Delta f\ge1/(4\pi)\)</td><td>5-2</td></tr>
<tr><td>Mel 刻度</td><td>\(m(f)=2595\log_{10}(1+f/700)\)</td><td>6-3</td></tr>
<tr><td>通道能量</td><td>\(E_m=\sum_kP[k]H_m[k]\)</td><td>6-4</td></tr>
<tr><td>对数能量</td><td>\(L_m=\ln(E_m+\varepsilon)\)</td><td>6-5</td></tr>
<tr><td>DCT-II</td><td>\(c_i=\sqrt{2/M}\sum_mL_m\cos[\frac{\pi i}{M}(m-\frac12)]\)</td><td>6-6</td></tr>
<tr><td>一阶差分</td><td>\(d_t=\frac{\sum_n n(c_{t+n}-c_{t-n})}{2\sum_nn^2}\)</td><td>6-7</td></tr>
<tr><td>CWT</td><td>\(W(a,b)=\int x(t)\,\overline{\psi((t-b)/a)}/\sqrt a\,\mathrm dt\)</td><td>7-1</td></tr>
<tr><td>softmax</td><td>\(p_c=e^{z_c}/\sum_je^{z_j}\)</td><td>8-2</td></tr>
<tr><td>交叉熵</td><td>\(L=-\sum_cy_c\ln p_c\)</td><td>8-3</td></tr>
<tr><td>输出层误差</td><td>\(\boldsymbol\delta_2=\mathbf p-\mathbf y\)</td><td>8-4</td></tr>
<tr><td>隐层误差</td><td>\(\boldsymbol\delta_1=(W_2^{\mathsf T}\boldsymbol\delta_2)\odot\sigma'(\mathbf z_1)\)</td><td>8-5</td></tr>
<tr><td>卷积尺寸</td><td>\(H_{\mathrm{out}}=\lfloor(H_{\mathrm{in}}+2P-F)/S\rfloor+1\)</td><td>9-2</td></tr>
<tr><td>检测代价</td><td>\(C_{\det}=C_{\mathrm{FR}}\mathrm{FRR}P_{\mathrm{tar}}+C_{\mathrm{FA}}\mathrm{FAR}P_{\mathrm{nontarget}}\)</td><td>12-5</td></tr>
<tr><td>GMM</td><td>\(p(\mathbf x\mid\lambda)=\sum_c\pi_c\mathcal N(\mathbf x\mid\boldsymbol\mu_c,\Sigma_c)\)</td><td>13-1</td></tr>
<tr><td>i-vector</td><td>\(\mathbf M=\mathbf m+T\mathbf w\)</td><td>13-5</td></tr>
<tr><td>统计池化</td><td>\(\mathbf e=[\boldsymbol\mu;\boldsymbol\sigma]\)</td><td>14-1</td></tr>
</table>

<h4>C. 关于公式排版的说明</h4>
<p>本版起，全部公式改用 <b>KaTeX</b> 排版（本地字体，离线可用），并按「讲-序」编号。
编号如 <b>(4-9)</b> 中的 4 表示第 4 讲、9 表示该讲的公式序号；带「推导详解」字样的编号（如 4-9、6-10）
出现在各讲末尾的推导补充中，与正文公式属于同一编号体系。
所有下式里的中文说明、变量表、数值算例都放在公式<b>之外</b>，以免中文字形干扰数学排版。</p>
</div>
"""
