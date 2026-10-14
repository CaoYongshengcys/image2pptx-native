#!/usr/bin/env python3
"""Author the manifest for slide (3): 机理引导下大小模型协同驱动的稳定边界快速推理估测建模方法"""
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
    E.append({"kind":"shape","shape":sh,"x":x,"y":y,"w":w,"h":h,"fill":fill,
              "stroke":stroke,"stroke_w":stroke_w,"rot":rot,"adj":adj,"alpha":alpha,"name":name or sh})

def line(x1,y1,x2,y2,stroke=DARK,stroke_w=2,name="Line"):
    E.append({"kind":"line","x1":x1,"y1":y1,"x2":x2,"y2":y2,"stroke":stroke,"stroke_w":stroke_w,"name":name})

def freeform(pts,x,y,w,h,closed=True,fill=None,stroke=None,stroke_w=2,alpha=None,name="Freeform"):
    E.append({"kind":"freeform","pts":pts,"x":x,"y":y,"w":w,"h":h,"closed":closed,
              "fill":fill,"stroke":stroke,"stroke_w":stroke_w,"alpha":alpha,"name":name})

def text(x,y,w,h,paras,size=12,bold=False,color=DARK,align="left",valign="middle",name="Text"):
    if isinstance(paras,str): paras=[{"text":paras}]
    ps=[]
    for p in paras:
        ps.append({"text":p} if isinstance(p,str) else p)
    E.append({"kind":"text","x":x,"y":y,"w":w,"h":h,"paras":ps,"size":size,
              "bold":bold,"color":color,"align":align,"valign":valign,"name":name})

# ---- icon helpers (reused from example + new ones) ----
def icon_db(x,y,w,h,color=ICON_BLUE):
    shape("CAN",x,y,w,h,fill=color,name="icon_db")
    line(x+0.08*w,y+0.40*h,x+0.92*w,y+0.40*h,"FFFFFF",2.5,"icon_db_l1")
    line(x+0.08*w,y+0.66*h,x+0.92*w,y+0.66*h,"FFFFFF",2.5,"icon_db_l2")

def icon_doc(x,y,w,h,color=ICON_BLUE):
    shape("ROUNDED_RECTANGLE",x,y,w,h,fill="FFFFFF",stroke=color,stroke_w=2.5,adj=0.12,name="icon_doc")
    for i,f in enumerate((0.30,0.50,0.70)):
        line(x+0.22*w,y+f*h,x+0.78*w,y+f*h,color,2.2,f"icon_doc_l{i}")

def icon_bars(x,y,w,h,color=ICON_BLUE,heights=(0.45,0.7,1.0)):
    n=len(heights); step=1.0/n
    for i,hf in enumerate(heights):
        shape("RECTANGLE",x+i*step*w+0.04*w,y+h-hf*h,step*w-0.08*w,hf*h,fill=color,name=f"icon_bar{i}")

def icon_network(x,y,w,h,color=ICON_BLUE):
    c=(0.5,0.52); nodes=[(0.18,0.2),(0.82,0.16),(0.14,0.82),(0.85,0.78)]
    for i,n in enumerate(nodes):
        line(x+c[0]*w,y+c[1]*h,x+n[0]*w,y+n[1]*h,color,2.5,f"icon_net_l{i}")
    line(x+0.18*w,y+0.2*h,x+0.82*w,y+0.16*h,color,2.5,"icon_net_l4")
    d=0.24*w
    for i,n in enumerate([c]+nodes):
        shape("OVAL",x+n[0]*w-d/2,y+n[1]*h-d/2,d,d,fill=color,name=f"icon_net_n{i}")

