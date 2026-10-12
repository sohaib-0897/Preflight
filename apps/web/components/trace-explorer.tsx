'use client';
import {useState} from 'react';
import {useQuery} from '@tanstack/react-query';
import {api,type Json} from './api';
import {Badge,Evidence} from './ui';

export function TraceExplorer({runId,attempt,runs}:{runId:string;attempt:Json;runs:Json[]}) {
 const [kind,setKind]=useState('');const [selected,setSelected]=useState<number|null>(null);const [peer,setPeer]=useState('');const [peerAttempt,setPeerAttempt]=useState('');const [difference,setDifference]=useState<Json|null>(null);const [error,setError]=useState('');
 const graph=useQuery<Json>({queryKey:['trace',runId,attempt.id],queryFn:()=>api(`/runs/${runId}/attempts/${attempt.id}/trace`)});
 const candidate=useQuery<Json>({queryKey:['run',peer],queryFn:()=>api(`/runs/${peer}`),enabled:!!peer});
 const events:Json[]=attempt.result.events??[];
 const chosen=events.find(e=>e.sequence===selected);
 const children=chosen?events.filter(e=>e.parent===chosen.sequence&&e.sequence!==chosen.sequence):[];
 async function compare(){try{setError('');const id=peerAttempt||candidate.data?.attempts?.[0]?.id;if(!id)return;setDifference(await api(`/trace-comparisons?baseline_run=${runId}&baseline_attempt=${attempt.id}&candidate_run=${peer}&candidate_attempt=${id}`));}catch(e){setError(String(e));}}
 return <><p className="muted">Accessible recorded events. Agent-reported metadata is distinct from enforcing-broker evidence. Recording spans measure collection; tool durations come from actual execution.</p><div className="actions"><a href={`/api/v1/runs/${runId}/attempts/${attempt.id}/trace.json`}>Export trace JSON</a><label>Event type<select aria-label="Event type" value={kind} onChange={e=>setKind(e.target.value)}><option value="">All events</option>{Array.from(new Set(events.map(e=>e.kind))).map(k=><option key={k}>{k}</option>)}</select></label></div>
 {graph.error&&<p role="alert">Trace graph could not be loaded.</p>}
 <nav aria-label="Execution graph" className="trace-graph">{events.filter(e=>!kind||e.kind===kind).map(e=><button key={e.sequence} aria-pressed={selected===e.sequence} onClick={()=>setSelected(e.sequence)}><span className="mono">#{e.sequence}</span> {e.tool??e.kind}<span className="muted small">{e.sequence===0?'Root':`Parent #${e.parent??0}`} · {e.source??'captured runner event'}</span>{e.status&&<Badge value={e.status}/>}</button>)}</nav>
 {chosen&&<section><h3>Selected event #{chosen.sequence}</h3><div className="actions">{chosen.sequence!==0&&<button onClick={()=>setSelected(chosen.parent??0)}>Go to parent</button>}{children.map(e=><button key={e.sequence} onClick={()=>setSelected(e.sequence)}>Child #{e.sequence}</button>)}</div><Evidence label="Selected trace event" value={chosen}/></section>}
 <details><summary>Trace analysis and failure evidence</summary><Evidence value={{analysis:graph.data,diagnostics:attempt.result.diagnostics,failure:attempt.result.failure}}/></details>
 <ol className="timeline">{events.filter(e=>!kind||e.kind===kind).map(e=><li key={e.sequence}><details><summary><span className="mono">#{e.sequence}</span> {e.tool??e.kind} {e.duration_ms!==undefined&&<span className="muted">{Number(e.duration_ms).toFixed(2)} ms</span>}</summary><Evidence value={e}/></details></li>)}</ol>
 <section><h3>Compare recorded trajectories</h3><label>Candidate run<select aria-label="Candidate run" value={peer} onChange={e=>{setPeer(e.target.value);setPeerAttempt('');setDifference(null);}}><option value="">Choose a completed run</option>{runs.filter(r=>r.id!==runId&&r.status==='COMPLETED').map(r=><option key={r.id} value={r.id}>{r.id.slice(0,8)} · {r.created_at}</option>)}</select></label>{candidate.data&&<label>Candidate attempt<select aria-label="Candidate attempt" value={peerAttempt||candidate.data.attempts?.[0]?.id||''} onChange={e=>setPeerAttempt(e.target.value)}>{candidate.data.attempts?.map((a:Json)=><option key={a.id} value={a.id}>{a.scenario_id} · trial {a.trial+1}</option>)}</select></label>}<button disabled={!candidate.data} onClick={compare}>Compare traces</button>{error&&<p role="alert">{error}</p>}{difference&&<Evidence label="Trace differences" value={difference}/>}</section></>;
}
