# OpenAI Codex + artifact-tool 图片转可编辑PPT 操作手册

> 本手册记录了在本地 Windows 环境下配置和使用 OpenAI Codex CLI + `@oai/artifact-tool` 将图片转换为全矢量可编辑 PPTX 的完整流程。经过实际验证，artifact-tool 的渲染质量优于纯 python-pptx 方案（字体度量更精确、图标细节更丰富）。

## 目录

- [1. 方案对比](#1-方案对比)
- [2. 环境准备](#2-环境准备)
- [3. 安装 Codex CLI](#3-安装-codex-cli)
- [4. 配置 API 和认证](#4-配置-api-和认证)
- [5. 启用 artifact 功能](#5-启用-artifact-功能)
- [6. 解决沙箱和审批问题](#6-解决沙箱和审批问题)
- [7. 执行图片转PPT](#7-执行图片转ppt)
- [8. 常见问题排查](#8-常见问题排查)
- [9. 完整配置文件参考](#9-完整配置文件参考)
- [10. 工作原理深度解析](#10-工作原理深度解析)

---

## 1. 方案对比

| 维度 | artifact-tool (Codex) | image2pptx-native (python-pptx) |
|------|----------------------|-------------------------------|
| **渲染质量** | ⭐⭐⭐⭐⭐ 字体度量精确，图标细节丰富 | ⭐⭐⭐⭐ 良好，复杂图标需简化 |
| **依赖** | Codex CLI + @oai/artifact-tool (私有包) | python-pptx (pip install) |
| **运行环境** | Codex Cloud 沙箱 或 本地 Codex CLI | 本地任意机器 |
| **API 费用** | 需要 ChatGPT Plus($20/月) 或 API Key | 免费（可用任意多模态API） |
| **网络需求** | 需要联网调用 LLM API | 仅 AI 分析图片时需要 |
| **离线使用** | ❌ | ✅ |
| **图标精度** | 更高（skia-canvas 字体度量引擎） | 良好（MSO 形状近似） |
| **文字排版** | 精确（自动计算行高、字间距） | 固定文本框，需手动调 |
| **迭代速度** | 较慢（每次需调用 LLM，约3-5分钟） | 快（修改脚本后秒级重建） |
| **可控性** | AI 自主决策，不可预测 | 完全可控，每个元素精确定义 |
| **适用场景** | 追求最高质量、一次性生成 | 需要反复微调、批量处理 |

**建议**：先用 artifact-tool 生成高质量初版，再用 image2pptx-native 的方法进行微调。

---

## 2. 环境准备

### 系统要求

- Windows 10/11（本手册基于 Windows 11 验证）
- Node.js 18+（Codex CLI 运行时）
- Python 3.10+（辅助工具）
- PowerPoint 2016+（可选，用于渲染验证）
- Git（可选）

### 检查环境

```powershell
node --version    # 需要 v18+
python --version  # 需要 3.10+
where.exe git     # 可选
```

---

## 3. 安装 Codex CLI

### 方式一：npm 安装（推荐）

```powershell
# 使用国内镜像加速
npm install -g @openai/codex --registry https://registry.npmmirror.com

# 或使用官方源
npm install -g @openai/codex
```

### 方式二：PowerShell 一键安装

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"
```

### 方式三：Homebrew（macOS）

```bash
brew install --cask codex
```

### 验证安装

```powershell
codex --version
# 预期输出: codex-cli 0.162.1 (或更新版本)
```

### 安装后的文件位置

```
C:\Users\<用户名>\AppData\Roaming\npm\
├── codex.cmd                          # 入口脚本
└── node_modules\@openai\codex\
    └── node_modules\@openai\codex-win32-x64\
        └── vendor\x86_64-pc-windows-msvc\
            ├── bin\codex.exe           # 主程序
            ├── codex-resources\        # 运行时资源
            └── codex-path\rg.exe       # 内置 ripgrep
```

---

## 4. 配置 API 和认证

Codex CLI 支持两种认证方式：

### 方式一：ChatGPT 账号登录（推荐）

```powershell
codex login
# 会打开浏览器让你登录 ChatGPT 账号
# 需要 ChatGPT Plus / Pro / Business / Edu / Enterprise 订阅
```

### 方式二：API Key 直连

在 `~/.codex/config.toml` 中配置：

```toml
model = "gpt-4o"
model_provider = "openai"

[model_providers.openai]
base_url = "https://api.openai.com/v1"
name = "OpenAI"
wire_api = "responses"

[model_providers.openai.auth]
command = "cmd"
args = ["/d", "/c", "echo", "sk-your-api-key-here"]
```

### 方式三：第三方 API 代理（如阿里云、Aizex 等）

```toml
model = "qwen3.8-max"
model_provider = "aliyun"

[model_providers.aliyun]
base_url = "https://your-endpoint.example.com/compatible-mode/v1"
name = "Aliyun Qwen"
wire_api = "responses"
requires_openai_auth = false

[model_providers.aliyun.auth]
command = "cmd"
args = ["/d", "/c", "echo", "sk-your-key-here"]
```

> **注意**：artifact-tool 的 Presentation skill 需要一个**支持视觉理解的多模态模型**（能看懂图片）。推荐使用 GPT-4o、Qwen-VL 等。纯文本模型无法分析图片版式。

### 配置文件位置

```
C:\Users\<用户名>\.codex\config.toml
```

---

## 5. 启用 artifact 功能

artifact-tool 的 Presentation 功能在 Codex CLI 中是一个 **under development** 的 feature flag，默认关闭。需要手动启用：

### 方法一：命令行启用

```powershell
codex features enable artifact
```

### 方法二：直接编辑配置文件

在 `~/.codex/config.toml` 中添加：

```toml
[features]
artifact = true
```

### 验证启用状态

```powershell
codex features list 2>&1 | Select-String "artifact"
# 预期输出: artifact    under development    true
```

### artifact-tool 运行时位置

启用后，Codex 会在首次使用时自动下载 artifact-tool 运行时到：

```
C:\Users\<用户名>\.cache\codex-runtimes\codex-primary-runtime\
└── dependencies\node\node_modules\
    └── @oai\artifact-tool\          # ← 这就是核心包
        ├── dist\artifact_tool.mjs   # 主模块
        ├── package.json
        └── ...
```

验证是否已下载：

```powershell
Test-Path "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules\@oai\artifact-tool\package.json"
# 预期输出: True
```

> **如果返回 False**：说明运行时还未下载。运行一次 `codex exec "hello"` 触发初始化，或者手动运行 Codex App (`codex app`) 让它自动下载。

---

## 6. 解决沙箱和审批问题

这是本地使用 Codex CLI 最容易踩的坑。Codex 默认在沙箱中运行，**禁止写入文件**，而生成 PPTX 必须写文件。

### 问题现象

```
sandbox: read-only
Set-Content : 访问被拒绝
PermissionError: [Errno 13] Permission denied
```

### 解决方案

#### 方案 A：使用 `--dangerously-bypass-approvals-and-sandbox`（最简单）

```powershell
codex exec --skip-git-repo-check \
  --dangerously-bypass-approvals-and-sandbox \
  -i "图片路径.png" \
  "请按照这张图片制作可编辑PPTX"
```

这个参数同时跳过沙箱限制和审批流程。**仅在信任的环境下使用**。

#### 方案 B：配置审批模式为 never

在 `~/.codex/config.toml` 中：

```toml
approval_policy = "never"
# 注释掉 auto_review（如果有的话）
# approvals_reviewer = "auto_review"
```

然后配合 Windows sandbox 设置：

```toml
[windows]
sandbox = "elevated"
```

> **注意**：如果 `approvals_reviewer = "auto_review"` 存在且对应的审核模型不可用，会导致所有提权命令被拒绝，报错 `Model not found: codex-auto-review`。**务必注释掉这一行**。

#### 方案 C：使用 Codex App（桌面应用）

```powershell
codex app
```

桌面应用有自己的审批 UI，可以在弹窗中点击"允许"来授权写入操作。

### 沙箱模式说明

| 模式 | 配置值 | 说明 |
|------|--------|------|
| 只读 | `read-only`（默认） | 只能读文件，不能写入 |
| 工作区写入 | `workspace-write` | 可以写入当前工作目录 |
| 完全访问 | `danger-full-access` | 无限制 |
| 提升权限 | `elevated` | Windows 下以提权方式运行 |

Windows 下 `[windows] sandbox` 只接受 `elevated`、`unelevated`、`mxc` 三个值。

---

## 7. 执行图片转PPT

### 基本命令

```powershell
codex exec --skip-git-repo-check \
  --dangerously-bypass-approvals-and-sandbox \
  -i "D:\path\to\source_image.png" \
  --enable artifact \
  "请按照这张图片的版式和内容制作一页 PPTX，尽量让文字和图形可编辑。输出到 D:\path\to\output.pptx"
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `--skip-git-repo-check` | 跳过 Git 仓库检查（非 Git 目录也能用） |
| `--dangerously-bypass-approvals-and-sandbox` | 跳过沙箱和审批 |
| `-i "图片路径"` | 附加图片文件（可多次使用附加多张图） |
| `--enable artifact` | 启用 artifact 功能 |
| 最后的字符串 | 给 AI 的提示词 |

### 提示词建议

**基础版**（简单任务）：
```
请按照这张图片制作一页可编辑的PPTX，输出到 D:\output.pptx
```

**精确版**（推荐）：
```
请按照这张图片的版式和内容制作一页 PPTX，尽量让文字和图形可编辑。
输出到 D:\path\to\output.pptx
```

**详细版**（复杂图）：
```
请按照这张图片的版式和内容制作一页 PPTX，要求：
1. 所有文字做成可编辑的文本框
2. 所有图形用原生PPT形状绘制（不要用图片）
3. 图标尽量用矢量形状近似
4. 保持原图的配色方案和布局比例
输出到 D:\path\to\output.pptx
```

### 执行过程

Codex 会自动执行以下步骤（你可以在终端看到实时输出）：

1. **读取 PowerPoint Skill** — 加载 `SKILL.md` 了解工作流
2. **分析源图** — 用多模态模型识别版式、文字、图标、颜色、坐标
3. **检查运行时** — 确认 `@oai/artifact-tool` 和 Node.js 可用
4. **初始化项目** — 创建临时构建目录，建立 node_modules 链接
5. **编写构建脚本** — 生成 `.mjs` JavaScript 构建器
6. **运行构建** — 用 Node.js 执行构建器，生成 PPTX
7. **渲染验证** — 导出 PNG 预览，与原图比对
8. **迭代修正** — 如果有偏差，修改构建器重新生成（通常2-3轮）
9. **输出最终文件** — 复制到指定路径

### 预期耗时

| 步骤 | 耗时 |
|------|------|
| 模型分析图片 | 30-60秒 |
| 编写构建脚本 | 60-120秒 |
| 运行构建 + 渲染 | 10-20秒 |
| 迭代修正（1-2轮） | 60-120秒 |
| **总计** | **3-5分钟** |

### 实际执行示例

```powershell
# 我们的实际执行命令
codex exec --skip-git-repo-check `
  --dangerously-bypass-approvals-and-sandbox `
  -i "D:\code_cys\公司计划\source_slide.png" `
  --enable artifact `
  "请按照这张图片的版式和内容制作一页 PPTX，尽量让文字和图形可编辑。输出到 D:\code_cys\公司计划\技术流程图_codex.pptx"
```

输出摘要：
```
OpenAI Codex v0.162.1
--------
workdir: D:\code_cys\公司计划
model: qwen3.8-max
provider: aliyun
approval: never
sandbox: danger-full-access
--------

codex: 我先读取 PowerPoint skill 的说明...
exec: cat SKILL.md ... succeeded
codex: 确认 artifact-tool 运行时...
exec: Test-Path ...artifact-tool/package.json → True
codex: 初始化构建目录...
exec: node init_pro_deck_builder_js.js ... succeeded
codex: 编写构建脚本...
exec: Set-Content build_deck.mjs ... succeeded
codex: 运行构建...
exec: node build_deck.mjs ... succeeded
codex: 渲染验证...
exec: PowerPoint COM export ... succeeded
codex: 修正盾牌/漏斗/铁塔形状...
exec: patch + rebuild ... succeeded
codex: 完成。

交付: D:\code_cys\公司计划\技术流程图_codex.pptx
- 52 个原生文本框
- 172 个原生矢量对象
- 0 张位图
```

---

## 8. 常见问题排查

### Q1: `Model not found: codex-auto-review`

**原因**：`approvals_reviewer = "auto_review"` 配置了一个不存在的审核模型。

**解决**：在 `config.toml` 中注释掉或删除这一行：
```toml
# approvals_reviewer = "auto_review"
```

### Q2: `sandbox: read-only` 导致写入失败

**原因**：默认沙箱禁止写入文件。

**解决**：使用 `--dangerously-bypass-approvals-and-sandbox` 参数，或参考第6节配置。

### Q3: `session-flags: sandbox_permissions is ignored`

**原因**：`-c 'sandbox_permissions=["danger-full-access"]'` 这个参数在新版 Codex 中已被忽略。

**解决**：改用 `--dangerously-bypass-approvals-and-sandbox` 命令行参数。

### Q4: `failed to refresh available models: stream disconnected`

**原因**：第三方 API 代理的 `/models` 端点返回格式不兼容。

**影响**：**不影响正常使用**，只是一个警告。Codex 会使用 fallback metadata。

### Q5: artifact-tool 运行时未找到

**原因**：首次使用 artifact 功能时，运行时还未下载。

**解决**：
```powershell
# 方法1: 运行一次普通命令触发初始化
codex exec "hello"

# 方法2: 启动 Codex App
codex app

# 方法3: 检查并等待下载完成
Test-Path "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules\@oai\artifact-tool\package.json"
```

### Q6: API 额度不足

**原因**：第三方代理的周限/月限额度用完。

**解决**：切换到其他 API 提供商，或等待额度重置。在 `config.toml` 中修改 `model_provider` 和对应的 `[model_providers.xxx]` 配置。

### Q7: `Not inside a trusted directory`

**原因**：当前目录不在 Codex 的信任列表中。

**解决**：添加 `--skip-git-repo-check` 参数，或在 config.toml 中添加项目信任：
```toml
[projects.'D:\your\project\path']
trust_level = "trusted"
```

### Q8: 生成的 PPTX 中文字体显示异常

**原因**：artifact-tool 的 skia-canvas 渲染引擎可能找不到中文字体。

**解决**：确保系统安装了 Microsoft YaHei 字体。artifact-tool 会自动检测并使用可用字体。如果仍有问题，可以在提示词中指定：
```
请使用微软雅黑字体
```

---

## 9. 完整配置文件参考

以下是我们实际使用的 `~/.codex/config.toml` 完整配置：

```toml
# ===== 模型配置 =====
model = "qwen3.8-max"                    # 模型名称
model_reasoning_effort = "xhigh"          # 推理强度
model_context_window = 1000000            # 上下文窗口
model_auto_compact_token_limit = 900000   # 自动压缩阈值
model_provider = "aliyun"                 # 使用的 provider

# ===== 审批配置 =====
approval_policy = "never"                 # 不需要审批（自动执行）
# approvals_reviewer = "auto_review"      # ← 注释掉！否则报 codex-auto-review 错误

# ===== 功能开关 =====
[features]
artifact = true                           # 启用 artifact-tool（Presentation 功能）

# ===== Windows 沙箱 =====
[windows]
sandbox = "elevated"                      # elevated / unelevated / mxc

# ===== API Provider 配置 =====
[model_providers.aliyun]
base_url = "https://your-endpoint.example.com/compatible-mode/v1"
name = "Aliyun Qwen"
wire_api = "responses"
requires_openai_auth = false

[model_providers.aliyun.auth]
command = "cmd"
args = ["/d", "/c", "echo", "sk-your-api-key-here"]

# ===== 项目信任列表 =====
[projects.'D:\code_cys\公司计划']
trust_level = "trusted"

# ===== 插件 =====
[plugins."codex-app-tools@openai-bundled"]
enabled = true

[plugins."visualize@openai-bundled"]
enabled = true
```

---

## 10. 工作原理深度解析

### artifact-tool 架构

```
┌─────────────────────────────────────────────────┐
│                  Codex CLI                       │
│  ┌───────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ LLM Agent │→ │ Skill    │→ │ artifact-tool│  │
│  │ (qwen/gpt)│  │ Loader   │  │ (Node.js)    │  │
│  └───────────┘  └──────────┘  └──────┬───────┘  │
│                                       │          │
│                              ┌────────▼───────┐  │
│                              │ skia-canvas    │  │
│                              │ (字体度量/渲染) │  │
│                              └────────┬───────┘  │
│                                       │          │
│                              ┌────────▼───────┐  │
│                              │ PPTX Export    │  │
│                              │ (OOXML生成)    │  │
│                              └────────────────┘  │
└─────────────────────────────────────────────────┘
```

### 关键组件

| 组件 | 路径 | 作用 |
|------|------|------|
| Codex 主程序 | `vendor\...\bin\codex.exe` (71MB) | Rust 编写的 CLI 主程序 |
| artifact-tool | `~/.cache/codex-runtimes/.../@oai/artifact-tool/` | JS 模块，提供 Presentation API |
| skia-canvas | artifact-tool 内部依赖 | 字体度量、文本排版、PNG 渲染 |
| Node.js | `~/.cache/codex-runtimes/.../node/bin/node.exe` | 运行时 |
| PowerPoint Skill | `~/.codex/skills/codex-primary-runtime/slides/SKILL.md` | 工作流指令 |

### artifact-tool vs python-pptx 的质量差异来源

1. **字体度量引擎**：artifact-tool 使用 skia-canvas（Skia 图形库的 Node.js 绑定），能精确计算每个字符的宽度、行高、基线位置。python-pptx 没有字体度量能力，文本框大小需要手动估算。

2. **文本自动适配**：artifact-tool 支持 `autoFit: "shrinkText"` 和 `"resizeShapeToFitText"`，能自动调整字号或文本框大小以适应内容。python-pptx 需要手动计算。

3. **主题和样式系统**：artifact-tool 有完整的 theme color scheme、named styles、style inheritance。python-pptx 的主题支持有限。

4. **渲染验证**：artifact-tool 内置了 PNG 渲染能力（通过 skia-canvas），可以在生成 PPTX 的同时渲染预览图进行比对。python-pptx 方案需要依赖外部 PowerPoint COM。

### Skill 工作流详解

Codex 的 PowerPoint Skill (`SKILL.md`) 定义了严格的工作流：

```
1. Plan     → 分析图片，规划版式、元素列表、配色方案
2. Prepare  → 创建项目目录，建立 node_modules 链接
3. Author   → 编写 .mjs 构建脚本（使用 artifact-tool API）
4. Build    → 运行 Node.js 构建脚本
5. Render   → 导出 PNG 预览
6. Verify   → 与原图比对，检查文字可编辑性
7. Iterate  → 修正偏差，重新构建（最多3轮）
8. Export   → 输出最终 .pptx
```

构建脚本使用 artifact-tool 的核心 API：

```javascript
const { Presentation, PresentationFile } = await import("@oai/artifact-tool");

// 创建演示文稿
const presentation = Presentation.create({
  slideSize: { width: 1280, height: 720 }  // 像素单位
});

// 添加幻灯片
const slide = presentation.slides.add();

// 添加形状
const shape = slide.shapes.add({
  geometry: "roundRect",
  position: { left: 72, top: 64, width: 520, height: 300 },
  fill: "#E4EFF9",
  line: { style: "solid", fill: "#5B9BD5", width: 1 },
});

// 设置文字
shape.text = "可编辑文字";
shape.text.fontSize = 28;
shape.text.bold = true;
shape.text.typeface = "Microsoft YaHei";

// 导出
const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save("output.pptx");
```

---

## 附录：快速参考卡片

```powershell
# ===== 一键执行命令 =====
codex exec --skip-git-repo-check `
  --dangerously-bypass-approvals-and-sandbox `
  -i "源图.png" `
  --enable artifact `
  "请按照这张图片制作可编辑PPTX，输出到 输出.pptx"

# ===== 常用诊断命令 =====
codex --version                                    # 检查版本
codex features list 2>&1 | Select-String artifact  # 检查 artifact 状态
codex doctor                                        # 全面诊断
Test-Path "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules\@oai\artifact-tool\package.json"  # 检查运行时

# ===== 配置文件位置 =====
# C:\Users\<用户名>\.codex\config.toml

# ===== artifact-tool 运行时位置 =====
# C:\Users\<用户名>\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules\@oai\artifact-tool\

# ===== PowerPoint Skill 位置 =====
# C:\Users\<用户名>\.codex\skills\codex-primary-runtime\slides\SKILL.md
```
