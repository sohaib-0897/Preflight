import { defineConfig, devices } from '@playwright/test';
export default defineConfig({
 testDir:'tests/e2e',testMatch:'*.spec.ts',timeout:45000,workers:1,
 use:{baseURL:'http://127.0.0.1:8000',channel:'chrome',launchOptions:{chromiumSandbox:true},trace:'retain-on-failure'},
 projects:[{name:'desktop',use:{...devices['Desktop Chrome']}},{name:'mobile',use:{viewport:{width:390,height:844}}}],
 webServer:{command:'bash scripts/dev.sh',url:'http://127.0.0.1:8000/api/v1/health',reuseExistingServer:false,timeout:20000},
});
