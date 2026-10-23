# -*- coding: utf-8 -*-
"""档位 × 国家 日度异常监控。

背景:2026-09 至 10 月连续三起疑似盗刷(菲律宾年卡99.99、俄罗斯周卡$5.99、
10/08 跨42国 49.99+19.99),共同特征是「单一档位 + 短期尖峰 + 次日归零 + 走 adyen」。
人工发现滞后 1-2 天,故建立自动监控。

规则(单元格 = 档位 × 国家 × 日):
  触发 = 当日收入 ≥ MIN_REV 且(基线为 0 且订单数 ≥ MIN_UV_NEW,或 当日收入 ≥ 基线日均 × MULT)
  基线 = 目标日前 BASE_DAYS 天的日均(剔除已标记的异常日,避免基线被污染)

用法(仓库根目录):
    python3 ci/anomaly_watch.py                 # 扫最新一个完整日
    python3 ci/anomaly_watch.py 2026-10-08      # 扫指定日
    python3 ci/anomaly_watch.py 2026-10-01 2026-10-08   # 扫区间
输出:stdout 报告 + ci/anomaly_log.json(累积,供播报/复盘)
"""
import openpyxl, glob, os, re, json, sys, collections, datetime, warnings
warnings.simplefilter("ignore")

ARC = os.path.expanduser("~/rs-web-dashboard/bi_archive")
REF = os.path.expanduser("~/rs-web-dashboard/ref_exports")
LOG = "ci/anomaly_log.json"
BASE_DAYS  = 16      # 基线窗口
MULT       = 5.0     # 相对基线倍数阈值
MIN_REV    = 200.0   # 单元格当日收入下限($),低于此不报(避免噪音)
MIN_UV_NEW = 5       # 基线为 0 时的订单数下限
# 订单数维度(2026-10-16 加):低单价档位放量时金额未必超阈值,但订单数会暴涨。
# 10/13-10/15 的 $5.99 周卡 951-1078 单/日(常态 27-44),金额仅 $4-6k 却覆盖近百国。
MIN_UV     = 30      # 订单数触发的最低单数
UV_MULT    = 8.0     # 订单数相对基线的倍数阈值(比金额阈值更严,避免小基数噪音)
# 档位级(跨国家汇总)规则:单档位当日总订单数相对基线放大
SKU_MIN_UV = 200
SKU_MULT   = 5.0
# 标红门槛:新增(首订)异常达到此金额或单元格数才算「新攻击」,否则只标黄。
# 10/19 新增仅 $331(1.3%)而续订回声 $4,489,旧版一律标红会造成告警疲劳。
NEW_ALERT_REV = 800.0
NEW_ALERT_N   = 3
TYPES = ("0-", "1-", "2-")

def num(v):
    try: return float(v)
    except Exception: return 0.0

def sniff(rows, ndim):
    """自动识别 档位/价格/国家/类型 列 —— BI 改过三次维度顺序,固定列号不可靠"""
    cols = {i: {str(r[i]).strip() for r in rows[:400] if len(r) > i} for i in range(1, ndim + 1)}
    ti = next((i for i, s in cols.items() if any(x.startswith(TYPES) for x in s)), None)
    pi = next((i for i, s in cols.items() if i != ti and sum(1 for x in s if x.isdigit()) > len(s) * 0.7), None)
    si = next((i for i, s in cols.items() if i not in (ti, pi)
               and any(('Coins' in x) or ('周卡' in x) or ('月卡' in x) or ('年卡' in x) for x in s)), None)
    ci = next((i for i, s in cols.items() if i not in (ti, pi, si) and len(s) > 20 and 'ALL' not in s), None)
    if ci is None:
        ci = next((i for i, s in cols.items() if i not in (ti, pi, si) and len(s) > 20), None)
    return si, pi, ci, ti

