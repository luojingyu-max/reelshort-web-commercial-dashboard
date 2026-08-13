# -*- coding: utf-8 -*-
"""把新版 BI 4-表导出适配成引擎认的旧格式数据文件,并与历史增量合并。
用法: BI_FILE=/path/to/今日导出.xlsx  python3 ci/adapt_bi.py   (从仓库根目录运行)
      不设 BI_FILE 时,取当前目录下最新的 SEO数据看板*.xlsx / bi_*.xlsx。
合并规则: 每张表按"新文件该表的最早日期"为界 —— 保留现有 < 该日期的历史,追加新文件全部行。
新表→旧格式列位(已用 8/05 逐列验证):
 官网监控明细数据: 维度 日期/付费/国家/ALL; 老充值uv=新总付费uv(13),触达付费集uv=7,金币15,订阅17,总收入23,ltv 33-63
 交叉表1(策略):   日期/付费/国家/策略; 充值率插在8→后面右移1
 交叉表3(SKU):     日期/SKU/价格/类型/国家(16列原生)
 SEO监控明细(引流App): 维度2=官网引流APP; 支付成功uv11,订阅uv16,总收入25,广告31
"""
import openpyxl, warnings, re, os, glob
warnings.simplefilter("ignore")
def num(x):
    try: return float(x)
    except: return 0.0
D="ci/data"
NEW=os.environ.get("BI_FILE") or sorted(glob.glob("SEO数据看板*.xlsx")+glob.glob("bi_*.xlsx"))[-1]
print("适配输入:", NEW)
nb=openpyxl.load_workbook(NEW, read_only=True, data_only=True)
def is2026(v): return bool(re.match(r'2026-\d\d-\d\d', str(v)[:10]))
def newmin(sheet, r0):
    ds=[str(r[0])[:10] for r in nb[sheet].iter_rows(min_row=r0, values_only=True) if r and is2026(r[0])]
    return min(ds) if ds else "9999-99-99"

# ---------- 1) 官网监控明细_recent.xlsx (2 行表头) ----------
cut=newmin("官网监控明细数据",3)
sr=list(openpyxl.load_workbook(f"{D}/官网监控明细_recent.xlsx", read_only=True, data_only=True).worksheets[0].iter_rows(values_only=True))
out=openpyxl.Workbook(); w=out.active; w.title="官网监控明细数据"
for r in sr[:2]: w.append(list(r))
kept=0
for r in sr[2:]:
    if r and is2026(r[0]) and str(r[0])[:10]<cut: w.append(list(r)); kept+=1
add=0
for r in nb["官网监控明细数据"].iter_rows(min_row=3, values_only=True):
    if not r or not is2026(r[0]): continue
    o=[0]*63
    o[0]=str(r[0])[:10]; o[1]=r[2]; o[2]=r[1]; o[3]="ALL"
    o[4]=r[4]; o[5]=r[5]; o[7]=r[7]; o[9]=r[9]; o[11]=r[13]; o[12]=r[12]
    o[14]=r[15]; o[16]=r[17]; o[22]=r[23]; o[30]=r[31]
    for k in range(31): o[32+k]=r[33+k]
    w.append(o); add+=1
out.save(f"{D}/官网监控明细_recent.xlsx"); print("官网监控明细 (界<%s): 保留%d + 新增%d"%(cut,kept,add))

# ---------- 2) 策略交叉表.xlsx (1 行表头) ----------
cut=newmin("交叉表1",2)
sr=list(openpyxl.load_workbook(f"{D}/策略交叉表.xlsx", read_only=True, data_only=True).worksheets[0].iter_rows(values_only=True))
out=openpyxl.Workbook(); w=out.active; w.title="策略交叉表"; w.append(list(sr[0])); kept=0
for r in sr[1:]:
    if r and is2026(r[0]) and str(r[0])[:10]<cut: w.append(list(r)); kept+=1
add=0
for r in nb["交叉表1"].iter_rows(min_row=2, values_only=True):
    if not r or not is2026(r[0]): continue
    o=[0]*16
    o[0]=str(r[0])[:10]; o[1]=r[1]; o[2]=r[3]; o[3]=r[2]
    o[4]=r[4]; o[5]=r[5]; o[6]=r[6]; o[7]=r[7]; o[8]=r[9]; o[9]=r[10]
    o[10]=r[11]; o[11]=r[12]; o[12]=r[13]; o[13]=r[14]; o[14]=r[15]; o[15]=r[16]
    w.append(o); add+=1
out.save(f"{D}/策略交叉表.xlsx"); print("策略交叉表 (界<%s): 保留%d + 新增%d"%(cut,kept,add))

# ---------- 3) SKU交叉表.xlsx (统一16列含国家=col4; 历史行国家='全部') ----------
cut=newmin("交叉表3",2)
sr=list(openpyxl.load_workbook(f"{D}/SKU交叉表.xlsx", read_only=True, data_only=True).worksheets[0].iter_rows(values_only=True))
out=openpyxl.Workbook(); w=out.active; w.title="SKU交叉表"
hdr=list(sr[0]);
if len(hdr)==15: hdr=hdr[:4]+["国家"]+hdr[4:]
w.append(hdr); kept=0
for r in sr[1:]:
    if r and is2026(r[0]) and str(r[0])[:10]<cut:
        rr=list(r)
        if len(rr)==15: rr=rr[:4]+["全部"]+rr[4:]
        w.append(rr); kept+=1
_SKC={"美国","加拿大","澳大利亚","英国","法国","日本","意大利","巴西","墨西哥","智利","阿根廷","韩国","泰国"}  # SKU只看13策略国
add=0
for r in nb["交叉表3"].iter_rows(min_row=2, values_only=True):
    if not r or not is2026(r[0]) or str(r[4]) not in _SKC: continue
    w.append([str(r[0])[:10],r[1],r[2],r[3],r[4]]+[round(num(r[5+k]),2) for k in range(11)]); add+=1
out.save(f"{D}/SKU交叉表.xlsx"); print("SKU交叉表 (界<%s): 保留%d + 新增%d(仅13策略国)"%(cut,kept,add))

# ---------- 4) 收入明细.xlsx (引流App=SEO监控明细口径; 合并历史) ----------
cut=newmin("SEO监控明细数据",3)
cols=["维度1","维度2","维度3","充值uv","金币充值uv","订阅uv","首订uv","续订uv","金币充值收入","订阅(续订)收入","首订收入","续订收入","总收入","广告收入"]
out=openpyxl.Workbook(); w=out.active; w.title="收入明细"; w.append(cols); kept=0
if os.path.exists(f"{D}/收入明细.xlsx"):
    for r in list(openpyxl.load_workbook(f"{D}/收入明细.xlsx", read_only=True, data_only=True).worksheets[0].iter_rows(values_only=True))[1:]:
        if r and is2026(r[0]) and str(r[0])[:10]<cut: w.append(list(r)); kept+=1
add=0
for r in nb["SEO监控明细数据"].iter_rows(min_row=3, values_only=True):
    if not r or not is2026(r[0]): continue
    row=[0]*14
    row[0]=str(r[0])[:10]; row[1]="官网引流APP"; row[2]=r[2]
    row[3]=num(r[11]); row[5]=num(r[16]); row[12]=num(r[25]); row[13]=num(r[31])
    w.append(row); add+=1
out.save(f"{D}/收入明细.xlsx"); print("收入明细·引流App (界<%s): 保留%d + 新增%d"%(cut,kept,add))
