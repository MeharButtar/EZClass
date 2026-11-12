"""
Loads EVERY live major through the API and prints its sections, groups and courses.
Run it after each deploy (a few spot checks missed the major id that was too long for the API).

Usage (from the project root):
    python3 scripts/check_live_majors.py                    # https://www.ezclass.win
    python3 scripts/check_live_majors.py --site http://localhost:5000
    python3 scripts/check_live_majors.py --local            # this checkout, through the app itself

Exits with status 1 when a live major does not load, has no groups, or an open rule's course lookup fails.
Only GET requests; standard library only.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_AGENT = "EzClass-check"


def http_getter(site):
    def get(path):
        req = urllib.request.Request(site.rstrip("/") + path, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, None
    return get


def local_getter():
    sys.path.insert(0, ROOT)
    from backend.app import app          # builds or reuses the local database like a normal start
    client = app.test_client()

    def get(path):
        res = client.get(path)
        return res.status_code, res.get_json(silent=True)
    return get


def describe(group):
    if group["rule"] == "open":
        o = group.get("open") or {}
        ranges = o.get("ranges") or ([o] if o.get("subjects") else [])
        text = " or ".join(f"{'|'.join(r['subjects'])} {r['min']}-{r['max']}"
                           + (f" except {', '.join(r['exclude'])}" if r.get("exclude") else "") for r in ranges)
        listed = [c["code"] for c in o.get("courses") or []]
        return text + (f" or listed: {', '.join(listed)}" if listed else "")
    return ", ".join(c["code"] + ("" if c["has_sections"] else "*") for c in group["courses"])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--site", default="https://www.ezclass.win")
    ap.add_argument("--local", action="store_true", help="check this checkout through the app, not a site")
    args = ap.parse_args(argv)
    get = local_getter() if args.local else http_getter(args.site)

    status, majors = get("/api/majors")
    if status != 200 or not isinstance(majors, list):
        print(f"/api/majors answered {status}")
        return 1
    live = [m for m in majors if m.get("status") == "live"]
    print(f"{len(majors)} majors, {len(live)} live ({'local checkout' if args.local else args.site})\n")
    problems = []
    for m in live:
        mid = m["major_id"]
        status, tree = get(f"/api/majors/{urllib.parse.quote(mid)}/requirements")
        if status != 200 or not tree:
            problems.append(f"{mid}: requirements answered {status}")
            print(f"{mid}: ** {status} **\n")
            continue
        groups = [g for s in tree["sections"] for g in s["groups"]]
        courses = sum(len(g["courses"]) for g in groups)
        print(f"{mid} ({len(tree['sections'])} sections, {len(groups)} groups, {courses} listed courses)")
        if not groups:
            problems.append(f"{mid}: no groups")
        for s in tree["sections"]:
            print(f"  {s['name']}" + (f"  [{s['pool_units']} units]" if s.get("pool_units") else ""))
            for g in s["groups"]:
                rule = g["rule"] + (f" {g['pick_n']}" if g.get("pick_n") else "") + (
                    f", {g['pick_units']} units" if g.get("pick_units") else "")
                print(f"    - {g['label']} [{rule}]: {describe(g)}")
                if g["rule"] == "open":
                    o = g.get("open") or {}
                    for r in o.get("ranges") or []:
                        q = urllib.parse.urlencode({"subject": "|".join(r["subjects"]), "min": r["min"],
                                                    "max": r["max"], "has_sections": 1})
                        st, found = get(f"/api/courses?{q}")
                        if st != 200:
                            problems.append(f"{mid}: course lookup for {g['label']} answered {st}")
        print()
    print("* no sections this term")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print("  " + p)
        return 1
    print(f"\nAll {len(live)} live majors loaded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
