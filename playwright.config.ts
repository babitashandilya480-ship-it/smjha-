import {defineConfig} from '@playwright/test';
import path from 'node:path';
const root=path.resolve('../..');
export default defineConfig({
 testDir:'./e2e',testIgnore:'foundation.spec.ts',workers:1,timeout:30000,reporter:'list',
 use:{baseURL:'http://127.0.0.1:5173',browserName:'chromium',channel:'msedge',trace:'retain-on-failure'},
 outputDir:'../../artifacts/browser',
 webServer:[
  {command:'"'+path.join(root,'.venv/Scripts/python.exe')+'" -m uvicorn main:app --app-dir "'+path.join(root,'backend')+'" --host 127.0.0.1 --port 8000',
   url:'http://127.0.0.1:8000/api/preferences',reuseExistingServer:false,env:{SAMJHA_DB:path.join(root,'artifacts/browser-test.sqlite3')}},
  {command:'npm run dev',url:'http://127.0.0.1:5173',reuseExistingServer:false}
 ]
});
