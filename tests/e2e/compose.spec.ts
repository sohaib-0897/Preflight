import {test,expect} from '@playwright/test';
import fs from 'node:fs';

test('complete Compose stack persists automatic worker evaluation through Next',async({page})=>{
 await page.goto('/');await page.getByRole('button',{name:'Create a new account'}).click();
 await page.getByLabel('Email',{exact:true}).fill(`compose-${test.info().project.name}-${Date.now()}@example.test`);await page.getByLabel('Password',{exact:true}).fill('browser-synthetic-passphrase');await page.getByRole('button',{name:'Create account',exact:true}).click();
 await page.getByRole('button',{name:'Create project',exact:true}).click();await page.getByLabel('Project name').fill('Compose persisted project');await page.getByRole('dialog').getByRole('button',{name:'Create project',exact:true}).click();
 await page.getByRole('link',{name:'Agents',exact:true}).click();await page.getByRole('button',{name:'Connect agent',exact:true}).first().click();await page.getByLabel('Agent name').fill('Automatic queue agent');await page.getByRole('dialog').getByRole('button',{name:'Connect agent',exact:true}).click();
 await page.getByRole('link',{name:'Evaluations',exact:true}).click();await page.getByRole('button',{name:'New evaluation',exact:true}).click();await page.getByRole('dialog').getByRole('button',{name:'Queue evaluation'}).click();
 // The real Redis-backed Compose worker executes; the browser never calls /execute.
 await expect(page.getByText('COMPLETED',{exact:true}).first()).toBeVisible({timeout:30000});
 await page.getByRole('button',{name:'Evaluate release policy'}).click();await expect(page.getByText('PASS',{exact:true})).toBeVisible();
 await page.reload();await expect(page.getByText('COMPLETED',{exact:true}).first()).toBeVisible();
 await page.getByRole('button',{name:'RealityCheck',exact:true}).click();await expect(page.getByLabel('RealityCheck assessment')).toContainText('task_success');
 const download=page.waitForEvent('download');await page.getByRole('link',{name:'Export JSON',exact:true}).click();expect((await download).suggestedFilename()).toMatch(/preflight-/);
 await page.evaluate(fs.readFileSync('node_modules/axe-core/axe.min.js','utf8'));const violations=await page.evaluate(async()=>(await (window as any).axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})).violations);expect(violations).toEqual([]);
 await page.screenshot({path:`test-results/compose-${test.info().project.name}.png`,fullPage:true});
});
