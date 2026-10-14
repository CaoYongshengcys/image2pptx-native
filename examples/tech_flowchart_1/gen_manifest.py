#!/usr/bin/env python3
"""Author the manifest for the technical flowchart slide (editable native shapes)."""
import json, math
from pathlib import Path

E = []

# palette
ICON_BLUE = "1E7AC2"; TEAL = "0E7C7B"; GREEN = "2E9E44"; RED = "E03C31"
YELLOW = "FFC000"; ORANGE = "ED7D31"; GRAY = "A6A6A6"; DARK = "1A1A1A"
SUB = "595959"; LB_FILL = "E4EFF9"; LB_STROKE = "5B9BD5"; IN_STROKE = "9DC3E7"
YB_FILL = "FBF1D3"; YB_STROKE = "D6C274"; HD_FILL = "FAF0CB"; HD_STROKE = "C9B458"
BLUE2 = "2E75B6"


def shape(sh, x, y, w, h, fill=None, stroke=None, stroke_w=2, rot=0, adj=None, alpha=None, name=None):
    E.append({"kind": "shape", "shape": sh, "x": x, "y": y, "w": w, "h": h, "fill": fill,
              "stroke": stroke, "stroke_w": stroke_w, "rot": rot, "adj": adj, "alpha": alpha, "name": name or sh})


def line(x1, y1, x2, y2, stroke=DARK, stroke_w=2, name="Line"):
    E.append({"kind": "line", "x1": x1, "y1": y1, "x2": x2, "y2": y2, "stroke": stroke, "stroke_w": stroke_w, "name": name})


def freeform(pts, x, y, w, h, closed=True, fill=None, stroke=None, stroke_w=2, alpha=None, name="Freeform"):
    E.append({"kind": "freeform", "pts": pts, "x": x, "y": y, "w": w, "h": h, "closed": closed,
              "fill": fill, "stroke": stroke, "stroke_w": stroke_w, "alpha": alpha, "name": name})


def text(x, y, w, h, paras, size=12, bold=False, color=DARK, align="left", valign="middle", name="Text"):
    if isinstance(paras, str):
        paras = [{"text": paras}]
    ps = []
    for p in paras:
        if isinstance(p, str):
            ps.append({"text": p})
        else:
            ps.append(p)
    E.append({"kind": "text", "x": x, "y": y, "w": w, "h": h, "paras": ps, "size": size,
              "bold": bold, "color": color, "align": align, "valign": valign, "name": name})


# ---------------- icons ----------------
def icon_db(x, y, w, h, color=ICON_BLUE):
    shape("CAN", x, y, w, h, fill=color, name="icon_db_body")
    line(x + 0.08 * w, y + 0.40 * h, x + 0.92 * w, y + 0.40 * h, "FFFFFF", 2.5, "icon_db_l1")
    line(x + 0.08 * w, y + 0.66 * h, x + 0.92 * w, y + 0.66 * h, "FFFFFF", 2.5, "icon_db_l2")


def icon_doc(x, y, w, h, color=ICON_BLUE):
    shape("ROUNDED_RECTANGLE", x, y, w, h, fill="FFFFFF", stroke=color, stroke_w=2.5, adj=0.12, name="icon_doc")
    for i, f in enumerate((0.30, 0.50, 0.70)):
        line(x + 0.22 * w, y + f * h, x + 0.78 * w, y + f * h, color, 2.2, f"icon_doc_l{i}")


def icon_monitor(x, y, w, h, color=ICON_BLUE, inner="bars", inner_color=None):
    ic = inner_color or color
    shape("RECTANGLE", x, y, w, h, fill="FFFFFF", stroke=color, stroke_w=3, name="icon_monitor")
    shape("RECTANGLE", x + 0.42 * w, y + h, 0.16 * w, 0.10 * h, fill=color, name="icon_monitor_stand")
    line(x + 0.26 * w, y + 1.12 * h, x + 0.74 * w, y + 1.12 * h, color, 3, "icon_monitor_base")
    ix, iy, iw, ih = x + 0.12 * w, y + 0.14 * h, 0.76 * w, 0.72 * h
    if inner == "bars":
        for i, hf in enumerate((0.45, 0.7, 1.0)):
            shape("RECTANGLE", ix + i * 0.30 * iw, iy + ih - hf * ih, 0.22 * iw, hf * ih, fill=ic, name=f"icon_mon_bar{i}")
        line(ix + 0.05 * iw, iy + 0.85 * ih, ix + 0.95 * iw, iy + 0.10 * ih, ic, 2.2, "icon_mon_trend")
    else:
        freeform([(0.02, 0.5), (0.2, 0.5), (0.32, 0.12), (0.45, 0.88), (0.58, 0.28), (0.68, 0.5), (0.98, 0.5)],
                 ix, iy, iw, ih, closed=False, stroke=ic, stroke_w=2.5, name="icon_mon_wave")


