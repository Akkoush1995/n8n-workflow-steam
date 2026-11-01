const aI_Agent = node({
  type: '@n8n/n8n-nodes-langchain.agent',
  version: 3.1,
  config: { name: 'AI Agent', parameters: { promptType: 'define', text: 'Salut, comment ca va ?', options: {} }, position: [496, 208], alwaysOutputData: true }
});

const schedule_Trigger = trigger({
  type: 'n8n-nodes-base.scheduleTrigger',
  version: 1.4,
  config: { name: 'Schedule Trigger', parameters: { rule: { interval: [{ field: 'weeks', triggerAtHour: 10 }] } }, position: [-32, 0] }
});

const rSS_Read = node({
  type: 'n8n-nodes-base.rssFeedRead',
  version: 1.2,
  config: { name: 'RSS Read', parameters: { url: 'https://www.google.fr/alerts/feeds/03213550684941102828/8386630499444897728', options: {} }, position: [352, -80] }
});

const message_a_model = node({
  type: '@n8n/n8n-nodes-langchain.googleGemini',
  version: 1.2,
  config: { name: 'Message a model', parameters: { modelId: { __rl: true, mode: 'list', value: 'models/gemini-3-flash-preview' }, messages: { values: [{ content: expr('"Voici les articles de la semaine : {{ $json.link }} {{ $json.content }} {{ $json.contentSnippet }}. Rédige un résumé structuré en français classé par thèmes (Nouveaux Modèles, Outils, Entreprises). Pour chaque point, mets un résumé de 2 phrases et inclus le lien source."') }] }, jsonOutput: true, builtInTools: {}, options: {} }, credentials: { googlePalmApi: newCredential('n8n-server (aighouba@eugeniaschool.com)', '1hUBQJpQWZsBpeH8') }, position: [576, -80] }
});

const hTTP_Request = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.5,
  config: { name: 'HTTP Request', parameters: { options: {} }, position: [208, 640] }
});

const basic_LLM_Chain = node({
  type: '@n8n/n8n-nodes-langchain.chainLlm',
  version: 1.9,
  config: { name: 'Basic LLM Chain', parameters: { batching: {} }, position: [144, 352] }
});

const wf = workflow('Cn7UE1vhkMwM4Bl7', 'My workflow', { executionOrder: 'v1', binaryMode: 'separate', availableInMCP: true });

export default wf
  .add(aI_Agent)
  .add(schedule_Trigger)
  .to(rSS_Read)
  .to(message_a_model)
  .add(hTTP_Request)
  .to(basic_LLM_Chain)