import fs from 'node:fs';
import {createClient} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';
const client=createClient({chain:studionet});
const {transactions}=JSON.parse(fs.readFileSync('evidence/deployment.json','utf8'));
const r=await client.getTransaction({hash:transactions.at(-1).hash});
console.log(JSON.stringify({status:r.statusName||r.status_name,result:r.result_name,executions:r.consensus_data?.leader_receipt?.map(x=>({execution:x.execution_result,error:x.genvm_result?.error_code})),votes:r.consensus_data?.votes},null,2));