def icon_bars(x, y, w, h, color=ICON_BLUE, heights=(0.45, 0.7, 1.0)):
    n = len(heights)
    step = 1.0 / n
    for i, hf in enumerate(heights):
        shape("RECTANGLE", x + i * step * w + 0.04 * w, y + h - hf * h, step * w - 0.08 * w, hf * h, fill=color, name=f"icon_bar{i}")


def icon_network(x, y, w, h, color=ICON_BLUE):
    c = (0.5, 0.52); nodes = [(0.18, 0.2), (0.82, 0.16), (0.14, 0.82), (0.85, 0.78)]
    for i, n in enumerate(nodes):
        line(x + c[0] * w, y + c[1] * h, x + n[0] * w, y + n[1] * h, color, 2.5, f"icon_net_l{i}")
    line(x + 0.18 * w, y + 0.2 * h, x + 0.82 * w, y + 0.16 * h, color, 2.5, "icon_net_l4")
    d = 0.24 * w
    for i, n in enumerate([c] + nodes):
        shape("OVAL", x + n[0] * w - d / 2, y + n[1] * h - d / 2, d, d, fill=color, name=f"icon_net_n{i}")


def icon_brain(x, y, w, h, color=TEAL):
    shape("CLOUD", x, y, w, h, fill=None, stroke=color, stroke_w=3, name="icon_brain")


def icon_book(x, y, w, h, color=ICON_BLUE):
    freeform([(0.5, 0.18), (0.06, 0.06), (0.06, 0.84), (0.5, 0.96)], x, y, w, h, fill="FFFFFF", stroke=color, stroke_w=2.5, name="icon_book_l")
    freeform([(0.5, 0.18), (0.94, 0.06), (0.94, 0.84), (0.5, 0.96)], x, y, w, h, fill="FFFFFF", stroke=color, stroke_w=2.5, name="icon_book_r")
    line(x + 0.16 * w, y + 0.32 * h, x + 0.40 * w, y + 0.40 * h, color, 1.8, "icon_book_ll1")
    line(x + 0.16 * w, y + 0.52 * h, x + 0.40 * w, y + 0.60 * h, color, 1.8, "icon_book_ll2")
    line(x + 0.60 * w, y + 0.40 * h, x + 0.84 * w, y + 0.32 * h, color, 1.8, "icon_book_rl1")
    line(x + 0.60 * w, y + 0.60 * h, x + 0.84 * w, y + 0.52 * h, color, 1.8, "icon_book_rl2")


def icon_turbine(x, y, w, h, color=ICON_BLUE):
    hx, hy = x + 0.5 * w, y + 0.40 * h
    line(hx, hy, hx, y + 0.98 * h, color, 3, "icon_turb_pole")
    for ang in (90, 210, 330):
        r = math.radians(ang)
        cx = hx + 0.26 * h * math.cos(r)
        cy = hy - 0.26 * h * math.sin(r)
        shape("OVAL", cx - 0.10 * w, cy - 0.23 * h, 0.20 * w, 0.46 * h, fill=color, rot=90 - ang, name=f"icon_turb_b{ang}")
    d = 0.16 * w
    shape("OVAL", hx - d / 2, hy - d / 2, d, d, fill=color, name="icon_turb_hub")


def icon_shield(x, y, w, h, color=RED):
    freeform([(0.5, 0.0), (0.94, 0.12), (0.94, 0.52), (0.5, 1.0), (0.06, 0.52), (0.06, 0.12)],
             x, y, w, h, fill=color, name="icon_shield")
    shape("LIGHTNING_BOLT", x + 0.30 * w, y + 0.24 * h, 0.40 * w, 0.50 * h, fill="FFFFFF", name="icon_shield_bolt")


