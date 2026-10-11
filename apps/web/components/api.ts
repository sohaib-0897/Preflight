export type Json = Record<string, any>;
let csrf = '';
export function setCsrf(value: string) { csrf = value; }
export async function api<T = Json>(path: string, body?: unknown): Promise<T> {
 const response = await fetch(`/api/v1${path}`, {method: body === undefined ? 'GET' : 'POST', credentials:'same-origin', headers:{'Content-Type':'application/json','X-CSRF-Token':csrf}, body:body === undefined ? undefined : JSON.stringify(body)});
 const data = await response.json();
 if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Request rejected. Check the fields and your permissions.');
 return data;
}
export function percent(value: unknown) { return typeof value === 'number' ? `${(value*100).toFixed(1)}%` : 'Unavailable'; }
export function duration(value: unknown) { return typeof value === 'number' ? `${value.toFixed(2)} ms` : 'Unavailable'; }
