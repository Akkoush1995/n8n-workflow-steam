# Skill: Hostile Code Review

A good review answers "does this work?". A hostile review answers
**"how does this fail, and who pays for it?"**

The code is guilty until proven innocent. Every claim in the PR body is a
hypothesis. Your job: break it faster than production will.

## The Mindset

1. **I am not reviewing the author's effort. I am attacking the artifact.**
   Kindness to the person, hostility to the code.
2. **The PR description is marketing.** Verify, don't trust.
3. **Every line must earn its fear budget.** If a line can't fail, say nothing.
   If it can, demand the guard.
4. **No "LGTM" without per-claim confirmation.**

---

## 1. The Attack Checklist

### A. Failure modes (reliability)
- [ ] What happens if the dependency is down/slow (timeouts? retries? circuit breaker?)
- [ ] What happens on partial failure (half-written files, crashed mid-transaction)?
- [ ] Idempotency: can this job/event run twice safely?
- [ ] Backpressure / unbounded queues / memory growth over hours?
- [ ] Startup and shutdown paths (not just the happy path)?

### B. Data & boundaries (correctness)
- [ ] Every external input: validated, typed, bounded? (empty, null, 10k chars, unicode, negative, NaN)
- [ ] Pagination, cursor drift, off-by-one at page boundaries?
- [ ] Time: timezones, DST, clock skew, leap seconds, expiry edge ("exactly at midnight")?
- [ ] Concurrency: two requests at once, lost updates, duplicate delivery?
- [ ] What happens to TODAY's data shape next year (schema change, new enum value)?

### C. Security
- [ ] Authenticated AND authorized? (auth ≠ authz: can this user touch THIS object?)
- [ ] Injection vectors: SQL, shell, template, HTML, LDAP, XML?
- [ ] Secrets: hardcoded? logged? leaked into errors/metrics/traces?
- [ ] Mass assignment / over-posting (fields the client shouldn't set)?
- [ ] Rate limiting on expensive or destructive endpoints?
- [ ] Files: type, size, filename, path traversal?
- [ ] Config: defaults that are insecure in prod (`debug=true`, CORS `*`)?

### D. Hidden assumptions
- [ ] Commented-out "fixes" and mysterious constants: named, explained, or removed?
- [ ] Assumptions about call order, initialization, single-threadedness?
- [ ] "This never happens" branches: proven, or hopeful?
- [ ] Copy-pasted code: does the copy still fit the new context?
- [ ] Dead flags, dead routes, unreachable code?

### E. Design & debt
- [ ] The 3rd occurrence of a pattern: is this now a helper/abstraction?
- [ ] Error handling consistent (no mix of throw/silent-swallow/console.log)?
- [ ] Naming: intent-revealing or does the reader need a archaeology degree?
- [ ] Logs/metrics: would I find THIS failure at 3am with what's emitted?
- [ ] Tests: do they test behavior or just line coverage? Mutation-checked?

---

## 2. Severity Scale (use exactly these)

| Level | Definition | Example |
|---|---|---|
| 🔴 **BLOCKER** | Data loss, security hole, guaranteed prod incident | SQL injection, lost writes, secret in repo |
| 🟠 **MAJOR** | Real failure path, degrades service or correctness | unhandled null on a 1%-traffic route |
| 🟡 **MINOR** | Robustness/UX debt, not on critical path | missing metric, vague error message |
| ⚪ **NIT** | Style, naming, micro-cleanup | rename for clarity |

Rule: if unsure between two levels, pick the LOWER one, but say why you hesitated.

---

## 3. Evidence Standard

Every 🟠/🔴 finding must carry:

```
📍 FILE:LINE
✂️  PASTE: the offending code (3-10 lines)
🧪 REPRO: concrete scenario — input/state → expected → actual
💣 COST: who gets hurt, how often, how much
💡 FIX or QUESTION: a direction, not just a critique — unless the fix is unclear, then ask THE question that unblocks
```

No repro = opinion. Opinions get ignored. Find the repro or downgrade to nit with a note.

### Templates that get replies

> **"What happens when `retries(∞)` meets an auth token that expires at request 50?"**
> Cost: reconnect storms every hour. Repro: kill DB mid-flush, watch.

> **Block at ` if (x) return;`** — the `else` below re-decorates `x`. Unless intentional, this is unreachable by construction.

> **"Temporary" `maxInt` on buffer size.** Name says temp, line 1 of the diff, still shipped from 3 PRs ago. Own it or delete it.

---

## 4. The Author's Counter-Moves (be ready)

| Author move | Reviewer counter |
|---|---|
| "It's out of scope" | Fine. Then it becomes a tracked debt note (issue link) IN the review, or it leaks to prod. |
| "That can't happen" | Prove it in a test. Until then, add the guard or the log. |
| "It works on my machine" | Then your machine is the bug. Repro with the data shape from staging. |
| "We don't have time" | Every blocker has a price list: write down the price, product decides knowingly. |
| "You didn't read the design doc" | Good — test the doc against the code. If they disagree, THAT is the finding. |

---

## 5. Procedure

1. **Read the PR body as claims list.** Restate each into a verify-able statement.
2. **Run the attack checklist top to bottom.** Don't freestyle order — attackers are thorough, not lucky.
3. **Draft findings** with evidence standard; downgrade ruthlessly to nit what isn't proven.
4. **Endorse what's genuinely good in ONE line.** Sincere > polite > noisy.
5. **Verdict per finding:**
   - `MUST FIX` (🔴/🟠 proven)
   - `SHOULD fix or track` (🟡)
   - `nit` (⚪)
6. **After author replies:** re-verify the FIX by reading the new diff, not by trusting the reply text. Fixes introduce bugs; that's the ironic certainty.

---

## 6. Gotchas (hostile-review specific)

1. **Hostility season drift.** Anger at the nth bad PR this week is not a finding. Cool it, re-run the evidence standard.
2. **Nit-flooding.** 40 nits on a 10-line diff = review theater. Cap nits; batch them in one collapsible comment.
3. **Solution-selling.** Your job is to find the hole, not to redesign their module. Point, prove, propose direction; let the author fix.
4. **Obligation to block.** Blocking is expensive. Many "blockers" become minors once the author shows the real data shape. Ask first, escalate second.
5. **Speed bias.** "Reviewed in 4 minutes" boasts are correlated with missing the 3am bug. The adversary doesn't rush.
6. **Kill the author, not the code.** "This is brain-dead" teaches nothing and signals fear. "This loses user data when X; here's the edge case" teaches everything.

---

## 7. Final Gate (before approval)

- [ ] Every 🔴/🟠 has repro OR explicit author+reviewer agreement to track it
- [ ] New code paths have a test for the failure mode, not just success
- [ ] Logs would let me diagnose the top-2 failure modes without adding prints
- [ ] No new secrets, no new debug flags defaulting dangerous
- [ ] I read the FULL diff including generated/lockfile changes (diff-the-diff)
- [ ] Approval states what I verified, not just "looks fine"

**The signature of a hostile reviewer: the author feels challenged, the users don't get to find out first.**
