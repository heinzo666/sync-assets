const fs=require('fs'); 
const OFF=parseInt(process.env.QD_OFFSET_MS||'0',10);
if(OFF){const _d=Date.now.bind(Date); Date.now=()=>_d()+OFF;}
 const w=(s)=>fs.writeSync(1,s+'\n'); const we=(s)=>fs.writeSync(2,s+'\n');
const SRC=fs.readFileSync(process.env.QD_GUARD||'/tmp/qdm.cjs','utf8');
function mkwin(){ 
  const win={};
  win.window=win;
  win.document={querySelector:()=>null,createElement:()=>({setAttribute(){},addEventListener(){},appendChild(){},style:{}}),head:{appendChild(){}},body:{},readyState:'complete',addEventListener(){}};
  win.navigator={userAgent:'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131 Safari/537.36',languages:['en-US'],platform:'Win32',hardwareConcurrency:8};
  win.location={href:'https://app.quantumproxies.io/register',origin:'https://app.quantumproxies.io',hostname:'app.quantumproxies.io',protocol:'https:',pathname:'/register'};
  const LS={}; win.localStorage={getItem:k=>LS[k]??null,setItem:(k,v)=>{LS[k]=String(v)},removeItem:k=>{delete LS[k]}};
  const SS={}; win.sessionStorage={getItem:k=>SS[k]??null,setItem:(k,v)=>{SS[k]=String(v)},removeItem:k=>{delete SS[k]}};
  win.atob=s=>Buffer.from(s,'base64').toString('binary'); win.btoa=s=>Buffer.from(s,'binary').toString('base64');
  win.setTimeout=setTimeout; win.clearTimeout=clearTimeout; win.Date=Date; win.Math=Math; win.JSON=JSON;
  win.crypto=require('crypto').webcrypto; win.performance={now:()=>Date.now()%100000};
  win.TextEncoder=TextEncoder; win.TextDecoder=TextDecoder; win.fetch=fetch; win.console=console;
  win.globalThis=win; win.self=win;
  return win;
}
const W=mkwin();
try{
  const runner=new Function('window','self','globalThis','document','navigator','location','localStorage','sessionStorage','atob','btoa','crypto','performance','setTimeout','clearTimeout',
    'with(this){'+SRC+'}\n;return (typeof qdGuard!=="undefined")?qdGuard:((this&&this.window&&this.window.qdGuard)||(window&&window.qdGuard)||null);');
  const g=runner.call(W,W,W,W.document,W.navigator,W.location,W.localStorage,W.sessionStorage,W.atob,W.btoa,W.crypto,W.performance,setTimeout,clearTimeout);
  if(!g){we('NO_GUARD keys='+Object.keys(W).slice(-20).join(','));process.exit(4);}
  w('GUARD_OK keys='+Object.keys(g).join(','));
  Promise.resolve(g.sign(process.argv[2]||'{"t":1}')).then(r=>{
     if(typeof r==='string'){try{r=JSON.parse(r)}catch(_){}}
     w('RESULT '+JSON.stringify({ts:String(r?.ts??''),token:String(r?.token??''),rawType:typeof r}));
  }).catch(e=>w('SIGN_ERR '+String(e.message||e).slice(0,200)));
}catch(e){ we('LOAD_ERR '+String(e.stack||e.message).slice(0,400)); process.exit(3);}
