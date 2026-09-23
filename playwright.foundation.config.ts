import {defineConfig} from '@playwright/test';
import path from 'node:path';
const root=path.resolve('../..');
export default defineConfig({
 testDir:'./e2e',testMatch:'foundation.spec.ts',workers:1,timeout:30000,reporter:'list',
 use:{baseURL:'http://127.0.0.1:5173',browserName:'chromium',channel:'msedge',trace:'retain-on-failure'},
 outputDir:'../../artifacts/p1-browser',
 webServer:[
  {command:'"'+path.join(root,'.venv/Scripts/python.exe')+'" -m uvicorn p1_browser_app:app --app-dir "'+path.join(root,'scripts')+'" --host 127.0.0.1 --port 8000',
   url:'http://127.0.0.1:8000/api/preferences',reuseExistingServer:false,
   env:{SAMJHA_DB:path.join(root,'artifacts/p1-browser-legacy.sqlite3'),SAMJHA_CHAT_DB:path.join(root,'artifacts/p1-browser-chat.sqlite3'),CI_ENABLED:'false',CI_API_KEY:'',CI_MAX_REQUESTS:'0'}},
  {command:'npm run dev',url:'http://127.0.0.1:5173',reuseExistingServer:false}
 ]
});
