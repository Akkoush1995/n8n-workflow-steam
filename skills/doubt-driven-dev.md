# Skill: Doubt-Driven Development (DDD)

Write code only on ground you've checked. Every uncertainty becomes an explicit,
resolvable statement — then gets evidence — then becomes code.

## The Core Loop

```
   ┌──────────────────────────────────────────────────────┐
   │  1. NAME the doubt      "I believe X, but I'm not    │
   │                          sure because Y"             │
   │                       ↓                              │
   │  2. FIND minimal evidence (test / spike / measure)   │
   │                       ↓                              │
   │  3. PROVE or KILL the doubt                         │
   │                       ↓                              │
   │  4. Only then write production code                  │
   └──────────────────────────────────────────────────────┘
```

Rule zero: **a doubt without a name is a future bug.**

---

## 1. The Doubt Registry

Maintain doubts as a first-class artifact — a table at the top of the issue, the
design doc, or the PR. Format:

```
| # | Doubt (falsifiable) | Type | Cheapest evidence | Status |
|---|---|---|---|---|
| D1 | "This endpoint stays under 200ms at 10k req/s" | perf | bench with 100 loc | OPEN |
| D2 | "The parser handles nested quotes" | correctness | 3 unit tests | DONE-TRUE |
| D3 | "Users will paste URLs unprompted" | product | 1 user interview | KILLED |
```

Statuses: `OPEN` → `IN PROGRESS` → `TRUE` (belief confirmed) / `KILLED` (belief
dead, adjust design) / `RENEGOTIATED` (turned out to be someone else's decision).

### Doubt quality bar

Every doubt must be **falsifiable**: if nothing could prove you wrong, it's not a
doubt, it's a preference. Rewrite:

- Bad: "The library is probably slow."
- Good: "Cold-start latency exceeds 300ms if the library loads at boot."

---

## 2. Types of Doubt → Evidence Map

| Type | Ask | Cheapest evidence | Cost |
|---|---|---|---|
| **Correctness** | "Is my mental model of the API right?" | unit test / REPL probe | minutes |
| **Performance** | "Will it be fast enough?" | micro-benchmark, `console.time`, load test | 10 min–1h |
| **Compatibility** | "Does it work on their stack?" | CI matrix / version check script | minutes |
| **Product** | "Will anyone do this?" | user interview, prototype click-through | hours |
| **Architecture** | "Will this scale to N?" | 1-page spike, quick load sim | hours |
| **Security** | "Can this be abused?" | abuse-case walkthrough, authz matrix | 30 min |
| **Data** | "Is the assumption about the data true?" | real sample query, not fixtures you invented | minutes |

**Order by Risk ÷ Cost:** biggest risk, cheapest evidence first. Never run the
expensive (interview a user, build the spike service) while a cheap test is open.

---

## 3. Rules

**R1. No production code on unproven ground.**
If the doubt is correctness/perf/compat → evidence first. Only product/architecture
doubts may defer to a written assumption with an owner + expiry date.

**R2. Evidence is throwaway.**
Spikes, probes, benchmark scripts are disposable. Do NOT refactor them into the
system "since it works". Copy the RESULTS, delete the probe.

**R3. One doubt, one resolution mechanism.**
Don't "investigate" vaguely. Say: "I will resolve D2 with a failing test that
passes after the fix." When the mechanism finishes, the doubt closes — no
open-ended research.

**R4. Killed doubts feed the design.**
When a belief dies, the FIRST update is to the design doc/issue, the second is the
code. Never leave a corpse doubt silently coded over.

**R5. Diffs must reference doubts.**
In the PR: "Closes D1, D2. D3 left OPEN (owner: @x, check by Friday)". Reviewers
audit doubt-closure, not just code shape.

---

## 4. Relationship with TDD

Doubt-driven dev is TDD with a wider lens:

```
TDD:        [red: write failing test] → [green: make it pass]

DDD-TDD:    [name the doubt] → [write failing test = evidence] → [green]
                              → [am I now sure? no more doubts? → then done]
```

The test you write first IS the minimal evidence for a correctness doubt.
If you can't write the test, you haven't understood the doubt well enough — go
back to naming it.

---

## 5. Before / After Example

### Before (vibes-driven)

```
// Doute enfoui : "ça devrait marcher avec les flux venant de salons"
function parseFlux(s) { return JSON.parse(s).d || []; }
// → Produit cassé quand d absent ET quand JSON invalide
```

### After (doubt-driven)

```
// Doute D1 : "d peut manquer"        → preuve: 1 test, KILLED/testé
// Doute D2 : "JSON invalide possible" → preuve: 1 test, KILLED/testé

function parseFlux(s) {
  try { return (JSON.parse(s)?.d) ?? []; }
  catch { return []; } // trace une métrique: parse_failures++
}
```

Same lines, but every branch now owns an evidence-backed doubt.

---

## 6. Gotchas

1. **Perfectionism in disguise.** If the list of doubts never ends, you're
   stalling. Rule: >3 OPEN doubts on a small task = split the task.
2. **Invented data.** Evidence from fixtures you wrote yourself proves nothing
   about the real world. Sample real data early (D-breadth vs D-depth).
3. **Resolved but unrecorded.** A doubt you settled in your head but didn't log
   is a doubt the reviewer will re-open. Log it, even if one line.
4. **Proof-by-vibes CI.** "It worked on my machine" ≠ evidence. Automated, or it
   didn't happen.
5. **Over-fitting the spike.** Don't let 200 lines of spike become production
   code because it "already works". Copy results, rebuild clean.
6. **Killing the messenger.** A killed doubt is a WIN (cheap learning). Never
   hide KILLED rows to save face.

---

## 7. Daily Checklist

- [ ] New task: j'ai nommé mes doutes dans le registre (falsifiable, typés)
- [ ] Chaque doute ouvert a UN mécanisme de preuve le plus cheap possible
- [ ] Aucun code prod écrit sur un doute correctness/perf/compat non PROUVÉ
- [ ] La PR référence les doutes qu'elle ferme et ceux qu'elle laisse ouverts
- [ ] Les spikes sont jetables : résultats copiés, pas de merge du probe
