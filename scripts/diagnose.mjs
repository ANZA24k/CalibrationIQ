// Compact public transaction diagnostics, with no node configuration export.
import fs from 'node:fs';
import {createClient} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';
const client=createClient({chain:studionet});
const d=JSON.parse(fs.readFileSync('evidence/deployment.json','utf8'));
const r=await client.getTransaction({hash:d.transactions.at(-1).hash});
const compact=(k,v)=>['node_config','raw','calldata','contract_state','contract_state_hash','result','execution_stats'].includes(k)?undefined:v;
console.log('status',r.statusName,'rotations',r.rotation_count,JSON.stringify(r.consensus_history,compact,2));
