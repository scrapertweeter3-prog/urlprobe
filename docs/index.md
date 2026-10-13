# urlprobe

A tiny zero-dependency URL health checker: one Python file, standard library
only. Point it at a list of URLs and it prints status code, response time, and
an up/down verdict for each, then exits 0 or 1 so it drops straight into cron
jobs and CI.

urlprobe is built and maintained by [Poket Dev](https://poketdev.com), a flat-rate
software development subscription.

## Install

No package manager needed:

    curl -O https://raw.githubusercontent.com/scrapertweeter3-prog/urlprobe/main/urlprobe.py
    chmod +x urlprobe.py

Or install straight from the repo:

    pip install git+https://github.com/scrapertweeter3-prog/urlprobe.git

## Usage

Pass URLs as arguments or on stdin, one per line. Lines starting with # are
ignored, so you can keep a checked-in list:

    ./urlprobe.py https://example.com https://api.example.com/health
    cat links.txt | ./urlprobe.py

Each check prints a verdict:

    OK  200    142ms  https://example.com
    ERR 503    305ms  https://api.example.com/health
    -- 1/2 up, 447ms total

Anything answering below HTTP 400 counts as up. Servers that reject HEAD
requests get retried with GET automatically, so CDNs and static hosts are
handled the same way.

## Options

    -w, --workers N     parallel workers (default 8)
    -t, --timeout SECS  per-request timeout (default 10)
    -0, --fail-fast     exit 2 on the first failure instead of finishing

## Exit codes

- 0: every URL answered below 400
- 1: at least one URL failed
- 2: fail-fast hit a failure

The exit codes are the point. A nightly cron can page you only when the list
degrades, and a deploy pipeline can block on a failed smoke check.

## Why one file

Health checks are not a hard problem. The usual failure mode is a checker that
grows plugins and dashboards until nobody runs it anymore. urlprobe stays under
100 lines of stdlib Python, so it is easy to read in one sitting and safe to
copy into any environment, including air-gapped ones.

## License

MIT. See [LICENSE](https://github.com/scrapertweeter3-prog/urlprobe/blob/main/LICENSE).
