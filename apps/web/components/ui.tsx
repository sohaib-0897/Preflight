'use client';
import * as Dialog from '@radix-ui/react-dialog';
import { useState, useRef, type ReactNode } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
export function Badge({value}:{value:unknown}) { const text=String(value ?? 'NOT_RUN'); return <span className={`badge ${['PASS','PASSED','COMPLETED','AVAILABLE','SUPPORTED'].includes(text)?'good':['FAIL','FAILED','CONTRADICTED'].includes(text)?'bad':'neutral'}`}>{text.replace(/_/g,' ')}</span>; }
export function Evidence({value,label='Execution evidence'}:{value:unknown;label?:string}) {return <pre tabIndex={0} aria-label={label}>{JSON.stringify(value,null,2)}</pre>;}
export function Empty({title,children}:{title:string;children:ReactNode}) {return <section className="empty"><h2>{title}</h2>{children}</section>;}
export type Field={name:string;label:string;type?:string;value?:string;optional?:boolean;options?:{value:string;label:string}[];help?:string};
export type FormSpec={title:string;fields:Field[];submit:(data:Record<string,string>)=>Promise<void>};
export function Form({spec,onDone}:{spec:FormSpec;onDone:()=>void}) {
 const [error,setError]=useState('');
 const schema=z.record(z.string(),z.string()).superRefine((values,ctx)=>{
  for(const f of spec.fields) {
   const value=values[f.name]??'';
   if(!f.optional&&!value.trim())ctx.addIssue({code:'custom',path:[f.name],message:'This field is required.'});
   if(f.type==='email'&&!z.email().safeParse(value).success)ctx.addIssue({code:'custom',path:[f.name],message:'Enter a valid email.'});
   if(f.type==='password'&&value.length<12)ctx.addIssue({code:'custom',path:[f.name],message:'Use at least 12 characters.'});
  }
 });
 const {register,handleSubmit,formState:{errors,isSubmitting}}=useForm<Record<string,string>>({resolver:zodResolver(schema),defaultValues:Object.fromEntries(spec.fields.map(f=>[f.name,f.value??f.options?.[0]?.value??'']))});
 return <form onSubmit={handleSubmit(async data=>{try{setError('');await spec.submit(data);onDone();}catch(err){setError(err instanceof Error?err.message:'Operation failed');}})}>
  {error&&<p role="alert" className="error">{error}</p>}
  {spec.fields.map(f=><div className="field" key={f.name}><label htmlFor={`field-${f.name}`}>{f.label}</label>{f.options?<select id={`field-${f.name}`} {...register(f.name)}>{f.options.map(o=><option key={o.value} value={o.value}>{o.label}</option>)}</select>:f.type==='textarea'?<textarea id={`field-${f.name}`} {...register(f.name)}/>:<input id={`field-${f.name}`} type={f.type??'text'} autoComplete={f.type==='password'?'new-password':f.type==='email'?'email':'off'} {...register(f.name)} aria-invalid={Boolean(errors[f.name])} aria-describedby={errors[f.name]?`error-${f.name}`:undefined}/>}{f.help&&<p className="muted small">{f.help}</p>}{errors[f.name]&&<p id={`error-${f.name}`} className="error" role="alert">{String(errors[f.name]?.message)}</p>}</div>)}
  <button className="primary" disabled={isSubmitting}>{isSubmitting?'Saving…':spec.title}</button>
 </form>;
}
export function Modal({spec,close}:{spec:FormSpec|null;close:()=>void}) {const opener=useRef<HTMLElement|null>(null);return <Dialog.Root open={Boolean(spec)} onOpenChange={open=>{if(!open)close();}}><Dialog.Portal><Dialog.Overlay className="overlay"/><Dialog.Content className="dialog" aria-describedby={undefined} onOpenAutoFocus={()=>{opener.current=document.activeElement instanceof HTMLElement?document.activeElement:null;}} onCloseAutoFocus={event=>{event.preventDefault();const target=opener.current;if(target?.isConnected&&!target.hasAttribute('disabled'))target.focus({preventScroll:true});else {const main=document.getElementById('main');if(main){main.tabIndex=-1;main.focus({preventScroll:true});}}}}><Dialog.Title>{spec?.title}</Dialog.Title><Dialog.Close className="dialog-close" aria-label="Close dialog">×</Dialog.Close>{spec&&<Form key={spec.title} spec={spec} onDone={close}/>}</Dialog.Content></Dialog.Portal></Dialog.Root>;}
export function Table({caption,columns,rows}:{caption:string;columns:string[];rows:ReactNode[][]}) {return <div className="table-wrap"><table><caption>{caption}</caption><thead><tr>{columns.map(c=><th scope="col" key={c}>{c}</th>)}</tr></thead><tbody>{rows.map((row,i)=><tr key={i}>{row.map((cell,j)=><td key={j}>{cell}</td>)}</tr>)}</tbody></table>{!rows.length&&<p className="muted empty-row">No matching records.</p>}</div>;}