def icon_book(x,y,w,h,color=ICON_BLUE):
    freeform([(0.5,0.18),(0.06,0.06),(0.06,0.84),(0.5,0.96)],x,y,w,h,fill="FFFFFF",stroke=color,stroke_w=2.5,name="icon_book_l")
    freeform([(0.5,0.18),(0.94,0.06),(0.94,0.84),(0.5,0.96)],x,y,w,h,fill="FFFFFF",stroke=color,stroke_w=2.5,name="icon_book_r")
    line(x+0.16*w,y+0.32*h,x+0.40*w,y+0.40*h,color,1.8,"icon_book_ll1")
    line(x+0.16*w,y+0.52*h,x+0.40*w,y+0.60*h,color,1.8,"icon_book_ll2")
    line(x+0.60*w,y+0.40*h,x+0.84*w,y+0.32*h,color,1.8,"icon_book_rl1")
    line(x+0.60*w,y+0.60*h,x+0.84*w,y+0.52*h,color,1.8,"icon_book_rl2")

def icon_gear(x,y,w,h,color=ICON_BLUE):
    shape("GEAR_9",x,y,w,h,fill=color,name="icon_gear")

def icon_linechart(x,y,w,h,color=ICON_BLUE):
    line(x+0.12*w,y+0.06*h,x+0.12*w,y+0.92*h,color,2.5,"icon_lc_ax")
    line(x+0.12*w,y+0.92*h,x+0.96*w,y+0.92*h,color,2.5,"icon_lc_ay")
    freeform([(0.2,0.75),(0.42,0.42),(0.6,0.58),(0.9,0.18)],x,y,w,h,closed=False,stroke=color,stroke_w=3,name="icon_lc_curve")

def icon_brain(x,y,w,h,color=TEAL):
    shape("CLOUD",x,y,w,h,fill=None,stroke=color,stroke_w=3,name="icon_brain")

def icon_monitor(x,y,w,h,color=ICON_BLUE,inner="bars",inner_color=None):
    ic=inner_color or color
    shape("RECTANGLE",x,y,w,h,fill="FFFFFF",stroke=color,stroke_w=3,name="icon_monitor")
    shape("RECTANGLE",x+0.42*w,y+h,0.16*w,0.10*h,fill=color,name="icon_monitor_stand")
    line(x+0.26*w,y+1.12*h,x+0.74*w,y+1.12*h,color,3,"icon_monitor_base")
    ix,iy,iw,ih=x+0.12*w,y+0.14*h,0.76*w,0.72*h
    if inner=="bars":
        for i,hf in enumerate((0.45,0.7,1.0)):
            shape("RECTANGLE",ix+i*0.30*iw,iy+ih-hf*ih,0.22*iw,hf*ih,fill=ic,name=f"icon_mon_bar{i}")
        line(ix+0.05*iw,iy+0.85*ih,ix+0.95*iw,iy+0.10*ih,ic,2.2,"icon_mon_trend")
    else:
        freeform([(0.02,0.5),(0.2,0.5),(0.32,0.12),(0.45,0.88),(0.58,0.28),(0.68,0.5),(0.98,0.5)],
                 ix,iy,iw,ih,closed=False,stroke=ic,stroke_w=2.5,name="icon_mon_wave")

def icon_shield_check(x,y,w,h,color=GREEN):
    freeform([(0.5,0.0),(0.94,0.12),(0.94,0.52),(0.5,1.0),(0.06,0.52),(0.06,0.12)],
             x,y,w,h,fill=color,name="icon_shield_chk")
    freeform([(0.25,0.50),(0.45,0.72),(0.78,0.30)],x,y,w,h,closed=False,stroke="FFFFFF",stroke_w=3,name="icon_chk_mark")

def icon_calculator(x,y,w,h,color=ICON_BLUE):
    shape("ROUNDED_RECTANGLE",x,y,w,h,fill="FFFFFF",stroke=color,stroke_w=2.5,adj=0.10,name="icon_calc")
    shape("RECTANGLE",x+0.15*w,y+0.08*h,0.70*w,0.22*h,fill=color,name="icon_calc_screen")
    for r in range(3):
        for c in range(3):
            shape("RECTANGLE",x+(0.15+c*0.25)*w,y+(0.38+r*0.20)*h,0.18*w,0.14*h,fill=color,name=f"icon_calc_b{r}{c}")

