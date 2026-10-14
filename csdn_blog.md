# 图片一键转全矢量可编辑PPT——纯Python实现，零依赖，离线可用

> 把一张技术流程图截图丢给AI，3分钟后拿到一个**所有文字可编辑、所有图形可编辑、0张位图**的PPTX文件。不需要LibreOffice，不需要云端API，不需要任何私有包——只需要一个 `pip install python-pptx`。

## 背景：为什么需要这个工具？

科研汇报、项目答辩、学术交流中，我们经常遇到这样的场景：

- 手头有一张精美的技术路线图/流程图（PNG/JPG），想放进PPT里**修改几个字**
- 别人的PPT截图很好看，想**复用版式**但找不到源文件
- AI生成的PPT图片很精美，但**文字不可编辑**，改一个字都要重新生成

传统方案的痛点：

| 方案 | 问题 |
|------|------|
| 手动在PPT里重画 | 耗时巨大，复杂流程图可能要画半天 |
| OCR + 手动排版 | 文字识别还行，但图形/箭头/图标全部丢失 |
| python-pptx 硬编码坐标 | 代码冗长，没有系统化的工作流 |
| OpenAI Codex artifact-tool | **私有包**，只能在Codex Cloud沙箱里用，本地装不了 |
| LibreOffice 转换 | 丢失格式，文字变成图片 |

我需要的方案是：**AI看懂图片版式 → 自动生成原生PPT形状和文本框 → 输出完全可编辑的PPTX**。

## 效果展示

### 示例1：稳定边界主导特征参量辨识技术

<table>
<tr>
<td width="50%"><b>源图（PNG截图）</b></td>
<td width="50%"><b>生成的可编辑PPTX渲染</b></td>
</tr>
<tr>
<td><img src="https://raw.githubusercontent.com/CaoYongshengcys/image2pptx-native/main/examples/tech_flowchart_1/original_inputs/source.png" width="100%"/></td>
<td><img src="https://raw.githubusercontent.com/CaoYongshengcys/image2pptx-native/main/examples/tech_flowchart_1/diagnostics/render.png" width="100%"/></td>
</tr>
</table>

**统计：225个原生元素 = 108个形状 + 52条连接线 + 12个自由形状 + 52个文本框 + 1个背景，0张位图。**

### 示例2：快速推理估测建模方法

<table>
<tr>
<td width="50%"><b>源图（PNG截图）</b></td>
<td width="50%"><b>生成的可编辑PPTX渲染</b></td>
</tr>
<tr>
<td><img src="https://raw.githubusercontent.com/CaoYongshengcys/image2pptx-native/main/examples/tech_flowchart_2/original_inputs/source.png" width="100%"/></td>
<td><img src="https://raw.githubusercontent.com/CaoYongshengcys/image2pptx-native/main/examples/tech_flowchart_2/diagnostics/render.png" width="100%"/></td>
</tr>
</table>

**统计：203个原生元素 = 105个形状 + 39条连接线 + 15个自由形状 + 43个文本框 + 1个背景，0张位图。**

在PowerPoint中打开后，每一个文字都可以直接点击编辑，每一个图标都可以选中、改色、移动、缩放。

## 核心原理

整个工作流分四步：

```
源图片 ──→ AI视觉分析 ──→ gen_manifest.py ──→ manifest.json ──→ build_pptx.py ──→ output.pptx
                                                                    ↓
                                                          PowerPoint COM 渲染验证
```

### Step 1: AI观察源图

用AI的多模态能力（GPT-4V、Qwen-VL等）观察源图，识别出：
- 画布尺寸和比例
- 每个元素的位置（像素坐标）、大小、颜色
- 文字内容、字号、粗细、对齐方式
- 图标类型（数据库、齿轮、箭头、漏斗等）

### Step 2: 编写设计脚本 gen_manifest.py

这是核心步骤。用一组 helper 函数描述每个元素：

```python
# 基础原语
shape("ROUNDED_RECTANGLE", x, y, w, h, fill="E4EFF9", stroke="5B9BD5")  # 圆角矩形
text(x, y, w, h, "标题文字", size=13, bold=True, align="center")          # 文本框
line(x1, y1, x2, y2, stroke="333333", stroke_w=2)                       # 连接线
freeform([(0,0),(1,0),(0.5,1)], x, y, w, h, fill="E03C31")              # 自由形状（三角形）

# 内置图标库（20+种）
icon_db(x, y, w, h)           # 数据库圆柱
icon_gear(x, y, w, h)         # 齿轮
icon_funnel(x, y, w, h)       # 漏斗
icon_shield(x, y, w, h)       # 盾牌+闪电
icon_network(x, y, w, h)      # 网络节点图
icon_bars(x, y, w, h)         # 柱状图
down_arrow(x, y)              # 橙色下箭头
```

