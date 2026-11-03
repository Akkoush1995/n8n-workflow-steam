# n8n-workflow-steam — Steam Key Deal Watch

Watch de prix de clés Steam : tous les **mardis et samedis à 08:00 UTC** (10:00 France en été), le workflow compare **le prix du store Steam (FR)** avec **le prix des revendeurs de clés (keyshops USD convertis en EUR)** pour chaque jeu d'une wishlist Steam, génère un CSV, puis envoie un email avec le tableau complet + un résumé rédigé par l'IA (Gemini Flash-Lite, en français).

Développé en **workflow-as-code** : le workflow est défini en TypeScript avec le [SDK builder n8n](https://github.com/n8n-io/n8n/tree/master/packages/workflow-sdk) et synchronisé avec l'instance via [**n8ncli** CLI](https://github.com/workflows-accelerator/workflows-accelerator).

## Démo

Vidéo de présentation du projet (exécution du workflow + commandes n8ncli + feedback) :

- 🎥 **Vidéo** : [IGHOUBA Axil Fodil - n8n Worfklow DEMO(1).mp4](IGHOUBA%20Axil%20Fodil%20-%20n8n%20Worfklow%20DEMO(1).mp4) — 205 Mo (Git LFS)
- 📝 **Transcript / sous-titres** : [IGHOUBA_Axil_Fodil_-_n8n_Worfklow_DEMO_fra.txt](IGHOUBA_Axil_Fodil_-_n8n_Worfklow_DEMO_fra.txt)
- 📋 **Notes de démo** : [DEMO-steam-key-deal-watch.md](DEMO-steam-key-deal-watch.md)

## Fonctionnement (déroulé)

```
Scheduled Trigger (mar + sam 08:00 UTC)
  → Steam Game Wishlist           lecture de la wishlist publique Steam (steamid)
  → Appid List                    extraction de la liste d'appids
  → Steam Official FR Prices (EUR)  API appdetails (cc=fr) → prix officiels FR
  → GG Deals Steam Keys (USD)     API gg.deals → prix keyshops USD (credential GG.deals)
  → EUR to USD Fix                Frankfurter (ECB) → taux USD→EUR
  → Report Builder                Code node : merge, calcul des écarts, détection region lock
  → Convert To File               export CSV (steam-deals-YYYY-MM-DD.csv)
  → Compose Deals XML             Code node : XML pour l'IA
  → Summarize Deals               Gemini (flash-lite) → résumé FR 5–8 lignes
  → Merge                         CSV (binaire) + contenu du mail
  → Email Alert                   SMTP : mail texte + CSV en pièce jointe
```

## Contenu du repo

| Fichier | Description |
| --- | --- |
| `n8n/workflows/Steam Key Deal Watch.workflow.ts` | Définition du workflow en TypeScript (SDK builder n8n) — **référence unique**, code review friendly |
| `n8n/config/n8n-cli.json` | Configuration de l'environnement (`development`) + projectId |
| `n8n/config/n8n-standards.json` / `n8n-layout.json` | Standards (noms, langue, notes) et réglages de layout |

## Workflow-as-code avec n8ncli

```bash
n8ncli status                 # état de sync local ↔ instance (comme git status)
n8ncli validate --lint        # contrôle schéma, versions de nœuds, standards
n8ncli layout --dry-run       # simulate un réagencement automatique des nœuds
n8ncli pull                   # importe les workflows de l'instance
n8ncli push                   # déploie les modifications locales sur l'instance
```

## Import dans n8n

Depuis l'éditeur, le workflow est **déjà sur l'instance** (poussé avec n8ncli). Pour repartir de zéro :

```bash
n8ncli init                   # initialise le workspace
n8ncli pull                   # rapatrie les workflows
```

Le workflow doit être renseigné dans le workspace avant d'être poussé (mapping nom de fichier ↔ workflow distant).

## Prérequis sur l'instance

- Credential **GG.deals API Key** (`httpTemplatedCustomAuth`) — clé API gg.deals
- Credential **Google Gemini** (`googlePalmApi`) — compte Google avec Gemini
- Credential **SMTP** (`smtp`) — pour l'envoi du rapport
- Le workflow reste **inactif** (`active: false`) tant qu'on ne le publie pas (`n8ncli publish`)

## Licence

MIT
