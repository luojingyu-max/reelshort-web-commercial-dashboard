# -*- coding: utf-8 -*-
"""Excel -> payload2.json (CI 重建引擎). 读 data/官网大盘.xlsx, data/国家+付费.xlsx,
data/引流app.xlsx + strategy.json,产出与 Lark 版一致的 payload2.json 供 html2.py 渲染。
4 维 Excel 列位:DAU=4, 充值uv=11, 订阅uv=16, 总收入=22, 总收入ARPPU=30, 充值率=13, 订阅率=18, ltv0..30=32..62。"""
import json, datetime, glob, os, warnings
warnings.simplefilter("ignore")
import openpyxl
from collections import defaultdict

DATA = "data"
def wb(path):
    return openpyxl.load_workbook(path, read_only=True, data_only=True).worksheets[0]
def s2d(s):
    if s is None: return None
    if isinstance(s, datetime.datetime): return s.date().isoformat()
    if isinstance(s, datetime.date): return s.isoformat()
    ss=str(s).strip()
    if len(ss)>=10 and ss[4]=='-' and ss[7]=='-': return ss[:10]
    try: return (datetime.date(1899,12,30)+datetime.timedelta(days=int(float(ss)))).isoformat()
    except: return None
def num(x):
    try: return float(x)
    except: return 0.0

# ---------------- 官网大盘 (site daily) ----------------
ws = wb(f"{DATA}/官网大盘.xlsx")
rows = list(ws.iter_rows(min_row=2, values_only=True))
field = list(rows[0])                      # row2 field headers
data = rows[1:]
DA,PAYUV,PAYR,SUBUV,SUBR,REV,ARPPU = 4,11,13,16,18,22,30
site=[]
for r in data:
    d=s2d(r[0])
    if not d: continue
    site.append({"date":d,"row":list(r)})
site.sort(key=lambda x:x["date"])
dates=[x["date"] for x in site]
col=lambda i:[ (num(x["row"][i]) if x["row"][i] is not None else None) for x in site]
dau=col(DA); rev=col(REV); arppu=col(ARPPU); chargeuv=col(PAYUV); subuv=col(SUBUV)
payrate=[ (num(x["row"][PAYR])*100 if x["row"][PAYR] is not None else None) for x in site]
subrate=[ (num(x["row"][SUBR])*100 if x["row"][SUBR] is not None else None) for x in site]
# mature LTV cohort (<= maxd-30), DAU curve just uses that day's ltv
end=datetime.date.fromisoformat(dates[-1]); mi=0
for i,x in enumerate(site):
    if datetime.date.fromisoformat(x["date"])<=end-datetime.timedelta(days=30): mi=i
ltv=[ (round(num(site[mi]["row"][32+k]),4) if site[mi]["row"][32+k] is not None else None) for k in range(31)]
ltv_date=site[mi]["date"]
def kpi(a):
    cur=a[-1]; prev=a[-2] if len(a)>1 else None
    pct=((cur-prev)/prev*100) if (cur is not None and prev) else None
    return {"cur":cur,"pct":pct}
rev30=sum(v for v in rev[-30:] if v)

# site_detail (大盘明细): [日期]+fields[4:]
sd_cols=["日期"]+[f for f in field[4:] if f is not None]
ncol=4+len(sd_cols)-1
site_detail=[[x["date"]]+[ (round(v,4) if isinstance(v,float) else v) for v in x["row"][4:ncol]] for x in site]

# ---------------- 引流app ----------------
wsa = wb(f"{DATA}/引流app.xlsx")
arows=list(wsa.iter_rows(min_row=2, values_only=True))  # row1 header, row2+ data
app=[]
for r in arows:
    d=s2d(r[0])
    if not d: continue
    charge=num(r[12]); ad=num(r[13]) if len(r)>13 else 0
    app.append({"date":d,"rev":round(charge+ad,2),"charge":charge,"ad":ad,"pay_uv":num(r[3]),"sub_uv":num(r[5])})
