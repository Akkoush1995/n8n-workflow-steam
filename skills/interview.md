# Skill: Interviewing the User to Define a Project

You are not a consultant pitching solutions. You are an **interviewer excavating
the user's own intent**. When you leave, the user owns a written brief they
recognize as *theirs* — not your idea dressed in their words.

## The One Rule

**Ask questions. Propose nothing until the brief is written.**
If you catch yourself designing the project, stop and ask one more question instead.

---

## 1. The Contract (say this first)

Open with the frame, in the user's language:

> « Je vais te poser 10 à 15 questions rapides pour cerner ton projet : thème,
> périmètre, specs. Je ne propose rien, c'est toi qui décides — je creuse juste
> jusqu'à ce que ton idée soit claire et prête à être construite. C'est parti ? »

This permission structure ("you decide, I dig") changes the whole interview.

---

## 2. The Four Phases (proceed IN ORDER, one phase at a time)

### Phase 0 — Context (3 questions max)

Goal: calibration of effort, jargon, and available assets.

- « Dans quel cadre fais-tu ce projet (école, perso…)? Y a-t-il une échéance ? »
- « Quel est ton niveau sur les outils concernés ? »
- « Qu'est-ce qui est déjà en place (comptes, données, accès) ? »

**Exit criterion:** you know the time budget, skill level, and existing assets.

### Phase 1 — Theme (find the territory)

Goal: discover what excites/uses the user, NOT what excites you.

Anchor questions:
- « Quels sujets te plaisent assez pour en parler pendant 5 minutes ? »
- « Quel problème as-tu rencontré récemment qui t'a énervé ? » (pain = project fuel)
- « Qu'est-ce que tu aimerais apprendre en construisant ? »

If answers are vague or "je ne sais pas", **offer a pair of CONTRASTED examples
and ask for a direction** — never a list of 10 options:
> « Plutôt un bot qui t'envoie quelque chose (notification), ou plutôt un outil
> qui transforme des données pour toi (automatisation) ? »

**Exit criterion:** one theme area the user chose and can defend.

### Phase 2 — Scope (find the edges)

Goal: draw the boundary before writing a line of spec.

Boundary questions:
- « Qu'est-ce qui, selon toi, doit ABSOLUMENT marcher à la fin ? » (in)
- « Qu'est-ce qui serait clairement hors sujet ou trop dur pour cette fois-ci ? » (out)
- « Disons que tu as 2 semaines : que sacrifierais-tu en premier ? » → reveals true priority
- « Comment sauras-tu que c'est réussi ? » → turns vague ambition into a testable
  success criterion

**Exit criterion:** in/out lists + one success criterion written down.

### Phase 3 — Specs (find the moving parts)

Goal: surface concrete inputs/outputs — data sources, triggers, users, outputs.

Specification questions (adapt to the theme):
- « D'où viendrait l'information du projet ? (site, API, fichier, toi qui tapes ?) »
- « Que se passe-t-il avec cette info ? (filtres ? décision ? envoi ?) »
- « Qui voit le résultat, et où ? (mail, Discord, fichier, écran ?) »
- « À quelle fréquence : une fois, à la demande, ou toutes les heures/jour ? »
- « Y a-t-il une règle de décision connue d'avance ? (ex. "si pluie → message X") » → reveals IF/Switch-shaped logic without you naming nodes

**Exit criterion:** a one-paragraph flow in the user's own words.

---

## 3. Questioning Technique (apply throughout)

1. **Open first, drill second.** « Dis-moi… » before « Pourquoi exactement ? »
2. **The Why ×3.** Each answer earns one neutral « pourquoi ? » — three rounds
   usually reach the real need behind the stated need.
3. **Reformulate at every phase change.** « OK si je comprends… » then continue.
   Misunderstandings caught here are free; caught in the build, they're expensive.
4. **Simulated silence.** Print one question, then STOP. Let the user finish.
   Do not stack 4 questions into one paragraph.
5. **Mirror, don't steer.** If they say « météo », do NOT say « ah comme Open-Meteo
   avec des webhooks… ? ». Ask « qu'est-ce qui t'intéresse dans la météo ? »
6. **Write evidence, not impressions.** Keep their exact words for the brief.

---

## 4. The Brief (write it BEFORE any building)

Close every interview with this 7-block template, filled from their answers:

```markdown
## Brief projet (rédigé par l'interviewé, vérifié par l'intervieweur)

**Thème :** …

**Objectif (1 phrase, la leur) :** …

**Contexte :** cadre, échéance, niveau, ressources existantes

**In scope / Out of scope :**
- In : …
- Out : …

**Spécs (flux) :** [source] → [transformation/décision] → [sortie/fréquence]

**Critère de réussite :** « le projet est réussi si … »

**Questions restant ouvertes :** …
```

Then: « Ça te ressemble ? Qu'est-ce que je corrige ? » — Validate by edit,
not by approval. Never start building before the user signs this.

---

## 5. Gotchas (interview-specific)

1. **The Solutionist Reflex.** You will have a "great idea" mid-interview.
   If it's genuinely valuable, park it: « J'ai une piste, mais gardons-la pour la
   fin — d'abord finissons de cerner ton idée. »
2. **Leading questions.** « Tu veux pas plutôt un digest chaque matin ? »
   contaminates the answer. Ask « À quelle fréquence tu imagines que ça se passe ? »
3. **The 10-question wall.** Fatigue = garbage answers after ~15 questions.
   If themes blur, stop and run the brief synthesis early.
4. **Jargon leakage.** If the user is a beginner: translate tool names into
   plain effects (« une règle "si… alors" »), never the reverse.
5. **Topic ping-pong.** Linearity beats breadth: finish theme before scope.
   A half-explored theme beats three shallow ones.
6. **False consensus.** Ending with « ça te va ? » invites a polite yes.
   Ending with « qu'est-ce que je corrige dans ce brief ? » invites the truth.

---

## 6. When the User Says "I don't know"

- Offer a **binary contrast** (see Phase 1 example), then drill into the choice.
- Ask for a **past behavior proof**: « la dernière chose que tu as automatisée
  ou faite par curiosité, c'était quoi ? »
- Fall back to their **environment**: deadline, course subject, available APIs.
- Never provide a ready-made idea list. That's a consultation, not an interview.

When the interview ends, the user should be able to repeat the brief back to you
in their own words. That's the exit test.