def icon_speedometer(x,y,w,h,color=ICON_BLUE):
    shape("BLOCK_ARC",x,y,w,h,fill=None,stroke=color,stroke_w=3,name="icon_speed_arc")
    line(x+0.50*w,y+0.55*h,x+0.72*w,y+0.25*h,color,3,"icon_speed_needle")
    shape("OVAL",x+0.44*w,y+0.49*h,0.12*w,0.12*h,fill=color,name="icon_speed_hub")

def icon_target(x,y,w,h,color=ICON_BLUE):
    for i,f in enumerate((1.0,0.65,0.30)):
        shape("OVAL",x+(1-f)/2*w,y+(1-f)/2*h,f*w,f*h,fill=None,stroke=color,stroke_w=2.5,name=f"icon_tgt_{i}")
    shape("OVAL",x+0.42*w,y+0.42*h,0.16*w,0.16*h,fill=color,name="icon_tgt_dot")

def icon_cycle_db(x,y,w,h,color=ICON_BLUE):
    icon_db(x,y,w*0.55,h,color)
    # circular arrows on right side
    cx,cy=x+0.72*w,y+0.50*h; r=0.22*w
    shape("BLOCK_ARC",cx-r,cy-r,2*r,2*r,fill=None,stroke=color,stroke_w=2.5,name="icon_cyc_arc")
    # arrow heads approximated with small triangles
    freeform([(0.0,0.0),(1.0,0.3),(0.3,1.0)],cx+r-4,cy-r-4,10,10,fill=color,name="icon_cyc_a1")
    freeform([(1.0,1.0),(0.0,0.7),(0.7,0.0)],cx-r-6,cy+r-6,10,10,fill=color,name="icon_cyc_a2")

def icon_scatter(x,y,w,h):
    line(x+0.10*w,y+0.06*h,x+0.10*w,y+0.94*h,"333333",2,"icon_sc_ax")
    line(x+0.10*w,y+0.94*h,x+0.96*w,y+0.94*h,"333333",2,"icon_sc_ay")
    import random; random.seed(42)
    for i in range(8):
        px_=0.15+random.random()*0.75; py_=0.15+random.random()*0.70
        shape("OVAL",x+px_*w-3,y+py_*h-3,6,6,fill=RED,name=f"icon_sc_p{i}")
    freeform([(0.15,0.80),(0.40,0.55),(0.65,0.40),(0.90,0.20)],x,y,w,h,closed=False,stroke=BLUE2,stroke_w=2.5,name="icon_sc_trend")

def icon_decision(x,y,w,h,color=ICON_BLUE):
    shape("DIAMOND",x,y,w,h,fill="FFFFFF",stroke=color,stroke_w=2.5,name="icon_diamond")
    # small colored squares below
    shape("RECTANGLE",x+0.15*w,y+h+4,0.20*w,0.18*h,fill=GREEN,name="icon_dec_g")
    shape("RECTANGLE",x+0.40*w,y+h+4,0.20*w,0.18*h,fill=YELLOW,name="icon_dec_y")
    shape("RECTANGLE",x+0.65*w,y+h+4,0.20*w,0.18*h,fill=RED,name="icon_dec_r")

def icon_dist_curve(x,y,w,h):
    line(x+0.08*w,y+0.06*h,x+0.08*w,y+0.94*h,"333333",2,"icon_dc_ax")
    line(x+0.08*w,y+0.94*h,x+0.96*w,y+0.94*h,"333333",2,"icon_dc_ay")
    # bell curve
    freeform([(0.10,0.90),(0.25,0.70),(0.40,0.30),(0.50,0.15),(0.60,0.30),(0.75,0.70),(0.90,0.90)],
             x,y,w,h,closed=False,stroke=BLUE2,stroke_w=3,name="icon_dc_bell")
    # Qα dashed line
    line(x+0.65*w,y+0.15*h,x+0.65*w,y+0.94*h,RED,1.5,"icon_dc_qa")
    text(x+0.66*w,y+0.08*h,40,16,[{"text":"Qα","size":8,"color":RED,"italic":True}],name="icon_dc_qa_t")
    text(x+0.66*w,y+0.78*h,40,14,[{"text":"下界","size":7,"color":RED}],name="icon_dc_lb")

