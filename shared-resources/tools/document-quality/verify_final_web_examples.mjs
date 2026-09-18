// Run with Node and a separate dependency workspace containing React, TypeScript,
// @tanstack/react-query, jsdom and @testing-library/react. No app server is started.
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const workspace = resolve(process.argv[2]);
const require = createRequire(resolve(workspace, 'package.json'));
const ts = require('typescript');
const work = resolve(workspace, 'final-web-samples');
await mkdir(work, { recursive: true });
const results = [], sources = [];
async function source(path) {
  const text = await readFile(resolve(root, path), 'utf8');
  sources.push({ path, sha256: createHash('sha256').update(text).digest('hex') });
  return text;
}
const blocks = text => [...text.matchAll(/```(?:js|ts|tsx|typescript)\s*\n([\s\S]*?)\n```/g)].map(x => x[1]);
function run(file, expected) {
  const done = spawnSync(process.execPath, [file], { encoding: 'utf8', timeout: 20000 });
  assert.equal(done.status, 0, done.stderr);
  if (expected !== undefined) assert.equal(done.stdout.trim(), expected);
  return done.stdout.trim();
}
function transpile(code) {
  return ts.transpileModule(code, { compilerOptions: {
    target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ESNext, jsx: ts.JsxEmit.ReactJSX,
  }}).outputText;
}

const lru = blocks(await source('02-nextjs-frontend/advanced-topics/performance/02-advanced-optimization.md')).find(x => x.includes('class LruCache'));
assert.ok(lru);
const lruFile = resolve(work, 'lru.mjs');
await writeFile(lruFile, lru + '\n' + `
import assert from 'node:assert/strict';
const tested = new LruCache(2);
tested.set('a',1); tested.set('b',2); tested.get('a'); tested.set('c',3);
assert.equal(tested.get('b'),undefined); assert.equal(tested.get('a'),1);
tested.set('a',9); assert.equal(tested.get('a'),9);
assert.throws(() => new LruCache(0));
`);
results.push({ case: 'LRU demo and eviction/update/invalid-capacity assertions', output: run(lruFile), status:'PASS' });

const hydration = blocks(await source('03-tanstack-stack/reference/framework-essentials/04-prefetch-ssr.md'))[0];
const hydrationFile = resolve(work,'hydration.mjs'); await writeFile(hydrationFile,hydration);
run(hydrationFile,'你好'); results.push({case:'Query dehydrate JSON hydrate round trip',status:'PASS'});

const search = blocks(await source('03-tanstack-stack/reference/language-concepts/11-search-params.md')).find(x => x.includes('function pageNumber'));
const searchFile = resolve(work,'page-number.mjs');
await writeFile(searchFile,transpile(search)+`\nimport assert from 'node:assert/strict';
for(const x of [undefined,null,true,{},[],NaN,Infinity,-1,0,'abc','',10001]) assert.equal(pageNumber(x,1,10000),1);
assert.equal(pageNumber('2',1,10000),2); assert.equal(pageNumber(3,1,10000),3);`);
run(searchFile); results.push({case:'pageNumber unknown input and range rejection',status:'PASS'});

const original = await source('02-nextjs-frontend/reference/framework-patterns/03-client-components-patterns.md');
const renderBlock = blocks(original).find(x => x.includes('// components/render-props-data-fetcher.tsx'));
assert.ok(renderBlock);
const fetcher = renderBlock.split('// 高级数据获取器')[0];
const fetcherTs = resolve(work,'DataFetcher.tsx');
await writeFile(fetcherTs,fetcher);
await writeFile(resolve(work,'page-number.ts'),search);
const compile=spawnSync(process.execPath,[require.resolve('typescript/bin/tsc'),'--strict','--noEmit','--skipLibCheck','--target','ES2022','--module','ESNext','--moduleResolution','Bundler','--jsx','react-jsx','--lib','ES2022,DOM',fetcherTs,resolve(work,'page-number.ts')],{encoding:'utf8',timeout:20000});
assert.equal(compile.status,0,compile.stdout+'\n'+compile.stderr);
results.push({case:'DataFetcher and pageNumber TypeScript strict with actual dependencies',status:'PASS'});
const fetcherJs=resolve(work,'DataFetcher.mjs');await writeFile(fetcherJs,transpile(fetcher));
const {JSDOM}=require('jsdom');
const dom=new JSDOM('<!doctype html><html><body></body></html>',{url:'http://localhost/'});
for(const key of ['window','document','HTMLElement','MutationObserver','navigator']) Object.defineProperty(globalThis,key,{value:dom.window[key],configurable:true});
globalThis.IS_REACT_ACT_ENVIRONMENT=true;
const React=require('react');
const {render,screen,act,cleanup}=require('@testing-library/react');
const {DataFetcher}=await import(pathToFileURL(fetcherJs).href);
const pending=[];
globalThis.fetch=(url,options)=>new Promise(resolve=>pending.push({url,options,resolve}));
const view=url=>React.createElement(DataFetcher,{url},state=>React.createElement('div',null,state.error?'failed':state.data?.text??'loading'));
try {
  const rendered=render(view('/old'));
  assert.equal(pending.length,1);
  rendered.rerender(view('/new'));
  assert.equal(pending.length,2);assert.equal(pending[0].options.signal.aborted,true);
  await act(async()=>pending[1].resolve({ok:true,json:async()=>({text:'new result'})}));
  assert.ok(screen.getByText('new result'));
  await act(async()=>pending[0].resolve({ok:true,json:async()=>({text:'stale result'})}));
  assert.ok(screen.getByText('new result'));assert.equal(screen.queryByText('stale result'),null);
  results.push({case:'Old response cannot overwrite new URL even when mock ignores abort',status:'PASS'});
  rendered.rerender(view('/failure'));
  await act(async()=>pending[2].resolve({ok:false,status:503}));
  assert.ok(screen.getByText('failed'));
  results.push({case:'HTTP failure reaches error state',status:'PASS'});
  rendered.rerender(view('/unmount'));rendered.unmount();
  assert.equal(pending[3].options.signal.aborted,true);
  await act(async()=>pending[3].resolve({ok:true,json:async()=>({text:'late'})}));
  assert.equal(screen.queryByText('late'),null);
  results.push({case:'Unmount cancels and ignores late completion',status:'PASS'});
} finally {cleanup();dom.window.close();}
const report={runtime:process.version,typescript:ts.version,results,sources,scope:'Selected extracted examples only. jsdom does not verify browser layout, actual network, Next.js build, polling policy, or full historical snippets.'};
await writeFile(resolve(root,'shared-resources/tools/document-quality/reports/final-web-examples.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({checks:results.length,status:'PASS'}));