app.sort(key=lambda x:x["date"])

# ---------------- overall (官网 vs 引流) from site+app ----------------
site_rev_by={x["date"]:num(x["row"][REV]) for x in site}
ov=[]
for a in app:
    ov.append({"date":a["date"],"site_rev":site_rev_by.get(a["date"]),"app_rev":a["rev"]})
ov_dates=[x["date"] for x in ov]; ov_site=[x["site_rev"] for x in ov]; ov_app=[x["app_rev"] for x in ov]

# ---------------- 国家+付费 (country recs w/ ltv) ----------------
wsc = wb(f"{DATA}/国家+付费.xlsx")
recs=[]
for r in wsc.iter_rows(min_row=3, values_only=True):
    if not r or r[0] is None: continue
    d=s2d(r[0])
    if not d: continue
    ltvc=[num(r[32+k]) if len(r)>32+k and r[32+k] is not None else 0 for k in range(31)]
    recs.append({"d":d,"c":r[1],"paid":(r[2]=="已付费用户"),"dau":num(r[4]),"uv":num(r[11]),"sub":num(r[16]),"rev":num(r[22]),"ltv":ltvc})
maxd=max(x["d"] for x in recs); md=datetime.date.fromisoformat(maxd)

# ctab (MoM/WoW)
def win(a,b): return [x for x in recs if a<=x["d"]<=b]
def arev(rows,c,paid=None): return sum(x["rev"] for x in rows if x["c"]==c and (paid is None or x["paid"]==paid))
def agg(rows,c,paid=None):
    dau_=uv_=sub_=rev_=0.0; days=set()
    for x in rows:
        if x["c"]!=c or (paid is not None and x["paid"]!=paid): continue
        dau_+=x["dau"]; uv_+=x["uv"]; sub_+=x["sub"]; rev_+=x["rev"]; days.add(x["d"])
    nd=len(days) or 1
    return {"rev":round(rev_,2),"dau":round(dau_/nd),"payrate":round(uv_/dau_*100,3) if dau_ else 0,
            "subrate":round(sub_/dau_*100,3) if dau_ else 0,"arppu":round(rev_/uv_,2) if uv_ else 0}
iso=lambda x:x.isoformat()
tm=(iso(md.replace(day=1)),maxd)
lme=md.replace(day=1)-datetime.timedelta(days=1)
lm=(iso(lme.replace(day=1)),iso(lme.replace(day=min(md.day,lme.day))))
wk=(iso(md-datetime.timedelta(days=6)),maxd); pw=(iso(md-datetime.timedelta(days=13)),iso(md-datetime.timedelta(days=7)))
TM,LM,W,PW=win(*tm),win(*lm),win(*wk),win(*pw)
countries=sorted({x["c"] for x in recs}, key=lambda c:-arev(recs,c))
pctc=lambda cur,prev: round((cur-prev)/prev*100,1) if prev else None
ctab=[]
for c in countries:
    cur=agg(TM,c); paid=agg(TM,c,True); unpaid=agg(TM,c,False)
    ctab.append({"c":c,**cur,"rev_paid":paid["rev"],"rev_unpaid":unpaid["rev"],
                 "rev_mom":pctc(arev(TM,c),arev(LM,c)),"rev_wow":pctc(arev(W,c),arev(PW,c))})
cwindows={"month":list(tm),"lastmonth":list(lm),"week":list(wk),"pastweek":list(pw)}

# country LTV (mature, DAU-weighted)
mature_cut=iso(md-datetime.timedelta(days=30))
def cltv(c):
    rs=[x for x in recs if x["c"]==c and x["d"]<=mature_cut]
    w=sum(x["dau"] for x in rs)
    if not w: return [None]*31
    return [round(sum(x["ltv"][k]*x["dau"] for x in rs)/w,4) for k in range(31)]
