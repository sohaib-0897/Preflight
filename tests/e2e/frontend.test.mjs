import { test } from 'node:test';
import assert from 'node:assert/strict';
import { escapeHtml, formatPercent } from '../../apps/web/public/app.js';

test('output rendering escapes hostile agent text and markup',()=>{
 assert.equal(escapeHtml('<script>"&\'</script>'),'&lt;script&gt;&quot;&amp;&#39;&lt;/script&gt;');
 assert.equal(escapeHtml(null),'');
});
test('missing and zero metrics remain distinct',()=>{
 assert.equal(formatPercent(undefined),'Unavailable');
 assert.equal(formatPercent(0),'0.0%');
 assert.equal(formatPercent(.875),'87.5%');
});
