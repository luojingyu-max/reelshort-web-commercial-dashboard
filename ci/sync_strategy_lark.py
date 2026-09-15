# -*- coding: utf-8 -*-
"""从 Lark《面板策略记录》表1(sheet b0c630)同步策略明细到看板,并按各策略的
上架/下架时间自动重算前后效果对比。

用法(仓库根目录):
    LARK_APP_ID=... LARK_APP_SECRET=... python3 ci/sync_strategy_lark.py
    # 不传则自动从 ~/.claude.json 的 lark-mcp 配置里取 kim 应用凭证

产出(写入 ci/strategy.json):
    strategy_header / strategy   —— 表1 全字段(含下架时间、是否AB、状态),取代原先手写的快照
    strat_eff_header / strat_eff —— 每条策略按自身上架日算的前后对比(含 DiD 净效应)
    strat_synced                 —— 同步时间戳 + 源表信息

panel1 / panel1_header(一期/二期人工分析)原样保留,不覆盖。
"""
import json, os, re, sys, datetime, urllib.request, collections
import openpyxl, warnings
warnings.simplefilter("ignore")

SS_TOKEN_WIKI = "PtpvwMqkai4v1LkaWhslD2YWgnI"   # wiki 节点
SHEET_ID      = "b0c630"                        # 表1 SEO策略面板定价
YEAR          = 2026
MON           = "ci/data/官网监控明细_recent.xlsx"
OUT           = "ci/strategy.json"

