// 数据静态加密工具(与 Worker 同方案:PBKDF2-SHA256/250k + AES-256-GCM,输出 base64(salt|iv|ct))
// 用法:
//   node dataenc.mjs encrypt <infile> <outfile.enc>     # 加密单个文件(种子/本地)
//   node dataenc.mjs decrypt-all                         # 解密 data/*.enc 和 strategy.json.enc -> 明文(CI 构建前)
// 密钥来自环境变量 DASH_PW。
import fs from "fs";
const ITER = 250000;
const KEY = process.env.DASH_PW;
if (!KEY) { console.error("DASH_PW missing"); process.exit(1); }

async function deriveKey(salt) {
  const base = await crypto.subtle.importKey("raw", new TextEncoder().encode(KEY), "PBKDF2", false, ["deriveKey"]);
  return crypto.subtle.deriveKey({ name: "PBKDF2", salt, iterations: ITER, hash: "SHA-256" },
    base, { name: "AES-GCM", length: 256 }, false, ["encrypt", "decrypt"]);
}
async function encFile(inp, outp) {
  const data = fs.readFileSync(inp);
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const key = await deriveKey(salt);
  const ct = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, data));
  const blob = new Uint8Array(16 + 12 + ct.length);
  blob.set(salt, 0); blob.set(iv, 16); blob.set(ct, 28);
  fs.writeFileSync(outp, Buffer.from(blob).toString("base64"));
  console.log("encrypted", inp, "->", outp, `(${data.length}->${ct.length}b)`);
}
async function decFile(enc, outp) {
  const blob = new Uint8Array(Buffer.from(fs.readFileSync(enc, "utf8"), "base64"));
  const salt = blob.slice(0, 16), iv = blob.slice(16, 28), ct = blob.slice(28);
  const key = await deriveKey(salt);
  const data = new Uint8Array(await crypto.subtle.decrypt({ name: "AES-GCM", iv }, key, ct));
  fs.writeFileSync(outp, Buffer.from(data));
  console.log("decrypted", enc, "->", outp, `(${data.length}b)`);
}

const [, , mode, a, b] = process.argv;
if (mode === "encrypt") await encFile(a, b);
else if (mode === "decrypt-all") {
  for (const f of fs.readdirSync("data")) if (f.endsWith(".enc")) await decFile(`data/${f}`, `data/${f.slice(0, -4)}`);
  for (const f of fs.readdirSync(".")) if (f.endsWith(".json.enc")) await decFile(f, f.slice(0, -4));
} else { console.error("mode?"); process.exit(1); }