def read(path):
    try:
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    except Exception:
        return []
    if "档位支付明细" not in wb.sheetnames: return []
    ws = wb["档位支付明细"]; it = ws.iter_rows(values_only=True)
    r1 = list(next(it))
    H = [str(x).strip() for x in (r1 if str(r1[0]).strip() != "维度" else list(next(it)))]
    I = {x: i for i, x in enumerate(H)}
    if "总收入" not in I: return []
    rows = [r for r in it if r and str(r[0]).startswith("2026")]
    if not rows: return []
    ndim = min(5, next((i for i, x in enumerate(H) if x == "充值pv"), 5) - 1)
    si, pi, ci, ti = sniff(rows, ndim)
    has_stage = all(c in I for c in ("首订uv", "续订uv", "首订收入", "续订收入"))
    out = []
    for r in rows:
        meta = {"d": str(r[0])[:10],
                "sku": str(r[si]).strip() if si else "",
                "price": str(r[pi]).strip() if pi else "",
                "country": str(r[ci]).strip() if ci else "ALL",
                "type": str(r[ti]).strip() if ti else "全部"}
        tot = num(r[I["总收入"]]); uv = num(r[I["充值uv"]]) if "充值uv" in I else 0.0
        # 首订/续订拆分(2026-10-23 加):同一档位的 599 首周价与 1299 续订价是同一个 sku,
        # 混在一起算基线会让「续订回声」被误报成新攻击 —— 10/19 的 $12.99 1154 单就是
        # 10/12-10/13 那批 $5.99 的续订,不是新发生的盗刷。两者风险含义完全不同:
        # 首订异常 = 新攻击,要立即封堵;续订异常 = 存量订阅在扣款,看衰减趋势即可。
        if has_stage:
            fo_uv, re_uv = num(r[I["首订uv"]]), num(r[I["续订uv"]])
            fo_rev, re_rev = num(r[I["首订收入"]]), num(r[I["续订收入"]])
            if fo_uv or fo_rev:
                out.append(dict(meta, stage="首订", rev=fo_rev, uv=fo_uv))
            if re_uv or re_rev:
                out.append(dict(meta, stage="续订", rev=re_rev, uv=re_uv))
            # 非订阅部分(金币/一次性商品):总收入扣掉订阅后的余额
            oth_rev = tot - fo_rev - re_rev; oth_uv = uv - fo_uv - re_uv
            if oth_rev > 0.01 or oth_uv > 0.5:
                out.append(dict(meta, stage="非订阅", rev=oth_rev, uv=oth_uv))
        else:
            out.append(dict(meta, stage="全部", rev=tot, uv=uv))
    return out

def load_all():
    """每日选源:优先「国家数>1 且类型完整」,其次导出日期最晚"""
    pool = collections.defaultdict(list)
    for p in sorted(glob.glob(ARC + "/SEO数据看板_2026*.xlsx")) + sorted(glob.glob(REF + "/*档位支付明细*.xlsx")):
        m = re.search(r"_(\d{8})", os.path.basename(p)); ed = m.group(1) if m else "0"
        by = collections.defaultdict(list)
        for r in read(p): by[r["d"]].append(r)
        for d, rs in by.items():
            pool[d].append((len({x["country"] for x in rs}) > 1, len({x["type"] for x in rs}) > 1, ed, rs))
    out = {d: sorted(v)[-1][3] for d, v in pool.items()}
    # 剔除残缺日:当日数据未跑完时 SKU 表把全部成交塞进 others 桶(国家维度未归因),
    # 不剔除会把整天误报为异常(10/11 曾因此误报 12 个单元格、82% 收入)。判据:有效国家数 ≤ 2。
    bad = [d for d, rs in out.items() if len({x["country"] for x in rs} - {"others", "ALL", ""}) <= 2]
    for d in bad: out.pop(d)
    if bad: print("[info] 跳过残缺日(国家维度未归因): %s" % ", ".join(sorted(bad)))
    return out

def scan(SRC, target, known_bad):
    days = sorted(SRC)
    if target not in SRC: return None
    base_days = [d for d in days if d < target and d not in known_bad][-BASE_DAYS:]
    if len(base_days) < 5: return None
    base = collections.defaultdict(lambda: [0.0, 0.0])
    for d in base_days:
        for x in SRC[d]:
            k = (x["sku"], x["country"], x.get("stage", "全部"))
            base[k][0] += x["rev"] / len(base_days); base[k][1] += x["uv"] / len(base_days)
    cur = collections.defaultdict(lambda: [0.0, 0.0, ""])
    for x in SRC[target]:
        k = (x["sku"], x["country"], x.get("stage", "全部"))
        cur[k][0] += x["rev"]; cur[k][1] += x["uv"]; cur[k][2] = x["price"]
    hits = []
    for k, (rev, uv, price) in cur.items():
        b_rev, b_uv = base.get(k, [0.0, 0.0])
        rec = {"sku": k[0], "country": k[1], "stage": k[2], "price": price,
               "rev": round(rev, 2), "uv": int(uv),
               "base_rev": round(b_rev, 2), "base_uv": round(b_uv, 1)}
        # 金额维度
        if rev >= MIN_REV:
            if b_rev == 0 and uv >= MIN_UV_NEW:
                hits.append(dict(rec, mult=None, kind="新增")); continue
            if b_rev > 0 and rev / b_rev >= MULT:
                hits.append(dict(rec, mult=round(rev / b_rev, 1), kind="放大")); continue
        # 订单数维度:低单价档位放量时金额可能不过阈值,但单数会暴涨
        if uv >= MIN_UV and b_uv > 0 and uv / b_uv >= UV_MULT:
            hits.append(dict(rec, mult=round(rev / b_rev, 1) if b_rev else None,
                             uv_mult=round(uv / b_uv, 1), kind="单数放大"))
    # 首订排前面:新攻击要立即响应,续订只是存量回声
    _ord = {"首订": 0, "非订阅": 1, "全部": 1, "续订": 2}
    hits.sort(key=lambda h: (_ord.get(h["stage"], 1), -(h["rev"] - h["base_rev"])))
    # 档位级(跨国家汇总):整体放量但分摊到各国都不过阈值的情况
    sb = collections.defaultdict(lambda: [0.0, 0.0])
    for d in base_days:
        for x in SRC[d]:
            k = (x["sku"], x.get("stage", "全部"))
            sb[k][0] += x["rev"] / len(base_days); sb[k][1] += x["uv"] / len(base_days)
    sc = collections.defaultdict(lambda: [0.0, 0.0, set()])
    for x in SRC[target]:
        k = (x["sku"], x.get("stage", "全部"))
        sc[k][0] += x["rev"]; sc[k][1] += x["uv"]; sc[k][2].add(x["country"])
    sku_hits = []
    for (s_, st_), (rev, uv, ctys) in sc.items():
        b_rev, b_uv = sb.get((s_, st_), [0.0, 0.0])
        if uv >= SKU_MIN_UV and b_uv > 0 and uv / b_uv >= SKU_MULT:
            sku_hits.append({"sku": s_, "stage": st_, "uv": int(uv), "rev": round(rev, 2),
                             "base_uv": round(b_uv, 1), "base_rev": round(b_rev, 2),
                             "uv_mult": round(uv / b_uv, 1), "countries": len(ctys)})
    sku_hits.sort(key=lambda h: -h["uv_mult"])
    day_rev = sum(x["rev"] for x in SRC[target])
    anom = lambda hs: round(sum(h["rev"] - h["base_rev"] for h in hs), 2)
    new_hits = [h for h in hits if h["stage"] != "续订"]
    return {"date": target, "base_window": "%s~%s" % (base_days[0], base_days[-1]),
            "day_rev": round(day_rev, 2), "n": len(hits),
            "anom_rev": anom(hits),
            # 分阶段:新增攻击(首订/非订阅)与存量回声(续订)风险含义不同,分开计量
            "n_new": len(new_hits), "anom_rev_new": anom(new_hits),
            "n_renew": len(hits) - len(new_hits),
            "anom_rev_renew": anom([h for h in hits if h["stage"] == "续订"]),
            "hits": hits, "sku_hits": sku_hits}

