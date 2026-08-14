# -*- coding: utf-8 -*-
"""官网商业化数据播报 -> Lark 群自定义机器人(卡片原生表格组件 schema 2.0)。
读 payload2.json,发近7天大盘表 + 收入环比。用法: LARK_HOOK=<webhook> python broadcast.py"""
import json, os, urllib.request
P=json.load(open("payload2.json"))
HOOK=os.environ.get("LARK_HOOK")
if not HOOK: raise SystemExit("no LARK_HOOK")
dates=P["dates"]; rev=P["rev"]; dau=P["dau"]; pr=P["payrate"]; suv=P["subuv"]; srev=P["subrev_d"]; n=len(dates)
comma=lambda v: format(int(round(v)), ",")
arpu=lambda i: rev[i]/dau[i] if dau[i] else 0
subarppu=lambda i: srev[i]/suv[i] if suv[i] else 0
idx=range(max(0,n-7), n)
cols=[{"name":"date","display_name":"日期","data_type":"text"},
      {"name":"rev","display_name":"收入","data_type":"text","horizontal_align":"right"},
      {"name":"pr","display_name":"付费率","data_type":"text","horizontal_align":"right"},
      {"name":"arpu","display_name":"ARPU","data_type":"text","horizontal_align":"right"},
      {"name":"sarppu","display_name":"订阅ARPPU","data_type":"text","horizontal_align":"right"}]
rows=[{"date":dates[i][5:],"rev":"$"+comma(rev[i]),"pr":"%.3f%%"%(pr[i] or 0),
       "arpu":"$%.3f"%arpu(i),"sarppu":"$%.1f"%subarppu(i)} for i in idx]
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
print("sent:", r.read().decode())
