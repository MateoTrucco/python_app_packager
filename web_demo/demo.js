import {bootPython} from './pyodide-helper.js';let py;const out=document.querySelector('#output'),btn=document.querySelector('#build');async function init(){py=await bootPython(['builder.py']);py.runPython(`from pathlib import Path
Path('/demo').mkdir(exist_ok=True)
Path('/demo/out').mkdir(exist_ok=True)
Path('/demo/app.py').write_text("print('hello')",encoding='utf-8')`);btn.disabled=false;build();}
function build(){if(!py)return;py.globals.set('demo_name',document.querySelector('#appName').value);py.globals.set('one_file',document.querySelector('#oneFile').checked);py.globals.set('windowed',document.querySelector('#windowed').checked);py.globals.set('clean',document.querySelector('#clean').checked);try{const result=py.runPython(`import shlex
from pathlib import Path
from builder import BuildOptions, build_command
opts=BuildOptions(Path('/demo/app.py'),Path('/demo/out'),one_file=bool(one_file),windowed=bool(windowed),clean=bool(clean),name=demo_name)
shlex.join(build_command(opts))`);out.textContent=String(result);}catch(e){out.textContent='Validation error: '+e.message;}}
btn.disabled=true;btn.addEventListener('click',build);init().catch(()=>{});
