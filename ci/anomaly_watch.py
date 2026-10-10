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
    out = []
    for r in rows:
        out.append({"d": str(r[0])[:10],
                    "sku": str(r[si]).strip() if si else "",
                    "price": str(r[pi]).strip() if pi else "",
                    "country": str(r[ci]).strip() if ci else "ALL",
                    "type": str(r[ti]).strip() if ti else "全部",
                    "rev": num(r[I["总收入"]]), "uv": num(r[I["充值uv"]]) if "充值uv" in I else 0.0})
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
    return {d: sorted(v)[-1][3] for d, v in pool.items()}

def scan(SRC, target, known_bad):
    days = sorted(SRC)
    if target not in SRC: return None
    base_days = [d for d in days if d < target and d not in known_bad][-BASE_DAYS:]
    if len(base_days) < 5: return None
    base = collections.defaultdict(lambda: [0.0, 0.0])
    for d in base_days:
        for x in SRC[d]:
            k = (x["sku"], x["country"])
            base[k][0] += x["rev"] / len(base_days); base[k][1] += x["uv"] / len(base_days)
    cur = collections.defaultdict(lambda: [0.0, 0.0, ""])
    for x in SRC[target]:
        k = (x["sku"], x["country"]); cur[k][0] += x["rev"]; cur[k][1] += x["uv"]; cur[k][2] = x["price"]
    hits = []
    for k, (rev, uv, price) in cur.items():
        b_rev, b_uv = base.get(k, [0.0, 0.0])
        if rev < MIN_REV: continue
        if b_rev == 0:
            if uv >= MIN_UV_NEW:
                hits.append({"sku": k[0], "country": k[1], "price": price, "rev": round(rev, 2),
                             "uv": int(uv), "base_rev": 0.0, "base_uv": 0.0, "mult": None, "kind": "新增"})
        elif rev / b_rev >= MULT:
            hits.append({"sku": k[0], "country": k[1], "price": price, "rev": round(rev, 2),
                         "uv": int(uv), "base_rev": round(b_rev, 2), "base_uv": round(b_uv, 1),
                         "mult": round(rev / b_rev, 1), "kind": "放大"})
    hits.sort(key=lambda h: -(h["rev"] - h["base_rev"]))
    day_rev = sum(x["rev"] for x in SRC[target])
    return {"date": target, "base_window": "%s~%s" % (base_days[0], base_days[-1]),
            "day_rev": round(day_rev, 2), "n": len(hits),
            "anom_rev": round(sum(h["rev"] - h["base_rev"] for h in hits), 2),
            "hits": hits}

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
        flag = "🔴 触发" if r["n"] else "✅ 正常"
        print("\n%s %s  当日收入 $%s  异常单元格 %d 个  异常金额 $%s (%.1f%%)  基线 %s" % (
            flag, r["date"], format(r["day_rev"], ","), r["n"], format(r["anom_rev"], ","),
            r["anom_rev"] / r["day_rev"] * 100 if r["day_rev"] else 0, r["base_window"]))
        for h in r["hits"][:15]:
            m = "新增(基线0)" if h["mult"] is None else "%.0fx" % h["mult"]
            print("   %-24s %-12s 价%-6s %5d单 $%9.2f  基线 %.1f单/$%.2f  %s" % (
                h["sku"][:24], h["country"][:12], h["price"], h["uv"], h["rev"], h["base_uv"], h["base_rev"], m))
        if r["n"] > 15: print("   ...另有 %d 个" % (r["n"] - 15))
    log.setdefault("_confirmed_bad", sorted(known_bad))
    for r in out: log[r["date"]] = r
    json.dump(log, open(LOG, "w"), ensure_ascii=False, indent=1)
    print("\n已写入 %s" % LOG)
    return out

if __name__ == "__main__":
    main()