def icon_crown(x, y, w, h, color=YELLOW):
    freeform([(0.0, 1.0), (0.0, 0.32), (0.25, 0.58), (0.5, 0.08), (0.75, 0.58), (1.0, 0.32), (1.0, 1.0)],
             x, y, w, h, fill=color, name="icon_crown")


def icon_funnel(x, y, w, h, color=ICON_BLUE):
    freeform([(0.0, 0.0), (1.0, 0.0), (0.62, 0.48), (0.62, 1.0), (0.38, 1.0), (0.38, 0.48)],
             x, y, w, h, fill=color, name="icon_funnel")


def icon_gear(x, y, w, h, color=ICON_BLUE):
    shape("GEAR_9", x, y, w, h, fill=color, name="icon_gear")


def icon_venn3(x, y, w, h, colors=(RED, BLUE2, "7030A0")):
    centers = [(0.32, 0.34), (0.68, 0.34), (0.5, 0.66)]
    dw, dh = 0.56 * w, 0.60 * h
    for i, c in enumerate(centers):
        shape("OVAL", x + c[0] * w - dw / 2, y + c[1] * h - dh / 2, dw, dh, fill=colors[i], alpha=55, name=f"icon_venn{i}")


def icon_venn2(x, y, w, h, colors=(GREEN, YELLOW)):
    dw, dh = 0.62 * w, 0.86 * h
    for i, c in enumerate([(0.35, 0.5), (0.65, 0.5)]):
        shape("OVAL", x + c[0] * w - dw / 2, y + c[1] * h - dh / 2, dw, dh, fill=colors[i], alpha=70, name=f"icon_venn2_{i}")


def icon_linechart(x, y, w, h, color=ICON_BLUE):
    line(x + 0.12 * w, y + 0.06 * h, x + 0.12 * w, y + 0.92 * h, color, 2.5, "icon_lc_ax")
    line(x + 0.12 * w, y + 0.92 * h, x + 0.96 * w, y + 0.92 * h, color, 2.5, "icon_lc_ay")
    freeform([(0.2, 0.75), (0.42, 0.42), (0.6, 0.58), (0.9, 0.18)], x, y, w, h, closed=False, stroke=color, stroke_w=3, name="icon_lc_curve")


def icon_checklist(x, y, w, h, color=ICON_BLUE):
    shape("ROUNDED_RECTANGLE", x, y, w, h, fill="FFFFFF", stroke=color, stroke_w=2.5, adj=0.12, name="icon_chk")
    for i, f in enumerate((0.28, 0.52, 0.76)):
        freeform([(0.0, 0.5), (0.35, 0.9), (1.0, 0.0)], x + 0.16 * w, y + (f - 0.09) * h, 0.16 * w, 0.18 * h,
                 closed=False, stroke=color, stroke_w=2, name=f"icon_chk_c{i}")
        line(x + 0.42 * w, y + f * h, x + 0.84 * w, y + f * h, color, 2, f"icon_chk_l{i}")


def icon_dc(x, y, w, h, color=ICON_BLUE):
    shape("ROUNDED_RECTANGLE", x, y, w, h, fill=color, adj=0.25, name="icon_dc")
    text(x, y - 0.06 * h, w, h * 1.1, [{"text": "±", "color": "FFFFFF", "bold": True, "size": 16, "align": "center"}], name="icon_dc_t")


def icon_pie_red(x, y, w, h, color=RED):
    shape("OVAL", x, y, w, h, fill=color, name="icon_pie")
    shape("RECTANGLE", x + 0.26 * w, y + 0.46 * h, 0.11 * w, 0.30 * h, fill="FFFFFF", name="icon_pie_b1")
    shape("RECTANGLE", x + 0.44 * w, y + 0.28 * h, 0.11 * w, 0.48 * h, fill="FFFFFF", name="icon_pie_b2")
    shape("RECTANGLE", x + 0.62 * w, y + 0.52 * h, 0.11 * w, 0.24 * h, fill="FFFFFF", name="icon_pie_b3")


