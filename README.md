# 通勤学习语料库

一个人的通勤阅读材料库。每篇是一个自包含的 HTML 文件，下载到平板用浏览器打开即可阅读——**用 HTML 而不是 Markdown，唯一的原因是让数学公式（MathML）直接渲染出来**，对版式和外观没有别的要求。

## 仓库结构

```text
SKILL.md                  全局规则（先读这个）
README.md                 本文件，含语料目录表 = 编号的权威来源
GPT项目说明.md            粘贴到 ChatGPT 项目指令框的启动协议
待整合.md                 已生效但还没写进 SKILL 的规则改动（读 SKILL 后必读）
tools/intake.py           收稿：校验新文章 → 更新目录 → 提交推送
tools/build_index.py      重新生成下面的目录表
tools/export_for_gpt.py   导出 6 个 SKILL 供上传（联网不可用时的降级方案）
语料/
├── 数学/SKILL.md         + NN_*.html
├── 计算机/SKILL.md       + NN_*.html
├── AI/SKILL.md           + NN_*.html
├── 马列/SKILL.md         + NN_*.html
├── 其他/SKILL.md         + NN_*.html
└── 其他资料（非html）/    用户提供的原始素材，不是语料领域目录，不参与编号
```

## 给生成语料的模型

1. 先读 `SKILL.md`，再读目标领域的 `语料/<领域>/SKILL.md`。两层规则都要遵守。
2. **编号从下面的目录表取**：目标领域当前最大编号加一。动手前先同步仓库最新状态，不要用旧快照。
3. 文件名格式 `NN_主题系列_文章短标题.html`，每个领域独立编号。
4. 写完后更新下面的目录表（能执行命令的话跑 `python3 tools/build_index.py`），再提交推送。
5. 已交付的文章默认只读。用户反馈追加到文末 `#reader-feedback`，这不算修改；只有用户明确说这篇写失败了或要求改动时才动正文，且必须原地改、保留原编号。

领域边界：移除 AI 后结论仍成立 → 计算机；主题核心是模型/Agent/Skill/人机协作 → AI；马克思主义**理论部分**及其思想史 → 马列；其余一切（经济、历史、心理学、语言学、自然科学、新闻背景……）→ 其他。

### 无法直接读取文件时（ChatGPT 等）

GitHub 的 `/tree/` 和 `/commits/` 页面拒绝自动访问，只有 `raw.githubusercontent.com` 可抓。按上面第 1、2 条的顺序，对应地址如下（中文路径已百分号编码，**照原样使用，不要自己拼**）：

| 顺序 | 文件 | 地址 |
| --- | --- | --- |
| ① 先读 | 主 SKILL | `https://raw.githubusercontent.com/netzach-star/Commute-Learning-Corpus/main/SKILL.md` |
| ② 再读 | 本文件（取编号） | `https://raw.githubusercontent.com/netzach-star/Commute-Learning-Corpus/main/README.md` |
| ③ 确定领域后读 | 数学 | `https://raw.githubusercontent.com/netzach-star/Commute-Learning-Corpus/main/%E8%AF%AD%E6%96%99/%E6%95%B0%E5%AD%A6/SKILL.md` |
| | 计算机 | `https://raw.githubusercontent.com/netzach-star/Commute-Learning-Corpus/main/%E8%AF%AD%E6%96%99/%E8%AE%A1%E7%AE%97%E6%9C%BA/SKILL.md` |
| | AI | `https://raw.githubusercontent.com/netzach-star/Commute-Learning-Corpus/main/%E8%AF%AD%E6%96%99/AI/SKILL.md` |
| | 马列 | `https://raw.githubusercontent.com/netzach-star/Commute-Learning-Corpus/main/%E8%AF%AD%E6%96%99/%E9%A9%AC%E5%88%97/SKILL.md` |
| | 其他 | `https://raw.githubusercontent.com/netzach-star/Commute-Learning-Corpus/main/%E8%AF%AD%E6%96%99/%E5%85%B6%E4%BB%96/SKILL.md` |

这张表是给已经进到仓库的模型看的。**GPT 需要在读到本文件之前就有 ①② 两个地址**，所以启动那一份必须放在仓库外——见 [GPT项目说明.md](GPT%E9%A1%B9%E7%9B%AE%E8%AF%B4%E6%98%8E.md)，里面是可直接粘进 ChatGPT 项目指令框的完整文本。

