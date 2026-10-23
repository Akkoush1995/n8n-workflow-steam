# n8n-workflow-steam — Steam Key Deal Watch

Watch de prix de clés Steam : tous les mardis et samedis à 08:00 UTC, le workflow compare **le prix du store Steam (FR)** avec **le prix des revendeurs de clés (keyshops USD, convertis en EUR)** pour chaque jeu d'une wishlist Steam, génère un CSV et envoie un email avec le tableau complet + un résumé rédigé par l'IA (Gemini, en français).

## Fonctionnement (déroulé)

```
Schedule Trigger (mar + sam 08:00 UTC)
  → Steam Wishlist          lecture de la wishlist publique (steamid)
  → Appid List              extraction de la liste d'appids
  → Steam FR Prices         API appdetails (cc=fr) → prix officiels FR
  → GG Deals USD           API gg.deals → prix keyshops USD (credential GG.deals)
  → FX Rate EUR            Frankfurter (ECB) → taux USD→EUR
  → Build Report           Code node : merge, calcul des écarts, détection region lock
  → Convert To File        export CSV (steam-deals-YYYY-MM-DD.csv)
  → Compose Deals XML      Code node : XML pour l'IA
  → Summarize Deals        Gemini (flash-lite) → résumé FR 5–8 lignes
  → Merge                  CSV (bin) + contenu du mail
  → Send Deals Email       SMTP : mail texte + CSV en pièce jointe
```

## Contenu du repo

| Fichier | Description |
| --- | --- |
| `n8n/workflows/Steam Key Deal Watch.workflow.ts` | Définition du workflow en TypeScript avec le [SDK builder n8n](https://github.com/n8n-io/n8n/tree/master/packages/workflow-sdk) |

## Import dans n8n

Faire un build avec le SDK builder :

```bash
npm install @n8n/workflow-sdk
npx tsx build.ts   # génère Steam Key Deal Watch.workflow.json (n8n standard)
```

Ensuite importer le JSON via **Import from File** dans l'éditeur n8n, ou pousser vers une instance avec [n8ncli](https://github.com/workflows-accelerator/workflows-accelerator) :

```bash
n8ncli pull                       # init workspace
n8ncli push "Steam Key Deal Watch"
```

## Prérequis sur l'instance

- Credential **GG.deals API Key** (`httpTemplatedCustomAuth`) — clé API gg.deals
- Credential **Google Gemini** (`googlePalmApi`) — compte Google avec Gemini
- Credential **SMTP** (`smtp`) — pour l'envoi du rapport
- Optionnel : variable d'env `GG_DEALS_KEY` si vous repassez l'URL en key param

## Licence

MIT
