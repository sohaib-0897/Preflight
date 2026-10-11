import {test,expect} from '@playwright/test';
test('all Next modules render genuine empty states and logout ends session',async({page})=>{
 await page.goto('/');await page.getByRole('button',{name:'Create a new account'}).click();
 await page.getByLabel('Email',{exact:true}).fill(`navigation-${Date.now()}@example.test`);await page.getByLabel('Password',{exact:true}).fill('browser-synthetic-passphrase');await page.getByRole('button',{name:'Create account',exact:true}).click();
 for(const module of ['Organizations','Projects','Agents','Agent versions','Evaluations','Benchmarks','RealityCheck','Security','Traces','Comparisons','Release gates','Reports','Settings']) {
  await page.getByRole('navigation',{name:'Main navigation'}).getByRole('link',{name:module,exact:true}).click();
  await expect(page.getByRole('heading',{name:module,exact:true,level:1})).toBeVisible();
 }
 if(test.info().project.name==='desktop'){await page.getByRole('button',{name:'Sign out'}).click();await expect(page.getByRole('heading',{name:'Sign in to Preflight'})).toBeVisible();}
});
