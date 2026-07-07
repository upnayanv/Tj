# Breakout Desk — Setup Scanner

A single-file, client-side NSE breakout/breakdown scanner. You upload bhav copy
(EOD) CSVs, it does everything else in your browser — no backend required for
the scanner itself. Live price checks use an optional local proxy (below).

## 1. Put this on GitHub Pages

Same pattern as your other tools (e.g. `attendance.biguineindia.co.in`):

1. Create a new GitHub repo (public or private — Pages works on both if you're
   on GitHub Pro/Team/Enterprise; public repos get Pages free on any plan).
2. Push these files to the repo root:
   - `index.html` (the scanner itself — GitHub Pages serves this automatically
     at the root URL, no extra config needed)
   - `live_proxy.py` (optional, for reliable live prices — see below)
3. Repo → **Settings → Pages** → Source: **Deploy from a branch** → Branch:
   `main` (or `master`) → folder `/ (root)` → **Save**.
4. Wait ~1 minute, then your scanner is live at:
   `https://<your-username>.github.io/<repo-name>/`
   (or your own custom domain, if you map one via a `CNAME` file — same as you
   already do for your other Pages sites).

That's it — no build step, no dependencies, no server for the scanner itself.

## 2. Uploading stock data

Nothing changes here — open the live URL, drag your NSE bhav copy CSV/ZIP
files onto Step 01 same as you would with the local file. Everything runs in
your browser; nothing gets uploaded to GitHub or any server. Re-upload a new
day's file each evening and re-run the scan.

## 3. Live prices (optional, but recommended)

The scanner's "Check live" buttons need `live_proxy.py` running on **your own
machine** — GitHub Pages only hosts static files, it can't run this for you.

```
python live_proxy.py
```

Leave that terminal open while you use the scanner (works whether you're
opening the file locally or via the GitHub Pages URL — same `localhost:8899`
call either way).

### One browser detail (Chrome, Edge, other Chromium browsers)

When the scanner is served over **HTTPS** (like a `github.io` URL) and it
tries to reach `localhost`, Chrome shows a one-time **"Allow local network
access?"** popup. Click **Allow** — this is Chrome protecting your network by
design, not a bug. Firefox doesn't currently show this prompt.

If you skip running `live_proxy.py` entirely, the scanner still works for
scanning/backtesting — "Check live" will just fall back to a public,
best-effort CORS proxy (slower, sometimes rate-limited) instead of failing
outright.

## 4. Updating the scanner later

Any time you get an updated `index.html`, just commit/push it to the same
repo — GitHub Pages redeploys automatically within a minute or two, same as
your existing GitHub Pages workflow.
