# -*- coding: utf-8 -*-
"""官网商业化数据播报 -> Lark 群自定义机器人。读 payload2.json,发近7天大盘表 + 收入环比。
用法: LARK_HOOK=<webhook> python broadcast.py   (需先 ci_build_payload.py 生成 payload2.json)"""
import json, os, urllib.request
P=json.load(open("payload2.json"))
HOOK=os.environ.get("LARK_HOOK")
if not HOOK: raise SystemExit("no LARK_HOOK")
dates=P["dates"]; rev=P["rev"]; dau=P["dau"]; pr=P["payrate"]; suv=P["subuv"]; srev=P["subrev_d"]; n=len(dates)
comma=lambda v: format(int(round(v)), ",")
arpu=lambda i: rev[i]/dau[i] if dau[i] else 0
subarppu=lambda i: srev[i]/suv[i] if suv[i] else 0
idx=range(max(0,n-7), n)
head="| 日期 | 收入 | 付费率 | ARPU | 订阅ARPPU |\n| :-- | --: | --: | --: | --: |\n"
body="\n".join("| %s | $%s | %.3f%% | $%.3f | $%.1f |"%(dates[i][5:], comma(rev[i]), pr[i] or 0, arpu(i), subarppu(i)) for i in idx)
dm={m["key"]:m for m in P["dash_mom"]["metrics"]}
mom=dm["rev"]["mom"]; wow=dm["rev"]["wow"]
yday=((rev[-1]-rev[-2])/rev[-2]*100) if (n>1 and rev[-2]) else None
f=lambda v: "—" if v is None else (("🔺+%.1f%%"%v) if v>=0 else ("🔻%.1f%%"%v))
summ="**收入环比** · 月环比 %s · 周环比 %s · 昨日对比 %s"%(f(mom), f(wow), f(yday))
card={"msg_type":"interactive","card":{"config":{"wide_screen_mode":True},
  "header":{"title":{"tag":"plain_text","content":"📊 官网商业化日报 · 近7天(截至 %s)"%dates[-1]},"template":"blue"},
  "elements":[{"tag":"div","text":{"tag":"lark_md","content":head+body}},{"tag":"hr"},
    {"tag":"div","text":{"tag":"lark_md","content":summ}},
    {"tag":"note","elements":[{"tag":"lark_md","content":"官网直充口径 · 环比均为收入 · [进看板查看](https://luojingyu-max.github.io/reelshort-web-commercial-dashboard/)"}]}]}}
r=urllib.request.urlopen(urllib.request.Request(HOOK, data=json.dumps(card).encode(), headers={"Content-Type":"application/json"}))
print("sent:", r.read().decode())