def icon_clipboard(x, y, w, h, color=ICON_BLUE):
    shape("ROUNDED_RECTANGLE", x, y, w, h, fill="FFFFFF", stroke=color, stroke_w=2.5, adj=0.15, name="icon_clip")
    shape("ROUNDED_RECTANGLE", x + 0.30 * w, y - 0.07 * h, 0.40 * w, 0.17 * h, fill=color, adj=0.4, name="icon_clip_top")
    for i, f in enumerate((0.40, 0.58, 0.76)):
        line(x + 0.25 * w, y + f * h, x + 0.75 * w, y + f * h, color, 2, f"icon_clip_l{i}")


def icon_curves(x, y, w, h):
    line(x + 0.08 * w, y + 0.04 * h, x + 0.08 * w, y + 0.96 * h, "333333", 2.5, "icon_cv_ax")
    line(x + 0.08 * w, y + 0.96 * h, x + 0.96 * w, y + 0.96 * h, "333333", 2.5, "icon_cv_ay")
    freeform([(0.12, 0.9), (0.3, 0.42), (0.55, 0.24), (0.92, 0.16)], x, y, w, h, closed=False, stroke=RED, stroke_w=3, name="icon_cv_red")
    freeform([(0.12, 0.94), (0.35, 0.72), (0.62, 0.62), (0.92, 0.56)], x, y, w, h, closed=False, stroke=BLUE2, stroke_w=3, name="icon_cv_blue")


def down_arrow(x, y, w=50, h=56):
    shape("DOWN_ARROW", x, y, w, h, fill=ORANGE, name="arrow_down")


def right_arrow_gray(x, y, w=44, h=26):
    shape("RIGHT_ARROW", x, y, w, h, fill=GRAY, name="arrow_gray")


# ---------------- slide ----------------
E.append({"kind": "background", "fill": "FFFFFF"})

# title bar
shape("ROUNDED_RECTANGLE", 14, 10, 1892, 74, fill="ECECEC", stroke="595959", stroke_w=1.5, adj=0.12, name="title_bar")
text(34, 10, 1852, 74, [{"text": "（1）高比例电力电子化电网下大小模型协同的稳定边界主导特征参量辨识技术",
     "bold": True, "size": 19, "align": "center", "color": "000000"}], name="title_text")

# column headers
for hx, hw, t in ((14, 620, "① 复杂运行场景边界要素与表征"),
                  (648, 672, "② 大小模型协同辨识与特征筛选"),
                  (1334, 572, "③ 跨工况稳健性评估与结果输出")):
    shape("ROUNDED_RECTANGLE", hx, 98, hw, 62, fill=HD_FILL, stroke=HD_STROKE, stroke_w=1.25, adj=0.16, name="col_header")
    text(hx, 98, hw, 62, [{"text": t, "bold": True, "size": 16, "align": "center", "color": "000000"}], name="col_header_text")

# column bodies
for bx, bw in ((14, 620), (648, 672), (1334, 572)):
    shape("ROUNDED_RECTANGLE", bx, 166, bw, 902, fill="FFFFFF", stroke="8FAADC", stroke_w=1.5, adj=0.02, name="col_body")

# ===== column 1 =====
shape("ROUNDED_RECTANGLE", 28, 182, 296, 300, fill=LB_FILL, stroke=LB_STROKE, stroke_w=1.25, adj=0.05, name="c1_boxA")
text(28, 190, 296, 40, [{"text": "梳理边界要素输入", "bold": True, "size": 13, "align": "center"}], name="c1_boxA_t")
shape("ROUNDED_RECTANGLE", 40, 238, 272, 232, fill="FFFFFF", stroke=IN_STROKE, stroke_w=1, adj=0.06, name="c1_boxA_in")
icon_db(66, 262, 84, 84)
text(44, 352, 128, 80, ["多源数据", "输入"], size=11, align="center", name="c1_cap_db")
icon_doc(186, 262, 84, 84)
text(164, 352, 128, 80, ["运行场景", "条件集"], size=11, align="center", name="c1_cap_doc")

shape("ROUNDED_RECTANGLE", 338, 182, 282, 300, fill=LB_FILL, stroke=LB_STROKE, stroke_w=1.25, adj=0.05, name="c1_boxB")
text(338, 190, 282, 40, [{"text": "明确稳定边界表征", "bold": True, "size": 13, "align": "center"}], name="c1_boxB_t")
shape("ROUNDED_RECTANGLE", 350, 238, 258, 232, fill="FFFFFF", stroke=IN_STROKE, stroke_w=1, adj=0.06, name="c1_boxB_in")
icon_monitor(432, 262, 96, 84, inner="bars")
text(366, 352, 226, 80, ["稳定边界", "定义与表征"], size=11, align="center", name="c1_cap_mon")

