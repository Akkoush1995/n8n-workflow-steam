const schedule = trigger({
  type: 'n8n-nodes-base.scheduleTrigger',
  version: 1.4,
  config: { name: 'Schedule', parameters: { rule: { interval: [{}] } }, notes: 'Runs Tuesdays and Saturdays at 08:00 UTC (10:00 France in summer).', notesInFlow: true }
});

const steam_Wishlist = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.5,
  config: { name: 'Steam Wishlist', parameters: { url: 'https://api.steampowered.com/IWishlistService/GetWishlist/v1/?steamid=76561199667498679', options: {} }, position: [224, 0], notes: 'Reads the public Steam wishlist (appids).', notesInFlow: true }
});

const appid_List = node({
  type: 'n8n-nodes-base.set',
  version: 3.5,
  config: { name: 'Appid List', parameters: { assignments: { assignments: [{ id: '9c2a9f71-aaaa-bbbb-cccc-111122223333', name: 'ids', value: expr('{{ ($json.response?.items ?? []).map(i => i.appid).slice(0, 100).join(",") }}'), type: 'string' }, { id: '9c2a9f71-aaaa-bbbb-cccc-444455556666', name: 'profileSlug', value: '', type: 'string' }] }, options: {} }, position: [432, 0] }
});

const steam_FR_Prices = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.5,
  config: { name: 'Steam FR Prices', parameters: { url: expr('https://store.steampowered.com/api/appdetails?appids={{ $json.ids }}&cc=fr&filters=price_overview'), options: {} }, position: [80, 256], notes: 'Real store-front prices in France via appdetails (final price is in cents).', notesInFlow: true }
});

const gG_Deals_USD = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.5,
  config: { name: 'GG Deals USD', parameters: { url: expr('https://api.gg.deals/v1/prices/by-steam-app-id/?ids={{ $("Appid List").item.json.ids }}'), authentication: 'genericCredentialType', genericAuthType: 'httpTemplatedCustomAuth', options: {} }, credentials: { httpTemplatedCustomAuth: newCredential('GG.deals API Key (Axil I)', 'C3N1dHKpfApuQsXJ') }, position: [288, 256], notes: 'Key reseller prices in USD. Uses the GG.deals API Key credential.', notesInFlow: true }
});

const fX_Rate_EUR = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.5,
  config: { name: 'FX Rate EUR', parameters: { url: 'https://api.frankfurter.app/latest?from=USD&to=EUR', options: {} }, position: [480, 256], notes: 'USD to EUR daily rate from ECB, free and keyless.', notesInFlow: true }
});

const build_Report = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: { name: 'Build Report', parameters: { jsCode: '\n      const details = $(\'Steam FR Prices\').all()[0]?.json ?? {};\n      const dealsRaw = $(\'GG Deals USD\').all()[0]?.json?.data ?? {};\n      const rateObj = $(\'FX Rate EUR\').all()[0]?.json ?? {};\n      const rate = rateObj.rates?.EUR ?? 1;\n      const rows = [];\n      for (const [appid, g] of Object.entries(dealsRaw)) {\n        const s = details[appid]?.data;\n        const steamCents = s?.price_overview?.final;\n        if (g.prices == null || steamCents == null) {\n          rows.push({\n            json: {\n              appid,\n              title: s?.name ?? g.title ?? \'(unknown)\',\n              steamEUR: null,\n              keyEUR: null,\n              gapEUR: null,\n              gapPct: null,\n              deal: \'n/a\',\n              suspect: \'yes\',\n              offerUrl: g.url ?? \'\',\n              note: \'region lock or missing data - manual check\'\n            }\n          });\n          continue;\n        }\n        const steamEUR = Math.round((steamCents / 100) * 100) / 100;\n        const keyEUR = Math.round(g.prices.currentKeyshops * rate * 100) / 100;\n        const gapEUR = Math.round((steamEUR - keyEUR) * 100) / 100;\n        const gapPct = steamEUR > 0 ? Math.round((gapEUR / steamEUR) * 1000) / 10 : 0;\n        rows.push({\n          json: {\n            appid,\n            title: s?.name ?? g.title,\n            steamEUR,\n            keyEUR,\n            gapEUR,\n            gapPct,\n            deal: keyEUR < steamEUR ? \'yes\' : \'no\',\n            suspect: gapPct > 60 ? \'check region\' : \'no\',\n            offerUrl: g.url,\n            note: \'\'\n          }\n        });\n      }\n      return rows.length ? rows : [{ json: { title: \'(no deals data)\', note: \'all games null or missing\' } }];\n      ' }, position: [688, 496], notes: 'Merges Steam FR prices, GG.deals USD prices and EUR rate; marks region-locked games as manual checks.', notesInFlow: true }
});

