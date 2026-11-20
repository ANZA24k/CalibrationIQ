// Read-only export; uses no wallet key. Run from the repository root.
import fs from 'node:fs';
import crypto from 'node:crypto';
import {createClient} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';
import {TransactionHashVariant} from 'genlayer-js/types';
const deployment=JSON.parse(fs.readFileSync('evidence/deployment.json','utf8'));
const client=createClient({chain:studionet});
const save=(name,data)=>fs.writeFileSync(`evidence/${name}.json`,JSON.stringify(data,(_,v)=>typeof v==='bigint'?v.toString():v,2)+'\n');
const read=async(name,args=[])=>JSON.parse(await client.readContract({address:deployment.address,functionName:name,args,transactionHashVariant:TransactionHashVariant.LATEST_FINAL}));
const source=await client.getContractCode(deployment.address);
const deployed=source.startsWith('0x')?Buffer.from(source.slice(2),'hex'):Buffer.from(source);
const local=fs.readFileSync('contracts/calibration_iq.py');
if(!deployed.equals(local)) throw Error('Deployed source differs');
const transactions=[];
for(const tx of deployment.transactions){
 const r=await client.getTransaction({hash:tx.hash});
 const leaders=r.consensus_data?.leader_receipt||[];
 const status=r.statusName||r.status_name;
 if(status!=='FINALIZED'||r.result_name!=='MAJORITY_AGREE'||r.leader_only!==false||!leaders.some(x=>x.execution_result==='SUCCESS'))throw Error(`${tx.action} not finalized successfully: ${status}`);
 transactions.push({action:tx.action,hash:tx.hash,status,consensus_result:r.result_name,leader_only:r.leader_only,executions:leaders.map(x=>x.execution_result),votes:r.consensus_data?.votes});
}
const state=await read('get_status'); save('state',state);
save('policy',await read('get_policy'));
for(let n=1;n<=state.submissions;n++){
 save(`submission-${n}`,await read('get_submission',[n]));
 if(n===state.submissions&&state.pending) continue;
 const receipt=await read('get_receipt',[n]);
 const {receipt_hash,...body}=receipt;
 const canonical=value=>{if(Array.isArray(value))return value.map(canonical);if(value&&typeof value==='object')return Object.fromEntries(Object.keys(value).sort().map(k=>[k,canonical(value[k])]));return value;};
 // Contract JSON uses ensure_ascii=True. Fixtures and current receipts use ASCII.
 const serialized=JSON.stringify(canonical(body)).replace(/[\u007f-\uffff]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'));
 if(crypto.createHash('sha256').update(serialized).digest('hex')!==receipt_hash)throw Error('Receipt hash mismatch');
 save(`receipt-${n}`,receipt);
}
if(deployment.transactions.some(x=>x.action==='evaluate')&&state.pending)throw Error('Evaluation produced no finalized receipt');
save('verified',{...deployment,source_sha256:crypto.createHash('sha256').update(local).digest('hex'),source_matches:true,transactions,state});
console.log(JSON.stringify({source_matches:true,transactions,state},null,2));