<!-- INDEX:START -->

**最后更新：2026-08-14**　新增文章后请更新本表；编号取所在领域当前最大值加一。

### 语料/数学/　—　共 13 篇，下一篇编号 `14`

| 编号 | 标题 | 文件 |
| --- | --- | --- |
| 01 | 应用随机过程导论（一）：为什么一个随机变量不够？ | [01_应用随机过程导论_公式渲染阅读版.html](%E8%AF%AD%E6%96%99/%E6%95%B0%E5%AD%A6/01_%E5%BA%94%E7%94%A8%E9%9A%8F%E6%9C%BA%E8%BF%87%E7%A8%8B%E5%AF%BC%E8%AE%BA_%E5%85%AC%E5%BC%8F%E6%B8%B2%E6%9F%93%E9%98%85%E8%AF%BB%E7%89%88.html) |
| 02 | 泛函分析导论（一）：沿教材七章建立知识树 | [02_泛函分析导论_为什么有限维线性代数不够.html](%E8%AF%AD%E6%96%99/%E6%95%B0%E5%AD%A6/02_%E6%B3%9B%E5%87%BD%E5%88%86%E6%9E%90%E5%AF%BC%E8%AE%BA_%E4%B8%BA%E4%BB%80%E4%B9%88%E6%9C%89%E9%99%90%E7%BB%B4%E7%BA%BF%E6%80%A7%E4%BB%A3%E6%95%B0%E4%B8%8D%E5%A4%9F.html) |
| 03 | 复分析导论（一）：解析函数为何如此刚性？ | [03_复分析导论_解析函数为何如此刚性.html](%E8%AF%AD%E6%96%99/%E6%95%B0%E5%AD%A6/03_%E5%A4%8D%E5%88%86%E6%9E%90%E5%AF%BC%E8%AE%BA_%E8%A7%A3%E6%9E%90%E5%87%BD%E6%95%B0%E4%B8%BA%E4%BD%95%E5%A6%82%E6%AD%A4%E5%88%9A%E6%80%A7.html) |
| 04 | 图论导论（一）：七桥问题为什么通向拓扑？ | [04_图论导论_七桥问题为什么通向拓扑.html](%E8%AF%AD%E6%96%99/%E6%95%B0%E5%AD%A6/04_%E5%9B%BE%E8%AE%BA%E5%AF%BC%E8%AE%BA_%E4%B8%83%E6%A1%A5%E9%97%AE%E9%A2%98%E4%B8%BA%E4%BB%80%E4%B9%88%E9%80%9A%E5%90%91%E6%8B%93%E6%89%91.html) |
| 05 | 代数几何史纲（一）：方程如何成为几何？ | [05_代数几何史纲一_方程如何成为几何.html](%E8%AF%AD%E6%96%99/%E6%95%B0%E5%AD%A6/05_%E4%BB%A3%E6%95%B0%E5%87%A0%E4%BD%95%E5%8F%B2%E7%BA%B2%E4%B8%80_%E6%96%B9%E7%A8%8B%E5%A6%82%E4%BD%95%E6%88%90%E4%B8%BA%E5%87%A0%E4%BD%95.html) |
| 06 | 代数几何史纲（二）：黎曼几何、相对论与丘成桐在哪里相遇？ | [06_代数几何史纲二_黎曼几何微分几何与丘成桐.html](%E8%AF%AD%E6%96%99/%E6%95%B0%E5%AD%A6/06_%E4%BB%A3%E6%95%B0%E5%87%A0%E4%BD%95%E5%8F%B2%E7%BA%B2%E4%BA%8C_%E9%BB%8E%E6%9B%BC%E5%87%A0%E4%BD%95%E5%BE%AE%E5%88%86%E5%87%A0%E4%BD%95%E4%B8%8E%E4%B8%98%E6%88%90%E6%A1%90.html) |
| 07 | 代数几何史纲（三）：椭圆曲线、模性与费马大定理 | [07_代数几何史纲三_椭圆曲线模性与费马大定理.html](%E8%AF%AD%E6%96%99/%E6%95%B0%E5%AD%A6/07_%E4%BB%A3%E6%95%B0%E5%87%A0%E4%BD%95%E5%8F%B2%E7%BA%B2%E4%B8%89_%E6%A4%AD%E5%9C%86%E6%9B%B2%E7%BA%BF%E6%A8%A1%E6%80%A7%E4%B8%8E%E8%B4%B9%E9%A9%AC%E5%A4%A7%E5%AE%9A%E7%90%86.html) |
| 08 | 代数几何史纲（四）：格罗滕迪克革命与现代代数几何 | [08_代数几何史纲四_格罗滕迪克革命与现代代数几何.html](%E8%AF%AD%E6%96%99/%E6%95%B0%E5%AD%A6/08_%E4%BB%A3%E6%95%B0%E5%87%A0%E4%BD%95%E5%8F%B2%E7%BA%B2%E5%9B%9B_%E6%A0%BC%E7%BD%97%E6%BB%95%E8%BF%AA%E5%85%8B%E9%9D%A9%E5%91%BD%E4%B8%8E%E7%8E%B0%E4%BB%A3%E4%BB%A3%E6%95%B0%E5%87%A0%E4%BD%95.html) |
| 09 | 挂谷问题史纲：从面积为零到三维满维——分形维数、调和分析与王虹 | [09_挂谷问题史纲_从分形维数到王虹.html](%E8%AF%AD%E6%96%99/%E6%95%B0%E5%AD%A6/09_%E6%8C%82%E8%B0%B7%E9%97%AE%E9%A2%98%E5%8F%B2%E7%BA%B2_%E4%BB%8E%E5%88%86%E5%BD%A2%E7%BB%B4%E6%95%B0%E5%88%B0%E7%8E%8B%E8%99%B9.html) |
| 10 | 从物理定律到希尔伯特第六问题：数学物理、邓煜与微观—宏观极限 | [10_数学物理与希尔伯特第六问题_从牛顿粒子到宏观流体.html](%E8%AF%AD%E6%96%99/%E6%95%B0%E5%AD%A6/10_%E6%95%B0%E5%AD%A6%E7%89%A9%E7%90%86%E4%B8%8E%E5%B8%8C%E5%B0%94%E4%BC%AF%E7%89%B9%E7%AC%AC%E5%85%AD%E9%97%AE%E9%A2%98_%E4%BB%8E%E7%89%9B%E9%A1%BF%E7%B2%92%E5%AD%90%E5%88%B0%E5%AE%8F%E8%A7%82%E6%B5%81%E4%BD%93.html) |
| 11 | 从群与环到伽罗瓦理论：抽象代数怎样解释一般五次方程没有根式公式 | [11_抽象代数与伽罗瓦理论_从群环域到五次方程不可解.html](%E8%AF%AD%E6%96%99/%E6%95%B0%E5%AD%A6/11_%E6%8A%BD%E8%B1%A1%E4%BB%A3%E6%95%B0%E4%B8%8E%E4%BC%BD%E7%BD%97%E7%93%A6%E7%90%86%E8%AE%BA_%E4%BB%8E%E7%BE%A4%E7%8E%AF%E5%9F%9F%E5%88%B0%E4%BA%94%E6%AC%A1%E6%96%B9%E7%A8%8B%E4%B8%8D%E5%8F%AF%E8%A7%A3.html) |
| 12 | 常微分方程进阶：PDE——从三类原型到弱解 | [12_常微分方程进阶_PDE从三类原型到弱解.html](%E8%AF%AD%E6%96%99/%E6%95%B0%E5%AD%A6/12_%E5%B8%B8%E5%BE%AE%E5%88%86%E6%96%B9%E7%A8%8B%E8%BF%9B%E9%98%B6_PDE%E4%BB%8E%E4%B8%89%E7%B1%BB%E5%8E%9F%E5%9E%8B%E5%88%B0%E5%BC%B1%E8%A7%A3.html) |
| 13 | 常微分方程进阶：动力系统——从求解轨道到研究长期行为 | [13_常微分方程进阶_动力系统从轨道到长期行为.html](%E8%AF%AD%E6%96%99/%E6%95%B0%E5%AD%A6/13_%E5%B8%B8%E5%BE%AE%E5%88%86%E6%96%B9%E7%A8%8B%E8%BF%9B%E9%98%B6_%E5%8A%A8%E5%8A%9B%E7%B3%BB%E7%BB%9F%E4%BB%8E%E8%BD%A8%E9%81%93%E5%88%B0%E9%95%BF%E6%9C%9F%E8%A1%8C%E4%B8%BA.html) |

