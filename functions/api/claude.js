// functions/api/claude.js
// Cloudflare Pages Function. Becomes https://yoursite.pages.dev/api/claude
//
// Required environment variables (set in Cloudflare dashboard):
//   ANTHROPIC_API_KEY        — your Anthropic key, never sent to the client
//   DAILY_GLOBAL_CAP         — total requests/day across all users (e.g. "300")
//   DAILY_PER_IP_CAP         — requests/day per IP (e.g. "20")
//
// Required KV binding (also set in dashboard):
//   AOA_LIMITS               — Cloudflare KV namespace for counters
//
// Counters reset at midnight UTC. Each turn in the product is one request,
// so a 6-turn opening exchange uses 6 of the user's daily budget.

export async function onRequestPost({ request, env }) {
  // ---- 1. Read configuration ----
  const apiKey = env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return json({ error: "Server is missing its API key. Tell the host.", keys: Object.keys(env), hasKey: !!env.ANTHROPIC_API_KEY, keyLength: (env.ANTHROPIC_API_KEY || "").length }, 500);
  }
  const dailyGlobalCap = parseInt(env.DAILY_GLOBAL_CAP || "300", 10);
  const dailyPerIpCap = parseInt(env.DAILY_PER_IP_CAP || "20", 10);
  const kv = env.AOA_LIMITS;

  // ---- 2. Identify the caller ----
  const ip = request.headers.get("CF-Connecting-IP")
          || request.headers.get("X-Forwarded-For")?.split(",")[0]?.trim()
          || "unknown";

  // ---- 3. Enforce caps (only if KV is bound) ----
  if (kv) {
    const today = new Date().toISOString().slice(0, 10); // YYYY-MM-DD, UTC
    const globalKey = `global:${today}`;
    const ipKey = `ip:${today}:${ip}`;

    const [globalCountStr, ipCountStr] = await Promise.all([
      kv.get(globalKey),
      kv.get(ipKey),
    ]);
    const globalCount = parseInt(globalCountStr || "0", 10);
    const ipCount = parseInt(ipCountStr || "0", 10);

    if (globalCount >= dailyGlobalCap) {
      return json({
        error: "limit_global",
        message: "The reading room is full for today. The day's exchanges have all been spent. Come back tomorrow.",
      }, 429);
    }
    if (ipCount >= dailyPerIpCap) {
      return json({
        error: "limit_ip",
        message: "You've reached the daily limit for one visitor. Come back tomorrow.",
      }, 429);
    }

    // Increment both counters. KV writes are eventually consistent but fine
    // for a soft cap. Set TTL to 36h so keys expire on their own.
    const ttl = 60 * 60 * 36;
    await Promise.all([
      kv.put(globalKey, String(globalCount + 1), { expirationTtl: ttl }),
      kv.put(ipKey, String(ipCount + 1), { expirationTtl: ttl }),
    ]);
  }

  // ---- 4. Pass the request through to Anthropic ----
  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: "Bad request body" }, 400);
  }

  // Light input safety: cap the prompt size so a hostile client cannot
  // burn tokens. 30K characters is generous for our prompts (which top out
  // around 8K including transcripts) and rejects abuse.
  const totalChars = JSON.stringify(body).length;
  if (totalChars > 30000) {
    return json({ error: "Request too large" }, 413);
  }

  // Force the model and max_tokens server-side. Client cannot escalate.
  const allowedModels = new Set([
    "claude-sonnet-4-20250514",
    "claude-haiku-4-5-20251001",
  ]);
  const model = allowedModels.has(body.model) ? body.model : "claude-sonnet-4-20250514";
  const maxTokens = Math.min(parseInt(body.max_tokens || 1500, 10), 2500);

  const upstream = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model,
      max_tokens: maxTokens,
      messages: body.messages || [],
    }),
  });

  // Stream the upstream response back. Preserve status code so the client
  // can distinguish 401/429/500 from 200.
  const text = await upstream.text();
  return new Response(text, {
    status: upstream.status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
  });
}

export async function onRequestOptions() {
  // CORS preflight, in case the HTML is opened from a different origin.
  return new Response(null, {
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Access-Control-Max-Age": "86400",
    },
  });
}

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
  });
}
