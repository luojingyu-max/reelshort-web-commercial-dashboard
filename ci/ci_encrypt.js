// CI encrypt: read ./index.html (plaintext), encrypt with DASH_PW, overwrite ./index.html
const fs = require('fs');
const webcrypto = globalThis.crypto;
const subtle = webcrypto.subtle;
const ITER = 250000;

async function deriveKey(pw, salt) {
  const base = await subtle.importKey('raw', new TextEncoder().encode(pw), 'PBKDF2', false, ['deriveKey']);
  return subtle.deriveKey({ name: 'PBKDF2', salt, iterations: ITER, hash: 'SHA-256' },
    base, { name: 'AES-GCM', length: 256 }, false, ['encrypt', 'decrypt']);
}
const b64 = buf => Buffer.from(buf).toString('base64');

(async () => {
  const pw = process.env.DASH_PW || process.argv[2];
  if (!pw) { console.error('DASH_PW missing'); process.exit(1); }
  const plaintext = fs.readFileSync('index.html');
  const salt = webcrypto.getRandomValues(new Uint8Array(16));
  const iv = webcrypto.getRandomValues(new Uint8Array(12));
  const key = await deriveKey(pw, salt);
  const ct = await subtle.encrypt({ name: 'AES-GCM', iv }, key, plaintext);
  const dec = await subtle.decrypt({ name: 'AES-GCM', iv }, key, ct);
  if (Buffer.compare(Buffer.from(dec), plaintext) !== 0) { console.error('roundtrip fail'); process.exit(1); }

  const wrapper = `<!doctype html><html lang="zh"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<meta name="robots" content="noindex,nofollow"/>
<title>ReelShort 商业化看板 · 需要密码</title>
<style>
  html,body{height:100%} body{margin:0;background:#0d0d0d;color:#fff;font-family:system-ui,-apple-system,"Segoe UI",sans-serif;display:flex;align-items:center;justify-content:center}
  .card{background:#1a1a19;border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:32px 28px;width:340px;text-align:center}
  h1{font-size:17px;margin:0 0 4px} p{color:#898781;font-size:13px;margin:0 0 20px}
  input{width:100%;box-sizing:border-box;background:#0d0d0d;border:1px solid rgba(255,255,255,.15);border-radius:10px;color:#fff;padding:11px 12px;font-size:15px;margin-bottom:12px}
  input:focus{outline:none;border-color:#E52E2E}
  button{width:100%;background:#E52E2E;color:#fff;border:0;border-radius:10px;padding:11px;font-size:15px;font-weight:600;cursor:pointer}
  button:disabled{opacity:.6;cursor:default} .err{color:#e66767;font-size:13px;height:16px;margin-top:10px}
</style></head><body>
<form class="card" id="f">
  <h1>🔒 ReelShort 官网商业化看板</h1>
  <p>此看板含内部数据,请输入访问密码</p>
  <input id="pw" type="password" autocomplete="current-password" placeholder="访问密码" autofocus/>
  <button id="b" type="submit">进入看板</button>
  <div class="err" id="e"></div>
</form>
<script>
const SALT=Uint8Array.from(atob("${b64(salt)}"),c=>c.charCodeAt(0));
const IV=Uint8Array.from(atob("${b64(iv)}"),c=>c.charCodeAt(0));
const CT=Uint8Array.from(atob("${b64(new Uint8Array(ct))}"),c=>c.charCodeAt(0));
const ITER=${ITER};
async function unlock(pw){
  const base=await crypto.subtle.importKey('raw',new TextEncoder().encode(pw),'PBKDF2',false,['deriveKey']);
  const key=await crypto.subtle.deriveKey({name:'PBKDF2',salt:SALT,iterations:ITER,hash:'SHA-256'},base,{name:'AES-GCM',length:256},false,['decrypt']);
  return new TextDecoder().decode(await crypto.subtle.decrypt({name:'AES-GCM',iv:IV},key,CT));
}
document.getElementById('f').addEventListener('submit',async(ev)=>{
  ev.preventDefault();const b=document.getElementById('b'),e=document.getElementById('e');
  b.disabled=true;e.textContent='解密中…';
  try{const html=await unlock(document.getElementById('pw').value);document.open();document.write(html);document.close();}
  catch(err){e.textContent='密码错误';b.disabled=false;}
});
</script></body></html>`;
  fs.writeFileSync('index.html', wrapper);
  console.log('encrypted index.html:', wrapper.length, 'bytes (plaintext', plaintext.length, ')');
})();
