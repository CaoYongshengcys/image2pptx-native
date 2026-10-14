---
name: image2pptx-native
description: >
  将图片/截图/PPT页面截图转换为全矢量可编辑PPTX。纯 python-pptx 实现，
  不依赖 @oai/artifact-tool、Codex Cloud 或任何外部服务。
  所有文字为原生文本框，所有图形为原生PPT形状/自由形状，0张位图。
  当用户需要 image2ppt、图片转PPT、截图转可编辑幻灯片、把设计图拆成
  可编辑元素时使用此 skill。
---

# Image2PPTX Native — 图片→全矢量可编辑 PPTX

纯 `python-pptx` 实现，**零外部依赖**（不需要 `@oai/artifact-tool`、Codex Cloud、LibreOffice）。

## 核心原理

```
源图片 → AI视觉分析版式 → gen_manifest.py(设计脚本) → manifest.json → build_pptx.py → output.pptx
                                                                    ↓
                                                          PowerPoint COM 渲染验证
```

1. **AI 观察源图**：识别标题、栏头、文本框、图标、箭头、颜色、坐标
2. **编写 gen_manifest.py**：用 helper 函数（shape/text/line/freeform/icon_*）描述每个元素
3. **生成 manifest.json**：中间格式，像素坐标，跨项目复用
4. **build_pptx.py 构建**：读取 manifest → 生成原生 PPTX（任意 MSO 形状、旋转、透明度、自由形状、多段落文本）
5. **PowerPoint COM 渲染验证**：导出 PNG 目视比对，迭代修正

## 文件结构

```
image2pptx-native/
├── SKILL.md                          ← 本文件
├── scripts/
│   ├── build_pptx.py                 ← 通用 manifest→PPTX 构建器（不要修改）
│   └── gen_manifest_example.py       ← 示例设计脚本（技术流程图）
└── projects/
    └── YYYYMMDD_slug/                ← 每次转换的独立项目记录
        ├── original_inputs/          ← 源图副本
        ├── diagnostics/              ← 渲染预览 PNG
        ├── gen_manifest.py           ← 本项目的设计脚本
        ├── manifest.json             ← 中间格式
        ├── output.pptx               ← 最终输出
        ├── summary.json              ← 构建统计
        └── process_notes.md          ← 过程记录
```

## 工作流

### Step 1: 初始化项目

```powershell
$proj = "C:/Users/$env:USERNAME/.agents/skills/image2pptx-native/projects/YYYYMMDD_slug"
New-Item -ItemType Directory -Force -Path "$proj/original_inputs","$proj/diagnostics" | Out-Null
Copy-Item "源图路径.png" "$proj/original_inputs/source.png" -Force
```

### Step 2: AI 分析源图

用 `read_image` 观察源图，记录：
- 画布尺寸和比例（通常 16:9）
- 每个元素的类型、位置（像素坐标）、尺寸、颜色、文字内容
- 图标类型（数据库、文档、箭头、齿轮等）

### Step 3: 编写 gen_manifest.py

参考 `scripts/gen_manifest_example.py`，为当前图片编写设计脚本。

#### 可用的 helper 函数

