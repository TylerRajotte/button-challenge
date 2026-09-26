import {chromium} from 'playwright';
import {existsSync,readdirSync} from 'node:fs';
import {homedir} from 'node:os';
import {join} from 'node:path';
export async function launchBrowser(){
  let executablePath=process.env.BROWSER_PATH || chromium.executablePath();
  const cache=join(homedir(),'.cache/ms-playwright');
  if(!existsSync(executablePath)&&existsSync(cache)){
    const installations=readdirSync(cache).filter(n=>/^chromium-\d+$/.test(n)).sort((a,b)=>+b.split('-')[1]-+a.split('-')[1]);
    for(const name of installations){for(const dir of ['chrome-linux64','chrome-linux']){const p=join(cache,name,dir,'chrome');if(existsSync(p)){executablePath=p;break;}}if(existsSync(executablePath))break;}
  }
  return chromium.launch({headless:true,executablePath,args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage']});
}
