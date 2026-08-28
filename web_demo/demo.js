import { bootPython, parsePythonJson } from './pyodide-helper.js';

let py;
const out = document.querySelector('#output');
const button = document.querySelector('#build');
const controls = ['appName', 'oneFile', 'windowed', 'clean'];

async function init() {
  py = await bootPython(['builder.py']);
  py.runPython(`from pathlib import Path\nPath('/demo').mkdir(exist_ok=True)\nPath('/demo/out').mkdir(exist_ok=True)\nPath('/demo/app.py').write_text("print('hello')",encoding='utf-8')`);
  button.disabled = false;
  build();
}

function build() {
  if (!py) return;
  py.globals.set('demo_name', document.querySelector('#appName').value);
  py.globals.set('one_file', document.querySelector('#oneFile').checked);
  py.globals.set('windowed', document.querySelector('#windowed').checked);
  py.globals.set('clean', document.querySelector('#clean').checked);
  try {
    const raw = py.runPython(`import json,shlex\nfrom pathlib import Path\nfrom builder import BuildOptions, build_command\nopts=BuildOptions(Path('/demo/app.py'),Path('/demo/out'),one_file=bool(one_file),windowed=bool(windowed),clean=bool(clean),name=demo_name)\ncommand=build_command(opts)\njson.dumps({'command':shlex.join(command),'arguments':len(command),'workpath':str(opts.destination / '.pyinstaller' / opts.name),'name':opts.name})`);
    const data = parsePythonJson(raw);
    out.textContent = data.command;
    document.querySelector('#buildMetrics').innerHTML = `<div class="metric"><strong>${data.arguments}</strong><small>Arguments</small></div><div class="metric"><strong>${document.querySelector('#oneFile').checked ? 'one file' : 'folder'}</strong><small>Output mode</small></div><div class="metric"><strong>${document.querySelector('#windowed').checked ? 'windowed' : 'console'}</strong><small>Runtime</small></div>`;
  } catch (error) {
    out.textContent = `Validation error: ${error.message}`;
    document.querySelector('#buildMetrics').innerHTML = '';
  }
}

button.disabled = true;
button.addEventListener('click', build);
for (const id of controls) document.querySelector(`#${id}`).addEventListener('input', build);
document.querySelector('#consolePreset').addEventListener('click', () => {
  document.querySelector('#oneFile').checked = false;
  document.querySelector('#windowed').checked = false;
  document.querySelector('#clean').checked = true;
  build();
});
init().catch(() => {});