down_arrow(295, 492)

shape("ROUNDED_RECTANGLE", 28, 556, 592, 496, fill=LB_FILL, stroke=LB_STROKE, stroke_w=1.25, adj=0.03, name="c1_boxC")
text(28, 564, 592, 40, [{"text": "分析复杂运行场景与边界定义", "bold": True, "size": 13, "align": "center"}], name="c1_boxC_t")
rows1 = [
    ("bars", "负荷水平、新能源出力、直流功率", "（负荷波动、新能源渗透率、直流送受功率等）", ICON_BLUE),
    ("tower", "网架结构、故障类型与位置", "（电网拓扑、故障类型、故障位置等）", ICON_BLUE),
    ("shield", "清除逻辑、控制方式等条件集", "（故障清除逻辑、保护控制方式、运行策略等）", RED),
    ("wave", "功角稳定裕度、电压稳定裕度表征", "（暂稳/动稳裕度、电压稳定裕度及临界指标）", GREEN),
]
for i, (kind, main, sub, color) in enumerate(rows1):
    ry = 612 + i * 110
    shape("ROUNDED_RECTANGLE", 40, ry, 568, 102, fill="FFFFFF", stroke=IN_STROKE, stroke_w=1, adj=0.10, name=f"c1_row{i}")
    if kind == "bars":
        icon_bars(56, ry + 17, 68, 68, ICON_BLUE, heights=(0.45, 0.7, 1.0))
    elif kind == "tower":
        shape("ISOSCELES_TRIANGLE", 56, ry + 15, 68, 72, fill=None, stroke=ICON_BLUE, stroke_w=3, name="icon_tower")
        line(78, ry + 40, 102, ry + 40, ICON_BLUE, 2.2, "icon_tower_l1")
        line(68, ry + 62, 112, ry + 62, ICON_BLUE, 2.2, "icon_tower_l2")
    elif kind == "shield":
        icon_shield(58, ry + 15, 64, 72, RED)
    else:
        icon_monitor(56, ry + 17, 68, 62, color=GREEN, inner="wave", inner_color=GREEN)
    text(136, ry + 12, 460, 36, [{"text": main, "bold": True, "size": 12}], name=f"c1_row{i}_main")
    text(136, ry + 50, 460, 42, [{"text": sub, "size": 9.5, "color": SUB}], name=f"c1_row{i}_sub")

# ===== column 2 =====
shape("ROUNDED_RECTANGLE", 662, 182, 644, 300, fill=LB_FILL, stroke=LB_STROKE, stroke_w=1.25, adj=0.04, name="c2_boxD")
text(662, 190, 644, 40, [{"text": "大模型抽取候选特征语义集与机理图谱", "bold": True, "size": 13, "align": "center"}], name="c2_boxD_t")
shape("ROUNDED_RECTANGLE", 674, 238, 620, 232, fill="FFFFFF", stroke=IN_STROKE, stroke_w=1, adj=0.05, name="c2_boxD_in")
icon_doc(704, 262, 88, 84)
text(675, 352, 146, 80, ["运行场景", "文本/数据"], size=11, align="center", name="c2_cap1")
right_arrow_gray(796, 292)
icon_brain(856, 262, 88, 84, TEAL)
text(827, 352, 146, 80, ["大模型", "语义理解"], size=11, align="center", name="c2_cap2")
right_arrow_gray(948, 292)
icon_network(1008, 262, 88, 84)
text(979, 352, 146, 80, ["候选特征", "语义集"], size=11, align="center", name="c2_cap3")
right_arrow_gray(1100, 292)
icon_book(1160, 262, 88, 84)
text(1131, 352, 146, 80, ["机理图谱", "与物理含义"], size=11, align="center", name="c2_cap4")

down_arrow(959, 492)

