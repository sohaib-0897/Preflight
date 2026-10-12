import { test, expect } from '@playwright/test';
import fs from 'node:fs';

test('first user runs native evaluation, inspects state and exports evidence',async({page})=>{
 await page.goto('/');
 await page.getByRole('button',{name:'Create a new account'}).click();
 await page.getByLabel('Email',{exact:true}).fill(`browser-${Date.now()}@example.test`);
 await page.getByLabel('Password',{exact:true}).fill('browser-synthetic-passphrase');
 await page.getByRole('button',{name:'Create account',exact:true}).click();
 await page.getByRole('button',{name:'Create project',exact:true}).click();
 await page.getByLabel('Project name').fill('Browser test project');
 await page.getByRole('dialog').getByRole('button',{name:'Create project',exact:true}).click();
 await page.getByRole('link',{name:'Agents',exact:true}).click();
 await page.getByRole('button',{name:'Connect agent',exact:true}).first().click();
 await page.getByLabel('Agent name').fill('Accurate native agent');
 await page.getByRole('dialog').getByRole('button',{name:'Connect agent',exact:true}).click();
 await page.getByRole('link',{name:'Evaluations',exact:true}).click();
 await page.getByRole('button',{name:'New evaluation',exact:true}).first().click();
 await page.getByRole('dialog').getByRole('button',{name:'Queue evaluation'}).click();
 await page.getByRole('button',{name:'Execute native demo'}).click();
 await expect(page.getByText('COMPLETED',{exact:true}).first()).toBeVisible();
 await page.getByRole('button',{name:'RealityCheck',exact:true}).click();
 await expect(page.getByText('Deterministic evidence.',{exact:false})).toBeVisible();
 await page.getByRole('button',{name:'Evaluate release policy'}).click();
 await expect(page.getByText('PASS',{exact:true})).toBeVisible();
 const download=page.waitForEvent('download');
 await page.getByRole('link',{name:'Export JSON'}).click();
 expect((await download).suggestedFilename()).toMatch(/preflight-.*\.json/);
 // Inject through the test runner's execution context; keep the application's CSP intact.
 await page.evaluate(fs.readFileSync('node_modules/axe-core/axe.min.js','utf8'));
 const violations=await page.evaluate(async()=>{return (await (window as any).axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})).violations;});
 expect(violations).toEqual([]);
 await page.keyboard.press('Tab');
 await expect(page.locator(':focus')).toBeVisible();
 await page.screenshot({path:`test-results/journey-${test.info().project.name}.png`,fullPage:true});
 const baseline=page.url().split('/').pop()!;
 const session=await (await page.request.get('/api/v1/auth/me')).json();
 const original=await (await page.request.get(`/api/v1/runs/${baseline}`)).json();
 const projectId=original.project_id;
 const headers={'x-csrf-token':session.csrf_token};
 const second=await page.request.post(`/api/v1/projects/${projectId}/runs`,{headers,data:{version_id:original.version_id,idempotency_key:`trace-browser-${Date.now()}`,scenarios:['refund']}});
 expect(second.status()).toBe(201);
 const candidate=(await second.json()).id;
 expect((await page.request.post(`/api/v1/runs/${candidate}/execute`,{headers,data:{}})).status()).toBe(200);
 await page.reload();
 await page.getByRole('button',{name:'Trace',exact:true}).click();
 const nodes=page.getByRole('navigation',{name:'Execution graph'}).getByRole('button');
 await nodes.nth(1).focus();await page.keyboard.press('Enter');
 await expect(page.getByLabel('Selected trace event')).toContainText('trace_id');
 await page.getByRole('button',{name:'Go to parent'}).click();
 await expect(page.getByRole('heading',{name:'Selected event #0'})).toBeVisible();
 await page.getByLabel('Candidate run',{exact:true}).selectOption(candidate);
 await page.getByRole('button',{name:'Compare traces',exact:true}).click();
 await expect(page.getByLabel('Trace differences')).toContainText('equal_ignoring_timings');
 const traceDownload=page.waitForEvent('download');await page.getByRole('link',{name:'Export trace JSON'}).click();
 expect((await traceDownload).suggestedFilename()).toMatch(/preflight-trace-/);
 await page.evaluate(fs.readFileSync('node_modules/axe-core/axe.min.js','utf8'));
 const traceViolations=await page.evaluate(async()=>(await (window as any).axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})).violations);
 expect(traceViolations).toEqual([]);
 await page.screenshot({path:`test-results/trace-${test.info().project.name}.png`,fullPage:true});
 const agent=(await (await page.request.get(`/api/v1/projects/${projectId}/agents`)).json())[0];
 const version=await (await page.request.post(`/api/v1/agents/${agent.id}/versions`,{headers,data:{version:'regression-2',config:{mode:'regressed'}}})).json();
 const regression=await (await page.request.post(`/api/v1/projects/${projectId}/runs`,{headers,data:{version_id:version.id,idempotency_key:`regression-browser-${Date.now()}`}})).json();
 expect((await page.request.post(`/api/v1/runs/${regression.id}/execute`,{headers,data:{}})).status()).toBe(200);
 await page.getByRole('link',{name:'Comparisons',exact:true}).click();
 await page.getByLabel('Baseline',{exact:true}).selectOption(baseline);
 await page.getByLabel('Candidate',{exact:true}).selectOption(candidate);
 await page.getByRole('button',{name:'Compare runs',exact:true}).click();
 await expect(page.getByText('Incompatible:',{exact:false})).toBeVisible();
 await page.reload();
 await page.getByLabel('Baseline',{exact:true}).selectOption(baseline);
 await page.getByLabel('Candidate',{exact:true}).selectOption(regression.id);
 await page.getByRole('button',{name:'Compare runs',exact:true}).click();
 await expect(page.getByRole('table',{name:'Comparable evidence dimensions'})).toContainText('recovery success');
 await page.evaluate(fs.readFileSync('node_modules/axe-core/axe.min.js','utf8'));
 const comparisonViolations=await page.evaluate(async()=>(await (window as any).axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})).violations);
 expect(comparisonViolations).toEqual([]);
 if(test.info().project.name==='mobile'){
  const region=page.getByRole('region',{name:'Comparable evidence dimensions scroll area'});
  await region.focus();await page.keyboard.press('ArrowRight');
  await expect.poll(()=>region.evaluate(element=>element.scrollLeft)).toBeGreaterThan(0);
 }
 await page.screenshot({path:`test-results/comparison-${test.info().project.name}.png`,fullPage:true});
 await page.goto(`/evaluations/${regression.id}`);
 await page.getByRole('button',{name:'Evaluate release policy'}).click();
 await expect(page.getByText('FAIL',{exact:true})).toBeVisible();


});

test('keyboard account switch and dialog focus',async({page})=>{
 await page.goto('/');
 await page.keyboard.press('Tab');
 await expect(page.getByRole('link',{name:'Skip to content'})).toBeFocused();
 await page.keyboard.press('Enter');
 await page.getByRole('button',{name:'Create a new account'}).focus();
 await page.keyboard.press('Enter');
 await expect(page.getByRole('heading',{name:'Create your account'})).toBeVisible();
});
