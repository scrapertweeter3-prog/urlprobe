#!/usr/bin/env python3
"""urlprobe - tiny zero-dependency URL health checker (Python stdlib only)."""

import argparse
import concurrent.futures
import sys
import time
import urllib.request

UA = "urlprobe/1.0 (+https://github.com/scrapertweeter3-prog/urlprobe)"


def check(url, timeout):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    start = time.perf_counter()
    status = None
    err = ""
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
    except urllib.error.HTTPError as e:
        status = e.code
    except Exception as e:
        err = str(getattr(e, "reason", e)) or type(e).__name__
    ms = round((time.perf_counter() - start) * 1000)
    if err or status >= 400:  # some servers reject HEAD; retry with GET
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status, err = resp.status, ""
        except urllib.error.HTTPError as e:
            status = e.code
        except Exception as e:
            err = err or (str(getattr(e, "reason", e)) or type(e).__name__)
    return (url, status, ms, err)


def main():
    ap = argparse.ArgumentParser(description="Check a list of URLs. One per line on stdin or as args. Comments (#) and blank lines ignored.")
    ap.add_argument("urls", nargs="*", help="URLs to check (reads stdin if none given)")
    ap.add_argument("-w", "--workers", type=int, default=8, help="parallel workers (default 8)")
    ap.add_argument("-t", "--timeout", type=float, default=10.0, help="per-request timeout seconds (default 10)")
    ap.add_argument("-0", "--fail-fast", action="store_true", help="exit 2 immediately if any check fails")
    args = ap.parse_args()

    urls = args.urls or [l.strip() for l in sys.stdin if l.strip() and not l.strip().startswith("#")]
    if not urls:
        ap.error("no URLs given (stdin or args)")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(check, u, args.timeout): u for u in urls}
        for f in concurrent.futures.as_completed(futs):
            r = f.result()
            results.append(r)
            mark = "OK " if (r[1] and r[1] < 400) else "ERR"
            err = f" ({r[3]})" if r[3] else ""
            print(f"{mark} {r[1] if r[1] is not None else '---'} {r[2]:>6}ms  {r[0]}{err}", flush=True)
            if args.fail_fast and mark == "ERR":
                sys.exit(2)

    bad = [r for r in results if not (r[1] and r[1] < 400)]
    total_ms = sum(r[2] for r in results)
    print(f"-- {len(results) - len(bad)}/{len(results)} up, {total_ms}ms total")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