### 语料/计算机/　—　共 16 篇，下一篇编号 `17`

| 编号 | 标题 | 文件 |
| --- | --- | --- |
| 01 | 从一个简单想法到完整设计初稿：先证明问题，再设计产品 | [01_产品设计方法_从简单想法到设计初稿.html](%E8%AF%AD%E6%96%99/%E8%AE%A1%E7%AE%97%E6%9C%BA/01_%E4%BA%A7%E5%93%81%E8%AE%BE%E8%AE%A1%E6%96%B9%E6%B3%95_%E4%BB%8E%E7%AE%80%E5%8D%95%E6%83%B3%E6%B3%95%E5%88%B0%E8%AE%BE%E8%AE%A1%E5%88%9D%E7%A8%BF.html) |
| 02 | 现代软件项目入门：如何看懂一个项目，如何写好它的文档 | [02_项目外部文档编写_黑盒使用.html](%E8%AF%AD%E6%96%99/%E8%AE%A1%E7%AE%97%E6%9C%BA/02_%E9%A1%B9%E7%9B%AE%E5%A4%96%E9%83%A8%E6%96%87%E6%A1%A3%E7%BC%96%E5%86%99_%E9%BB%91%E7%9B%92%E4%BD%BF%E7%94%A8.html) |
| 03 | 从黑盒使用到白盒维护：陌生项目的内部结构重建与安全变更 | [03_项目内部理解_黑盒灰盒白盒.html](%E8%AF%AD%E6%96%99/%E8%AE%A1%E7%AE%97%E6%9C%BA/03_%E9%A1%B9%E7%9B%AE%E5%86%85%E9%83%A8%E7%90%86%E8%A7%A3_%E9%BB%91%E7%9B%92%E7%81%B0%E7%9B%92%E7%99%BD%E7%9B%92.html) |
| 04 | 项目还没有开始写代码之前，我们究竟在做什么 | [04_项目如何立项：市场评估与价值判断.html](%E8%AF%AD%E6%96%99/%E8%AE%A1%E7%AE%97%E6%9C%BA/04_%E9%A1%B9%E7%9B%AE%E5%A6%82%E4%BD%95%E7%AB%8B%E9%A1%B9%EF%BC%9A%E5%B8%82%E5%9C%BA%E8%AF%84%E4%BC%B0%E4%B8%8E%E4%BB%B7%E5%80%BC%E5%88%A4%E6%96%AD.html) |
| 05 | 从完整工程闭环到 Vibe Coding：软件开发全生命周期与 AI 的真实边界 | [05_软件开发全生命周期_传统工程与VibeCoding的边界.html](%E8%AF%AD%E6%96%99/%E8%AE%A1%E7%AE%97%E6%9C%BA/05_%E8%BD%AF%E4%BB%B6%E5%BC%80%E5%8F%91%E5%85%A8%E7%94%9F%E5%91%BD%E5%91%A8%E6%9C%9F_%E4%BC%A0%E7%BB%9F%E5%B7%A5%E7%A8%8B%E4%B8%8EVibeCoding%E7%9A%84%E8%BE%B9%E7%95%8C.html) |
| 06 | 壳、终端与内核：从《攻壳机动队》理解 Shell 的历史与操作系统边界 | [06_操作系统接口_Shell终端与命令行历史.html](%E8%AF%AD%E6%96%99/%E8%AE%A1%E7%AE%97%E6%9C%BA/06_%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E6%8E%A5%E5%8F%A3_Shell%E7%BB%88%E7%AB%AF%E4%B8%8E%E5%91%BD%E4%BB%A4%E8%A1%8C%E5%8E%86%E5%8F%B2.html) |
| 07 | 从需求到设计（一）：为什么项目要分阶段，设计文档又为什么不只有接口和组件 | [07_软件设计方法_从需求到设计为何分阶段.html](%E8%AF%AD%E6%96%99/%E8%AE%A1%E7%AE%97%E6%9C%BA/07_%E8%BD%AF%E4%BB%B6%E8%AE%BE%E8%AE%A1%E6%96%B9%E6%B3%95_%E4%BB%8E%E9%9C%80%E6%B1%82%E5%88%B0%E8%AE%BE%E8%AE%A1%E4%B8%BA%E4%BD%95%E5%88%86%E9%98%B6%E6%AE%B5.html) |
| 08 | 从需求到设计（二）：逐条拆解 D-01～D-06——六个技术实验究竟在验证什么 | [08_软件设计方法_逐条拆解技术实验D01至D06.html](%E8%AF%AD%E6%96%99/%E8%AE%A1%E7%AE%97%E6%9C%BA/08_%E8%BD%AF%E4%BB%B6%E8%AE%BE%E8%AE%A1%E6%96%B9%E6%B3%95_%E9%80%90%E6%9D%A1%E6%8B%86%E8%A7%A3%E6%8A%80%E6%9C%AF%E5%AE%9E%E9%AA%8CD01%E8%87%B3D06.html) |
| 09 | 从需求到设计（三）：事务、Outbox、幂等与最终一致性——一次发布怎样穿过所有故障 | [09_软件设计方法_事务Outbox幂等与最终一致性.html](%E8%AF%AD%E6%96%99/%E8%AE%A1%E7%AE%97%E6%9C%BA/09_%E8%BD%AF%E4%BB%B6%E8%AE%BE%E8%AE%A1%E6%96%B9%E6%B3%95_%E4%BA%8B%E5%8A%A1Outbox%E5%B9%82%E7%AD%89%E4%B8%8E%E6%9C%80%E7%BB%88%E4%B8%80%E8%87%B4%E6%80%A7.html) |
| 10 | 从需求到设计（四）：怎样审查 AI 生成的设计文档——从“看起来专业”到“可以稳定实现” | [10_软件设计方法_如何审查AI生成的设计文档.html](%E8%AF%AD%E6%96%99/%E8%AE%A1%E7%AE%97%E6%9C%BA/10_%E8%BD%AF%E4%BB%B6%E8%AE%BE%E8%AE%A1%E6%96%B9%E6%B3%95_%E5%A6%82%E4%BD%95%E5%AE%A1%E6%9F%A5AI%E7%94%9F%E6%88%90%E7%9A%84%E8%AE%BE%E8%AE%A1%E6%96%87%E6%A1%A3.html) |
| 11 | Docker 入门：从“把环境装进盒子”到真正理解容器如何运行 | [11_容器技术_Docker功能原理与两个微型项目.html](%E8%AF%AD%E6%96%99/%E8%AE%A1%E7%AE%97%E6%9C%BA/11_%E5%AE%B9%E5%99%A8%E6%8A%80%E6%9C%AF_Docker%E5%8A%9F%E8%83%BD%E5%8E%9F%E7%90%86%E4%B8%8E%E4%B8%A4%E4%B8%AA%E5%BE%AE%E5%9E%8B%E9%A1%B9%E7%9B%AE.html) |
| 12 | SSH：从第一次连接到密钥、隧道与独立排错 | [12_SSH_从第一次连接到密钥隧道与独立排错.html](%E8%AF%AD%E6%96%99/%E8%AE%A1%E7%AE%97%E6%9C%BA/12_SSH_%E4%BB%8E%E7%AC%AC%E4%B8%80%E6%AC%A1%E8%BF%9E%E6%8E%A5%E5%88%B0%E5%AF%86%E9%92%A5%E9%9A%A7%E9%81%93%E4%B8%8E%E7%8B%AC%E7%AB%8B%E6%8E%92%E9%94%99.html) |
| 13 | 远程操控计算机：从分时终端到 SSH 与远程桌面 | [13_远程操控计算机_从分时终端到SSH与远程桌面.html](%E8%AF%AD%E6%96%99/%E8%AE%A1%E7%AE%97%E6%9C%BA/13_%E8%BF%9C%E7%A8%8B%E6%93%8D%E6%8E%A7%E8%AE%A1%E7%AE%97%E6%9C%BA_%E4%BB%8E%E5%88%86%E6%97%B6%E7%BB%88%E7%AB%AF%E5%88%B0SSH%E4%B8%8E%E8%BF%9C%E7%A8%8B%E6%A1%8C%E9%9D%A2.html) |
| 14 | Windows 开发环境：与类 Unix 开发体验的结构差异 | [14_Windows开发环境_与类Unix开发体验的结构差异.html](%E8%AF%AD%E6%96%99/%E8%AE%A1%E7%AE%97%E6%9C%BA/14_Windows%E5%BC%80%E5%8F%91%E7%8E%AF%E5%A2%83_%E4%B8%8E%E7%B1%BBUnix%E5%BC%80%E5%8F%91%E4%BD%93%E9%AA%8C%E7%9A%84%E7%BB%93%E6%9E%84%E5%B7%AE%E5%BC%82.html) |
| 15 | Windows 开发环境：从 DOS 兼容到 NT 与 WSL 的历史成因 | [15_Windows开发环境_从DOS兼容到NT与WSL的历史成因.html](%E8%AF%AD%E6%96%99/%E8%AE%A1%E7%AE%97%E6%9C%BA/15_Windows%E5%BC%80%E5%8F%91%E7%8E%AF%E5%A2%83_%E4%BB%8EDOS%E5%85%BC%E5%AE%B9%E5%88%B0NT%E4%B8%8EWSL%E7%9A%84%E5%8E%86%E5%8F%B2%E6%88%90%E5%9B%A0.html) |
| 16 | Windows 开发环境：命令行与注册表的设计地图 | [16_Windows开发环境_命令行与注册表的设计地图.html](%E8%AF%AD%E6%96%99/%E8%AE%A1%E7%AE%97%E6%9C%BA/16_Windows%E5%BC%80%E5%8F%91%E7%8E%AF%E5%A2%83_%E5%91%BD%E4%BB%A4%E8%A1%8C%E4%B8%8E%E6%B3%A8%E5%86%8C%E8%A1%A8%E7%9A%84%E8%AE%BE%E8%AE%A1%E5%9C%B0%E5%9B%BE.html) |