所有坐标使用 **1920×1080 像素画布**，构建器自动映射到 13.333×7.5 英寸的标准16:9幻灯片。

### Step 3: 构建PPTX

```bash
python gen_manifest.py          # 生成 manifest.json
python build_pptx.py --manifest manifest.json --output output.pptx
```

`build_pptx.py` 是一个 **216行的通用构建器**，支持：
- 任意 MSO 自动形状（矩形、圆角矩形、椭圆、圆柱、齿轮、大括号、箭头、云形、闪电等）
- 旋转、填充透明度、圆角调整
- 自由形状（多边形/折线，用于盾牌、漏斗、王冠、曲线等）
- 多段落文本框（不同行可以有不同字号、颜色、粗细）
- 中西文字体统一设置（latin + ea + cs 三个 typeface 同时设置）

### Step 4: 渲染验证（可选）

如果本地装了PowerPoint，可以用COM接口导出PNG预览：

```powershell
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open("output.pptx", $true, $false, $false)
$pres.Slides.Item(1).Export("preview.png", "PNG", 1920, 1080)
$pres.Close(); $app.Quit()
```

然后对比源图和渲染图，修正 gen_manifest.py 中的坐标/颜色/文字，重新构建。通常 **2-3轮迭代** 就能达到很高的还原度。

## 与 OpenAI artifact-tool 的对比

这个项目的灵感来源于 OpenAI Codex 的 `@oai/artifact-tool` Presentation API。我在实际使用中发现：

| | image2pptx-native（本项目） | @oai/artifact-tool |
|---|---|---|
| **依赖** | `pip install python-pptx` | `@oai/artifact-tool`（npm私有包） |
| **安装** | ✅ 一行命令 | ❌ npm registry 404，无法公开安装 |
| **运行环境** | 本地任意机器 | 仅 Codex Cloud 沙箱 |
| **网络需求** | 无 | 需要 OpenAI API + ChatGPT Plus/Pro |
| **费用** | 免费 | $20/月 ChatGPT Plus 起 |
| **图标** | 原生形状程序化绘制 | 同 |
| **文字** | 原生文本框 | 同 |
| **位图** | 0 张 | 0 张 |
| **渲染验证** | PowerPoint COM | 内置 skia-canvas |
| **离线使用** | ✅ | ❌ |
| **输出质量** | 字节级一致（已验证） | — |

实际上，我用 Codex CLI + artifact-tool 生成了第一张图，然后用本项目的纯 python-pptx 方案重新生成，**两个文件大小完全相同（37,998 bytes），形状数量完全相同（224个），文本框数量完全相同（52个）**。

这说明 python-pptx 完全可以达到 artifact-tool 的效果，而且不需要任何私有依赖。

## 作为 AI Agent Skill 使用

这个项目最大的价值不只是工具本身，而是它可以作为 **AI编码助手的 Skill** 使用。

### 什么是 Skill？

Skill 是一份结构化的指令文件（SKILL.md），告诉AI助手"当用户需要做X时，按照这个流程执行"。DSH、Codex CLI、Claude Code 等AI编码助手都支持 Skill 机制。

### 安装

```bash
# DSH (DeepSeek Harness)
git clone https://github.com/CaoYongshengcys/image2pptx-native.git ~/.agents/skills/image2pptx-native

# Codex CLI
git clone https://github.com/CaoYongshengcys/image2pptx-native.git ~/.codex/skills/image2pptx-native

# Claude Code
git clone https://github.com/CaoYongshengcys/image2pptx-native.git ~/.claude/skills/image2pptx-native
```

### 使用

安装后，对AI说：

> **"把这张图片转成可编辑PPT"**

AI会自动：
1. 加载 `image2pptx-native` skill
2. 用视觉能力分析图片版式
3. 编写 `gen_manifest.py` 设计脚本
4. 运行 `build_pptx.py` 生成PPTX
5. 用PowerPoint COM渲染验证
6. 迭代修正直到满意
7. 交付最终文件

整个过程 **全自动**，用户只需要提供一张图片和一句话。

## 内置图标库

所有图标都是用 MSO 原生形状 + 连接线 + 自由形状程序化绘制的，**完全可编辑**（改色、改大小、移动）：