def icon_huber(x,y,w,h):
    line(x+0.08*w,y+0.06*h,x+0.08*w,y+0.94*h,"333333",2,"icon_hb_ax")
    line(x+0.08*w,y+0.94*h,x+0.96*w,y+0.94*h,"333333",2,"icon_hb_ay")
    # Huber loss: quadratic then linear
    freeform([(0.12,0.15),(0.30,0.40),(0.45,0.65),(0.55,0.78),(0.70,0.86),(0.90,0.92)],
             x,y,w,h,closed=False,stroke=RED,stroke_w=3,name="icon_hb_curve")
    text(x+0.30*w,y+0.50*h,60,16,[{"text":"L_Huber","size":8,"color":RED,"italic":True}],name="icon_hb_t")

def icon_mono_bars(x,y,w,h,color=ICON_BLUE):
    heights=(0.30,0.50,0.70,0.90,1.0)
    n=len(heights); step=1.0/n
    for i,hf in enumerate(heights):
        shape("RECTANGLE",x+i*step*w+0.03*w,y+h-hf*h,step*w-0.06*w,hf*h,fill=color,name=f"icon_mb{i}")

def icon_grad_curve(x,y,w,h):
    line(x+0.08*w,y+0.06*h,x+0.08*w,y+0.94*h,"333333",2,"icon_gc_ax")
    line(x+0.08*w,y+0.94*h,x+0.96*w,y+0.94*h,"333333",2,"icon_gc_ay")
    freeform([(0.12,0.88),(0.35,0.55),(0.60,0.35),(0.90,0.20)],x,y,w,h,closed=False,stroke=RED,stroke_w=3,name="icon_gc_r")
    freeform([(0.12,0.92),(0.35,0.70),(0.60,0.55),(0.90,0.42)],x,y,w,h,closed=False,stroke=BLUE2,stroke_w=2.5,name="icon_gc_b")
    text(x+0.55*w,y+0.10*h,50,28,[{"text":"∂f","size":9,"italic":True,"align":"center"},{"text":"∂x","size":9,"italic":True,"align":"center"}],name="icon_gc_frac")

def down_arrow(x,y,w=50,h=56):
    shape("DOWN_ARROW",x,y,w,h,fill=ORANGE,name="arrow_down")

def right_arrow_gray(x,y,w=44,h=26):
    shape("RIGHT_ARROW",x,y,w,h,fill=GRAY,name="arrow_gray")

# ================================================================
# SLIDE CONTENT
# ================================================================
E.append({"kind":"background","fill":"FFFFFF"})

# Title bar
shape("ROUNDED_RECTANGLE",14,10,1892,74,fill="ECECEC",stroke="595959",stroke_w=1.5,adj=0.12,name="title_bar")
text(34,10,1852,74,[{"text":"（3）机理引导下大小模型协同驱动的稳定边界快速推理估测建模方法",
     "bold":True,"size":19,"align":"center","color":"000000"}],name="title_text")

# Column headers
for hx,hw,t in ((14,620,"① 输入基础与映射关系构建"),
                (648,672,"② 大小模型协同融合建模"),
                (1334,572,"③ 快速推理、精算复核与结果回流")):
    shape("ROUNDED_RECTANGLE",hx,98,hw,62,fill=HD_FILL,stroke=HD_STROKE,stroke_w=1.25,adj=0.16,name="col_header")
    text(hx,98,hw,62,[{"text":t,"bold":True,"size":16,"align":"center","color":"000000"}],name="col_header_text")

# Column bodies
for bx,bw in ((14,620),(648,672),(1334,572)):
    shape("ROUNDED_RECTANGLE",bx,166,bw,902,fill="FFFFFF",stroke="8FAADC",stroke_w=1.5,adj=0.02,name="col_body")

