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

test('RealityCheck ingests references and validates a custom persisted scenario',async({page})=>{
 const email=`reality-browser-${Date.now()}@example.test`;
 await page.goto('/');
 await page.getByRole('button',{name:'Create a new account'}).click();
 await page.getByLabel('Email',{exact:true}).fill(email);
 await page.getByLabel('Password',{exact:true}).fill('browser-synthetic-passphrase');
 await page.getByRole('button',{name:'Create account',exact:true}).click();
 await page.getByRole('button',{name:'Create project',exact:true}).click();
 await page.getByLabel('Project name').fill('RealityCheck browser project');
 await page.getByRole('dialog').getByRole('button',{name:'Create project',exact:true}).click();
 await page.getByRole('link',{name:'RealityCheck',exact:true}).click();
 await page.getByRole('button',{name:'Import reference',exact:true}).first().click();
 await page.getByLabel('Document name').fill('Trusted fixture policy');
 await page.getByRole('dialog').getByRole('button',{name:'Import reference',exact:true}).click();
 await expect(page.getByRole('cell',{name:'Trusted fixture policy',exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Verify claims',exact:true}).click();
 await page.getByRole('dialog').getByRole('button',{name:'Verify claims',exact:true}).click();
 await expect(page.getByLabel('Execution evidence').last()).toContainText('SUPPORTED');
 await page.getByRole('link',{name:'Agents',exact:true}).click();
 await page.getByRole('button',{name:'Connect agent',exact:true}).first().click();
 await page.getByLabel('Agent name').fill('Fixture refund agent');
 await page.getByRole('dialog').getByRole('button',{name:'Connect agent',exact:true}).click();
 await page.getByRole('link',{name:'Benchmarks',exact:true}).click();
 await page.getByRole('button',{name:'Create custom dataset',exact:true}).click();
 await page.getByLabel('Dataset name').fill('Custom refund checks');
 await page.getByRole('dialog').getByRole('button',{name:'Create custom dataset',exact:true}).click();
 await page.getByRole('link',{name:'Evaluations',exact:true}).click();
 await page.getByRole('button',{name:'New evaluation',exact:true}).click();
 await page.getByLabel('Scenario set').selectOption({label:'Custom refund checks'});
 await page.getByRole('dialog').getByRole('button',{name:'Queue evaluation'}).click();
 await page.getByRole('button',{name:'Execute native demo'}).click();
 await expect(page.getByText('COMPLETED',{exact:true}).first()).toBeVisible();
 await page.getByRole('button',{name:'RealityCheck',exact:true}).click();
 await expect(page.getByLabel('RealityCheck assessment')).toContainText('configured_assertions');
 await page.getByRole('button',{name:'Assign reviewer',exact:true}).click();
 await page.getByLabel('Registered reviewer email').fill(email);
 await page.getByRole('dialog').getByRole('button',{name:'Assign reviewer',exact:true}).click();
 await page.getByRole('link',{name:'RealityCheck',exact:true}).click();
 await page.getByRole('table',{name:'Review assignments'}).getByRole('button',{name:'Review',exact:true}).click();
 await page.getByLabel('Evidence and justification').fill('Verified actual fixture transaction and invariant evidence.');
 await page.getByRole('dialog').getByRole('button',{name:'Submit assigned review'}).click();
 await expect(page.getByRole('table',{name:'Review assignments'})).toContainText('COMPLETED');
 await expect(page.getByRole('dialog')).toHaveCount(0);
 await expect(page.getByRole('link',{name:'Skip to content'})).not.toBeFocused();
 await page.screenshot({path:`test-results/realitycheck-${test.info().project.name}.png`,fullPage:true});
});

test('authorized security scan exposes findings and incomplete coverage',async({page})=>{
 await page.goto('/');await page.getByRole('button',{name:'Create a new account'}).click();
 await page.getByLabel('Email',{exact:true}).fill(`security-${Date.now()}@example.test`);await page.getByLabel('Password',{exact:true}).fill('browser-synthetic-passphrase');await page.getByRole('button',{name:'Create account',exact:true}).click();
 await page.getByRole('button',{name:'Create project',exact:true}).click();await page.getByLabel('Project name').fill('Security fixtures');await page.getByRole('dialog').getByRole('button',{name:'Create project',exact:true}).click();
 await page.getByRole('link',{name:'Agents',exact:true}).click();await page.getByRole('button',{name:'Connect agent',exact:true}).first().click();await page.getByLabel('Agent name').fill('Unsafe reference agent');await page.getByLabel('Native behavior').selectOption('unsafe');await page.getByRole('dialog').getByRole('button',{name:'Connect agent',exact:true}).click();
 await page.getByRole('link',{name:'Security',exact:true}).click();await page.getByRole('button',{name:'Start security scan',exact:true}).click();await page.getByLabel('Security mode').selectOption('adversarial');await page.getByRole('dialog').getByRole('button',{name:'Start security scan',exact:true}).click();await expect(page.getByRole('alert').last()).toContainText('authorized-target');
 await page.getByLabel('Target authorization').selectOption('true');await page.getByRole('dialog').getByRole('button',{name:'Start security scan',exact:true}).click();await page.getByRole('button',{name:'Execute native demo'}).click();await expect(page.getByText('COMPLETED',{exact:true}).first()).toBeVisible();await page.getByRole('button',{name:'Security',exact:true}).click();await page.getByRole('button',{name:'View security coverage'}).click();await expect(page.getByLabel('Execution evidence').last()).toContainText('critical');await expect(page.getByLabel('Execution evidence').last()).toContainText('NOT_RUN');await page.screenshot({path:`test-results/security-${test.info().project.name}.png`,fullPage:true});
});