```python
# 基础元素
shape(sh, x, y, w, h, fill, stroke, stroke_w, rot, adj, alpha, name)
#   sh: MSO_AUTO_SHAPE_TYPE 名称，如 "ROUNDED_RECTANGLE", "DOWN_ARROW", "CAN", "GEAR_9", "RIGHT_BRACE", "OVAL", "CLOUD", "LIGHTNING_BOLT", "ISOSCELES_TRIANGLE" 等
line(x1, y1, x2, y2, stroke, stroke_w, name)
freeform(pts, x, y, w, h, closed, fill, stroke, stroke_w, alpha, name)
#   pts: [(nx, ny), ...] 归一化坐标 0-1
text(x, y, w, h, paras, size, bold, color, align, valign, name)
#   paras: "单行" 或 ["多行", "文本"] 或 [{"text":"...", "size":12, "bold":True, "color":"FF0000", "align":"center"}]

# 图标库（从示例中提取，可按需扩展）
icon_db(x, y, w, h, color)          # 数据库圆柱
icon_doc(x, y, w, h, color)         # 文档
icon_monitor(x, y, w, h, color, inner, inner_color)  # 监视器（inner="bars"|"wave"）
icon_bars(x, y, w, h, color, heights)  # 柱状图
icon_network(x, y, w, h, color)     # 网络节点
icon_brain(x, y, w, h, color)       # 脑/AI（云形轮廓）
icon_book(x, y, w, h, color)        # 打开的书
icon_turbine(x, y, w, h, color)     # 风力发电机
icon_shield(x, y, w, h, color)      # 盾牌+闪电
icon_crown(x, y, w, h, color)       # 王冠
icon_funnel(x, y, w, h, color)      # 漏斗
icon_gear(x, y, w, h, color)        # 齿轮
icon_venn3(x, y, w, h, colors)      # 三圆 Venn 图
icon_venn2(x, y, w, h, colors)      # 双圆 Venn 图
icon_linechart(x, y, w, h, color)   # 折线图
icon_checklist(x, y, w, h, color)   # 清单
icon_dc(x, y, w, h, color)          # 直流电源
icon_pie_red(x, y, w, h, color)     # 饼图
icon_clipboard(x, y, w, h, color)   # 剪贴板
icon_curves(x, y, w, h)             # 曲线坐标图（含∂f/x）

# 箭头
down_arrow(x, y, w, h)              # 橙色下箭头
right_arrow_gray(x, y, w, h)        # 灰色右箭头
```

#### 坐标系

- 画布默认 1920×1080 像素（16:9），映射到 13.333×7.5 英寸幻灯片
- 所有坐标以像素为单位，builder 自动转换
- 字号单位为 pt（point）

#### 颜色

使用 6 位十六进制字符串（不带 #），如 `"1E7AC2"`, `"ED7D31"`, `"FFFFFF"`

### Step 4: 生成 manifest 并构建

```powershell
python -X utf8 "$proj/gen_manifest.py"
python -X utf8 "scripts/build_pptx.py" --manifest "$proj/manifest.json" --output "$proj/output.pptx"
```

### Step 5: 渲染验证（可选，需要 PowerPoint）

```powershell
# 用 PowerPoint COM 导出 PNG 预览
$pptx = "$proj/output.pptx"
$png = "C:/temp/render.png"
$ps1 = @'
param($pptx, $png)
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($pptx, $true, $false, $false)
$pres.Slides.Item(1).Export($png, "PNG", 1920, 1080)
$pres.Close()
$app.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($app) | Out-Null
'@
$ps1 | Set-Content "$env:TEMP/render.ps1" -Encoding UTF8
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:TEMP/render.ps1" -pptx $pptx -png $png
```

然后用 `read_image` 查看渲染结果，与原图比对，修正 gen_manifest.py 后重新构建。

### Step 6: 交付

```powershell
Copy-Item "$proj/output.pptx" "目标路径.pptx" -Force
```

## 依赖

- Python 3.10+
- python-pptx (`pip install python-pptx`)
- PowerPoint（可选，仅用于渲染验证）

## 与 artifact-tool 方案的对比

| | image2pptx-native (本 skill) | artifact-tool (Codex Cloud) |
|---|---|---|
| 依赖 | python-pptx | @oai/artifact-tool (私有包) |
| 运行环境 | 本地任意机器 | Codex Cloud 沙箱 |
| 图标 | 原生形状程序化绘制 | 同 |
| 文字 | 原生文本框 | 同 |
| 位图 | 0 张 | 0 张 |
| 渲染验证 | PowerPoint COM | artifact-tool 内置渲染 |
| 可离线使用 | ✅ | ❌ |

## 已知限制

- 复杂图标（脑形、铁塔等）用简化形状近似，非像素级复刻
- 文本框为固定尺寸，大幅改字号需手动调框高
- 渲染验证需要本地安装 PowerPoint

## 扩展示例

要添加新图标类型，在 gen_manifest.py 中定义新的 helper 函数，组合 `shape()`、`line()`、`freeform()` 即可。所有 MSO_AUTO_SHAPE_TYPE 枚举值都可用（RECTANGLE, ROUNDED_RECTANGLE, OVAL, CAN, GEAR_9, FUNNEL, RIGHT_BRACE, DOWN_ARROW, RIGHT_ARROW, CLOUD, LIGHTNING_BOLT, ISOSCELES_TRIANGLE, PENTAGON, DONUT, PIE, CHEVRON, ARC 等）。
