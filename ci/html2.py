# -*- coding: utf-8 -*-
import json
import os as _os
P = json.load(open("payload2.json"))
CHARTJS = open("chartjs.min.js").read()
WEEKLY = open("weekly_report.json", encoding="utf-8").read() if _os.path.exists("weekly_report.json") else '{"weeks":[]}'

TPL = r"""<!doctype html><html lang="zh" class=""><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<meta name="robots" content="noindex,nofollow"/>
<title>ReelShort 官网商业化数据看板</title>
<script>__CHARTJS__</script>
<style>
:root{--page:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;
 --grid:#e1e0d9;--axis:#c3c2b7;--border:rgba(11,11,11,.10);
 --s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--s5:#e87ba4;--s6:#008300;
 --good:#006300;--bad:#d03b3b;--accent:#E52E2E;--chip:#f0efec;}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])){
 --page:#0d0d0d;--surface:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--muted:#898781;
 --grid:#2c2c2a;--axis:#383835;--border:rgba(255,255,255,.10);
 --s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--s5:#d55181;--s6:#008300;
 --good:#0ca30c;--bad:#e66767;--chip:#26261f;}}
:root[data-theme="dark"]{--page:#0d0d0d;--surface:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--muted:#898781;
 --grid:#2c2c2a;--axis:#383835;--border:rgba(255,255,255,.10);
 --s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--s5:#d55181;--s6:#008300;
 --good:#0ca30c;--bad:#e66767;--chip:#26261f;}
*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:1280px;margin:0 auto;padding:20px 20px 64px}
header.top{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap;margin-bottom:14px}
h1{font-size:20px;margin:0 0 4px;letter-spacing:-.01em}
.sub{color:var(--ink2);font-size:12.5px;line-height:1.5}
.sub b{color:var(--ink)}
.toggle{border:1px solid var(--border);background:var(--surface);color:var(--ink2);border-radius:10px;padding:8px 12px;font-size:13px;cursor:pointer}
.tabs{display:flex;gap:6px;border-bottom:1px solid var(--border);margin-bottom:20px}
.tab{padding:10px 18px;font-size:14px;font-weight:600;color:var(--muted);cursor:pointer;border:0;background:none;border-bottom:2px solid transparent;margin-bottom:-1px}
.tab.on{color:var(--ink);border-bottom-color:var(--accent)}
.panel{display:none}.panel.on{display:block}
h2{font-size:14px;margin:26px 0 12px;font-weight:650}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.grid5{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:16px 16px 12px}
.card h3{margin:0 0 2px;font-size:13.5px;font-weight:600}
.card .cap{color:var(--muted);font-size:11.5px;margin:0 0 10px}
.cwrap{position:relative;height:280px}.cwrap.sm{height:96px}
.mini .lbl{color:var(--muted);font-size:11.5px}.mini .v{font-size:20px;font-weight:650;letter-spacing:-.02em;margin:2px 0}
.badge{display:inline-block;font-size:11px;padding:1px 7px;border-radius:999px;background:var(--chip);color:var(--ink2);margin-left:6px}
.prog{height:12px;border-radius:6px;background:var(--chip);overflow:hidden;margin:8px 0}
.prog>span{display:block;height:100%;background:var(--accent);border-radius:6px}
.up{color:var(--good)}.dn{color:var(--bad)}
table{width:100%;border-collapse:collapse;font-size:12.5px;font-variant-numeric:tabular-nums}
th,td{text-align:right;padding:7px 9px;border-bottom:1px solid var(--border);white-space:nowrap}
th:first-child,td:first-child{text-align:left}
th{color:var(--muted);font-weight:600;font-size:11.5px}
.warnbox{background:var(--chip);border:1px dashed var(--axis);border-radius:10px;padding:10px 12px;font-size:12px;color:var(--ink2);margin-bottom:12px}
.concl{font-size:13px;line-height:1.7;color:var(--ink2)}.concl b{color:var(--ink)}
details{margin-top:12px}summary{cursor:pointer;font-size:13px;color:var(--ink2);font-weight:600}
.filters{display:flex;flex-wrap:wrap;gap:10px;align-items:center;font-size:12.5px;color:var(--ink2)}
.filters select,.filters input{background:var(--surface);color:var(--ink);border:1px solid var(--border);border-radius:8px;padding:6px 8px;font-size:12.5px}
.fbtn{background:var(--chip);color:var(--ink);border:1px solid var(--border);border-radius:8px;padding:6px 12px;cursor:pointer;font-size:12.5px}
.fbtn:hover{border-color:var(--accent)}
#t_detail th,#t_sdetail th{position:sticky;top:0;background:var(--surface);z-index:1}
#t_sdetail th,#t_detail th,#t_d1 th,#t_d2u th,#t_d2p th{cursor:pointer;user-select:none;white-space:nowrap}
#t_sdetail th:hover,#t_detail th:hover,#t_d1 th:hover,#t_d2u th:hover,#t_d2p th:hover{color:var(--ink)}
footer{margin-top:32px;color:var(--muted);font-size:11.5px;line-height:1.6}
@media(max-width:900px){.grid2,.grid4,.grid5{grid-template-columns:1fr 1fr}}
</style></head><body><div class="wrap">
<header class="top">
 <div><h1>ReelShort 官网商业化数据看板</h1>
 <div class="sub">数据源:Lark「官网商业化面板汇总记录」快照 · 大盘 <b>2026-01-01 → __GEN__</b> · 生成 <b>__GEN__</b></div></div>
 <div style="display:flex;gap:8px;flex-wrap:wrap">
  <button class="toggle" id="up" title="上传 官网大盘.xlsx / 国家+付费.xlsx / 引流app.xlsx,自动重建看板">📤 上传Excel更新</button>
  <button class="toggle" id="tg">◐ 深/浅色</button>
 </div>
</header>
<div class="tabs">
 <button class="tab on" data-t="dash">大盘</button>
 <button class="tab" data-t="country">国家</button>
 <button class="tab" data-t="strategy">商业化策略分析</button>
 <button class="tab" data-t="weekly">周报</button>
 <button class="tab" data-t="sdetail">面板流量监控</button>
 <button class="tab" data-t="sku">SKU趋势</button>
</div>

<section class="panel on" id="p-dash">
 <div class="warnbox" id="tgt-warn"></div>
 <div class="grid4" id="dash-kpi"></div>
 <h2>核心指标 · 月环比 / 周环比</h2>
 <div class="warnbox" id="mom-note" style="border-style:solid;color:var(--ink2)"></div>
 <div class="grid5" id="dash-mom"></div>
 <h2>官网 · 全指标趋势(一眼看清)</h2>
 <p class="sub" id="cap_minis" style="margin:-6px 0 10px"></p>
 <div class="grid4" id="minis"></div>
 <h2>收入与 LTV</h2>
 <div class="grid2">
  <div class="card"><h3>官网 vs 引流App 日收入</h3><p class="cap" id="cap_ov"></p><div class="cwrap"><canvas id="c_ov"></canvas></div></div>
  <div class="card"><h3>LTV 曲线(成熟批次)</h3><p class="cap" id="cap_ltv"></p><div class="cwrap"><canvas id="c_ltv"></canvas></div></div>
 </div>
 <h2>引流App</h2>
 <div class="grid2">
  <div class="card"><h3>引流App 日收入</h3><p class="cap" id="cap_apprev"></p><div class="cwrap"><canvas id="c_apprev"></canvas></div></div>
  <div class="card"><h3>引流App 付费/订阅 UV</h3><p class="cap" id="cap_appuv"></p><div class="cwrap"><canvas id="c_appuv"></canvas></div></div>
 </div>
 <h2>各国排行 Top20 · 策略覆盖诊断</h2>
 <p class="sub" style="margin:-6px 0 10px">颜色=<b>综合评估结论</b>(DAU/付费率/订阅率/续订率/收入 一起看,均对比已覆盖 13 国中位数):🔵 已覆盖 · 🔴 <b>新增·提价</b>(值得上新且转化&续订双高,支付意愿强) · 🟠 <b>新增·降价</b>(值得上新但转化或续订偏弱,靠降价换量/保留) · ⚪ 维持兜底(规模/收入不足)。判定"值得新增"=收入≥中位数 或(DAU≥中位数且付费率≥中位数)。悬停看各指标。本月至今口径。</p>
 <div class="card" style="margin-bottom:12px"><h3>总收入 Top20 国家</h3><p class="cap" id="cap_t20rev"></p><div class="cwrap" style="height:470px"><canvas id="c_t20rev"></canvas></div></div>
 <div class="card" style="margin-bottom:12px"><h3>付费率 Top20 国家(仅收录日均DAU≥1000)</h3><p class="cap" id="cap_t20pay"></p><div class="cwrap" style="height:470px"><canvas id="c_t20pay"></canvas></div></div>
 <div class="card" style="margin-bottom:12px"><h3>订阅金额 Top20 国家</h3><p class="cap" id="cap_t20sub"></p><div class="cwrap" style="height:470px"><canvas id="c_t20sub"></canvas></div></div>
 <h2>大盘明细(官网大盘 · 逐日全字段)</h2>
 <div class="card">
  <div class="filters">
   <label>日期 <input type="date" id="s_from"></label>
   <label>~ <input type="date" id="s_to"></label>
   <input type="text" id="s_kw" placeholder="关键词(日期)"/>
   <button class="fbtn" id="s_reset">重置</button>
   <button class="fbtn" id="s_csv">导出CSV</button>
   <span class="badge" id="s_count"></span>
  </div>
  <div style="overflow:auto;max-height:520px;margin-top:10px"><table id="t_sdetail"></table></div>
 </div>
</section>

<section class="panel" id="p-country">
 <div class="warnbox" id="cwin-note"></div>
 <div class="grid2">
  <div class="card"><h3>收入 Top10 国家(已付费 vs 未付费)</h3><p class="cap" id="cap_cstack"></p><div class="cwrap"><canvas id="c_cstack"></canvas></div></div>
  <div class="card"><h3>收入 Top10 · 月环比 MoM</h3><p class="cap" id="cap_cmom"></p><div class="cwrap"><canvas id="c_mom"></canvas></div></div>
 </div>
 <div class="grid2" style="margin-top:12px">
  <div class="card"><h3>盘口覆盖国家 vs 其余国家 · 收入占比</h3><p class="cap" id="cap_covpie"></p><div class="cwrap" style="height:300px"><canvas id="c_covpie"></canvas></div></div>
  <div class="card"><h3>各国收入占比(全部国家)</h3><p class="cap" id="cap_allpie"></p><div class="cwrap" style="height:300px"><canvas id="c_allpie"></canvas></div></div>
 </div>
 <h2>盘口覆盖国家 KPI 明细(带月/周环比 · 含漏斗)</h2>
 <p class="sub" id="cap_ctab" style="margin:-6px 0 10px"></p>
 <div class="card"><div style="overflow-x:auto"><table id="t_ctab"></table></div></div>
 <h2>各国 LTV 曲线(成熟批次 · DAU加权)</h2>
 <div class="grid2">
  <div class="card"><h3>LTV 曲线 · 收入 Top6 国家</h3><p class="cap" id="cap_cltv">ltv0→ltv30 · $/人</p><div class="cwrap"><canvas id="c_cltv"></canvas></div></div>
  <div class="card"><h3>各国 LTV(全部国家)</h3><p class="cap">$/人 · ltv0 / ltv7 / ltv14 / ltv30</p><div style="overflow-x:auto;max-height:300px"><table id="t_cltv"></table></div></div>
 </div>
 <h2>各国漏斗率趋势(面板策略覆盖国家 · 按盘口分组)</h2>
 <p class="sub" id="cap_funnel" style="margin:-6px 0 10px"></p>
 <div id="funnel-cards"></div>
 <h2>国家+付费明细(国家×付费状态×日期 · 全量,可自由筛选)</h2>
 <div class="card">
  <div class="filters">
   <label>国家 <select id="f_country"></select></label>
   <label>付费状态 <select id="f_paid"><option value="">全部</option><option>已付费</option><option>未付费</option></select></label>
   <label>日期 <input type="date" id="f_from"></label>
   <label>~ <input type="date" id="f_to"></label>
   <input type="text" id="f_kw" placeholder="关键词(国家/日期)"/>
   <button class="fbtn" id="f_reset">重置</button>
   <button class="fbtn" id="f_csv">导出CSV</button>
   <span class="badge" id="f_count"></span>
  </div>
  <div style="overflow:auto;max-height:600px;margin-top:10px"><table id="t_detail"></table></div>
 </div>
</section>

<section class="panel" id="p-strategy">
 <h2>一期(6.17 · 注册国家分层)</h2>
 <div class="grid2">
  <div class="card"><h3>付费率:策略前 vs 后</h3><p class="cap">% · 各国</p><div class="cwrap"><canvas id="c_p1pay"></canvas></div></div>
  <div class="card"><h3>IAP 变化</h3><p class="cap">日均IAP$ 前后</p><div style="overflow-x:auto;max-height:280px"><table id="t_p1"></table></div></div>
 </div>
 <div class="grid2" style="margin-top:12px">
  <div class="card"><h3>一期 LTV 曲线(各国均值 · 前 vs 后)</h3><p class="cap">$/人 · ltv0/7/14/30</p><div class="cwrap"><canvas id="c_p1ltv"></canvas></div></div>
  <div class="card"><h3>一期 各国 LTV30 前后</h3><p class="cap">$/人</p><div style="overflow-x:auto;max-height:280px"><table id="t_p1ltv"></table></div></div>
 </div>
 <div class="card" style="margin-top:12px"><h3>一期结论</h3><div class="concl" id="concl1"></div></div>

 <h2>二期(7.17 · 付费状态分层:未付费 / 已付费)</h2>
 <div class="warnbox" id="p2-note"></div>
 <div class="grid2">
  <div class="card"><h3>未付费 · 付费率前后</h3><p class="cap">%</p><div class="cwrap"><canvas id="c_p2u"></canvas></div></div>
  <div class="card"><h3>已付费 · 付费率前后</h3><p class="cap">%</p><div class="cwrap"><canvas id="c_p2p"></canvas></div></div>
 </div>
 <div class="grid2" style="margin-top:12px">
  <div class="card"><h3>未付费 · IAP 变化</h3><div style="overflow-x:auto;max-height:260px"><table id="t_p2u"></table></div></div>
  <div class="card"><h3>已付费 · IAP 变化</h3><div style="overflow-x:auto;max-height:260px"><table id="t_p2p"></table></div></div>
 </div>
 <div class="grid2" style="margin-top:12px">
  <div class="card"><h3>二期·未付费 LTV(前 vs 后)</h3><p class="cap">$/人 · ltv0/1/7/14/30 · 上线仅13天,后段未成熟(前向填充,偏低)</p><div class="cwrap"><canvas id="c_p2ultv"></canvas></div></div>
  <div class="card"><h3>二期·已付费 LTV(前 vs 后)</h3><p class="cap">$/人 · ltv0/1/7/14/30 · 后段未成熟</p><div class="cwrap"><canvas id="c_p2pltv"></canvas></div></div>
 </div>
 <div class="card" style="margin-top:12px"><h3>二期结论</h3><div class="concl" id="concl2"></div></div>
 <h2>策略明细(表2 · 面板数据回收 · 全字段)</h2>
 <div class="card"><h3>一期 · 注册国家</h3><div style="overflow:auto;max-height:340px"><table id="t_d1"></table></div></div>
 <div class="grid2" style="margin-top:12px">
  <div class="card"><h3>二期 · 未付费</h3><div style="overflow:auto;max-height:340px"><table id="t_d2u"></table></div></div>
  <div class="card"><h3>二期 · 已付费</h3><div style="overflow:auto;max-height:340px"><table id="t_d2p"></table></div></div>
 </div>
 <details><summary>策略定义明细(表1 · 面板策略记录)</summary><div style="overflow-x:auto;margin-top:10px"><table id="t_strat"></table></div></details>
</section>

<section class="panel" id="p-weekly">
 <h2>产运周报 · 官网+社媒(按周查看)</h2>
 <div class="card"><div class="filters"><label>选择周 <select id="wk_sel"></select></label><button class="fbtn" id="wk_copy" title="复制本周周报(含表格),粘贴进 Lark 文档即为原生表格">📋 复制到 Lark 文档</button><span class="badge" id="wk_src"></span></div></div>
 <div id="wk_body"></div>
</section>

<section class="panel" id="p-sdetail">
 <h2>面板流量监控 · 按策略(交叉表·纯官网)</h2>
 <p class="sub" id="cap_strat" style="margin:-6px 0 12px"></p>
 <div class="grid2" style="margin-bottom:12px">
  <div class="card"><h3>各策略总收入 Top12(已付费 vs 未付费)</h3><p class="cap">区间累计 $ · 堆叠 · 数据源:交叉表-纯官网</p><div class="cwrap"><canvas id="c_srev"></canvas></div></div>
  <div class="card"><h3>说明</h3><p class="cap" style="line-height:1.7">维度:日期 × <b>是否付费</b> × <b>策略</b> × <b>注册国家</b>;指标:曝光、充值、金币充值、首订、总收入、付费后播放等。<br>下表可按<b>策略 / 付费状态 / 日期 / 关键词(注册国家)</b>筛选、点表头排序、导出 CSV。数据源为最新下载的「交叉表-纯官网数据看板」。</p></div>
 </div>
 <h2>曝光 × 充值率 × 总收入 · 策略调优视图</h2>
 <p class="sub" style="margin:-6px 0 12px">覆盖国家的每个策略一个气泡:横轴=曝光uv(对数),纵轴=曝光→充值率%,气泡大小=总收入。<b>右上大气泡</b>=高曝光高转化高产出(保/加量);<b>右下小气泡</b>=曝光大但转化低产出低(该调价/收量);<b>左上</b>=转化高但曝光小(可放量)。悬停看明细。</p>
 <div class="card"><div class="cwrap" style="height:420px"><canvas id="c_sbub"></canvas></div></div>
 <h2>各覆盖国家 · 命中策略明细(曝光 / 充值uv / 充值率 / 订阅uv占比 / 总收入)</h2>
 <p class="sub" style="margin:-6px 0 12px">表1 点名覆盖的 13 国,各自命中策略的曝光量、曝光→充值率、订阅uv占比、总收入并排对比,按曝光uv 取 Top6。<b>可选日期区间</b>看指定期内的曝光分布。</p>
 <div class="filters" style="margin-bottom:10px"><label>日期 <input type="date" id="cb_from"></label><label>~ <input type="date" id="cb_to"></label><button class="fbtn" id="cb_reset">重置</button><span class="cap" id="cb_note"></span></div>
 <div class="grid2" id="cbys"></div>
 <h2>全量明细</h2>
 <div class="card">
  <div class="filters">
   <label>策略 <select id="x_strat"></select></label>
   <label>付费状态 <select id="x_paid"><option value="">全部</option><option>已付费</option><option>未付费</option></select></label>
   <label>日期 <input type="date" id="x_from"></label><label>~ <input type="date" id="x_to"></label>
   <input type="text" id="x_kw" placeholder="关键词(注册国家)"/>
   <button class="fbtn" id="x_reset">重置</button><button class="fbtn" id="x_csv">导出CSV</button><span class="badge" id="x_count"></span>
  </div>
  <div style="overflow:auto;max-height:600px;margin-top:10px"><table id="t_xd"></table></div>
 </div>
</section>

<section class="panel" id="p-sku">
 <h2>主力 SKU 收入日曲线 · 金币 vs 订阅</h2>
 <p class="sub" id="cap_sku" style="margin:-6px 0 8px"></p>
 <div class="filters" style="margin-bottom:10px"><label>国家 <select id="sku_ctry"></select></label><span class="cap">(Top6 按所选国家重算)</span></div>
 <div class="card" style="margin-bottom:12px"><h3>金币 · Top6 SKU</h3><div class="cwrap" style="height:360px"><canvas id="c_sku_coin"></canvas></div></div>
 <div class="card" style="margin-bottom:12px"><h3>订阅 · Top6 SKU</h3><div class="cwrap" style="height:360px"><canvas id="c_sku_sub"></canvas></div></div>
 <div class="card"><h3>金币 vs 订阅 · 各阶段日均收入对比</h3><div style="overflow-x:auto"><table id="t_ksum"></table></div>
  <p class="cap" id="sku_concl" style="line-height:1.7;margin-top:10px"></p></div>
 <h2>SKU 全量明细</h2>
 <p class="sub" style="margin:-6px 0 12px">每个定价 SKU 的逐日充值/订阅/首订/续订/收入,可按 <b>SKU / 类型 / 国家 / 日期 / 关键词</b> 筛选、点表头排序、导出 CSV。<b>注:</b>国家维度仅 8/01 起有(此前历史标「全部」)。</p>
 <div class="card">
  <div class="filters">
   <label>SKU <select id="k_sku"></select></label>
   <label>类型 <select id="k_type"><option value="">全部</option><option>金币</option><option>订阅首购</option><option>订阅续订</option></select></label>
   <label>国家 <select id="k_country"></select></label>
   <label>日期 <input type="date" id="k_from"></label><label>~ <input type="date" id="k_to"></label>
   <input type="text" id="k_kw" placeholder="关键词(SKU/国家)"/>
   <button class="fbtn" id="k_reset">重置</button><button class="fbtn" id="k_csv">导出CSV</button><span class="badge" id="k_count"></span>
  </div>
  <div style="overflow:auto;max-height:600px;margin-top:10px"><table id="t_kd"></table></div>
 </div>
</section>

<footer id="foot"></footer>
</div>
<script>
const D=__PAYLOAD__;
const WR=__WEEKLY__;
const css=v=>getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const SC=()=>['--s1','--s2','--s3','--s4','--s5','--s6'].map(css);
const usd=n=>n==null?'—':'$'+Math.round(n).toLocaleString();
const usd1=n=>n==null?'—':'$'+Number(n).toFixed(1);
const ltvf=n=>n==null?'—':'$'+Number(n).toFixed(3);
const int=n=>n==null?'—':Math.round(n).toLocaleString();
const pc=(n,d=2)=>n==null?'—':n.toFixed(d)+'%';
const chg=p=>p==null?'':`<span class="${p>=0?'up':'dn'}">${p>=0?'▲':'▼'}${Math.abs(p).toFixed(1)}%</span>`;

/* ---- Chart helpers ---- */
function base(){Chart.defaults.font.family='system-ui,-apple-system,sans-serif';Chart.defaults.color=css('--muted');
 return{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},
  plugins:{legend:{display:true,labels:{color:css('--ink2'),boxWidth:12,boxHeight:12,usePointStyle:true,pointStyle:'rectRounded'}},
   tooltip:{backgroundColor:css('--surface'),titleColor:css('--ink'),bodyColor:css('--ink2'),borderColor:css('--border'),borderWidth:1,padding:9,usePointStyle:true}},
  scales:{x:{grid:{color:'transparent'},ticks:{color:css('--muted'),maxRotation:0,autoSkip:true,maxTicksLimit:8}},
   y:{grid:{color:css('--grid')},border:{display:false},ticks:{color:css('--muted')}}}};}
const L=(y,c,label)=>({label,data:y,borderColor:c,backgroundColor:c,borderWidth:2,pointRadius:0,pointHoverRadius:4,tension:.25,fill:false});
let reg={};
function mk(id,cfg){if(reg[id])reg[id].destroy();reg[id]=new Chart(document.getElementById(id),cfg);}

/* ---- header/warn ---- */
document.getElementById('cap_ltv').textContent='$ · ltv0→ltv30 · '+D.ltv_date+' 批次(已成熟)';
const compPct=D.target_cur?Math.round(D.mtd/D.target_cur*100):null;
const hit=compPct!=null&&compPct>=100;
const wb=document.getElementById('tgt-warn');
wb.style.borderStyle='solid';wb.style.color=css('--good');
wb.innerHTML=(hit?'✅ ':'')+`<b>官网大盘 = 官网直充口径</b>(不含引流App)。${D.cur_month} `+
 (hit?`<b>已达标</b>:实际 ${usd(D.mtd)} / 目标 ${usd(D.target_cur)} = <b>${compPct}%</b>(超额 ${(D.mtd/D.target_cur).toFixed(1)}×)。`
     :`实际 ${usd(D.mtd)} / 目标 ${usd(D.target_cur)} = <b>${compPct}%</b>。`)+
 ` 月度目标:7月$60k / 8月$80k / 9月$100k。`;

/* ---- KPI cards (dash) ---- */
const K=D.kpi;
document.getElementById('dash-kpi').innerHTML=[
 ['近30日总收入',usd(K.rev30),'官网大盘合计'],
 [`完成进度 (${D.cur_month})`,(compPct==null?'—':compPct+'%')+(hit?' <span class="badge" style="color:var(--good)">🎉 已达标</span>':''),`${usd(D.mtd)} / 目标 ${usd(D.target_cur)}`],
 ['最新日 DAU',int(K.dau.cur),chg(K.dau.pct)+' vs 前一日'],
 ['最新日 ARPPU',usd1(K.arppu.cur),chg(K.arppu.pct)+' vs 前一日'],
].map(([l,v,s])=>`<div class="card"><div class="mini"><div class="lbl">${l}</div><div class="v">${v}</div><div class="lbl">${s}</div></div>${l.includes('完成进度')?`<div class="prog"><span style="width:${Math.min(100,compPct||0)}%;background:${hit?css('--good'):css('--accent')}"></span></div>`:''}</div>`).join('');

/* ---- small multiples (dash) ---- */
const MINIS=[['DAU',D.dau,int],['总收入',D.rev,usd],['付费率',D.payrate,x=>pc(x,3)],['订阅率',D.subrate,x=>pc(x,3)],
 ['ARPPU',D.arppu,usd1],['充值uv',D.chargeuv,int],['订阅uv',D.subuv,int]];
document.getElementById('minis').innerHTML=MINIS.map((m,i)=>{
 const last=[...m[1]].reverse().find(v=>v!=null);
 return `<div class="card"><div class="mini"><div class="lbl">${m[0]}</div><div class="v">${m[2](last)}</div></div><div class="cwrap sm"><canvas id="mini${i}"></canvas></div></div>`;
}).join('');

/* ---- render per tab ---- */
const done={};
function top20chart(id,capId,metric,fmt,floor){
 const sc=SC(), cov={}; Object.keys(D.strat_by_country||{}).forEach(c=>cov[c]=1);
 const pool=(D.ctab||[]).filter(x=>x.rev>0 && (!floor||x.dau>=floor) && (x[metric]||0)>0);
 const rows=pool.slice().sort((a,b)=>(b[metric]||0)-(a[metric]||0)).slice(0,20);
 const md=k=>{const v=(D.ctab||[]).filter(x=>cov[x.c]).map(x=>x[k]||0).sort((a,b)=>a-b);return v.length?v[Math.floor((v.length-1)/2)]:0;};
 const medRev=md('rev'),medDau=md('dau'),medPay=md('payrate'),medRen=md('renewrate');
 const BLUE=sc[0],RED='#d64550',ORA='#eb6834',GRAY=css('--axis');
 function rec(x){
   if(cov[x.c])return['已覆盖',BLUE];
   const worth=(x.rev>=medRev)||(x.dau>=medDau && x.payrate>=medPay);   // 收入够 或 (盘子大+转化好)
   if(!worth)return['⚪维持兜底(规模/收入不足)',GRAY];
   const strong=(x.payrate>=medPay)&&((x.renewrate||0)>=medRen);        // 转化&续订双高→提价;否则降价换量
   return strong?['🔴新增·提价(转化&续订双高)',RED]:['🟠新增·降价('+(x.payrate<medPay?'转化偏弱':'续订偏弱')+')',ORA];
 }
 let o=base();o.indexAxis='y';o.plugins.legend.display=false;o.scales.x.grid.color=css('--grid');o.scales.y.grid.color='transparent';o.scales.y.ticks.autoSkip=false;o.scales.y.ticks.font={size:10};
 o.scales.x.ticks.callback=metric==='payrate'?(v=>v+'%'):(v=>'$'+(v>=1000?(v/1000).toFixed(0)+'k':v));
 o.plugins.tooltip.callbacks={label:c=>{const x=rows[c.dataIndex];return [fmt(x[metric]||0)+' · '+rec(x)[0],
   'DAU '+int(x.dau)+' · 付费率 '+Number(x.payrate).toFixed(3)+'% · 订阅率 '+Number(x.subrate).toFixed(3)+'% · 续订率 '+Number(x.renewrate||0).toFixed(0)+'%'];}};
 mk(id,{type:'bar',data:{labels:rows.map(x=>x.c),datasets:[{data:rows.map(x=>x[metric]||0),backgroundColor:rows.map(x=>rec(x)[1]),borderRadius:3,barThickness:11}]},options:o});
 const up=rows.filter(x=>rec(x)[1]===RED).map(x=>x.c), dn=rows.filter(x=>rec(x)[1]===ORA).map(x=>x.c);
 g(capId).innerHTML='综合 DAU/付费率/订阅率/续订率/收入(vs覆盖国中位数)· 🔴 新增·提价:<b>'+(up.join('、')||'无')+'</b> · 🟠 新增·降价:<b>'+(dn.join('、')||'无')+'</b>';
}
function renderDash(){
 const sc=SC();
 // 大盘 月环比/周环比
 const dm=D.dash_mom, fmtV={usd:usd,usd1:usd1,usd4:n=>'$'+Number(n).toFixed(4),pct3:n=>pc(n,3)};
 document.getElementById('dash-mom').innerHTML=dm.metrics.map(m=>
  `<div class="card"><div class="mini"><div class="lbl">${m.label}</div><div class="v">${fmtV[m.fmt](m.cur)}</div>`+
  `<div class="lbl">月环比 ${chg(m.mom)}</div><div class="lbl">周环比 ${chg(m.wow)}</div></div></div>`).join('');
 const mw=dm.win;
 document.getElementById('mom-note').innerHTML=`月环比 = 本月至今 <b>${mw.month[0]}~${mw.month[1]}</b> vs 上月同期 <b>${mw.lastmonth[0]}~${mw.lastmonth[1]}</b> · 周环比 = <b>${mw.week[0]}~${mw.week[1]}</b> vs <b>${mw.pastweek[0]}~${mw.pastweek[1]}</b>`;
 const R=D.ranges||{};
 g('cap_minis').textContent='时间范围 '+R.dash+' · 悬停看每日值';
 g('cap_ov').textContent='$ · '+R.ov;
 g('cap_apprev').textContent='$ · 充值+广告 · '+R.ov+' · 口径:7月=收入数据、8月起=每日附件(8/1有切换)';
 g('cap_appuv').textContent='人 · '+R.ov;
 mk('c_ov',{type:'line',data:{labels:D.ov_dates,datasets:[L(D.ov_site,sc[0],'官网'),L(D.ov_app,sc[1],'引流App')]},options:base()});
 let ol=base();ol.plugins.legend.display=false;ol.scales.x.ticks.maxTicksLimit=12;
 mk('c_ltv',{type:'line',data:{labels:D.ltv.map((_,i)=>'D'+i),datasets:[L(D.ltv,sc[0],'LTV')]},options:ol});
 let a1=base();a1.plugins.legend.display=false;
 mk('c_apprev',{type:'line',data:{labels:D.app.map(x=>x.date),datasets:[L(D.app.map(x=>x.rev),sc[1],'引流App收入')]},options:a1});
 mk('c_appuv',{type:'line',data:{labels:D.app.map(x=>x.date),datasets:[L(D.app.map(x=>x.pay_uv),sc[0],'付费uv'),L(D.app.map(x=>x.sub_uv),sc[2],'订阅uv')]},options:base()});
 MINIS.forEach((m,i)=>{let o=base();o.plugins.legend.display=false;o.plugins.tooltip.enabled=true;
  o.scales.x.display=true;o.scales.x.grid.display=false;o.scales.x.ticks.maxTicksLimit=2;o.scales.x.ticks.maxRotation=0;o.scales.x.ticks.font={size:9};o.scales.x.ticks.color=css('--muted');o.scales.y.display=false;o.elements={point:{radius:0}};
  mk('mini'+i,{type:'line',data:{labels:D.dates,datasets:[{data:m[1],borderColor:css('--s1'),borderWidth:1.8,pointRadius:0,pointHoverRadius:3,tension:.3,fill:true,backgroundColor:'rgba(42,120,214,.10)'}]},options:o});});
 top20chart('c_t20rev','cap_t20rev','rev',usd,0);
 top20chart('c_t20pay','cap_t20pay','payrate',v=>Number(v).toFixed(3)+'%',1000);
 top20chart('c_t20sub','cap_t20sub','subrev',usd,0);
 renderSiteDetail();
}
function renderCountry(){
 const sc=SC(),ct=D.ctab,top=ct.slice(0,10);
 let os=base();os.scales.x.stacked=true;os.scales.y.stacked=true;os.scales.x.ticks.autoSkip=false;os.scales.x.ticks.maxRotation=45;os.scales.x.ticks.minRotation=45;
 mk('c_cstack',{type:'bar',data:{labels:top.map(c=>c.c),datasets:[
   {label:'已付费',data:top.map(c=>c.rev_paid),backgroundColor:sc[0],borderRadius:3,stack:'s'},
   {label:'未付费',data:top.map(c=>c.rev_unpaid),backgroundColor:sc[3],borderRadius:3,stack:'s'}]},options:os});
 let om=base();om.plugins.legend.display=false;om.scales.x.ticks.autoSkip=false;om.scales.x.ticks.maxRotation=45;om.scales.x.ticks.minRotation=45;
 mk('c_mom',{type:'bar',data:{labels:top.map(c=>c.c),datasets:[{data:top.map(c=>c.rev_mom),
   backgroundColor:top.map(c=>c.rev_mom>=0?css('--s3'):css('--s2')),borderRadius:3}]},options:om});
 const w=D.cwindows;
 document.getElementById('cwin-note').innerHTML=`月环比 = 本月至今 <b>${w.month[0]}~${w.month[1]}</b> vs 上月同期 <b>${w.lastmonth[0]}~${w.lastmonth[1]}</b> · 周环比 = <b>${w.week[0]}~${w.week[1]}</b> vs <b>${w.pastweek[0]}~${w.pastweek[1]}</b>。收入区分已付费/未付费。`;
 const R=D.ranges||{};
 // 盘口覆盖 vs 其余 收入占比(本月至今)
 const covSet={}; Object.keys(D.strat_by_country||{}).forEach(x=>covSet[x]=1);
 let covRev=0,restRev=0; ct.forEach(x=>{ x.c in covSet? covRev+=x.rev : restRev+=x.rev; });
 const totRev=covRev+restRev||1;
 mk('c_covpie',{type:'doughnut',data:{labels:['盘口覆盖 13 国','其余国家'],datasets:[{data:[Math.round(covRev),Math.round(restRev)],backgroundColor:[sc[0],css('--axis')],borderColor:css('--surface'),borderWidth:2}]},
  options:{responsive:true,maintainAspectRatio:false,cutout:'58%',plugins:{legend:{position:'right',labels:{color:css('--ink2'),usePointStyle:true,pointStyle:'rectRounded',boxWidth:12}},tooltip:{callbacks:{label:c=>c.label+': '+usd(c.raw)+' ('+(c.raw/totRev*100).toFixed(1)+'%)'}}}}});
 g('cap_covpie').textContent='本月至今 '+R.country+' · 盘口13国 '+(covRev/totRev*100).toFixed(1)+'% / 其余 '+(restRev/totRev*100).toFixed(1)+'%';
 // 全部国家收入占比:每个有收入的国家各一块(不聚合),按收入排序,金色角度分色
 const allc=ct.filter(x=>x.rev>0);
 const acols=allc.map((_,i)=>`hsl(${(i*137.508)%360},62%,55%)`);
 mk('c_allpie',{type:'doughnut',data:{labels:allc.map(x=>x.c),
   datasets:[{data:allc.map(x=>Math.round(x.rev)),backgroundColor:acols,borderColor:css('--surface'),borderWidth:1}]},
  options:{responsive:true,maintainAspectRatio:false,cutout:'55%',plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>c.label+': '+usd(c.raw)+' ('+(c.raw/totRev*100).toFixed(1)+'%)'}}}}});
 g('cap_allpie').textContent='本月至今 '+R.country+' · 全部 '+allc.length+' 个有收入国家各占一块(按收入排序)· 悬停看明细';
 g('cap_cstack').textContent='本月至今 '+R.country+' · $ · 堆叠 · 收入前10';
 g('cap_cmom').textContent='本月至今 '+R.country+' vs 上月同期 '+R.country_prev+' · %';
 g('cap_ctab').textContent='时间窗口:本月至今 '+R.country+' · 仅列盘口覆盖国家(按盘口分组)。漏斗逐级转化:观看率=观看/DAU、触达付费集率=触达/观看、创建订单率=订单/触达;付费率=充值uv/DAU;ARPU=总收入/DAU。全量国家见下方明细。';
 const gmap={},gord=[]; ((D.funnel||{}).groups||[]).forEach(gr=>gr.countries.forEach(c=>{gmap[c]=gr.name;gord.push(c);}));
 const ctf=gord.map(cn=>ct.find(x=>x.c===cn)).filter(Boolean);
 document.getElementById('t_ctab').innerHTML=
  '<thead><tr><th>盘口</th><th>国家</th><th>本月收入</th><th>已付费</th><th>未付费</th><th>MoM</th><th>WoW</th><th>观看率</th><th>触达付费集率</th><th>创建订单率</th><th>付费率</th><th>ARPU</th><th>ARPPU</th><th>日均DAU</th></tr></thead><tbody>'+
  ctf.map(c=>`<tr><td>${gmap[c.c]||''}</td><td>${c.c}</td><td>${usd(c.rev)}</td><td>${usd(c.rev_paid)}</td><td>${usd(c.rev_unpaid)}</td><td>${chg(c.rev_mom)}</td><td>${chg(c.rev_wow)}</td><td>${pc(c.viewrate,2)}</td><td>${pc(c.reachrate,2)}</td><td>${pc(c.orderrate,3)}</td><td>${pc(c.payrate,3)}</td><td>$${Number(c.arpu).toFixed(4)}</td><td>${usd1(c.arppu)}</td><td>${int(c.dau)}</td></tr>`).join('')+'</tbody>';
 // 各国 LTV 曲线(Top6)+ 全量表
 const cl=D.country_ltv, top6=ct.slice(0,6).map(c=>c.c);
 let ol=base(); ol.scales.x.ticks.maxTicksLimit=8;
 mk('c_cltv',{type:'line',data:{labels:cl.curve[cl.countries[0]].map((_,i)=>'D'+i),
   datasets:top6.map((c,i)=>L(cl.curve[c],sc[i%6],c))},options:ol});
 document.getElementById('cap_cltv').textContent='ltv0→ltv30 · $/人 · 成熟批次(≤'+cl.mature_cut+')';
 document.getElementById('t_cltv').innerHTML='<thead><tr><th>国家</th><th>LTV0</th><th>LTV7</th><th>LTV14</th><th>LTV30</th></tr></thead><tbody>'+
  D.country_ltv_table.map(r=>`<tr><td>${r.c}</td><td>${ltvf(r.ltv0)}</td><td>${ltvf(r.ltv7)}</td><td>${ltvf(r.ltv14)}</td><td>${ltvf(r.ltv30)}</td></tr>`).join('')+'</tbody>';
 // 各国漏斗率日趋势(按盘口分组,组内国家可筛选)
 const F=D.funnel||{dates:[],groups:[],raw:{}}, sc3=SC();
 g('funnel-cards').innerHTML=F.groups.map((grp,i)=>`<div class="card" style="margin-bottom:12px"><div class="filters" style="align-items:center"><h3 style="margin:0 8px 0 0">${grp.name}</h3><label>国家 <select id="fsel${i}"><option>全部</option>${grp.countries.map(c=>`<option>${c}</option>`).join('')}</select></label></div><div class="cwrap" style="height:290px"><canvas id="fc${i}"></canvas></div></div>`).join('');
 function fdraw(i){const grp=F.groups[i], sel=g('fsel'+i).value, cs=(sel==='全部')?grp.countries:[sel], n=F.dates.length;
  const sum=key=>{let a=new Array(n).fill(0); cs.forEach(c=>{const r=F.raw[c]; if(r)for(let j=0;j<n;j++)a[j]+=r[key][j];}); return a;};
  const vv=sum('view'),rc=sum('reach'),oo=sum('order'),pp=sum('pay'),dd=sum('dau');
  const div=(a,b)=>a.map((x,j)=>b[j]?+(x/b[j]*100).toFixed(2):null);
  let o=base();o.interaction={mode:'index',intersect:false};o.scales.x.ticks.maxTicksLimit=9;o.scales.y.ticks.callback=v=>v+'%';
  mk('fc'+i,{type:'line',data:{labels:F.dates,datasets:[L(div(vv,dd),sc3[0],'观看率(观看/DAU)'),L(div(rc,vv),sc3[1],'触达付费集率(触达/观看)'),L(div(oo,rc),sc3[2],'创建订单率(订单/触达)'),L(div(pp,dd),sc3[3],'付费率(充值uv/DAU)')]},options:o});}
 F.groups.forEach((_,i)=>{g('fsel'+i).addEventListener('change',()=>fdraw(i)); fdraw(i);});
 g('cap_funnel').textContent='漏斗逐级转化率:观看率=观看/DAU、触达付费集率=触达/观看、创建订单率=订单/触达、付费率=充值uv/DAU · 按盘口分 5 组,组内国家可筛选(默认=组内汇总)· '+(F.dates.length?F.dates[0]+' ~ '+F.dates[F.dates.length-1]:'');
 renderCountryDetail();
}
function grouped(id,rows,ka,kb){const sc=SC();let o=base();o.scales.x.ticks.autoSkip=false;o.scales.x.ticks.maxRotation=50;o.scales.x.ticks.minRotation=50;
 mk(id,{type:'bar',data:{labels:rows.map(r=>r.c),datasets:[
  {label:'前',data:rows.map(r=>r[ka]),backgroundColor:sc[0],borderRadius:3},
  {label:'后',data:rows.map(r=>r[kb]),backgroundColor:sc[1],borderRadius:3}]},options:o});}
function iapTable(id,rows){document.getElementById(id).innerHTML=
 '<thead><tr><th>国家</th><th>IAP前</th><th>IAP后</th><th>变化</th></tr></thead><tbody>'+
 rows.map(r=>{const u=String(r.iapchg||r.iapchg).includes('+');return `<tr><td>${r.c}</td><td>${usd(r.iap_a!=null?r.iap_a:r[11])}</td><td>${usd(r.iap_b!=null?r.iap_b:r[12])}</td><td class="${u?'up':'dn'}">${r.iapchg}</td></tr>`}).join('')+'</tbody>';}
function renderStrategy(){
 // 一期 from doc panel1: cols 0国家,3付费率前,4付费率后,11 IAP前,12 IAP后,13 变化
 const p1=D.panel1.map(r=>({c:r[0],pr_a:+r[3],pr_b:+r[4],iap_a:+r[11],iap_b:+r[12],iapchg:r[13]}));
 grouped('c_p1pay',p1,'pr_a','pr_b');
 iapTable('t_p1',p1);
 grouped('c_p2u',D.phase2_unpaid,'pr_a','pr_b');
 grouped('c_p2p',D.phase2_paid,'pr_a','pr_b');
 iapTable('t_p2u',D.phase2_unpaid);
 iapTable('t_p2p',D.phase2_paid);
 // ---- strategy LTV curves ----
 const sc=SC();
 const P1=D.panel1;
 function aggLtv(front){const wi=front?1:2, cols=front?[14,16,18,20]:[15,17,19,21];
   let w=0,acc=[0,0,0,0]; P1.forEach(r=>{const dw=+r[wi]||0; w+=dw; cols.forEach((ci,k)=>acc[k]+=(+r[ci]||0)*dw);});
   return w?acc.map(v=>+(v/w).toFixed(4)):[null,null,null,null];}
 mk('c_p1ltv',{type:'line',data:{labels:['D0','D7','D14','D30'],datasets:[L(aggLtv(true),sc[0],'前'),L(aggLtv(false),sc[1],'后')]},options:base()});
 document.getElementById('t_p1ltv').innerHTML='<thead><tr><th>国家</th><th>LTV30前</th><th>LTV30后</th></tr></thead><tbody>'+
  P1.map(r=>`<tr><td>${r[0]}</td><td>${ltvf(+r[20])}</td><td>${ltvf(+r[21])}</td></tr>`).join('')+'</tbody>';
 const pl=D.phase2_ltv, plab=pl.pts.map(k=>'D'+k);
 mk('c_p2ultv',{type:'line',data:{labels:plab,datasets:[L(pl.unpaid_pre,sc[0],'前'),L(pl.unpaid_post,sc[1],'后')]},options:base()});
 mk('c_p2pltv',{type:'line',data:{labels:plab,datasets:[L(pl.paid_pre,sc[0],'前'),L(pl.paid_post,sc[1],'后')]},options:base()});
 // conclusions
 const upc=a=>a.filter(x=>String(x.iapchg).includes('+')).map(x=>x.c);
 const dnc=a=>a.filter(x=>!String(x.iapchg).includes('+')).map(x=>x.c);
 document.getElementById('concl1').innerHTML=
  `一期按<b>注册国家</b>分层(6.17)。付费率普遍抬升,美国 ${p1[0].pr_a}%→${p1[0].pr_b}%。IAP 增长显著的有 ${upc(p1).slice(0,6).join('、')} 等。详见上表与柱图。`;
 const u=D.phase2_unpaid,p=D.phase2_paid, R=D.ranges||{};
 g('p2-note').innerHTML=`二期按同口径<b>实时增量计算</b>——前窗 <b>${R.phase2_pre}</b> / 后窗 <b>${R.phase2_post}</b>(后窗随最新日 ${R.maxd} 滚动;IAP=日均总收入)。当时该 Lark 表 App 无写权限,故此处为计算值;LTV 后段未成熟仅供参考。`;
 document.getElementById('concl2').innerHTML=
  `二期按<b>付费状态</b>分层(7.17),对比窗口 前 <b>${R.phase2_pre}</b> / 后 <b>${R.phase2_post}</b>。<br><b>已付费</b>:IAP 上涨 ${upc(p).length}/${p.length} 国,策略生效,建议保留推广。<br><b>未付费</b>:分化明显——涨的 ${upc(u).join('、')||'无'};跌的 ${dnc(u).join('、')||'无'} 多为成熟市场,需回调定价或再测。`;
 // strategy definition table
 const sh=D.strategy_header;
 document.getElementById('t_strat').innerHTML='<thead><tr>'+['层级','国家','策略名称/画像ID','上架时间','盘口','用户画像'].map(x=>`<th>${x}</th>`).join('')+'</tr></thead><tbody>'+
  D.strategy.map(r=>`<tr><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${r[10]}</td><td>${r[11]}</td><td style="text-align:left">${r[5]}</td></tr>`).join('')+'</tbody>';
 // 策略明细(表2)
 document.getElementById('t_d1').innerHTML='<thead><tr>'+D.panel1_header.map(c=>`<th>${c}</th>`).join('')+'</tr></thead><tbody>'+
  D.panel1.map(r=>'<tr>'+r.map(v=>`<td>${v==null?'':v}</td>`).join('')+'</tr>').join('')+'</tbody>';
 const p2cols=['国家','付费率前','付费率后','订阅率前','订阅率后','ARPPU前','ARPPU后','IAP前','IAP后','IAP变化','LTV0前','LTV0后','LTV7前','LTV7后','LTV14前','LTV14后','LTV30前','LTV30后'];
 const p2row=r=>`<tr><td>${r.c}</td><td>${r.pr_a}</td><td>${r.pr_b}</td><td>${r.sr_a}</td><td>${r.sr_b}</td><td>${usd1(r.arppu_a)}</td><td>${usd1(r.arppu_b)}</td><td>${usd(r.iap_a)}</td><td>${usd(r.iap_b)}</td><td>${r.iapchg}</td><td>${ltvf(r.l0_a)}</td><td>${ltvf(r.l0_b)}</td><td>${ltvf(r.l7_a)}</td><td>${ltvf(r.l7_b)}</td><td>${ltvf(r.l14_a)}</td><td>${ltvf(r.l14_b)}</td><td>${ltvf(r.l30_a)}</td><td>${ltvf(r.l30_b)}</td></tr>`;
 const p2html=rows=>'<thead><tr>'+p2cols.map(c=>`<th>${c}</th>`).join('')+'</tr></thead><tbody>'+rows.map(p2row).join('')+'</tbody>';
 document.getElementById('t_d2u').innerHTML=p2html(D.phase2_unpaid);
 document.getElementById('t_d2p').innerHTML=p2html(D.phase2_paid);
 ['t_d1','t_d2u','t_d2p'].forEach(makeSortable);
}
const g=id=>document.getElementById(id);
function makeSortable(id){
 const t=g(id); if(!t||t.dataset.sortable)return; t.dataset.sortable='1';
 t.addEventListener('click',e=>{
  const th=e.target.closest('th'); if(!th||!th.parentNode||th.parentNode.parentNode.tagName!=='THEAD')return;
  const heads=[...th.parentNode.children], idx=heads.indexOf(th), asc=th.dataset.dir!=='asc';
  heads.forEach(h=>{h.dataset.dir='';h.innerHTML=h.innerHTML.replace(/\s*[▲▼]$/,'');});
  th.dataset.dir=asc?'asc':'desc';
  const tb=t.querySelector('tbody'); if(!tb)return;
  const parse=s=>{const c=String(s).replace(/[$%\s]/g,'').replace(/,/g,''); return (c!==''&&/^[+-]?\d*\.?\d+$/.test(c))?Number(c):String(s);};
  [...tb.children].sort((a,b)=>{const x=parse(a.children[idx]?a.children[idx].textContent:''),y=parse(b.children[idx]?b.children[idx].textContent:'');
    if(typeof x==='number'&&typeof y==='number')return asc?x-y:y-x;
    return asc?String(x).localeCompare(String(y),'zh'):String(y).localeCompare(String(x),'zh');})
   .forEach(r=>tb.appendChild(r));
  th.innerHTML=th.innerHTML.replace(/\s*[▲▼]$/,'')+(asc?' ▲':' ▼');
 });
}
function makeFilterTable(o){
 let filt=[];
 function apply(){
  const c=o.ids.country?g(o.ids.country).value:'',p=o.ids.paid?g(o.ids.paid).value:'',e=o.ids.extra?g(o.ids.extra).value:'';
  const fr=g(o.ids.from).value,to=g(o.ids.to).value,kw=(g(o.ids.kw).value||'').trim();
  filt=o.rows.filter(r=>(!c||r[o.cIdx]===c)&&(!p||r[o.pIdx]===p)&&(!e||r[o.eIdx]===e)&&(!fr||r[0]>=fr)&&(!to||r[0]<=to)&&(!kw||(o.kwCols||[0,1]).map(i=>r[i]).join(' ').indexOf(kw)>=0));
  g(o.ids.table).querySelector('tbody').innerHTML=filt.map(r=>'<tr>'+r.map((v,i)=>`<td>${o.fmt(v,i)}</td>`).join('')+'</tr>').join('');
  g(o.ids.count).textContent=filt.length+' / '+o.rows.length+' 行';
 }
 return function(){
  g(o.ids.table).innerHTML='<thead><tr>'+o.cols.map(c=>`<th>${c}</th>`).join('')+'</tr></thead><tbody></tbody>';
  const t=g(o.ids.table);
  makeSortable(o.ids.table);
  if(!t.dataset.init){
   if(o.ids.country)g(o.ids.country).innerHTML=`<option value="">${o.selLabel||'全部国家'}</option>`+o.countries.map(c=>`<option>${c}</option>`).join('');
   if(o.ids.extra)g(o.ids.extra).innerHTML=`<option value="">${o.extraLabel||'全部'}</option>`+(o.extraOpts||[]).map(x=>`<option>${x}</option>`).join('');
   const mn=o.rows[0][0],mx=o.rows[o.rows.length-1][0];
   g(o.ids.from).value=mn;g(o.ids.to).value=mx;
   [o.ids.from,o.ids.to,o.ids.country,o.ids.paid,o.ids.extra].filter(Boolean).forEach(id=>g(id).addEventListener('change',apply));
   g(o.ids.kw).addEventListener('input',apply);
   g(o.ids.reset).onclick=()=>{if(o.ids.country)g(o.ids.country).value='';if(o.ids.paid)g(o.ids.paid).value='';if(o.ids.extra)g(o.ids.extra).value='';g(o.ids.from).value=mn;g(o.ids.to).value=mx;g(o.ids.kw).value='';apply();};
   g(o.ids.csv).onclick=()=>{const lines=[o.cols.join(',')].concat(filt.map(r=>r.join(',')));const a=document.createElement('a');a.href=URL.createObjectURL(new Blob(['﻿'+lines.join('\n')],{type:'text/csv;charset=utf-8'}));a.download=o.csv;a.click();};
   t.dataset.init='1';
  }
  apply();
 };
}
const gnum=v=>typeof v==='number'?(Math.abs(v)>=100?Math.round(v).toLocaleString():(Number.isInteger(v)?v:(Math.abs(v)<1?v.toFixed(4):v.toFixed(2)))):v;
const renderSiteDetail=makeFilterTable({rows:D.site_detail,cols:D.site_detail_cols,cIdx:-1,pIdx:-1,
 fmt:(v,i)=>i===0?v:gnum(v),csv:'大盘明细.csv',
 ids:{from:'s_from',to:'s_to',kw:'s_kw',reset:'s_reset',csv:'s_csv',count:'s_count',table:'t_sdetail'}});
const renderCountryDetail=makeFilterTable({rows:D.detail,cols:D.detail_cols,cIdx:1,pIdx:2,countries:D.detail_countries,
 fmt:(v,i)=>i<3?v:(i===6?usd(v):i>=7?ltvf(v):int(v)),csv:'国家付费明细.csv',
 ids:{country:'f_country',paid:'f_paid',from:'f_from',to:'f_to',kw:'f_kw',reset:'f_reset',csv:'f_csv',count:'f_count',table:'t_detail'}});
function wcell(v){const s=String(v);
 if(s.indexOf('→')>=0){const p=s.split('→');const a=parseFloat(p[0].replace(/[^0-9.\-]/g,'')),b=parseFloat(p[1].replace(/[^0-9.\-]/g,''));
   if(!isNaN(a)&&!isNaN(b)&&a!==b) return `<span class="${b>a?'up':'dn'}">${s}</span>`; return s;}
 const m=s.match(/^([+-])[\d.]/); if(m) return `<span class="${m[1]==='+'?'up':'dn'}">${s}</span>`;
 return s;}
function wtbl(o){return '<div style="overflow-x:auto"><table><thead><tr>'+o.cols.map(c=>`<th>${c}</th>`).join('')+'</tr></thead><tbody>'+o.rows.map(r=>'<tr>'+r.map((v,i)=>`<td${i===0?' style="text-align:left"':''}>${i===0?v:wcell(v)}</td>`).join('')+'</tr>').join('')+'</tbody></table></div>';}
function drawWeek(){
 const w=WR.weeks[+g('wk_sel').value||0]; if(!w){g('wk_body').innerHTML='<div class="card">暂无周报数据</div>';return;}
 let h='';
 if(w.summary&&w.summary.length) h+='<div class="card"><h3>本周摘要</h3><div class="concl">'+w.summary.map(s=>'• '+s).join('<br>')+'</div></div>';
 if(w.dapan) h+='<div class="card" style="margin-top:12px"><h3>大盘数据回收</h3>'+wtbl(w.dapan)+'</div>';
 if(w.phase2) h+='<div class="card" style="margin-top:12px"><h3>二期面板策略数据回收</h3><p class="cap">'+(w.phase2.note||'')+'</p>'+wtbl(w.phase2)+'</div>';
 if(w.ab) h+='<div class="card" style="margin-top:12px"><h3>AB 实验 · 美国 12.99 周卡(初步)</h3><p class="cap">'+(w.ab.note||'')+'</p>'+wtbl(w.ab)+'</div>';
 if(w.concl&&w.concl.length) h+='<div class="card" style="margin-top:12px"><h3>结论与现状</h3><div class="concl">'+w.concl.map(s=>'• '+s).join('<br>')+'</div></div>';
 h+='<div class="card" style="margin-top:12px"><h3>社媒</h3><div class="concl">'+(w.social||'暂无数据')+'</div></div>';
 g('wk_body').innerHTML=h;
}
function copyWeekLark(){
 const w=WR.weeks[+g('wk_sel').value||0]; if(!w) return;
 const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
 const htbl=o=>{if(!o||!o.cols)return'';return '<table border="1" cellspacing="0" cellpadding="5" style="border-collapse:collapse;font-size:13px"><thead><tr>'+o.cols.map(c=>`<th style="background:#f0f2f5">${esc(c)}</th>`).join('')+'</tr></thead><tbody>'+o.rows.map(r=>'<tr>'+r.map(v=>`<td>${esc(v)}</td>`).join('')+'</tr>').join('')+'</tbody></table>';};
 const ttbl=o=>{if(!o||!o.cols)return'';return o.cols.join('\t')+'\n'+o.rows.map(r=>r.join('\t')).join('\n')+'\n';};
 let H=`<h3>产运周报 · ${esc(w.date)}</h3>`, T=`产运周报 · ${w.date}\n\n`;
 if(w.summary&&w.summary.length){H+='<p><b>本周摘要</b></p><ul>'+w.summary.map(s=>`<li>${esc(s)}</li>`).join('')+'</ul>'; T+='【本周摘要】\n'+w.summary.map(s=>'• '+s).join('\n')+'\n\n';}
 if(w.dapan){H+='<p><b>大盘数据回收</b></p>'+htbl(w.dapan); T+='【大盘数据回收】\n'+ttbl(w.dapan)+'\n';}
 if(w.phase2){H+=`<p><b>二期面板策略数据回收</b><br><i>${esc(w.phase2.note||'')}</i></p>`+htbl(w.phase2); T+='【二期面板策略数据回收】\n'+(w.phase2.note||'')+'\n'+ttbl(w.phase2)+'\n';}
 if(w.ab){H+=`<p><b>AB 实验 · 美国 12.99 周卡</b><br><i>${esc(w.ab.note||'')}</i></p>`+htbl(w.ab); T+='【AB 实验 · 美国 12.99 周卡】\n'+(w.ab.note||'')+'\n'+ttbl(w.ab)+'\n';}
 if(w.concl&&w.concl.length){H+='<p><b>结论与现状</b></p><ul>'+w.concl.map(s=>`<li>${esc(s)}</li>`).join('')+'</ul>'; T+='【结论与现状】\n'+w.concl.map(s=>'• '+s).join('\n')+'\n';}
 const btn=g('wk_copy'), ok=()=>{const o=btn.textContent; btn.textContent='✅ 已复制,去 Lark 粘贴'; setTimeout(()=>btn.textContent=o,2200);};
 if(navigator.clipboard&&window.ClipboardItem){
   navigator.clipboard.write([new ClipboardItem({'text/html':new Blob([H],{type:'text/html'}),'text/plain':new Blob([T],{type:'text/plain'})})]).then(ok,()=>cpFallback(T,ok));
 }else cpFallback(T,ok);
}
function cpFallback(t,ok){const ta=document.createElement('textarea');ta.value=t;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.select();try{document.execCommand('copy');ok();}catch(e){alert('复制失败,请手动选择');}document.body.removeChild(ta);}
function renderWeekly(){
 const sel=g('wk_sel');
 if(!sel.dataset.init){ sel.innerHTML=(WR.weeks||[]).map((w,i)=>`<option value="${i}">${w.date}</option>`).join(''); sel.addEventListener('change',drawWeek); const cb=g('wk_copy'); if(cb) cb.addEventListener('click',copyWeekLark); sel.dataset.init='1'; }
 g('wk_src').textContent=WR.source||'';
 drawWeek();
}
const renderStratTable=makeFilterTable({rows:D.strat_detail,cols:D.strat_detail_cols,cIdx:2,pIdx:1,countries:D.strat_list,selLabel:'全部策略',kwCols:[0,3],
 fmt:(v,i)=>i<4?v:((i===12||i===13||i===14)?usd(v):int(v)),csv:'面板策略明细.csv',
 ids:{country:'x_strat',paid:'x_paid',from:'x_from',to:'x_to',kw:'x_kw',reset:'x_reset',csv:'x_csv',count:'x_count',table:'t_xd'}});
function drawCbys(){
 const cov=Object.keys(D.strat_by_country||{}), covset={}; cov.forEach(c=>covset[c]=1);
 const fr=g('cb_from').value, to=g('cb_to').value, agg={};
 (D.strat_detail||[]).forEach(r=>{ if(!covset[r[3]])return; if(fr&&r[0]<fr)return; if(to&&r[0]>to)return;
   const c=r[3],s=r[2]; (agg[c]=agg[c]||{}); const a=(agg[c][s]=agg[c][s]||{e:0,p:0,f:0,rev:0});
   a.e+=r[5]; a.p+=r[7]; a.f+=r[11]; a.rev+=r[12]; });
 const sl=s=>s.replace('官网-','').replace('-kim','').replace('kim ','');
 const cks=cov.filter(c=>agg[c]);
 g('cb_note').textContent='区间 '+(fr||'起')+' ~ '+(to||'今')+' · 命中 '+cks.length+' 国';
 g('cbys').innerHTML=cks.map(c=>{
   const its=Object.keys(agg[c]).map(s=>{const a=agg[c][s];return {sl:sl(s),exp:a.e,pay:a.p,rate:a.e?a.p/a.e*100:0,subr:a.p?a.f/a.p*100:0,rev:a.rev};}).filter(x=>x.exp>0).sort((a,b)=>b.exp-a.exp).slice(0,6);
   return `<div class="card"><h3 style="margin:0 0 8px">${c} · 命中 ${its.length} 策略</h3><div style="overflow-x:auto"><table><thead><tr><th style="text-align:left">策略</th><th>曝光uv</th><th>充值uv</th><th>充值率</th><th>订阅uv占比</th><th>总收入</th></tr></thead><tbody>`+its.map(x=>`<tr><td style="text-align:left">${x.sl}</td><td>${int(x.exp)}</td><td>${int(x.pay)}</td><td>${x.rate.toFixed(2)}%</td><td>${x.subr.toFixed(1)}%</td><td>${usd(x.rev)}</td></tr>`).join('')+`</tbody></table></div></div>`;
 }).join('');
}
function renderSdetail(){
 g('cap_strat').textContent='时间范围 '+((D.ranges||{}).strat||'')+' · 卡片为区间累计;下表可按策略/付费/国家/日期筛选';
 const sc=SC(); let o=base(); o.indexAxis='y';
 o.scales.y.grid.color='transparent'; o.scales.y.ticks.autoSkip=false; o.scales.x.stacked=true; o.scales.y.stacked=true; o.scales.x.grid.color=css('--grid'); o.scales.x.ticks.callback=v=>'$'+(v/1000)+'k';
 mk('c_srev',{type:'bar',data:{labels:D.strat_rev.map(x=>x.s),datasets:[
   {label:'已付费',data:D.strat_rev.map(x=>x.paid),backgroundColor:sc[0],borderRadius:3,barThickness:12,stack:'s'},
   {label:'未付费',data:D.strat_rev.map(x=>x.unpaid),backgroundColor:sc[3],borderRadius:3,barThickness:12,stack:'s'}]},options:o});
 // 气泡:曝光(x·对数) × 充值率(y) × 总收入(气泡大小)
 const ha=(h,a)=>{const n=parseInt(h.slice(1),16);return 'rgba('+(n>>16&255)+','+(n>>8&255)+','+(n&255)+','+a+')';};
 const bub=(D.strat_bubble||[]).map(p=>({x:Math.max(p.exp,1),y:p.rate,r:Math.max(3,Math.min(32,Math.sqrt(p.rev)/4)),_c:p.c,_s:p.sl,_e:p.exp,_rate:p.rate,_rev:p.rev}));
 let bo=base(); bo.plugins.legend.display=false; bo.interaction={mode:'nearest',intersect:true};
 bo.scales.x.type='logarithmic'; bo.scales.x.grid.color=css('--grid'); bo.scales.x.title={display:true,text:'曝光uv(对数)',color:css('--muted')}; bo.scales.x.ticks.callback=v=>{const L=[10,100,1000,10000,100000];return L.indexOf(v)>=0?int(v):'';};
 bo.scales.y.title={display:true,text:'曝光→充值率 %',color:css('--muted')}; bo.scales.y.ticks.callback=v=>v+'%';
 bo.plugins.tooltip.callbacks={title:()=>'',label:c=>{const d=c.raw;return [d._c+' · '+d._s,'曝光uv '+int(d._e)+'  ·  充值率 '+d._rate+'%','总收入 '+usd(d._rev)];}};
 mk('c_sbub',{type:'bubble',data:{datasets:[{data:bub,backgroundColor:ha(sc[0],.5),borderColor:sc[0],borderWidth:1,hoverBackgroundColor:ha(sc[1],.7)}]},options:bo});
 // 各覆盖国家命中策略明细(按日期区间前端重算,见 drawCbys)
 const cbDates=(D.strat_detail||[]).map(r=>r[0]);
 const cbMin=cbDates.length?cbDates.reduce((a,b)=>a<b?a:b):'', cbMax=cbDates.length?cbDates.reduce((a,b)=>a>b?a:b):'';
 if(!g('cb_from').dataset.init){ g('cb_from').value=cbMin; g('cb_to').value=cbMax;
   ['cb_from','cb_to'].forEach(id=>{g(id).addEventListener('change',drawCbys);g(id).addEventListener('input',drawCbys);});
   g('cb_reset').onclick=()=>{g('cb_from').value=cbMin;g('cb_to').value=cbMax;drawCbys();};
   g('cb_from').dataset.init='1'; }
 drawCbys();
 renderStratTable();
}
const renderSkuTable=makeFilterTable({rows:D.sku_detail,cols:D.sku_detail_cols,cIdx:1,pIdx:2,eIdx:4,countries:D.sku_list,selLabel:'全部SKU',
 extraOpts:D.sku_countries,extraLabel:'全部国家',kwCols:[1,4],
 fmt:(v,i)=>i<=2?v:(i===3?('$'+v):(i===4?v:(i<=9?int(v):usd(v)))),csv:'SKU明细.csv',
 ids:{country:'k_sku',paid:'k_type',extra:'k_country',from:'k_from',to:'k_to',kw:'k_kw',reset:'k_reset',csv:'k_csv',count:'k_count',table:'t_kd'}});
function skuChart(id,series){
 const sc=SC(), dts=D.sku_dates||[];
 const nodes=(D.sku_nodes||[]).map(n=>({i:dts.indexOf(n.date),label:n.label})).filter(n=>n.i>=0);
 const nodePlugin={id:'skunodes',afterDraw(ch){const a=ch.chartArea,x=ch.scales.x,ctx=ch.ctx;ctx.save();nodes.forEach(n=>{const px=x.getPixelForValue(n.i);ctx.strokeStyle=css('--axis');ctx.setLineDash([4,4]);ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(px,a.top);ctx.lineTo(px,a.bottom);ctx.stroke();ctx.setLineDash([]);ctx.fillStyle=css('--muted');ctx.font='10px system-ui';ctx.textAlign='center';ctx.fillText(n.label,px,a.top-4);});ctx.restore();}};
 let o=base(); o.layout={padding:{top:16}}; o.scales.x.ticks.maxTicksLimit=10; o.scales.y.ticks.callback=v=>'$'+(v>=1000?(v/1000)+'k':v); o.plugins.legend.labels.font={size:10};
 mk(id,{type:'line',data:{labels:dts,datasets:(series||[]).map((s,i)=>L(s.data,sc[i%6],s.name.length>20?s.name.slice(0,20)+'…':s.name))},options:o,plugins:[nodePlugin]});
}
function drawSku(){
 const country=g('sku_ctry').value, dts=D.sku_dates||[], di={}; dts.forEach((d,i)=>di[d]=i);
 const cB={},sB={},cT={},sT={};
 (D.sku_detail||[]).forEach(r=>{ if(country&&r[4]!==country)return; const sku=r[1],j=di[r[0]]; if(j==null)return;
  const coin=r[2]==='金币', by=coin?cB:sB, tot=coin?cT:sT; (by[sku]=by[sku]||new Array(dts.length).fill(0))[j]+=r[15]; tot[sku]=(tot[sku]||0)+r[15]; });
 const top=(by,tot)=>Object.keys(tot).sort((a,b)=>tot[b]-tot[a]).slice(0,6).map(k=>({name:k,data:by[k].map(v=>+v.toFixed(2))}));
 skuChart('c_sku_coin',top(cB,cT)); skuChart('c_sku_sub',top(sB,sT));
}
function renderSku(){
 g('cap_sku').innerHTML='各取 Top6 SKU 的每日收入($),按商品类型分两图,<b>可按国家筛选</b>;虚线节点:<b>6.17 一期</b> / <b>7.17 二期</b> / <b>8.8 三期(改未付费金币档位)</b>。时间范围 '+((D.ranges||{}).sku||'')+' · <b>仅面板策略覆盖 13 国</b>(约占官网直充 70%)。';
 const cs=g('sku_ctry');
 if(!cs.dataset.init){ cs.innerHTML='<option value="">全部国家</option>'+(D.sku_countries||[]).map(c=>`<option>${c}</option>`).join(''); cs.addEventListener('change',drawSku); cs.dataset.init='1'; }
 drawSku();
 const su=D.sku_summary||{wins:[],rows:[]}; const pc=(c,p)=>p?((c-p)/p*100>=0?'+':'')+((c-p)/p*100).toFixed(0)+'%':'—';
 g('t_ksum').innerHTML='<thead><tr><th style="text-align:left">类型 · 日均收入</th>'+su.wins.map(w=>`<th>${w}</th>`).join('')+'</tr></thead><tbody>'+
  su.rows.map(r=>'<tr><td style="text-align:left"><b>'+r.k+'</b></td>'+r.vals.map((v,i)=>`<td>${usd(v)}${i>0?' <span class="cap">('+pc(v,r.vals[i-1])+')</span>':''}</td>`).join('')+'</tr>').join('')+'</tbody>';
 g('sku_concl').innerHTML='<b>趋势小结:</b>订阅是主引擎——一期→二期日均收入 $5.0k→6.4k→7.6k,每次策略都有效;三期8.8 订阅仅 +5%($8.0k)。金币:一期 +25%、二期(未付费/已付费分层)反而微降 −5%,<b>三期8.8 改了未付费金币档位后,金币 +43%(1012→1450/日)</b>——针对性改档直接把金币拉起来,符合预期。<b>注意:</b>8.8 窗口仅 8/08–09 两天、样本小;针对性 AB 昨天(8/10)才开,数据尚未更新到看板(数据止 8/09),三期完整效果待后续数据确认。';
 renderSkuTable();
}
const R={dash:renderDash,country:renderCountry,strategy:renderStrategy,weekly:renderWeekly,sdetail:renderSdetail,sku:renderSku};
function show(t){
 document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('on',b.dataset.t===t));
 document.querySelectorAll('.panel').forEach(p=>p.classList.toggle('on',p.id==='p-'+t));
 R[t]();done[t]=true;
}
document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>show(b.dataset.t));
document.getElementById('tg').onclick=()=>{const c=document.documentElement.getAttribute('data-theme');
 const dark=c?c==='dark':matchMedia('(prefers-color-scheme:dark)').matches;
 document.documentElement.setAttribute('data-theme',dark?'light':'dark');
 const on=document.querySelector('.tab.on').dataset.t;R[on]();};
document.getElementById('foot').innerHTML='v2 · 3-Tab。数据可经「📤上传Excel更新」自动重建(约1–2分钟)。官网大盘=官网直充口径(不含引流App)。';
const GH_REPO='luojingyu-max/reelshort-web-commercial-dashboard';
const GH_TOKEN='__UPLOAD_TOKEN__';
const DATA_KEY='__DASH_PW__';
const ALLOW_NAMES=['官网大盘.xlsx','国家+付费.xlsx','引流app.xlsx'];
async function encData(buf){
 const salt=crypto.getRandomValues(new Uint8Array(16)),iv=crypto.getRandomValues(new Uint8Array(12));
 const base=await crypto.subtle.importKey('raw',new TextEncoder().encode(DATA_KEY),'PBKDF2',false,['deriveKey']);
 const key=await crypto.subtle.deriveKey({name:'PBKDF2',salt,iterations:250000,hash:'SHA-256'},base,{name:'AES-GCM',length:256},false,['encrypt']);
 const ct=new Uint8Array(await crypto.subtle.encrypt({name:'AES-GCM',iv},key,buf));
 const blob=new Uint8Array(28+ct.length);blob.set(salt,0);blob.set(iv,16);blob.set(ct,28);
 let bin='';for(let i=0;i<blob.length;i++)bin+=String.fromCharCode(blob[i]);
 return btoa(bin);
}
const ghApi=(path,method,body)=>fetch('https://api.github.com/repos/'+GH_REPO+'/'+path,{method,
 headers:{Authorization:'Bearer '+GH_TOKEN,Accept:'application/vnd.github+json'},body:body?JSON.stringify(body):undefined});
function toast(msg,err){let t=document.getElementById('uptoast');
 if(!t){t=document.createElement('div');t.id='uptoast';
  t.style.cssText='position:fixed;left:50%;bottom:24px;transform:translateX(-50%);z-index:99999;max-width:82vw;padding:12px 18px;border-radius:10px;font-size:14px;color:#fff;box-shadow:0 8px 30px rgba(0,0,0,.45);white-space:pre-wrap;line-height:1.5';
  document.body.appendChild(t);}
 t.style.background=err?'#c0392b':'#1a1a19';t.textContent=msg;t.style.display='block';
 clearTimeout(t._h);t._h=setTimeout(()=>{t.style.display='none';},err?15000:8000);}
document.getElementById('up').onclick=()=>{
 if(GH_TOKEN.indexOf('__')===0){toast('上传功能尚未配置(缺令牌),请联系管理员。',true);return;}
 const inp=document.createElement('input');inp.type='file';inp.accept='.xlsx';inp.multiple=true;
 inp.style.display='none';document.body.appendChild(inp);
 inp.onchange=async()=>{
  try{
   const files=[...inp.files];
   if(!files.length)return;
   const bad=files.filter(f=>ALLOW_NAMES.indexOf(f.name)<0);
   if(bad.length){toast('文件名必须是: '+ALLOW_NAMES.join(' / ')+'\\n收到: '+bad.map(f=>f.name).join(', '),true);return;}
   for(const f of files){
    toast('加密并上传 '+f.name+' …');
    const enc=await encData(new Uint8Array(await f.arrayBuffer()));
    const p='ci/data/'+encodeURIComponent(f.name+'.enc');
    let sha;const cur=await ghApi('contents/'+p,'GET');if(cur.ok)sha=(await cur.json()).sha;
    const put=await ghApi('contents/'+p,'PUT',{message:'upload '+f.name+' via dashboard',content:btoa(enc),sha});
    if(!put.ok)throw new Error('提交 '+f.name+' 失败 (HTTP '+put.status+'): '+(await put.text()).slice(0,300));
   }
   toast('触发重建…');
   const disp=await ghApi('dispatches','POST',{event_type:'rebuild'});
   if(!disp.ok)throw new Error('触发重建失败 (HTTP '+disp.status+'): '+(await disp.text()).slice(0,300));
   toast('✅ 已上传 '+files.length+' 个文件并触发重建。约 1–2 分钟后刷新本页看新数据。');
  }catch(e){console.error(e);toast('❌ '+(e&&e.message||e),true);}
  finally{inp.remove();}
 };
 inp.click();
};
show('dash');
</script></body></html>"""

import os
html=(TPL.replace("__PAYLOAD__",json.dumps(P,ensure_ascii=False))
        .replace("__GEN__",P["gen"]).replace("__WEEKLY__",WEEKLY).replace("__CHARTJS__",CHARTJS))
html=html.replace("__UPLOAD_TOKEN__", os.environ.get("UPLOAD_TOKEN","__UPLOAD_TOKEN__"))
html=html.replace("__DASH_PW__", os.environ.get("DASH_PW","__DASH_PW__"))
open("index.html","w").write(html)
print("index.html:",len(html),"bytes | upload token baked:", "__UPLOAD_TOKEN__" not in html)
