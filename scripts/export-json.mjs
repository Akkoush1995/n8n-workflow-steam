import { createRequire } from 'node:module';
import { writeFileSync } from 'node:fs';

const sessionDir = 'C:/Users/ighou/.config/openchamber/chats/2026-10-21/session-9eb7a812-28d3-4420-b5d2-f45bda7673ca';
const require = createRequire(sessionDir + '/node_modules/package.json');
const sdk = require('@n8n/workflow-sdk');

for (const k of ['workflow','node','trigger','expr','newCredential','merge','switchCase','ifElse','splitInBatches','dataTransformation','sort','loopOver','map','filter','code','function','itemLists']) {
  if (sdk[k]) globalThis[k] = sdk[k];
}

const tsPath = sessionDir + '/n8n/workflows/Steam Key Deal Watch.workflow.ts';
const { default: wf } = await import('file:///' + tsPath.replace(/\\/g, '/'));

const json = wf.toJSON();
writeFileSync(
  'C:/Users/ighou/Code/n8n/n8n/workflows/Steam Key Deal Watch.json',
  JSON.stringify(json, null, 2),
  'utf8'
);
console.log('Exported workflow JSON:', json.id, '-', json.name, '-', (json.nodes||[]).length, 'nodes');
