# Demo projet : Veille prix clés Steam — n8n

## 1. Contexte et objectif
Projet de fin d'étude (université) : construire un assistant n8n qui surveille les prix de jeux Steam **en France (prix réel magasin)** et qui compare avec les prix de **clés tierces moins chères (keyshops)**, puis envoie automatiquement par email un tableau comparatif et un **résumé IA des meilleures affaires**.
Programme : exécution **2 fois par semaine (mardi + samedi à 10h)**.

## 2. Stack et sources gratuites, sans clé sensible
| Source | Rôle | Gratuit |
|---|---|---|
| **Steam Storefront API** (`appdetails?cc=fr`) | Prix Steam FR réels | ✅ sans clé |
| **GG.deals API** (`by-steam-app-id`) | Prix clés chez revendeurs, en USD | ✅ clé à usage démo |
| **Frankfurter** (ECB) | Conversion USD → EUR du jour | ✅ sans clé |
| **Gemini (Google AI)** | Résumé des meilleurs deals en français | ✅ via credential Google existante |
| **n8n + SMTP (Gmail)** | automation + envoi d'email | ✅ |

## 3. Scope, en 3 étapes
1. **Ingestion des prix** : prix Steam FR du jour + prix clés GG.deals (USD → EUR via ECB)
2. **Comparaison intelligente** : calcul écart en € et en %, repérage des deals, gestion des jeux verrouillé par région (signalés “à vérifier manuellement”, jamais supprimés)
3. **Restitution** : génération d’un CSV attaché au mail + résumé rédigé par l’IA des 3 meilleures affaires

## 4. Nodes utilisées et leurs specs
| Node | Spécification |
|---|---|
| `Schedule` | Trigger cron `0 8 * * 2,6` (mar + sam 10:00 heure française été) |
| `Appid List` | Nœud Set préparant la liste d’appids Steam (5 jeux en fallback) + placeholder wishlist |
| `Steam FR Prices` | HTTP GET `appdetails?cc=fr`, prix réels FR |
| `GG Deals USD` | HTTP GET GG.deals, clé inline URL, retours prix clé |
| `FX Rate EUR` | HTTP GET Frankfurter USD→EUR taux ECB |
| `Build Report` | Code : fusionne les 3 sources, calcule `écart €` et `%`, marque n/a + notes |
| `Compose Deals XML` | Code : agrège toutes les lignes en un bloc XML unique (`$json.xml`) pour alimenter l’IA |
| `Summarize Deals` | **Node Gemini natif** (resource `text` / operation `message`, model Gemini 2.5 Flash) : demande le descript/résumé des meilleures affaires en XML |
| `Convert To File` | Rassemble les lignes en un fichier CSV joint |
| `Merge` | Combine le CSV et le résumé IA en un seul item |
| `Send Deals Email` | Envoi du mail au format texte : résumé IA + lien CSV attaché, par SMTP |

## 5. Cheminement du workflow
```
Schedule (mar/sam 10h)
   └─ Appid List
   └─ Steam FR Prices ─┐
   └─ GG Deals USD ────┤── Build Report (Code : merge + calculs)
   └─ FX Rate EUR ─────┘
   ├───────────────────────────┐
   ▼                           ▼
Convert To File (CSV)    Compose Deals XML (Code)
   │                    ▼
   │               Summarize Deals (Gemini IA)
   └────────── Merge ───────────┘
        ▼
   Send Deals Email (SMTP : résumé + CSV joint)
```

## 6. Résultat attendu
Toutes les 30s après exécution, le mail arrive avec :
- 1 paragraphe IA (top 3 affaires, économies € et %)
- un CSV listant chaque jeu (Steam €, clé €, écart €, écart %, statut Deal / à vérifier)

## 7. Limites du projet
- **Wishlist statique** (5 jeux codés en dur) : le branchement wishlist (`profileSlug`) est prévu mais non priorité pour la démo initiale
- Prix clés conscentés en **USD → conversion ECB** : pas de prix régionalisés, l’écart peut légèrement varier
- Prix Steam FR via `cc=fr` ; jeux à **région lockée** indiqués “à vérifier” (ex. Persona 5 Royal)
- **Sécurité** : la clé GG.deals est **inline dans l'URL** (le projet n8n cloud bloque `{{ $env }}`) — OK pour la démo, à migrer vers credential dans la version finale
- **Dépendance externe** : un blocage WAF depuis le cloud arrêt LA chaîne (circuit cassé, identifié facilement)
- Gemini = géré par l’IA donc le résumé peut varier (mais bien borné par la demande)
- **Extensible** : ajout simple de la wishlist réelle, d’alertes Push (Discord/Telegram), d’un tri par popularité

---

© Démo  — Veille Steam, n8n, 2026