| 图标 | 函数 | 实现方式 |
|------|------|----------|
| 数据库 | `icon_db()` | CAN形状 + 白色横线 |
| 文档 | `icon_doc()` | 圆角矩形 + 横线 |
| 监视器 | `icon_monitor()` | 矩形 + 底座 + 内部柱状图/波形 |
| 柱状图 | `icon_bars()` | N个递增高度的矩形 |
| 网络节点 | `icon_network()` | 圆形节点 + 连接线 |
| 脑/AI | `icon_brain()` | CLOUD形状轮廓 |
| 书本 | `icon_book()` | 两个自由形状四边形 + 内页线 |
| 风力发电机 | `icon_turbine()` | 3个旋转椭圆叶片 + 杆 + 轮毂 |
| 盾牌 | `icon_shield()` | 自由形状六边形 + LIGHTNING_BOLT |
| 王冠 | `icon_crown()` | 自由形状锯齿多边形 |
| 漏斗 | `icon_funnel()` | 自由形状梯形+管 |
| 齿轮 | `icon_gear()` | GEAR_9 预设形状 |
| 折线图 | `icon_linechart()` | 坐标轴 + 自由形状曲线 |
| 清单 | `icon_checklist()` | 圆角矩形 + 勾号 + 横线 |
| Venn图 | `icon_venn3()` / `icon_venn2()` | 半透明重叠椭圆 |
| 计算器 | `icon_calculator()` | 矩形 + 屏幕 + 按钮网格 |
| 速度表 | `icon_speedometer()` | BLOCK_ARC + 指针线 |
| 靶心 | `icon_target()` | 同心圆 |
| 盾牌勾 | `icon_shield_check()` | 自由形状盾牌 + 勾号 |
| 循环数据库 | `icon_cycle_db()` | CAN + BLOCK_ARC循环箭头 |
| 散点图 | `icon_scatter()` | 坐标轴 + 随机散点 + 趋势线 |
| 决策菱形 | `icon_decision()` | DIAMOND + 彩色小方块 |
| 分布曲线 | `icon_dist_curve()` | 钟形曲线 + Qα标注线 |
| Huber损失 | `icon_huber()` | 二次→线性曲线 |
| 单调柱状 | `icon_mono_bars()` | 5个递增柱 |
| 梯度曲线 | `icon_grad_curve()` | 双曲线 + ∂f/∂x分数 |

要添加新图标？只需组合 `shape()` + `line()` + `freeform()` 三个原语，几行代码就能画出任意图标。

## 技术细节

### 坐标系映射

```python
class Scale:
    def __init__(self, canvas_w=1920, canvas_h=1080, slide_w_in=13.333, slide_h_in=7.5):
        self.sx = slide_w_in / canvas_w  # 0.00694 in/px
        self.sy = slide_h_in / canvas_h  # 0.00694 in/px
    
    def x(self, v): return Inches(v * self.sx)
    def y(self, v): return Inches(v * self.sy)
```

设计时用直觉的像素坐标（1920×1080），构建器自动转换为 PowerPoint 的 EMU 单位。

### 字体设置

中文PPT最容易踩的坑是字体只显示西文不显示中文。解决方案是同时设置三个 typeface：

```python
def set_typeface(run, name="Microsoft YaHei"):
    run.font.name = name
    rPr = run._r.get_or_add_rPr()
    for tag in ("a:latin", "a:ea", "a:cs"):
        node = rPr.find(qn(tag))
        if node is None:
            node = rPr.makeelement(qn(tag), {})
            rPr.append(node)
        node.set("typeface", name)
```

### 填充透明度

Venn图等需要半透明叠加效果，通过直接操作 XML 实现：

```python
def set_fill_alpha(shape, alpha_pct):
    srgb = shape.fill.fore_color._xFill.find(qn("a:srgbClr"))
    alpha = srgb.makeelement(qn("a:alpha"), {"val": str(int(alpha_pct * 1000))})
    srgb.append(alpha)
```

## 项目地址

**GitHub**: [https://github.com/CaoYongshengcys/image2pptx-native](https://github.com/CaoYongshengcys/image2pptx-native)

```bash
git clone https://github.com/CaoYongshengcys/image2pptx-native.git
pip install python-pptx
cd image2pptx-native/examples/tech_flowchart_2
python gen_manifest.py
python ../../scripts/build_pptx.py --manifest manifest.json --output output.pptx
```

## 总结

| 维度 | 说明 |
|------|------|
| **输入** | 任意 PNG/JPG 技术流程图截图 |
| **输出** | 全矢量可编辑 PPTX（0张位图） |
| **依赖** | 仅 `python-pptx`（pip install） |
| **运行** | 本地离线，无需网络 |
| **AI集成** | 可作为 DSH/Codex/Claude Code 的 Skill |
| **扩展性** | 20+ 内置图标，可自定义新图标 |
| **验证** | 与 artifact-tool 输出字节级一致 |

核心思路很简单：**让AI看懂图片，用代码描述版式，用 python-pptx 生成原生PPT元素**。不需要任何黑盒工具，不需要云端API，不需要私有包。一个216行的通用构建器 + 一份设计脚本 = 一张完全可编辑的技术流程图PPT。
