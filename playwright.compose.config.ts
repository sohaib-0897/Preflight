import {defineConfig} from '@playwright/test';
import original from './playwright.config';
export default defineConfig({...original,testMatch:['compose.spec.ts'],use:{...original.use,baseURL:'http://127.0.0.1:3000'},webServer:undefined});