country_ltv={"countries":countries,"curve":{c:cltv(c) for c in countries},"mature_cut":mature_cut}
country_ltv_table=[{"c":c,"ltv0":country_ltv["curve"][c][0],"ltv7":country_ltv["curve"][c][7],
                    "ltv14":country_ltv["curve"][c][14],"ltv30":country_ltv["curve"][c][30]} for c in countries]

# ---------------- 二期 panel (未付费/已付费, 前6.17-7.16 / 后7.17-7.29) ----------------
PRE=("2026-06-17","2026-07-16"); POST=("2026-07-17","2026-07-29")
p2c=["美国","澳大利亚","意大利","墨西哥","英国","巴西","日本","法国","加拿大","智利","阿根廷"]
def segw(c,paid,w):
    rs=[x for x in recs if x["c"]==c and x["paid"]==paid and w[0]<=x["d"]<=w[1]]
    days=len(set(x["d"] for x in rs)) or 1
    return (sum(x["dau"] for x in rs)/days, sum(x["uv"] for x in rs)/days,
            sum(x["sub"] for x in rs)/days, sum(x["rev"] for x in rs)/days)
def seg_ltv_c(c,paid,w):
    rs=[x for x in recs if x["c"]==c and x["paid"]==paid and w[0]<=x["d"]<=w[1]]
    wt=sum(x["dau"] for x in rs) or 1
    return {k:round(sum(x["ltv"][k]*x["dau"] for x in rs)/wt,4) for k in (0,7,14,30)}
def build2(paid):
    out=[]
    for c in p2c:
        da,ua,sa,ra=segw(c,paid,PRE); db,ub,sb,rb=segw(c,paid,POST)
        pr=lambda u,d: round(u/d*100,3) if d else 0
        la=seg_ltv_c(c,paid,PRE); lb=seg_ltv_c(c,paid,POST)
        out.append({"c":c,"pr_a":pr(ua,da),"pr_b":pr(ub,db),"sr_a":pr(sa,da),"sr_b":pr(sb,db),
            "arppu_a":round(ra/ua,1) if ua else 0,"arppu_b":round(rb/ub,1) if ub else 0,
            "iap_a":round(ra),"iap_b":round(rb),
            "iapchg":("+" if rb>=ra else "")+(f"{(rb-ra)/ra*100:.0f}%" if ra else "N/A"),
            "l0_a":la[0],"l0_b":lb[0],"l7_a":la[7],"l7_b":lb[7],"l14_a":la[14],"l14_b":lb[14],"l30_a":la[30],"l30_b":lb[30]})
    return out
phase2_unpaid=build2(False); phase2_paid=build2(True)
pts=[0,1,7,14,30]
def seg_ltv_agg(paid,w):
    rs=[x for x in recs if x["paid"]==paid and x["c"] in p2c and w[0]<=x["d"]<=w[1]]
    wt=sum(x["dau"] for x in rs) or 1
    return [round(sum(x["ltv"][k]*x["dau"] for x in rs)/wt,4) for k in pts]
phase2_ltv={"pts":pts,"unpaid_pre":seg_ltv_agg(False,PRE),"unpaid_post":seg_ltv_agg(False,POST),
            "paid_pre":seg_ltv_agg(True,PRE),"paid_post":seg_ltv_agg(True,POST)}

# ---------------- country detail ----------------
detail=[]
for x in recs:
    detail.append([x["d"],x["c"],"已付费" if x["paid"] else "未付费",round(x["dau"]),round(x["uv"]),round(x["sub"]),
                   round(x["rev"],2),round(x["ltv"][0],4),round(x["ltv"][7],4),round(x["ltv"][14],4),round(x["ltv"][30],4)])
detail.sort(key=lambda r:(r[0],r[1]))
detail_cols=["日期","国家","付费状态","DAU","充值uv","订阅uv","总收入","LTV0","LTV7","LTV14","LTV30"]