const convert_To_File = node({
  type: 'n8n-nodes-base.convertToFile',
  version: 1.1,
  config: { name: 'Convert To File', parameters: { options: { delimiter: ',', fileName: expr('steam-deals-{{ $today }}.csv'), headerRow: true } }, position: [960, 496] }
});

const merge_node = merge({
  version: 3.2,
  config: { name: 'Merge', parameters: { mode: 'combine', combineBy: 'combineByPosition', options: {} }, position: [1248, 896] }
});

const summarize_Deals = node({
  type: '@n8n/n8n-nodes-langchain.googleGemini',
  version: 1.2,
  config: { name: 'Summarize Deals', parameters: { modelId: { __rl: true, mode: 'list', value: 'models/gemini-flash-lite-latest', cachedResultName: 'Gemini Flash-Lite Latest' }, messages: { values: [{ content: expr('Voici la liste des jeux Steam avec leurs prix (Steam FR vs revendeur de clés, en EUR) au format XML :\n{{ $json.xml }}\n\nRédige en français un court résumé (5 à 8 lignes) : les meilleures affaires (plus gros écarts), les jeux indisponibles ou à vérifier manuellement, et une recommandation. Texte brut, sans markdown.') }] }, builtInTools: {}, options: { includeMergedResponse: true, maxOutputTokens: 1024 } }, credentials: { googlePalmApi: newCredential('n8n-server (aighouba@eugeniaschool.com)', '1hUBQJpQWZsBpeH8') }, position: [880, 912] }
});

const compose_Deals_XML = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: { name: 'Compose Deals XML', parameters: { jsCode: 'const rows = $input.all().map(i => i.json);\nconst jeux = rows\n  .filter(r => r.title)\n  .map(r =>\n    r.deal === \'n/a\'\n      ? \'<jeu><nom>\' + r.title + \'</nom><statut>indisponible</statut></jeu>\'\n      : \'<jeu><nom>\' + r.title + \'</nom><steam>\' + r.steamEUR + \'</steam><cle>\' + r.keyEUR + \'</cle><ecart>\' + r.gapEUR + \'</ecart><ecartPct>\' + r.gapPct + \'</ecartPct><lien>\' + (r.offerUrl || \'none\') + \'</lien></jeu>\'\n  )\n  .join(\'\\n  \');\nreturn [{ json: { xml: \'<jeux>\\n  \' + jeux + \'\\n</jeux>\' } }];' }, position: [608, 912] }
});

const send_Deals_Email = node({
  type: 'n8n-nodes-base.emailSend',
  version: 2.1,
  config: { name: 'Send Deals Email', parameters: { fromEmail: 'justakkoush@gmail.com', toEmail: 'ighoubaaxilfodil@gmail.com', subject: expr('Steam key deal watch - {{ $today }}'), emailFormat: 'text', text: expr('{{ $json.output ?? $json.content?.parts?.[0]?.text }}\n\nLe tableau complet des jeux est dans le CSV joint.'), options: { appendAttribution: false, attachments: 'data' } }, credentials: { smtp: newCredential('SMTP account', '18Cy2CCV9KxoSd85') }, position: [1520, 896], webhookId: '0c2afd19-4ea6-449e-9456-45321fed4adf' }
});

const wf = workflow('YY9im7k4FoS6YrcI', 'Steam Key Deal Watch', { description: 'Twice-weekly CSV email comparing French store prices and key reseller prices for a Steam wishlist.', active: false, executionOrder: 'v1', availableInMCP: true, binaryMode: 'separate' });

export default wf
  .add(schedule)
  .to(steam_Wishlist)
  .to(appid_List)
  .to(steam_FR_Prices)
  .to(gG_Deals_USD)
  .to(fX_Rate_EUR)
  .to(build_Report
  .to([
    convert_To_File,
    compose_Deals_XML
    .to(summarize_Deals)]))
  .add(convert_To_File.to(merge_node.input(0)))
  .add(summarize_Deals.to(merge_node.input(1)))
  .add(merge_node)
  .to(send_Deals_Email)