def main():
    SRC = load_all()
    days = sorted(SRC)
    # 已确认的异常日,不参与基线
    log = json.load(open(LOG)) if os.path.exists(LOG) else {}
    known_bad = set(log.get("_confirmed_bad", ["2026-10-07", "2026-10-08"]))
    args = [a for a in sys.argv[1:] if re.match(r"\d{4}-\d\d-\d\d", a)]
    if len(args) == 2:
        tg = [d for d in days if args[0] <= d <= args[1]]
    elif len(args) == 1:
        tg = args
    else:
        tg = [days[-1]]
    out = []
    for t in tg:
        r = scan(SRC, t, known_bad)
        if r: out.append(r)
    for r in out:
        if r["anom_rev_new"] >= NEW_ALERT_REV or r["n_new"] >= NEW_ALERT_N:
            flag = "🔴 新增攻击"
        elif r["n_new"] or r["n_renew"]:
            flag = "🟡 偏高(新增量小/以续订为主)"
        else:
            flag = "✅ 正常"
        pct = lambda v: v / r["day_rev"] * 100 if r["day_rev"] else 0
        print("\n%s %s  当日收入 $%s  基线 %s" % (
            flag, r["date"], format(r["day_rev"], ","), r["base_window"]))
        print("   新增(首订/一次性): %d 个单元格  $%s (%.1f%%)   |   续订回声: %d 个  $%s (%.1f%%)" % (
            r["n_new"], format(r["anom_rev_new"], ","), pct(r["anom_rev_new"]),
            r["n_renew"], format(r["anom_rev_renew"], ","), pct(r["anom_rev_renew"])))
        for st in ("首订", "非订阅", "全部", "续订"):
            sub = [h for h in r["hits"] if h["stage"] == st]
            if not sub: continue
            print("   -- %s --" % st)
            for h in sub[:12]:
                m = "新增(基线0)" if h["mult"] is None else "%.0fx" % h["mult"]
                print("   %-22s %-10s 价%-6s %5d单 $%9.2f  基线 %.1f单/$%.2f  %s" % (
                    h["sku"][:22], h["country"][:10], h["price"], h["uv"], h["rev"],
                    h["base_uv"], h["base_rev"], m))
            if len(sub) > 12: print("      ...另有 %d 个" % (len(sub) - 12))
        for sh in r.get("sku_hits", []):
            print("   [档位级·%s] %-20s %5d单 $%9.2f  基线 %.1f单/$%.2f  单数 %.1fx  %d国" % (
                sh.get("stage", "全部"), sh["sku"][:20], sh["uv"], sh["rev"],
                sh["base_uv"], sh["base_rev"], sh["uv_mult"], sh["countries"]))
    log.setdefault("_confirmed_bad", sorted(known_bad))
    for r in out: log[r["date"]] = r
    json.dump(log, open(LOG, "w"), ensure_ascii=False, indent=1)
    print("\n已写入 %s" % LOG)
    return out

if __name__ == "__main__":
    main()
