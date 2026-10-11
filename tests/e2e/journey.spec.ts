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
