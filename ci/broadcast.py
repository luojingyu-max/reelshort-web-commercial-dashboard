# -*- coding: utf-8 -*-
"""官网商业化数据播报 -> Lark 群自定义机器人(卡片原生表格组件 schema 2.0)。
读 payload2.json,发近7天大盘表 + 收入环比。用法: LARK_HOOK=<webhook> python broadcast.py"""
import json, os, urllib.request, datetime
P=json.load(open("payload2.json"))
HOOK=os.environ.get("LARK_HOOK")
if not HOOK: raise SystemExit("no LARK_HOOK")

# ---------- 去重:同一天(CST)只播报一次 ----------
# 状态文件记录最近一次成功播报的 CST 日期 + 数据末日;跨 Action 运行持久化(随仓库提交)
STATE="broadcast_state.json"
TODAY=(datetime.datetime.utcnow()+datetime.timedelta(hours=8)).strftime("%Y-%m-%d")   # CST 今天
DATA_LAST=P["dates"][-1]
FORCE=os.environ.get("FORCE_BROADCAST")=="1"
_st={}
if os.path.exists(STATE):
    try: _st=json.load(open(STATE))
    except Exception: _st={}
if not FORCE and _st.get("last_sent_cst")==TODAY:
    print("SKIP: 今天(%s)已播报过(数据末日 %s),不重复发送。需强制发送请设 FORCE_BROADCAST=1"%(TODAY,_st.get("data_last")))
    raise SystemExit(0)
dates=P["dates"]; rev=P["rev"]; dau=P["dau"]; pr=P["payrate"]; suv=P["subuv"]; srev=P["subrev_d"]; n=len(dates)
comma=lambda v: format(int(round(v)), ",")
arpu=lambda i: rev[i]/dau[i] if dau[i] else 0
subarppu=lambda i: srev[i]/suv[i] if suv[i] else 0
idx=list(range(max(0,n-7), n))[::-1]   # 最新日期在最上
# 观看率/充值成功率 从大盘明细取(sd_cols: 3=观看率% 9=充值成功率%)
SD={r[0]:r for r in P.get("site_detail",[])}
vrate=lambda d: (SD[d][3] if d in SD else 0)
okrate=lambda d: (SD[d][9] if d in SD else 0)
cols=[{"name":"date","display_name":"日期","data_type":"text","width":"80px"},
      {"name":"dau","display_name":"DAU","data_type":"text","horizontal_align":"right","width":"88px"},
      {"name":"vr","display_name":"观看率","data_type":"text","horizontal_align":"right","width":"80px"},
      {"name":"pr","display_name":"付费率","data_type":"text","horizontal_align":"right","width":"80px"},
      {"name":"ok","display_name":"充值成功率","data_type":"text","horizontal_align":"right","width":"94px"},
      {"name":"rev","display_name":"收入","data_type":"text","horizontal_align":"right","width":"88px"},
      {"name":"arpu","display_name":"ARPU","data_type":"text","horizontal_align":"right","width":"80px"},
      {"name":"sarppu","display_name":"订阅ARPPU","data_type":"text","horizontal_align":"right","width":"94px"}]
rows=[{"date":dates[i][5:],"dau":comma(dau[i]),"vr":"%.1f%%"%vrate(dates[i]),"pr":"%.3f%%"%(pr[i] or 0),
       "ok":"%.1f%%"%okrate(dates[i]),"rev":"$"+comma(rev[i]),"arpu":"$%.3f"%arpu(i),"sarppu":"$%.1f"%subarppu(i)} for i in idx]
dm={m["key"]:m for m in P["dash_mom"]["metrics"]}
mom=dm["rev"]["mom"]; wow=dm["rev"]["wow"]
yday=((rev[-1]-rev[-2])/rev[-2]*100) if (n>1 and rev[-2]) else None
f=lambda v: "—" if v is None else (("🔺+%.1f%%"%v) if v>=0 else ("🔻%.1f%%"%v))
summ="**收入环比** · 月环比 %s · 周环比 %s · 昨日对比 %s"%(f(mom), f(wow), f(yday))
card={"msg_type":"interactive","card":{
  "schema":"2.0",
  "config":{"wide_screen_mode":True},
  "header":{"title":{"tag":"plain_text","content":"📊 官网商业化日报 · 近7天(截至 %s)"%dates[-1]},"template":"blue"},
  "body":{"elements":[
    {"tag":"table","page_size":10,"row_height":"low","header_style":{"bold":True,"background_style":"grey"},"columns":cols,"rows":rows},
    {"tag":"hr"},
    {"tag":"markdown","content":summ+"\n<font color='grey-500'>官网直充口径 · 环比均为收入 · </font>[进看板查看](https://luojingyu-max.github.io/reelshort-web-commercial-dashboard/)"}]}}}
r=urllib.request.urlopen(urllib.request.Request(HOOK, data=json.dumps(card).encode(), headers={"Content-Type":"application/json"}))
resp=r.read().decode()
print("sent:", resp)
# 仅在 Lark 确认成功时记账,失败不写(下次仍会重试)
if '"code":0' in resp or '"StatusCode":0' in resp:
    json.dump({"last_sent_cst":TODAY,"data_last":DATA_LAST,
               "sent_at_utc":datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")},
              open(STATE,"w"), ensure_ascii=False, indent=1)
    print("state written:", TODAY, DATA_LAST)
else:
    print("WARN: Lark 未返回成功码,不写状态文件(下次会重试)")