### 语料/AI/　—　共 10 篇，下一篇编号 `11`

| 编号 | 标题 | 文件 |
| --- | --- | --- |
| 01 | 从数学对象到完整 GPT：技术依赖全景图 | [01_GPT技术依赖全景图_从数学对象到完整系统.html](%E8%AF%AD%E6%96%99/AI/01_GPT%E6%8A%80%E6%9C%AF%E4%BE%9D%E8%B5%96%E5%85%A8%E6%99%AF%E5%9B%BE_%E4%BB%8E%E6%95%B0%E5%AD%A6%E5%AF%B9%E8%B1%A1%E5%88%B0%E5%AE%8C%E6%95%B4%E7%B3%BB%E7%BB%9F.html) |
| 02 | 从“想法水库”到“可检索表达”：纯文字与大模型高效交流 | [02_人机交流_从想法水库到可检索表达.html](%E8%AF%AD%E6%96%99/AI/02_%E4%BA%BA%E6%9C%BA%E4%BA%A4%E6%B5%81_%E4%BB%8E%E6%83%B3%E6%B3%95%E6%B0%B4%E5%BA%93%E5%88%B0%E5%8F%AF%E6%A3%80%E7%B4%A2%E8%A1%A8%E8%BE%BE.html) |
| 03 | Skill 工程：从提示词拼接到分层 HTML 生成系统 | [03_Skill工程_从提示词拼接到分层生成系统.html](%E8%AF%AD%E6%96%99/AI/03_Skill%E5%B7%A5%E7%A8%8B_%E4%BB%8E%E6%8F%90%E7%A4%BA%E8%AF%8D%E6%8B%BC%E6%8E%A5%E5%88%B0%E5%88%86%E5%B1%82%E7%94%9F%E6%88%90%E7%B3%BB%E7%BB%9F.html) |
| 04 | 让 AI 照着文档做出完整项目：从项目想法到可执行规格 | [04_AI协作开发_从项目想法到可执行规格.html](%E8%AF%AD%E6%96%99/AI/04_AI%E5%8D%8F%E4%BD%9C%E5%BC%80%E5%8F%91_%E4%BB%8E%E9%A1%B9%E7%9B%AE%E6%83%B3%E6%B3%95%E5%88%B0%E5%8F%AF%E6%89%A7%E8%A1%8C%E8%A7%84%E6%A0%BC.html) |
| 05 | Codex 系统设计：一次任务究竟怎样跑起来 | [05_Codex系统设计_模型与Harness如何协同.html](%E8%AF%AD%E6%96%99/AI/05_Codex%E7%B3%BB%E7%BB%9F%E8%AE%BE%E8%AE%A1_%E6%A8%A1%E5%9E%8B%E4%B8%8EHarness%E5%A6%82%E4%BD%95%E5%8D%8F%E5%90%8C.html) |
| 06 | AI协作开发：从想法到经验证的产品问题 | [06_AI协作开发_02_从想法到经验证的产品问题.html](%E8%AF%AD%E6%96%99/AI/06_AI%E5%8D%8F%E4%BD%9C%E5%BC%80%E5%8F%91_02_%E4%BB%8E%E6%83%B3%E6%B3%95%E5%88%B0%E7%BB%8F%E9%AA%8C%E8%AF%81%E7%9A%84%E4%BA%A7%E5%93%81%E9%97%AE%E9%A2%98.html) |
| 07 | AI协作开发：从需求到可执行规格与设计 | [07_AI协作开发_03_从需求到可执行规格与设计.html](%E8%AF%AD%E6%96%99/AI/07_AI%E5%8D%8F%E4%BD%9C%E5%BC%80%E5%8F%91_03_%E4%BB%8E%E9%9C%80%E6%B1%82%E5%88%B0%E5%8F%AF%E6%89%A7%E8%A1%8C%E8%A7%84%E6%A0%BC%E4%B8%8E%E8%AE%BE%E8%AE%A1.html) |
| 08 | AI协作开发：模型路由与低成本实施 | [08_AI协作开发_04_模型路由与低成本实施.html](%E8%AF%AD%E6%96%99/AI/08_AI%E5%8D%8F%E4%BD%9C%E5%BC%80%E5%8F%91_04_%E6%A8%A1%E5%9E%8B%E8%B7%AF%E7%94%B1%E4%B8%8E%E4%BD%8E%E6%88%90%E6%9C%AC%E5%AE%9E%E6%96%BD.html) |
| 09 | AI协作开发：验证、发布、上线与回滚 | [09_AI协作开发_05_验证发布上线与回滚.html](%E8%AF%AD%E6%96%99/AI/09_AI%E5%8D%8F%E4%BD%9C%E5%BC%80%E5%8F%91_05_%E9%AA%8C%E8%AF%81%E5%8F%91%E5%B8%83%E4%B8%8A%E7%BA%BF%E4%B8%8E%E5%9B%9E%E6%BB%9A.html) |
| 10 | AI协作开发：项目规模化后的治理系统 | [10_AI协作开发_06_项目规模化后的治理系统.html](%E8%AF%AD%E6%96%99/AI/10_AI%E5%8D%8F%E4%BD%9C%E5%BC%80%E5%8F%91_06_%E9%A1%B9%E7%9B%AE%E8%A7%84%E6%A8%A1%E5%8C%96%E5%90%8E%E7%9A%84%E6%B2%BB%E7%90%86%E7%B3%BB%E7%BB%9F.html) |