shape("ROUNDED_RECTANGLE", 662, 556, 644, 322, fill=YB_FILL, stroke=YB_STROKE, stroke_w=1.25, adj=0.04, name="c2_boxE")
icon_brain(820, 566, 44, 44, TEAL)
text(868, 568, 280, 40, [{"text": "AI辅助与仿真计算融合", "bold": True, "size": 13}], name="c2_boxE_t")
# sub box 1
shape("ROUNDED_RECTANGLE", 676, 616, 176, 246, fill="FFFFFF", stroke=LB_STROKE, stroke_w=1.25, adj=0.06, name="c2_s1")
text(682, 622, 164, 60, ["Clarke次梯度/", "灵敏度分析"], size=10.5, bold=True, align="center", name="c2_s1_t")
icon_curves(692, 696, 96, 92)
text(796, 700, 44, 28, [{"text": "∂f", "size": 11, "italic": True, "align": "center"}], name="c2_s1_f1")
line(798, 730, 838, 730, DARK, 1.5, "c2_s1_fl")
text(796, 734, 44, 28, [{"text": "∂x", "size": 11, "italic": True, "align": "center"}], name="c2_s1_f2")
right_arrow_gray(852, 726, 22, 26)
# sub box 2
shape("ROUNDED_RECTANGLE", 874, 616, 196, 246, fill="FFFFFF", stroke=LB_STROKE, stroke_w=1.25, adj=0.06, name="c2_s2")
text(880, 622, 184, 60, ["互信息与最大", "相关最小冗余筛选"], size=10.5, bold=True, align="center", name="c2_s2_t")
icon_venn3(898, 694, 80, 62)
icon_bars(986, 700, 50, 56, ICON_BLUE, heights=(0.45, 0.7, 1.0))
text(884, 766, 182, 90, ["• 互信息分析", "• 最大相关最小冗余", "（mRMR）"], size=9.5, align="left", valign="top", name="c2_s2_b")
right_arrow_gray(1070, 726, 22, 26)
# sub box 3
shape("ROUNDED_RECTANGLE", 1094, 616, 198, 246, fill="FFFFFF", stroke=LB_STROKE, stroke_w=1.25, adj=0.06, name="c2_s3")
text(1100, 622, 186, 60, ["融合先验权重", "形成主导特征集"], size=10.5, bold=True, align="center", name="c2_s3_t")
icon_funnel(1161, 692, 64, 72)
text(1104, 772, 180, 84, ["• 物理先验权重", "• 数据驱动权重", "• 主导特征筛选"], size=9.5, align="left", valign="top", name="c2_s3_b")

down_arrow(959, 884, 50, 50)

shape("ROUNDED_RECTANGLE", 662, 940, 644, 128, fill=YB_FILL, stroke=YB_STROKE, stroke_w=1.25, adj=0.10, name="c2_boxF")
icon_clipboard(806, 950, 36, 42)
text(848, 948, 330, 40, [{"text": "得到主导特征参量初步排序", "bold": True, "size": 13}], name="c2_boxF_t")
icon_bars(700, 996, 64, 58, ICON_BLUE, heights=(0.4, 0.62, 0.85, 1.0))
text(776, 994, 120, 64, ["特征重要性", "初步排序"], size=10.5, bold=True, align="center", name="c2_f_l")
text(940, 992, 22, 70, ["1", "2", "3"], size=10, bold=True, align="center", valign="top", name="c2_f_num")
shape("RECTANGLE", 968, 998, 64, 13, fill=RED, name="c2_f_r1")
shape("RECTANGLE", 968, 1021, 64, 13, fill=YELLOW, name="c2_f_r2")
shape("RECTANGLE", 968, 1044, 64, 13, fill=BLUE2, name="c2_f_r3")
text(1044, 994, 175, 64, ["主导特征", "参量集（初步）"], size=10.5, bold=True, align="left", name="c2_f_r")

# ===== column 3 =====
shape("ROUNDED_RECTANGLE", 1348, 182, 544, 300, fill=LB_FILL, stroke=LB_STROKE, stroke_w=1.25, adj=0.05, name="c3_boxG")
text(1348, 190, 544, 40, [{"text": "重采样稳健性评估（方式族）", "bold": True, "size": 13, "align": "center"}], name="c3_boxG_t")
shape("ROUNDED_RECTANGLE", 1360, 238, 520, 232, fill="FFFFFF", stroke=IN_STROKE, stroke_w=1, adj=0.06, name="c3_boxG_in")
g_rows = [("bars", "负荷水平变化"), ("turbine", "新能源出力变化"), ("dc", "直流功率变化"), ("network", "网架结构变化")]
for i, (kind, t) in enumerate(g_rows):
    ry = 252 + i * 50
    if kind == "bars":
        icon_bars(1376, ry, 44, 44, ICON_BLUE, heights=(0.45, 0.7, 1.0))
    elif kind == "turbine":
        icon_turbine(1376, ry, 44, 44)
    elif kind == "dc":
        icon_dc(1376, ry + 2, 40, 40)
    else:
        icon_network(1376, ry, 44, 44)
    text(1430, ry + 4, 210, 36, [{"text": t, "size": 11, "bold": True}], name=f"c3_g{i}")