# ---------------- Lark ----------------
def creds():
    a, s = os.environ.get("LARK_APP_ID"), os.environ.get("LARK_APP_SECRET")
    d = os.environ.get("LARK_DOMAIN", "https://open.larksuite.com")
    if a and s:
        return a, s, d
    p = os.path.expanduser("~/.claude.json")
    if not os.path.exists(p):
        sys.exit("缺少 LARK_APP_ID / LARK_APP_SECRET,且找不到 ~/.claude.json")
    def find(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "args" and isinstance(v, list) and any("cli_" in str(x) for x in v):
                    return v
                r = find(v)
                if r: return r
        elif isinstance(o, list):
            for v in o:
                r = find(v)
                if r: return r
        return None
    args = find(json.load(open(p))) or []
    g = lambda f: args[args.index(f) + 1] if f in args else None
    a, s, d = g("-a"), g("-s"), g("-d") or d
    if not (a and s):
        sys.exit("~/.claude.json 里没找到 lark 应用凭证")
    return a, s, d.rstrip("/")

def lark_rows():
    app, sec, dom = creds()
    tok = json.load(urllib.request.urlopen(urllib.request.Request(
        dom + "/open-apis/auth/v3/tenant_access_token/internal",
        data=json.dumps({"app_id": app, "app_secret": sec}).encode(),
        headers={"Content-Type": "application/json"})))["tenant_access_token"]
    H = {"Authorization": "Bearer " + tok}
    node = json.load(urllib.request.urlopen(urllib.request.Request(
        dom + "/open-apis/wiki/v2/spaces/get_node?token=%s&obj_type=wiki" % SS_TOKEN_WIKI, headers=H)))
    obj = node["data"]["node"]["obj_token"]
    r = json.load(urllib.request.urlopen(urllib.request.Request(
        dom + "/open-apis/sheets/v2/spreadsheets/%s/values/%s!A1:T200?valueRenderOption=ToString"
        % (obj, SHEET_ID), headers=H)))
    return r["data"]["valueRange"]["values"], obj

# ---------------- 解析 ----------------
def cell(row, i):
    if i is None or len(row) <= i or row[i] in (None, ""):
        return ""
    return re.sub(r"\s*\n\s*", " ", str(row[i])).strip()

def parse_date(s):
    """'8.8' / '9.4' / '6.17' -> '2026-08-08';'-' / '' -> None"""
    s = (s or "").strip()
    m = re.match(r"^(\d{1,2})[.\-/](\d{1,2})$", s)
    if not m:
        return None
    return "%d-%02d-%02d" % (YEAR, int(m.group(1)), int(m.group(2)))

# 表1 的国家写法 -> 监控明细里的注册国家名
GROUPS = {
    "美/加/澳/英": ["美国", "加拿大", "澳大利亚", "英国"],
    "美加澳英":   ["美国", "加拿大", "澳大利亚", "英国"],
    "加澳英":     ["加拿大", "澳大利亚", "英国"],
    "墨西哥/智利/阿根廷": ["墨西哥", "智利", "阿根廷"],
    "墨西哥、智利、阿根廷": ["墨西哥", "智利", "阿根廷"],
    "德国/以色列/捷克": ["德国", "以色列", "捷克"],
}
# 兜底盘不点名国家,无法做国家级对比
UNSCOPED = ("全部国家",)

# 盘口 -> 监控明细的付费状态维度。同国家的已付费/未付费盘若不分层,会算出一模一样的数
PANEL_PAID = {
    "已付费":   "已付费用户",
    "未付费":   "未付费用户",
    "D0未付费": "未付费用户",   # 合并表无 D0 维度,用未付费全量近似(偏保守,已在 口径 列标注)
}
def paid_of(panel):
    return PANEL_PAID.get(panel.strip())

def countries_of(expr):
    e = expr.strip()
    if e in GROUPS:
        return GROUPS[e]
    if any(e.startswith(u) for u in UNSCOPED):
        return None          # 兜底盘:不做国家级前后对比
    return [e]

# ---------------- 监控明细 ----------------
def load_mon():
    wb = openpyxl.load_workbook(MON, read_only=True, data_only=True)
    ws = wb.worksheets[0]
    it = ws.iter_rows(values_only=True)
    next(it)
    H = [str(x).strip() for x in next(it)]
    I = {n: i for i, n in enumerate(H)}
    ORD = "创建订单uv" if "创建订单uv" in I else "商品点击/订单创建uv"
    rows = []
    for r in it:
        if not r or not str(r[0]).startswith(str(YEAR)):
            continue
        rows.append((str(r[0])[:10], str(r[1]).strip(), str(r[2]).strip(), r))
    return rows, I, ORD

def num(v):
    try: return float(v)
    except Exception: return 0.0

SUMCOLS = ["DAU", "观看uv", "触达付费集uv", "充值uv", "金币充值uv", "订阅uv",
           "首订uv", "续订uv", "总收入", "金币充值收入", "订阅(续订)收入", "首订收入", "续订收入"]

def agg(rows, I, ORD, d0, d1, ctys=None, paid=None):
    a = collections.defaultdict(float); days = set()
    for d, c, p, r in rows:
        if d < d0 or d > d1: continue
        if ctys is not None and c not in ctys: continue
        if paid is not None and p != paid: continue
        days.add(d)
        for k in SUMCOLS: a[k] += num(r[I[k]])
        a["ord"] += num(r[I[ORD]])
    n = len(days) or 1
    dau = a["DAU"] or 1
    return {
        "days": len(days),
        "dau_d": a["DAU"] / n, "rev_d": a["总收入"] / n, "pay_d": a["充值uv"] / n,
        "ord_d": a["ord"] / n,
        "viewrate": a["观看uv"] / dau * 100,
        "ordrate": a["ord"] / (a["触达付费集uv"] or 1) * 100,
        "payrate": a["充值uv"] / dau * 100,
        "subrate": a["订阅uv"] / dau * 100,
        "arppu": a["总收入"] / (a["充值uv"] or 1),
        "subarppu": a["订阅(续订)收入"] / (a["订阅uv"] or 1),
        "coinshare": a["金币充值收入"] / (a["总收入"] or 1) * 100,
        "arpu": a["总收入"] / dau,
        "_rev": a["总收入"],
    }

def pct(b, a):
    return None if not a else round((b / a - 1) * 100, 1)

def main():
    vals, obj = lark_rows()
    hdr = [cell(vals[0], i) for i in range(len(vals[0]))]
    ix = {n: i for i, n in enumerate(hdr) if n}
    need = ["层级", "国家", "策略名称 / 画像ID", "盘口", "上架时间"]
    miss = [n for n in need if n not in ix]
    if miss:
        sys.exit("表1 表头缺列 %s;实际表头=%s" % (miss, hdr))

    COLS = ["层级", "国家", "策略名称 / 画像ID", "优先级", "是否AB实验", "配置ID", "用户画像",
            "金币档位", "周卡", "月卡", "年卡", "上架时间", "下架时间", "盘口", "剧包ID"]
    strat = []
    for row in vals[1:]:
        if not cell(row, ix.get("策略名称 / 画像ID")):
            continue
        rec = [cell(row, ix.get(c)) for c in COLS]
        on, off = parse_date(rec[11]), parse_date(rec[12])
        rec += [on or "", off or "", "已下架" if off else "在线"]
        strat.append(rec)
    print("表1 读到 %d 条策略(在线 %d / 已下架 %d)" % (
        len(strat), sum(1 for r in strat if r[-1] == "在线"), sum(1 for r in strat if r[-1] == "已下架")))

    # ---- 按各策略上架日自动算前后对比 ----
    rows, I, ORD = load_mon()
    alldates = sorted({d for d, _, _, _ in rows})
    DMIN, DMAX = alldates[0], alldates[-1]
    # 对照组:从未被任何点名策略覆盖的国家
    named = set()
    for r in strat:
        cs = countries_of(r[1])
        if cs: named.update(cs)
    ctrl = sorted({c for _, c, _, _ in rows} - named)
    print("对照组国家 %d 个(未被任何点名策略覆盖)" % len(ctrl))

    def shift(d, n):
        dt = datetime.date(*map(int, d.split("-"))) + datetime.timedelta(days=n)
        return dt.isoformat()

    EFF_H = ["策略", "国家", "盘口", "上架", "下架", "前窗口", "后窗口", "后天数", "前天数", "口径/提示",
             "DAU/日 前", "DAU/日 后", "DAU %", "收入/日 前", "收入/日 后", "收入 %",
             "ARPPU 前", "ARPPU 后", "ARPPU %", "付费率% 前", "付费率% 后", "收入净效应DiD(pp)"]

    # 不可算的行也必须补齐到表头长度,否则前端 map 会整列错位
    NA = lambda name, cexpr, panel, r, why: [
        name, cexpr, panel, r[11], r[12] or "-", "—", "—", 0, 0, why] + [None] * (len(EFF_H) - 10)

    eff = []
    for r in strat:
        name, cexpr, on, off, panel = r[2], r[1], r[15], r[16], r[13]
        cs = countries_of(cexpr)
        paid = paid_of(panel)
        cal = {"已付费": "仅已付费用户", "未付费": "仅未付费用户",
               "D0未付费": "未付费全量(无D0维度,近似)"}.get(panel.strip(), "全量")
        if not on:
            eff.append(NA(name, cexpr, panel, r, "无上架日")); continue
        if not cs:
            eff.append(NA(name, cexpr, panel, r, "兜底盘·不点名国家")); continue
        post_end = min(off and shift(off, -1) or DMAX, DMAX)
        if post_end < on:
            eff.append(NA(name, cexpr, panel, r, "上架后无数据")); continue
        # 后窗口:上架日起至下架前一天/数据末日,最长 21 天
        pe = min(post_end, shift(on, 20))
        nd = (datetime.date(*map(int, pe.split("-"))) - datetime.date(*map(int, on.split("-")))).days + 1
        # 前窗口:等长,紧邻上架日之前;被数据起点截断时如实记录天数
        ps, pend = max(shift(on, -nd), DMIN), shift(on, -1)
        if pend < ps:
            eff.append(NA(name, cexpr, panel, r, "上架日早于数据起点,无基线")); continue
        A = agg(rows, I, ORD, ps, pend, cs, paid); B = agg(rows, I, ORD, on, pe, cs, paid)
        CA = agg(rows, I, ORD, ps, pend, ctrl, paid); CB = agg(rows, I, ORD, on, pe, ctrl, paid)
        if A["days"] == 0 or B["days"] == 0:
            eff.append(NA(name, cexpr, panel, r, "窗口内无数据")); continue
        rv = pct(B["rev_d"], A["rev_d"]); cv = pct(CB["rev_d"], CA["rev_d"])
        did = None if (rv is None or cv is None) else round(rv - cv, 1)
        # 可信度:基线过短 / 后窗口过短 / 量级过小都会让百分比失真
        flags = []
        if A["days"] < max(3, B["days"] * 0.5): flags.append("基线仅%d天" % A["days"])
        if B["days"] < 5: flags.append("后窗口仅%d天" % B["days"])
        if B["rev_d"] < 50: flags.append("量级小")
        eff.append([
            name, cexpr, panel, r[11], r[12] or "-",
            "%s~%s" % (ps[5:], pend[5:]), "%s~%s" % (on[5:], pe[5:]), B["days"], A["days"],
            "、".join(flags) if flags else ("可比 · " + cal),
            round(A["dau_d"]), round(B["dau_d"]), pct(B["dau_d"], A["dau_d"]),
            round(A["rev_d"], 1), round(B["rev_d"], 1), rv,
            round(A["arppu"], 2), round(B["arppu"], 2), pct(B["arppu"], A["arppu"]),
            round(A["payrate"], 3), round(B["payrate"], 3), did,
        ])

    S = json.load(open(OUT)) if os.path.exists(OUT) else {}
    S["strategy_header"] = COLS + ["上架日", "下架日", "状态"]
    S["strategy"] = strat
    S["strat_eff_header"] = EFF_H
    S["strat_eff"] = eff
    S["strat_synced"] = {
        "at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sheet": "%s!%s" % (obj, SHEET_ID),
        "n": len(strat),
        "data_range": "%s~%s" % (DMIN, DMAX),
        "ctrl_n": len(ctrl),
    }
    json.dump(S, open(OUT, "w"), ensure_ascii=False, indent=1)
    ok = sum(1 for e in eff if e[15] is not None)
    print("写入 %s:策略 %d 条,可算前后对比 %d 条(其余为兜底盘/窗口不足)" % (OUT, len(strat), ok))

if __name__ == "__main__":
    main()
