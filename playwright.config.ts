import { defineConfig, devices } from '@playwright/test';
const baseURL = `http://127.0.0.1:${process.env.PREFLIGHT_PORT || '8000'}`;
export default defineConfig({
 testDir:'tests/e2e',testMatch:'*.spec.ts',timeout:45000,workers:1,
 use:{baseURL,channel:'chrome',launchOptions:{chromiumSandbox:true},trace:'retain-on-failure'},
 projects:[{name:'desktop',use:{...devices['Desktop Chrome']}},{name:'mobile',use:{viewport:{width:390,height:844}}}],
 webServer:{command:'bash scripts/dev.sh',url:`${baseURL}/api/v1/health`,reuseExistingServer:false,timeout:20000},
});