shape("RIGHT_BRACE", 1652, 258, 26, 180, fill=None, stroke="333333", stroke_w=1.5, name="c3_brace")
text(1686, 268, 190, 160, ["• 多工况场景构建", "• 参数扰动重采样", "• 稳健性评估计算"], size=10.5, valign="middle", name="c3_g_b")

down_arrow(1595, 492)

shape("ROUNDED_RECTANGLE", 1348, 556, 544, 262, fill=LB_FILL, stroke=LB_STROKE, stroke_w=1.25, adj=0.05, name="c3_boxH")
text(1348, 564, 544, 40, [{"text": "排序一致性与适用条件分析", "bold": True, "size": 13, "align": "center"}], name="c3_boxH_t")
shape("ROUNDED_RECTANGLE", 1360, 612, 520, 194, fill="FFFFFF", stroke=IN_STROKE, stroke_w=1, adj=0.08, name="c3_boxH_in")
h_rows = [("linechart", "Spearman等级相关系数"), ("gear", "作用方向一致率"), ("venn2", "Jaccard集合重合度"), ("checklist", "形成稳定类型适用条件")]
for i, (kind, t) in enumerate(h_rows):
    ry = 622 + i * 46
    if kind == "linechart":
        icon_linechart(1378, ry + 2, 40, 40)
    elif kind == "gear":
        icon_gear(1378, ry + 2, 40, 40)
    elif kind == "venn2":
        icon_venn2(1378, ry + 2, 40, 40)
    else:
        icon_checklist(1378, ry + 2, 40, 40)
    text(1428, ry + 4, 444, 36, [{"text": t, "size": 11, "bold": True}], name=f"c3_h{i}")

down_arrow(1595, 826)

shape("ROUNDED_RECTANGLE", 1348, 888, 544, 180, fill=LB_FILL, stroke=LB_STROKE, stroke_w=1.25, adj=0.07, name="c3_boxI")
text(1348, 894, 544, 38, [{"text": "输出结果", "bold": True, "size": 13, "align": "center"}], name="c3_boxI_t")
shape("ROUNDED_RECTANGLE", 1360, 936, 520, 120, fill="FFFFFF", stroke=IN_STROKE, stroke_w=1, adj=0.10, name="c3_boxI_in")
icon_db(1382, 950, 64, 74)
icon_doc(1452, 956, 50, 62)
i_rows = [("pie", "主导特征参量集"), ("crown", "关键参量排序"), ("doc", "适用条件说明"), ("network", "统一特征输入")]
for i, (kind, t) in enumerate(i_rows):
    ry = 940 + i * 29
    if kind == "pie":
        icon_pie_red(1560, ry, 26, 26)
    elif kind == "crown":
        icon_crown(1560, ry + 2, 26, 24)
    elif kind == "doc":
        icon_doc(1560, ry, 26, 26)
    else:
        icon_network(1560, ry, 26, 26, GREEN)
    text(1594, ry, 280, 28, [{"text": t, "size": 10.5, "bold": True}], name=f"c3_i{i}")

# inter-column arrows
shape("RIGHT_ARROW", 612, 578, 52, 50, fill=ORANGE, name="arrow_col12")
shape("RIGHT_ARROW", 1300, 578, 52, 50, fill=ORANGE, name="arrow_col23")

manifest = {
    "deck": {"canvas_width": 1920, "canvas_height": 1080, "slide_width_in": 13.333,
             "slide_height_in": 7.5, "name": "技术流程图"},
    "slides": [{"name": "技术流程图", "elements": E}],
}
out = Path(__file__).parent / "manifest.json"
out.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
print("elements:", len(E))
