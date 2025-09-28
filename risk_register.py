#!/usr/bin/env python3
import argparse, json, os, uuid, csv
from datetime import datetime
STORE = "risks.json"

def _load():
    if not os.path.exists(STORE): return []
    with open(STORE, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except json.JSONDecodeError: return []

def _save(data):
    with open(STORE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _level(score):
    if score <= 5: return "Low"
    if score <= 10: return "Moderate"
    if score <= 15: return "High"
    return "Critical"

def add_risk(args):
    L = int(args.likelihood); I = int(args.impact)
    if not (1 <= L <= 5 and 1 <= I <= 5):
        raise SystemExit("likelihood/impact must be 1–5.")
    score = L * I
    risk = {
        "id": str(uuid.uuid4())[:8],
        "title": args.title,
        "category": (args.category or "").lower(),
        "owner": args.owner or "",
        "likelihood": L,
        "impact": I,
        "score": score,
        "level": _level(score),
        "status": "open",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "notes": args.notes or ""
    }
    data = _load(); data.append(risk); _save(data)
    print(f"✅ Added {risk['id']} | {risk['level']} ({risk['score']}) — {risk['title']}")

def list_risks(args):
    data = _load()
    if args.category: data = [r for r in data if r["category"] == args.category.lower()]
    if args.owner: data = [r for r in data if r["owner"].lower() == args.owner.lower()]
    data.sort(key=lambda r: r["score"], reverse=True)
    if not data: return print("No risks found.")
    for r in data:
        print(f"{r['id']} | {r['level']}({r['score']}) L{r['likelihood']}xI{r['impact']} | {r['title']} "
              f"(cat:{r['category'] or '-'} owner:{r['owner'] or '-'}) [{r['status']}]")

def update_risk(args):
    data = _load()
    for r in data:
        if r["id"] == args.id:
            if args.status: r["status"] = args.status
            if args.notes: r["notes"] = (r["notes"] + "\n" if r["notes"] else "") + args.notes
            _save(data); print(f"🛠️ Updated {r['id']}"); return
    print("No risk with that id.")

def stats(args):
    from collections import Counter
    data = _load()
    if not data: return print("No risks yet.")
    by_level = Counter([r["level"] for r in data])
    by_cat = Counter([r["category"] or "(uncat)"] for r in data)
    print("== By Level ==");   [print(f"- {k}: {v}") for k,v in by_level.items()]
    print("\n== By Category =="); [print(f"- {k}: {v}") for k,v in by_cat.items()]

def export_csv(args):
    data = _load()
    if not data: return print("No data to export.")
    out = args.output or "risks_export.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
        w.writeheader(); [w.writerow(r) for r in data]
    print(f"📤 Exported {len(data)} risks to {out}")

def main():
    p = argparse.ArgumentParser(description="Mini Risk Register (Likelihood x Impact)")
    sub = p.add_subparsers(dest="cmd")

    sp = sub.add_parser("add", help="Add a risk")
    sp.add_argument("title")
    sp.add_argument("--likelihood", required=True, type=int, help="1-5")
    sp.add_argument("--impact", required=True, type=int, help="1-5")
    sp.add_argument("--category", help="e.g., vendor, cloud, privacy")
    sp.add_argument("--owner", help="person/team")
    sp.add_argument("--notes")
    sp.set_defaults(func=add_risk)

    sp = sub.add_parser("list", help="List risks (sorted by score)")
    sp.add_argument("--category"); sp.add_argument("--owner")
    sp.set_defaults(func=list_risks)

    sp = sub.add_parser("update", help="Update a risk by id")
    sp.add_argument("id"); sp.add_argument("--status", choices=["open","mitigating","accepted","transferred","closed"])
    sp.add_argument("--notes"); sp.set_defaults(func=update_risk)

    sp = sub.add_parser("stats", help="Counts by level/category")
    sp.set_defaults(func=stats)

    sp = sub.add_parser("export", help="Export risks to CSV")
    sp.add_argument("--output"); sp.set_defaults(func=export_csv)

    args = p.parse_args()
    if not hasattr(args, "func"): return p.print_help()
    args.func(args)

if __name__ == "__main__":
    main()