# ===== COLUMN 1 =====
# Box A: 接收课题1主导特征输入
shape("ROUNDED_RECTANGLE",28,182,296,280,fill=LB_FILL,stroke=LB_STROKE,stroke_w=1.25,adj=0.05,name="c1_boxA")
text(28,188,296,36,[{"text":"接收课题1主导特征输入","bold":True,"size":12,"align":"center"}],name="c1_boxA_t")
shape("ROUNDED_RECTANGLE",40,230,272,220,fill="FFFFFF",stroke=IN_STROKE,stroke_w=1,adj=0.06,name="c1_boxA_in")
icon_db(60,250,70,70)
text(42,328,106,60,["主导特征","参量数据"],size=10,align="center",name="c1_cap_db")
icon_bars(180,250,70,70,ICON_BLUE,(0.45,0.7,1.0))
text(162,328,106,60,["特征类型","与表征"],size=10,align="center",name="c1_cap_bars")

# Box B: 接收课题2样本库与规则
shape("ROUNDED_RECTANGLE",338,182,282,280,fill=LB_FILL,stroke=LB_STROKE,stroke_w=1.25,adj=0.05,name="c1_boxB")
text(338,188,282,36,[{"text":"接收课题2样本库与规则","bold":True,"size":12,"align":"center"}],name="c1_boxB_t")
shape("ROUNDED_RECTANGLE",350,230,258,220,fill="FFFFFF",stroke=IN_STROKE,stroke_w=1,adj=0.06,name="c1_boxB_in")
icon_db(370,250,70,70)
text(352,328,106,60,["稳定边界","样本库"],size=10,align="center",name="c1_cap_db2")
icon_doc(480,250,70,70)
text(462,328,106,60,["物理知识","规则库"],size=10,align="center",name="c1_cap_doc")

down_arrow(295,472)

# Box C: 建立关键特征与边界映射基础
shape("ROUNDED_RECTANGLE",28,540,592,520,fill=LB_FILL,stroke=LB_STROKE,stroke_w=1.25,adj=0.03,name="c1_boxC")
text(28,548,592,36,[{"text":"建立关键特征与边界映射基础","bold":True,"size":13,"align":"center"}],name="c1_boxC_t")

rows1=[
    ("bars","主导特征参量与稳定边界样本库","（多源特征数据、边界位置/物理裕度标签）",ICON_BLUE),
    ("book","物理知识规则与稳定裕度标签","（机理规则、工程经验、语义知识约束）",ICON_BLUE),
    ("linechart","关键特征参量到边界位置/物理裕度\n的映射","（特征与边界/裕度的映射关系构建）",ICON_BLUE),
    ("gear","面向复杂工况的降维特征输入","（特征筛选、降维表示、复杂工况适配）",ICON_BLUE),
]
for i,(kind,main,sub,color) in enumerate(rows1):
    ry=592+i*118
    shape("ROUNDED_RECTANGLE",40,ry,568,110,fill="FFFFFF",stroke=IN_STROKE,stroke_w=1,adj=0.10,name=f"c1_row{i}")
    if kind=="bars": icon_bars(56,ry+18,64,64,ICON_BLUE,(0.45,0.7,1.0))
    elif kind=="book": icon_book(56,ry+18,64,64)
    elif kind=="linechart": icon_linechart(56,ry+18,64,64)
    elif kind=="gear": icon_gear(56,ry+18,64,64)
    text(136,ry+10,460,40,[{"text":main,"bold":True,"size":11.5}],name=f"c1_row{i}_main")
    text(136,ry+52,460,40,[{"text":sub,"size":9,"color":SUB}],name=f"c1_row{i}_sub")

# ===== COLUMN 2 =====
# Box D: 粗估 + 残差修正协同结构
shape("ROUNDED_RECTANGLE",662,182,644,310,fill=LB_FILL,stroke=LB_STROKE,stroke_w=1.25,adj=0.04,name="c2_boxD")
text(662,188,644,36,[{"text":"粗估 + 残差修正协同结构","bold":True,"size":13,"align":"center"}],name="c2_boxD_t")
shape("ROUNDED_RECTANGLE",674,230,620,250,fill="FFFFFF",stroke=IN_STROKE,stroke_w=1,adj=0.05,name="c2_boxD_in")

