from contextlib import nullcontext
import os.path
import requests
import sys

import pyperf
import netutils


DATADIR = os.path.join(
    os.path.dirname(__file__),
    "data",
)
ARGV = [sys.executable, "serve.py"]


#############################
# benchmarks

def bench_aiohttp_requests(loops=3000):
    elapsed, _ = _bench_aiohttp_requests(loops)
    return elapsed


def _bench_aiohttp_requests(loops=3000, legacy=False):
    """Measure N HTTP requests to a local server.

    Note that the server is freshly started here.

    Only the time for requests is measured here.  The following are not:

    * preparing the site the server will serve
    * starting the server
    * stopping the server

    Hence this should be used with bench_time_func()
    insted of bench_func().
    """
    start = pyperf.perf_counter()
    elapsed = 0
    times = []

    requests_get = requests.get
    for i in range(loops):
        # This is a macro benchmark for a Python implementation
        # so "elapsed" covers more than just how long a request takes.
        t0 = pyperf.perf_counter()
        requests_get("http://localhost:8080/blog/").text
        t1 = pyperf.perf_counter()

        elapsed += t1 - t0
        times.append(t0)
    times.append(pyperf.perf_counter())
    return elapsed, times


#############################
# the script

if __name__ == "__main__":
    from legacyutils import maybe_handle_legacy
    maybe_handle_legacy(_bench_aiohttp_requests, legacyarg='legacy')

    if "--worker" not in sys.argv:
        context = netutils.serving(ARGV, DATADIR, "127.0.0.1:8080")
    else:
        context = nullcontext()

    with context:
        runner = pyperf.Runner()
        runner.metadata['description'] = "Test the performance of aiohttp"
        runner.bench_time_func("aiohttp", bench_aiohttp_requests)
