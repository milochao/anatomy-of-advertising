# Deploying The Anatomy of Advertising

This guide gets you from your laptop to a live URL on Cloudflare Pages in
about ten minutes. It assumes you have a GitHub account and a Cloudflare
account.

## What's in this folder

```
.
├── index.html              ← the app
├── portraits/              ← 30 portrait images
├── functions/
│   └── api/
│       └── claude.js       ← serverless proxy that holds your API key
└── DEPLOY.md               ← you are here
```

The HTML calls `/api/claude` instead of calling Anthropic directly. The
function adds your API key server-side and enforces request caps. Your
key never reaches the browser.

> Note: rename `anatomy_of_advertising.html` to `index.html` before pushing.
> Cloudflare Pages serves the root URL from `index.html` by default.

## Step 1 — Push to GitHub

Create a new repository on GitHub. Push these files at the root of the
repo. The folder structure shown above must be preserved exactly —
Cloudflare Pages auto-discovers `functions/` and turns each file inside
into an endpoint.

## Step 2 — Connect to Cloudflare Pages

1. Log in to the Cloudflare dashboard.
2. Go to **Workers & Pages** → **Create** → **Pages** → **Connect to Git**.
3. Pick the repo you just pushed.
4. Build settings: leave everything blank. This is a static site with
   functions — no build step.
5. Click **Save and Deploy**. Cloudflare gives you a URL like
   `your-site.pages.dev`. The site is live but the AI calls won't work
   yet — the API key isn't set.

## Step 3 — Set the API key (required)

In the Cloudflare dashboard for your Pages project:

1. **Settings** → **Environment variables**.
2. Add a **Production** variable:
   - Name: `ANTHROPIC_API_KEY`
   - Value: your `sk-ant-...` key from console.anthropic.com
   - Click **Encrypt** so the key is hidden after saving.
3. Add two more variables to set the caps (plain text, not encrypted):
   - `DAILY_GLOBAL_CAP` — total exchanges per day across all visitors.
     Start with `300`. (Each opening exchange is ~6 turns, so this
     allows roughly 50 full opening exchanges before rate-limiting.)
   - `DAILY_PER_IP_CAP` — exchanges per visitor per day. Start with `20`.

## Step 4 — Set up the rate-limit storage (required)

Without this step, the caps will not be enforced.

1. **Workers & Pages** → **KV** → **Create namespace**.
2. Name it `aoa-limits`. Click **Add**.
3. Go back to your Pages project → **Settings** → **Functions** →
   **KV namespace bindings**.
4. Click **Add binding**.
   - Variable name: `AOA_LIMITS`
   - KV namespace: select `aoa-limits`
5. Save.

## Step 5 — Set the hard ceiling at Anthropic (do this first, actually)

This is the single most important step. It is the only thing standing
between you and a viral-spike bill. If everything below fails, this stops
the bleeding.

1. Log in to console.anthropic.com.
2. Go to **Billing** → **Usage limits**.
3. Set a monthly spend cap. For a teaching tool, start with `$50` per
   month. The API will start returning errors once you hit the cap.
4. Set up a notification email at 50%, 75%, 90% of the cap.

## Step 6 — Redeploy

After setting environment variables and KV, trigger a new deploy from
the Cloudflare dashboard (**Deployments** → **Retry deployment**) or
push any change to GitHub. The variables only take effect on a fresh
deploy.

Visit your `pages.dev` URL. Pick a pairing. The room sets, the figures
take their seats, the exchange begins. No API key gate appears.

## How the caps work

The proxy runs three checks on every request:

1. **Anthropic-side cap** — your monthly $ ceiling. Fires last but
   guarantees the bill cannot exceed your number.
2. **Daily global cap** — total requests across all users today.
   Resets at midnight UTC. Returns a friendly *the room is full for
   today* message.
3. **Daily per-IP cap** — requests from one visitor today. Same reset.
   Same message register.

Counters live in Cloudflare KV, not in your code. They cost ~zero and
expire automatically after 36 hours.

## What costs what

A single opening exchange uses roughly:

- 6 turn-generation calls (Sonnet, ~600 tokens each)
- 5 referee calls (Sonnet, ~200 tokens each)
- 1 topic call if no topic given (~150 tokens)

At Sonnet 4 prices, that's roughly **$0.04 to $0.06 per opening exchange**.

So with the suggested caps:
- 300 exchanges/day × $0.05 = **$15/day worst case**
- 30-day month at the daily cap = **~$450/month worst case**

That's why the Anthropic-side $50 monthly cap is the real ceiling.
The per-day caps are there to flatten spikes.

## Custom domain (optional)

Once it's working on `your-site.pages.dev`, you can add a custom domain
in **Custom domains** in the Pages settings. Point the DNS as instructed.
Free and one-click if your domain is already on Cloudflare.

## Adjusting the caps

Edit the environment variables in the Cloudflare dashboard. No code
change needed. New values take effect after a few seconds.

## If something breaks

- **AI calls fail with 500.** Check that `ANTHROPIC_API_KEY` is set in
  the Pages environment variables and the deployment was redone after
  setting it.
- **Caps don't fire.** Check that the `AOA_LIMITS` KV binding is in
  place. Without the KV binding, the proxy will let every request through.
- **CORS errors in the browser console.** Shouldn't happen on Pages
  since the function and the HTML are on the same origin. If it does,
  hard-refresh the page.

## Local testing (optional)

To test the proxy locally before pushing:

```bash
npm install -g wrangler
wrangler pages dev .
```

This starts a local server at `http://localhost:8788` that runs the
function and serves the HTML. You'll need to set the API key as a local
environment variable: `ANTHROPIC_API_KEY=sk-ant-... wrangler pages dev .`