# Step 1: calculator + tower/curve (with sub-box)
shape("ROUNDED_RECTANGLE",686,240,170,228,fill=LB_FILL,stroke=IN_STROKE,stroke_w=1,adj=0.06,name="c2_s1_box")
icon_calculator(730,248,72,72)
text(690,326,162,40,["稳定问题","数值求解粗估"],size=9.5,align="center",name="c2_s1_t")
# mini tower+curve below (larger)
shape("ISOSCELES_TRIANGLE",700,374,52,52,fill=None,stroke=ICON_BLUE,stroke_w=2.5,name="c2_mini_tower")
line(714,396,738,396,ICON_BLUE,2,"c2_mini_tower_l1")
line(708,414,744,414,ICON_BLUE,2,"c2_mini_tower_l2")
freeform([(0.15,0.80),(0.40,0.50),(0.65,0.35),(0.90,0.20)],756,374,56,52,closed=False,stroke=RED,stroke_w=2.5,name="c2_mini_curve_r")
freeform([(0.15,0.85),(0.40,0.65),(0.65,0.55),(0.90,0.45)],756,374,56,52,closed=False,stroke=BLUE2,stroke_w=2,name="c2_mini_curve_b")

right_arrow_gray(858,280)

# Step 2: network + scatter (with sub-box)
shape("ROUNDED_RECTANGLE",878,240,170,228,fill=LB_FILL,stroke=IN_STROKE,stroke_w=1,adj=0.06,name="c2_s2_box")
icon_network(920,248,72,72)
text(882,326,162,40,["小模型","残差修正"],size=9.5,align="center",name="c2_s2_t")
icon_scatter(910,374,70,52)
text(900,430,90,14,[{"text":"残差建模","size":7.5,"color":SUB,"align":"center"}],name="c2_s2_label")

right_arrow_gray(1050,280)

# Step 3: gear+doc + decision (with sub-box)
shape("ROUNDED_RECTANGLE",1070,240,170,228,fill=LB_FILL,stroke=IN_STROKE,stroke_w=1,adj=0.06,name="c2_s3_box")
icon_gear(1108,248,36,36)
icon_doc(1138,244,50,56)
text(1074,326,162,40,["语义规则加性","修正/越域门控"],size=9.5,align="center",name="c2_s3_t")
icon_decision(1120,374,44,40)

down_arrow(959,500)

# Box E: 物理信息联合损失与双层闭环优化 (yellow)
shape("ROUNDED_RECTANGLE",662,568,644,240,fill=YB_FILL,stroke=YB_STROKE,stroke_w=1.25,adj=0.04,name="c2_boxE")
icon_brain(790,576,36,36,TEAL)
text(830,576,420,36,[{"text":"物理信息联合损失与双层闭环优化","bold":True,"size":13}],name="c2_boxE_t")

# 4 sub-items
sub_items=[
    ("huber","Huber数据损失"),
    ("grad","梯度匹配项"),
    ("mono","单调性约束"),
    ("dist","分位数损失/\n区间下界头"),
]
for i,(kind,t) in enumerate(sub_items):
    sx=676+i*158
    shape("ROUNDED_RECTANGLE",sx,620,148,176,fill="FFFFFF",stroke=LB_STROKE,stroke_w=1,adj=0.06,name=f"c2_sub{i}")
    text(sx+4,624,140,32,[{"text":t,"bold":True,"size":9.5,"align":"center"}],name=f"c2_sub{i}_t")
    if kind=="huber": icon_huber(sx+14,662,120,80)
    elif kind=="grad": icon_grad_curve(sx+14,662,120,80)
    elif kind=="mono": icon_mono_bars(sx+24,668,100,70)
    elif kind=="dist": icon_dist_curve(sx+14,662,120,80)

down_arrow(959,816,50,50)

# Box F: 兼顾精度、快速性与物理可信性 (yellow)
shape("ROUNDED_RECTANGLE",662,876,644,184,fill=YB_FILL,stroke=YB_STROKE,stroke_w=1.25,adj=0.06,name="c2_boxF")
icon_target(790,884,36,36)
text(830,884,420,36,[{"text":"兼顾精度、快速性与物理可信性","bold":True,"size":13}],name="c2_boxF_t")

