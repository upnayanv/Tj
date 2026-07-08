#!/usr/bin/env python3
"""
live_proxy.py -- tiny local proxy so the Breakout Desk scanner's
"live price" buttons can reach Yahoo Finance without hitting
browser CORS restrictions.

No installs needed (uses only the Python standard library).

Run:
    python live_proxy.py
    (or: python3 live_proxy.py)

Then leave this running and use the scanner HTML page as usual --
it automatically checks http://localhost:8899 first, before any
fallback. Stop with Ctrl+C.
"""
import json
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

PORT = 8899
CACHE_SECONDS = 5
_cache = {}  # symbol -> (timestamp, payload)

YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{}.NS?interval=1m&range=1d"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; BreakoutDeskProxy/1.0)"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # keep the terminal quiet

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/quote":
            self._send_json(404, {"error": "unknown endpoint, use /quote?symbol=RELIANCE"})
            return

        qs = parse_qs(parsed.query)
        symbol = (qs.get("symbol") or [""])[0].strip().upper()
        if not symbol:
            self._send_json(400, {"error": "missing ?symbol="})
            return

        now = time.time()
        cached = _cache.get(symbol)
        if cached and now - cached[0] < CACHE_SECONDS:
            self._send_json(200, cached[1])
            return

        try:
            req = urllib.request.Request(YAHOO_URL.format(symbol), headers=HEADERS)
            with urllib.request.urlopen(req, timeout=8) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
            result = raw.get("chart", {}).get("result", [{}])[0]
            meta = result.get("meta", {})
            if not meta or "regularMarketPrice" not in meta:
                self._send_json(502, {"error": "no data for " + symbol})
                return
            # Pass the whole result through (meta + today's minute-by-minute
            # OHLCV) so the page can draw today's intraday chart and walk
            # through the day to see exactly when entry/targets/SL were hit,
            # not just where price is right now.
            payload = {"symbol": symbol, "result": result}
            _cache[symbol] = (now, payload)
            self._send_json(200, payload)
        except Exception as e:
            self._send_json(502, {"error": str(e)})


if __name__ == "__main__":
    server = HTTPServer(("localhost", PORT), Handler)
    print("live_proxy.py running at http://localhost:" + str(PORT) + "  (Ctrl+C to stop)")
    print("Try it: http://localhost:" + str(PORT) + "/quote?symbol=RELIANCE")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\nStopped.")
