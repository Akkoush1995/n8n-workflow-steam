const when_clicking_Execute_workflow = trigger({
  type: 'n8n-nodes-base.manualTrigger',
  version: 1,
  config: { name: 'When clicking \u2018Execute workflow\u2019' }
});

const hTTP_Request = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.5,
  config: { name: 'HTTP Request', parameters: { method: 'POST', url: expr('https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent'), authentication: 'predefinedCredentialType', nodeCredentialType: 'googlePalmApi', sendBody: true, specifyBody: 'json', jsonBody: '{\n  "contents": [\n    {\n      "parts": [\n        {\n          "text": "Voici les actualités de la semaine : {{ JSON.stringify($json.items) }}. Rédige un résumé en français structuré par thèmes avec des puces et inclus les liens originaux."\n        }\n      ]\n    }\n  ]\n}', options: {} }, credentials: { googlePalmApi: newCredential('n8n-server (aighouba@eugeniaschool.com)', '1hUBQJpQWZsBpeH8') }, position: [240, 16] }
});

const if_node = node({
  type: 'n8n-nodes-base.if',
  version: 2.4,
  config: { name: 'If', parameters: { conditions: { options: { caseSensitive: true, leftValue: '', typeValidation: 'strict', version: 4 }, conditions: [{ id: '3e8ce291-37ce-471f-9d73-539925c93734', leftValue: expr('{{ $json.candidates[0].content.parts[0].text }}'), rightValue: expr('actualité'), operator: { type: 'string', operation: 'contains' } }, { id: '3d5867d8-9f77-4b9b-b1a5-25d36b7f1d71', leftValue: '', rightValue: '', operator: { type: 'string', operation: 'equals', name: 'filter.operator.equals' } }], combinator: 'and' }, options: {} }, position: [448, -48] }
});

const edit_Fields = node({
  type: 'n8n-nodes-base.set',
  version: 3.5,
  config: { name: 'Edit Fields', parameters: { assignments: { assignments: [{ id: '4c8c621b-18ab-405b-9503-c8a3f3a586fe', name: 'candidates[0].content.parts[0].text', value: expr('{{ $json.candidates[0].content.parts[0].text }}'), type: 'string' }] }, options: {} }, position: [672, -144] }
});

const switch_node = node({
  type: 'n8n-nodes-base.switch',
  version: 3.5,
  config: { name: 'Switch', parameters: { rules: { values: [{ conditions: { options: { caseSensitive: true, leftValue: '', typeValidation: 'strict', version: 4 }, conditions: [{ leftValue: expr('{{ $(\'HTTP Request\').item.json.candidates[0].content.parts[0].text }}'), rightValue: 'semaine', operator: { type: 'string', operation: 'contains' }, id: '05589478-e451-4e81-9a5c-5019b3f5dc00' }], combinator: 'and' } }, { conditions: { options: { caseSensitive: true, leftValue: '', typeValidation: 'strict', version: 4 }, conditions: [{ id: 'bc1d227b-e1e9-45d3-a589-14432051fe5f', leftValue: expr('{{ $(\'HTTP Request\').item.json.candidates[0].content.parts[0].text }}'), rightValue: 'LLM', operator: { type: 'string', operation: 'contains' } }], combinator: 'and' } }] }, options: {} }, position: [832, -128] }
});

const edit_Fields1 = node({
  type: 'n8n-nodes-base.set',
  version: 3.5,
  config: { name: 'Edit Fields1', parameters: { assignments: { assignments: [{ id: '2a5142fc-dcde-46f5-875d-c0c21dfe9810', name: 'candidates[0].content.parts[0].text', value: expr('Priorite Normale'), type: 'string' }] }, options: {} }, position: [672, 32] }
});

const message_a_model = node({
  type: '@n8n/n8n-nodes-langchain.googleGemini',
  version: 1.2,
  config: { name: 'Message a model', parameters: { modelId: { __rl: true, value: 'models/gemini-flash-lite-latest', mode: 'list', cachedResultName: 'Gemini Flash-Lite Latest' }, messages: { values: [{}] }, builtInTools: {}, options: {} }, credentials: { googlePalmApi: newCredential('n8n-server (aighouba@eugeniaschool.com)', '1hUBQJpQWZsBpeH8') }, position: [320, -288] }
});

const wf = workflow('8PIUlMslSnxZq2PH', 'My workflow 3', { executionOrder: 'v1', binaryMode: 'separate', availableInMCP: true });

export default wf
  .add(when_clicking_Execute_workflow)
  .to(hTTP_Request)
  .to(if_node.onTrue(edit_Fields
    .to(switch_node)).onFalse(edit_Fields1))
  .add(message_a_model)