# ---------------- targets / dash_mom ----------------
targets={"2026-07":6*10000,"2026-08":8*10000,"2026-09":10*10000}
cur_month=dates[-1][:7]; mtd=sum(v for dd,v in zip(dates,rev) if dd[:7]==cur_month and v); target_cur=targets.get(cur_month)
def sw(a,b):
    ix=[i for i,dd in enumerate(dates) if a<=dd<=b]
    R=sum(rev[i] or 0 for i in ix); DAt=sum(dau[i] or 0 for i in ix); UV=sum(chargeuv[i] or 0 for i in ix); n=len(ix) or 1
    return {"rev":R,"iap_day":R/n,"arpu":R/DAt if DAt else 0,"arppu":R/UV if UV else 0,"payrate":UV/DAt*100 if DAt else 0}
mds=datetime.date.fromisoformat(dates[-1])
tmv=(iso(mds.replace(day=1)),dates[-1]); lmee=mds.replace(day=1)-datetime.timedelta(days=1)
lmv=(iso(lmee.replace(day=1)),iso(lmee.replace(day=min(mds.day,lmee.day))))
wkv=(iso(mds-datetime.timedelta(days=6)),dates[-1]); pwv=(iso(mds-datetime.timedelta(days=13)),iso(mds-datetime.timedelta(days=7)))
TMv,LMv,Wv,PWv=sw(*tmv),sw(*lmv),sw(*wkv),sw(*pwv)
pctm=lambda c,p: round((c-p)/p*100,1) if p else None
dash_metrics=[]
for key,label,fmt in [("rev","收入(本月至今)","usd"),("arpu","ARPU","usd4"),("arppu","ARPPU","usd1"),("payrate","付费率","pct3"),("iap_day","日均IAP$","usd")]:
    dash_metrics.append({"key":key,"label":label,"fmt":fmt,"cur":round(TMv[key],4),"mom":pctm(TMv[key],LMv[key]),"wow":pctm(Wv[key],PWv[key])})
dash_mom={"metrics":dash_metrics,"win":{"month":list(tmv),"lastmonth":list(lmv),"week":list(wkv),"pastweek":list(pwv)}}

# ---------------- strategy (snapshot) ----------------
strat=json.load(open("strategy.json"))

P={"gen":dates[-1],"dates":dates,"dau":dau,"rev":rev,"payrate":payrate,"subrate":subrate,"arppu":arppu,
   "chargeuv":chargeuv,"subuv":subuv,"ltv":ltv,"ltv_date":ltv_date,
   "kpi":{"dau":kpi(dau),"payrate":kpi(payrate),"arppu":kpi(arppu),"rev":kpi(rev),"ltv30":ltv[30],"rev30":rev30},
   "app":app,"ov_dates":ov_dates,"ov_site":ov_site,"ov_app":ov_app,
   "targets":targets,"cur_month":cur_month,"mtd":round(mtd),"target_cur":target_cur,"dash_mom":dash_mom,
   "ctab":ctab,"cwindows":cwindows,
   "panel1":strat["panel1"],"panel1_header":strat["panel1_header"],
   "phase2_unpaid":phase2_unpaid,"phase2_paid":phase2_paid,
   "strategy":strat["strategy"],"strategy_header":strat["strategy_header"],
   "country_ltv":country_ltv,"country_ltv_table":country_ltv_table,"phase2_ltv":phase2_ltv,
   "detail":detail,"detail_cols":detail_cols,"detail_countries":countries,
   "site_detail_cols":sd_cols,"site_detail":site_detail}
json.dump(P,open("payload2.json","w"),ensure_ascii=False)
print("CI payload built: site",len(dates),dates[0],"->",dates[-1],"| app",len(app),"| ctab",len(ctab),
      "| curmonth",cur_month,"MTD",round(mtd),"target",target_cur,"| detail",len(detail))