### 语料/马列/　—　共 8 篇，下一篇编号 `09`

| 编号 | 标题 | 文件 |
| --- | --- | --- |
| 01 | 马克思主义思想史（一）：从理论来源到主要分流 | [01_马克思主义思想史_从理论来源到主要分流.html](%E8%AF%AD%E6%96%99/%E9%A9%AC%E5%88%97/01_%E9%A9%AC%E5%85%8B%E6%80%9D%E4%B8%BB%E4%B9%89%E6%80%9D%E6%83%B3%E5%8F%B2_%E4%BB%8E%E7%90%86%E8%AE%BA%E6%9D%A5%E6%BA%90%E5%88%B0%E4%B8%BB%E8%A6%81%E5%88%86%E6%B5%81.html) |
| 02 | 马克思主义思想史（二）：马克思与恩格斯怎样把批判连接成理论 | [02_马克思主义思想史_马克思恩格斯的理论骨架.html](%E8%AF%AD%E6%96%99/%E9%A9%AC%E5%88%97/02_%E9%A9%AC%E5%85%8B%E6%80%9D%E4%B8%BB%E4%B9%89%E6%80%9D%E6%83%B3%E5%8F%B2_%E9%A9%AC%E5%85%8B%E6%80%9D%E6%81%A9%E6%A0%BC%E6%96%AF%E7%9A%84%E7%90%86%E8%AE%BA%E9%AA%A8%E6%9E%B6.html) |
| 03 | 马克思主义思想史（三）：资本主义为何能在自由交换中持续产生阶级支配 | [03_马克思主义思想史_资本论的论证链.html](%E8%AF%AD%E6%96%99/%E9%A9%AC%E5%88%97/03_%E9%A9%AC%E5%85%8B%E6%80%9D%E4%B8%BB%E4%B9%89%E6%80%9D%E6%83%B3%E5%8F%B2_%E8%B5%84%E6%9C%AC%E8%AE%BA%E7%9A%84%E8%AE%BA%E8%AF%81%E9%93%BE.html) |
| 04 | 马克思主义思想史（四）：工人政党壮大后，改革通向社会主义还是稳定资本主义 | [04_马克思主义思想史_第二国际改革与革命之争.html](%E8%AF%AD%E6%96%99/%E9%A9%AC%E5%88%97/04_%E9%A9%AC%E5%85%8B%E6%80%9D%E4%B8%BB%E4%B9%89%E6%80%9D%E6%83%B3%E5%8F%B2_%E7%AC%AC%E4%BA%8C%E5%9B%BD%E9%99%85%E6%94%B9%E9%9D%A9%E4%B8%8E%E9%9D%A9%E5%91%BD%E4%B9%8B%E4%BA%89.html) |
| 05 | 马克思主义思想史（五）：俄国革命为何成功，又为何形成高度集中的党国结构 | [05_马克思主义思想史_俄国革命与苏联党国结构.html](%E8%AF%AD%E6%96%99/%E9%A9%AC%E5%88%97/05_%E9%A9%AC%E5%85%8B%E6%80%9D%E4%B8%BB%E4%B9%89%E6%80%9D%E6%83%B3%E5%8F%B2_%E4%BF%84%E5%9B%BD%E9%9D%A9%E5%91%BD%E4%B8%8E%E8%8B%8F%E8%81%94%E5%85%9A%E5%9B%BD%E7%BB%93%E6%9E%84.html) |
| 06 | 马克思主义思想史（六）：马克思主义进入农业中国后改变了什么，又付出了什么代价 | [06_马克思主义思想史_中国革命与毛泽东思想.html](%E8%AF%AD%E6%96%99/%E9%A9%AC%E5%88%97/06_%E9%A9%AC%E5%85%8B%E6%80%9D%E4%B8%BB%E4%B9%89%E6%80%9D%E6%83%B3%E5%8F%B2_%E4%B8%AD%E5%9B%BD%E9%9D%A9%E5%91%BD%E4%B8%8E%E6%AF%9B%E6%B3%BD%E4%B8%9C%E6%80%9D%E6%83%B3.html) |
| 07 | 马克思主义思想史（七）：为什么阶级政治没有按经典预期发展，今天还缺哪些维度 | [07_马克思主义思想史_西方扩展与现实分析框架.html](%E8%AF%AD%E6%96%99/%E9%A9%AC%E5%88%97/07_%E9%A9%AC%E5%85%8B%E6%80%9D%E4%B8%BB%E4%B9%89%E6%80%9D%E6%83%B3%E5%8F%B2_%E8%A5%BF%E6%96%B9%E6%89%A9%E5%B1%95%E4%B8%8E%E7%8E%B0%E5%AE%9E%E5%88%86%E6%9E%90%E6%A1%86%E6%9E%B6.html) |
| 08 | 资本为何既需要人，又会耗损人：社会再生产理论的现代化框架 | [08_社会再生产理论现代化_资本为何既需要人又会耗损人.html](%E8%AF%AD%E6%96%99/%E9%A9%AC%E5%88%97/08_%E7%A4%BE%E4%BC%9A%E5%86%8D%E7%94%9F%E4%BA%A7%E7%90%86%E8%AE%BA%E7%8E%B0%E4%BB%A3%E5%8C%96_%E8%B5%84%E6%9C%AC%E4%B8%BA%E4%BD%95%E6%97%A2%E9%9C%80%E8%A6%81%E4%BA%BA%E5%8F%88%E4%BC%9A%E8%80%97%E6%8D%9F%E4%BA%BA.html) |

### 语料/其他/　—　共 0 篇，下一篇编号 `01`

_（暂无文章）_

<!-- INDEX:END -->
