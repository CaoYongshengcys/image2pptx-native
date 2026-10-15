# AI 一键生成可编辑 PPT 的终极方案——从图片还原到论文汇报，三个开源 Skill 全覆盖

> 把一张技术流程图截图丢给 AI，几分钟后拿到一个**所有文字可编辑、所有图形可编辑、0 张位图**的 PPTX。把一篇 PDF 论文丢给 AI，自动生成 15 页学术汇报 PPT，图表还是原生 PowerPoint 图表。把一份 CSV 数据丢给 AI，自动生成带折线图柱状图的数据报告 PPT。
>
> 这一切都基于 OpenAI Codex CLI + `@oai/artifact-tool`，在本地 Windows 上运行，不需要 ChatGPT Plus 订阅（可以用任意第三方 API）。

## 项目地址

| 仓库 | 定位 | 链接 |
|------|------|------|
| **ai-pptx-generator** |  通用入口（4种模式全覆盖） | [GitHub](https://github.com/CaoYongshengcys/ai-pptx-generator) |
| **image2pptx-artifact** | 📸 图片→PPT（最高质量） | [GitHub](https://github.com/CaoYongshengcys/image2pptx-artifact) |
| **image2pptx-native** | 🔧 图片→PPT（离线降级） | [GitHub](https://github.com/CaoYongshengcys/image2pptx-native) |

## 背景：为什么需要这套工具？

科研汇报、项目答辩、学术交流中，我们经常遇到这些场景：

- 手头有一张精美的技术路线图（PNG），想放进 PPT 里**改几个字**
- 一篇刚发表的论文需要做**组会汇报 PPT**，手动做太耗时
- 实验数据在 CSV 里，需要快速生成**带图表的数据报告**
- 领导说"帮我做一个关于 XX 的 PPT"，从零开始太痛苦

传统方案的痛点：

| 方案 | 问题 |
|------|------|
| 手动在 PPT 里重画 | 复杂流程图要画半天 |
| OCR + 手动排版 | 图形/箭头/图标全部丢失 |
| python-pptx 硬编码 | 代码冗长，没有系统化工作流 |
| Gamma / Beautiful.ai | 云端服务，数据隐私风险，中文支持差 |
| ChatGPT Plus + Codex Web | $20/月，且 artifact-tool 是私有包无法本地复用 |

我需要的方案是：**AI 看懂内容 → 自动生成原生 PPT 元素 → 输出完全可编辑的 PPTX**，而且要在本地运行、用我自己的 API Key。

## 整体架构

```
用户输入（图片/PDF/CSV/文字）
    │
    ▼
┌─── ai-pptx-generator (DSH/Codex/Claude Code Skill) ───┐
│                                                         │
│  自动识别输入类型 → 选择模式 → 构建提示词               │
│       │                                                 │
│       ▼                                                 │
│  codex exec --enable artifact "提示词"                  │
│       │                                                 │
│       ▼                                                 │
│  ┌─────────────────────────────────────────────┐       │
│  │  Codex CLI + @oai/artifact-tool              │       │
│  │                                               │       │
│  │  LLM 分析内容 → 编写 JS 构建脚本             │       │
│  │       ↓                                       │       │
│  │  artifact-tool API:                           │       │
│  │  • slide.shapes.add()     形状/文本框         │       │
│  │  • slide.charts.add()     原生图表 ⭐         │       │
│  │  • slide.tables.add()     原生表格            │       │
│  │  • presentation.theme     主题配色            │       │
│  │  • skia-canvas            精确字体度量        │       │
│  │       ↓                                       │       │
│  │  渲染预览 → 比对修正（≤3轮）→ 导出 PPTX      │       │
│  └─────────────────────────────────────────────┘       │
│       │                                                 │
│       ▼                                                 │
│  验证输出 → 交付                                        │
│                                                         │
│  失败? → 降级到 image2pptx-native (纯 python-pptx)     │
└─────────────────────────────────────────────────────────┘
```

## 四种模式详解

### 模式 A：图片→PPT（像素级还原）

**输入**：一张 PNG/JPG 技术流程图
**输出**：全矢量可编辑 PPTX，250+ 原生元素，0 张位图

<table>
<tr><td width="50%"><b>源图</b></td><td width="50%"><b>生成的 PPTX 渲染</b></td></tr>
<tr>
<td><img src="https://raw.githubusercontent.com/CaoYongshengcys/image2pptx-native/main/examples/tech_flowchart_1/original_inputs/source.png" width="100%"/></td>
<td><img src="https://raw.githubusercontent.com/CaoYongshengcys/image2pptx-native/main/examples/tech_flowchart_1/diagnostics/render.png" width="100%"/></td>
</tr>
</table>

**工作原理**：
1. LLM 用视觉能力分析图片，识别每个元素的位置、大小、颜色、文字
2. 编写 JavaScript 构建脚本，用 artifact-tool API 逐个创建形状和文本框
3. 图标用 MSO 原生形状程序化绘制（CAN=数据库、GEAR_9=齿轮、freeform=盾牌/漏斗/王冠）
4. skia-canvas 渲染 PNG 预览，与原图裁剪比对，迭代修正（最多 3 轮）

**关键数据**：
- 225-250 个原生 PPT 元素
- 52+ 个可编辑文本框
- 0 张位图
- 文件大小 ~38KB

### 模式 B：论文→学术汇报 PPT

**输入**：一篇 PDF 论文
**输出**：10-15 页学术风格 PPT，含原生图表

**工作原理**：
1. 用 `pypdf` 提取论文全文
2. LLM 分析论文结构：标题、摘要、引言、方法、实验、结论
3. 自动规划 PPT 大纲（封面→背景→方法→实验→结论）
4. 实验数据用 `slide.charts.add("bar")` 生成**原生 PowerPoint 柱状图**（可在 PPT 中直接双击编辑数据！）
5. 公式用文本框排版，上下标用不同字号模拟

**提示词核心**：
```
请基于这篇论文生成学术汇报 PPTX（约 12 页）：
- 封面页：标题、作者、单位
- 研究背景（1-2页）
- 方法概述（2-3页）：框架图、关键公式
- 实验结果（2-3页）：原生图表展示数据
- 结论与展望（1页）
- 风格：白底 + 深蓝 #1E3A5F + 微软雅黑
- 图表必须用 slide.charts.add() 原生对象
```

### 模式 C：数据→图表 PPT

**输入**：CSV / Excel / JSON 数据文件
**输出**：8-12 页数据可视化 PPT，所有图表均为原生 PowerPoint 图表

**这是最强大的模式**——因为 artifact-tool 支持完整的原生图表 API：

```javascript
// 折线图
const chart = slide.charts.add("line");
chart.title = "月度趋势";
chart.categories = ["1月", "2月", "3月", "4月"];
const series = chart.series.add("营收");
series.values = [120, 140, 180, 210];
chart.lineOptions.grouping = "standard";  // 必须设置！

// 柱状图
const bar = slide.charts.add("bar");
bar.barOptions.direction = "column";
bar.barOptions.grouping = "stacked";

// 饼图
const pie = slide.charts.add("pie");

// 散点图
const scatter = slide.charts.add("scatter");
```

生成的图表在 PowerPoint 中**可以直接双击编辑数据**，跟手动插入的图表完全一样。

### 模式 D：文字/大纲→多页精美 PPT

**输入**：一段文字描述或大纲
**输出**：N 页精美演示文稿，自动设计版式配色

**内置 8 种风格**：

| 场景 | 主色 | 辅色 |
|------|------|------|
| 学术汇报 | `#1E3A5F` 深蓝 | `#E8EEF4` 浅蓝灰 |
| 商务提案 | `#0D47A1` 商务蓝 | `#E3F2FD` 天蓝 |
| 产品介绍 | `#4A148C` 科技紫 | `#F3E5F5` 浅紫 |
| 年终总结 | `#B71C1C` 稳重红 | `#FFF8E1` 暖金 |
| 教学课件 | `#1B5E20` 清新绿 | `#E8F5E9` 浅绿 |
| 项目复盘 | `#37474F` 专业灰 | `#ECEFF1` 浅灰 |
| 融资路演 | `#212121` 高端黑 | `#FFD700` 金色 |
| 团队分享 | `#E65100` 活力橙 | `#FFF3E0` 浅橙 |

## 环境搭建（完整踩坑记录）

### Step 1: 安装 Codex CLI

```powershell
npm install -g @openai/codex --registry https://registry.npmmirror.com
codex --version  # 预期: codex-cli 0.162.1
```

### Step 2: 配置 `~/.codex/config.toml`

```toml
model = "qwen3.8-max"                    # 需要支持视觉的多模态模型
model_provider = "aliyun"
approval_policy = "never"                 # 自动执行
# approvals_reviewer = "auto_review"      # ← 必须注释掉！

[features]
artifact = true                           # ← 关键！默认关闭

[windows]
sandbox = "elevated"

[model_providers.aliyun]
base_url = "https://your-endpoint/compatible-mode/v1"
name = "Aliyun Qwen"
wire_api = "responses"
requires_openai_auth = false

[model_providers.aliyun.auth]
command = "cmd"
args = ["/d", "/c", "echo", "sk-your-key"]
```

### Step 3: 安装 Skill

```powershell
git clone https://github.com/CaoYongshengcys/ai-pptx-generator.git ~/.agents/skills/ai-pptx-generator
```

### Step 4: 验证

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check_env.ps1
```

```
[1/5] Checking Codex CLI ........... OK (v0.162.1)
[2/5] Checking artifact-tool ....... OK (v2.6.9)
[3/5] Checking artifact feature .... OK (enabled)
[4/5] Checking API provider ........ OK (provider: aliyun)
[5/5] Checking approval policy ..... OK (never)
ALL CHECKS PASSED ✅
```

## 踩坑记录

### 坑1: `Model not found: codex-auto-review`

`approvals_reviewer = "auto_review"` 配置了一个不存在的审核模型。**必须注释掉这一行**。

### 坑2: `sandbox: read-only` 写入失败

Codex 默认沙箱禁止写文件。解决方案：命令行加 `--dangerously-bypass-approvals-and-sandbox`。

### 坑3: `sandbox_permissions` 参数被忽略

新版 Codex 中 `-c 'sandbox_permissions=["danger-full-access"]'` 已失效。只能用 `--dangerously-bypass-approvals-and-sandbox`。

### 坑4: artifact-tool 运行时未下载

首次使用 artifact 功能时，运行时还未下载。运行一次 `codex exec "hello"` 触发初始化。运行时位置：
```
~/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/
```

### 坑5: npm install TLS 超时

用国内镜像：`--registry https://registry.npmmirror.com`

### 坑6: `@oai/artifact-tool` 在 npm 公共 registry 上 404

这是 OpenAI 的**私有包**，只能通过 Codex 运行时自动获取，无法单独安装。

## artifact-tool vs python-pptx 质量对比

我用同一张技术流程图分别用两种方案生成 PPTX：

| 维度 | artifact-tool | python-pptx native |
|------|--------------|-------------------|
| 元素数量 | 250 | 203 |
| 文件大小 | 38,798 bytes | 37,037 bytes |
| 字体度量 | skia-canvas 精确计算 | 手动估算 |
| 图标细节 | 更丰富（额外线条/点/弧线） | 简化近似 |
| 文字换行 | 自动适配（autofit） | 需手动调整文本框宽度 |
| 迭代修正 | AI 自主 3 轮裁剪放大比对 | 人工 2 轮目视比对 |
| 原生图表 | ✅ `slide.charts.add()` | ❌ 不支持 |
| 主题/样式 | ✅ 完整主题系统 | ⚠️ 有限支持 |
| 耗时 | 3-15 分钟 | 1-3 分钟 |
| 离线可用 | ❌ | ✅ |
| 费用 | API 调用费 | 免费 |

**结论**：artifact-tool 在细节精度上明显更好（多 47 个元素，主要是图标内部的额外线条），但 python-pptx 方案在 90% 的还原度下实现了完全离线、秒级重建的优势。两者互补使用最佳。

## 作为 AI Agent Skill 使用

这三个项目都是 **AI Agent Skill**——不是独立的命令行工具，而是给 AI 编码助手（DSH、Codex CLI、Claude Code）使用的指令集。

安装后，对 AI 说：

| 你说 | AI 自动执行 |
|------|-----------|
| "把这张图转成可编辑PPT" | 模式 A：图片→PPT |
| "把这篇论文做成汇报PPT" | 模式 B：论文→PPT |
| "把这份数据做成PPT报告" | 模式 C：数据→PPT |
| "帮我做一个关于碳中和的PPT" | 模式 D：文字→PPT |

AI 会自动加载 skill、检查环境、构建提示词、调用 Codex、验证输出、交付文件。整个过程全自动。

## 总结

| 维度 | 说明 |
|------|------|
| **输入** | 图片 / PDF 论文 / CSV 数据 / 文字大纲 |
| **输出** | 全矢量可编辑 PPTX（原生形状 + 原生图表 + 原生表格） |
| **引擎** | Codex CLI + @oai/artifact-tool（skia-canvas 字体度量） |
| **降级** | 纯 python-pptx 离线方案 |
| **运行** | 本地 Windows，任意第三方 API |
| **费用** | API 调用费（可用阿里云等廉价代理） |
| **Skill** | DSH / Codex CLI / Claude Code 全局可用 |
| **开源** | MIT License，三个 GitHub 仓库 |

核心思路：**让 AI 理解内容，用 artifact-tool 的专业 API 生成原生 PPT 元素，而不是用 python-pptx 手动拼凑坐标**。artifact-tool 的 skia-canvas 字体度量引擎和原生图表 API 是质量的关键差异点。而把它封装成 AI Agent Skill，则让这一切变成了一句话的事。
