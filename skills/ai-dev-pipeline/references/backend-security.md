# Backend security — AuthZ vs AuthN, dangerous defaults

Read when implementing or verifying a **backend / API / money** task.
These rules exist because privileged write endpoints often ship with login-only
middleware (e.g. `auth:sanctum`) while any authenticated client can still mutate
balances or settle orders — the model satisfies "add auth middleware" literally
and misses **authorization**.

## AuthN ≠ AuthZ (privileged / money writes)

| Term | Meaning | Enough alone? |
|------|---------|---------------|
| AuthN | Caller is logged in (`auth:sanctum`) | No for admin / settle / payout |
| AuthZ | Caller is allowed (role / policy / gate / ability) | Required for privileged writes |

**Must-hold for privileged writes** (admin settle, warehouse weigh, force-cancel,
payout retry, config price edits, etc.):

1. Middleware or policy that restricts to admin / staff ability — not login alone.
2. At least one Feature test: **non-privileged user → 403** (or 401 if unauthenticated).
3. `route:list` (or equivalent) shows the privilege guard, not only `auth`.

Mutating C-end writes (create order, cancel, boost, withdraw apply) default to
**authenticated** unless acceptance explicitly allows anonymous with a why.
Responses must not leak another user's PII (phone, address, openid) to callers
who are not authorized for that resource.

Payout / withdraw **receive account** comes from server-side binding or snapshot —
do not trust a client-supplied arbitrary account as the sole source of truth.

## Dangerous defaults (Mock / skip-sign)

| Switch | Production / default | Allowed only when |
|--------|----------------------|-------------------|
| Auth / payment / express Mock | **off** | Explicit env (e.g. `MOCK_*=true`) and not production |
| Third-party callback skip-sign | **off** | Explicit env and non-production |

Verify by reading `.env.example` / config defaults / a test that production
forces these off. "Documented in README" alone is not a mechanism.

## Contrast pairs

**Privileged settle**
- Correct: `auth` + `admin` (or policy) + test `actingAs($user)->post(...settle)->assertForbidden()`.
- Incorrect: login middleware only with a comment like "admin UI auth later — open for now".
- Why: login proves identity; it does not prove warehouse/finance privilege. Money moves without AuthZ.

**Callback signature**
- Correct: verify signature by default; skip-sign env only in local/test.
- Incorrect: `if (config('payments.skip_sign', true))` — skip is the default.
- Why: a default-open callback is a public write API into order state.

**Withdraw account**
- Correct: load payout account from user profile / prior binding snapshot.
- Incorrect: accept any client-supplied account JSON from the request body as sole truth.
- Why: client-chosen payout destination enables theft after balance credit.