# 3 indicators
indicators=[
    ("speed","计算快速","工程可用"),
    ("bars2","预测精度","显著提升"),
    ("shield","物理一致","结果可信"),
]
for i,(kind,l1,l2) in enumerate(indicators):
    ix=686+i*210
    if kind=="speed": icon_speedometer(ix,932,56,56)
    elif kind=="bars2": icon_bars(ix,932,56,56,ICON_BLUE,(0.4,0.65,0.85,1.0))
    elif kind=="shield": icon_shield_check(ix,932,56,56,GREEN)
    text(ix+64,936,130,50,[{"text":l1,"bold":True,"size":10.5},{"text":l2,"bold":True,"size":10.5}],name=f"c2_ind{i}")

# ===== COLUMN 3 =====
# Box G: 快速推理估测
shape("ROUNDED_RECTANGLE",1348,182,544,280,fill=LB_FILL,stroke=LB_STROKE,stroke_w=1.25,adj=0.05,name="c3_boxG")
text(1348,188,544,36,[{"text":"快速推理估测","bold":True,"size":13,"align":"center"}],name="c3_boxG_t")
shape("ROUNDED_RECTANGLE",1360,230,520,220,fill="FFFFFF",stroke=IN_STROKE,stroke_w=1,adj=0.06,name="c3_boxG_in")
icon_monitor(1376,252,120,108,inner="wave",inner_color=ICON_BLUE)
text(1516,262,350,170,["• 稳定边界快速估测","• 稳定裕度快速估测","• 复杂工况快速推演"],size=12,bold=True,valign="middle",name="c3_g_bullets")

down_arrow(1595,472)

# Box H: 精算复核与语义解读
shape("ROUNDED_RECTANGLE",1348,540,544,260,fill=LB_FILL,stroke=LB_STROKE,stroke_w=1.25,adj=0.05,name="c3_boxH")
text(1348,548,544,36,[{"text":"精算复核与语义解读","bold":True,"size":13,"align":"center"}],name="c3_boxH_t")
shape("ROUNDED_RECTANGLE",1360,590,520,200,fill="FFFFFF",stroke=IN_STROKE,stroke_w=1,adj=0.06,name="c3_boxH_in")
icon_gear(1376,616,70,70)
icon_doc(1452,624,50,56)
text(1510,612,370,170,["• 仿真模型精算复核","• 大模型参与规则匹配与结果解释","• 形成最终输出结果"],size=11.5,bold=True,valign="middle",name="c3_h_bullets")

down_arrow(1595,808)

# Box I: 结果输出与回流
shape("ROUNDED_RECTANGLE",1348,868,544,192,fill=LB_FILL,stroke=LB_STROKE,stroke_w=1.25,adj=0.07,name="c3_boxI")
text(1348,874,544,36,[{"text":"结果输出与回流","bold":True,"size":13,"align":"center"}],name="c3_boxI_t")
shape("ROUNDED_RECTANGLE",1360,916,520,132,fill="FFFFFF",stroke=IN_STROKE,stroke_w=1,adj=0.08,name="c3_boxI_in")
icon_cycle_db(1376,926,90,90)
text(1490,924,380,120,["• 边界及裕度估测结果","• 增量样本池回流","• 为后续迁移学习提供支撑"],size=12,bold=True,valign="middle",name="c3_i_bullets")

# Inter-column arrows (positioned at mid-height between upper and lower sections)
shape("RIGHT_ARROW",612,560,52,50,fill=ORANGE,name="arrow_col12")
shape("RIGHT_ARROW",1300,560,52,50,fill=ORANGE,name="arrow_col23")

# ================================================================
manifest={
    "deck":{"canvas_width":1920,"canvas_height":1080,"slide_width_in":13.333,
            "slide_height_in":7.5,"name":"快速推理估测建模方法"},
    "slides":[{"name":"快速推理估测建模方法","elements":E}],
}
out=Path(__file__).parent/"manifest.json"
out.write_text(json.dumps(manifest,ensure_ascii=False,indent=1),encoding="utf-8")
print("elements:",len(E))
