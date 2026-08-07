// Cloudflare Worker: 收看板上传的 Excel → 静态加密 → 提交到仓库 ci/data/*.enc → 触发 GitHub Action 重建。
// 部署后设 Secret: GH_TOKEN(细粒度 PAT,本仓库 Contents:write)、DASH_PW(数据加密密钥,与看板密码相同)
// 可选 Var: ALLOW_ORIGIN(默认 * ;建议设为 https://luojingyu-max.github.io)
const REPO = "luojingyu-max/reelshort-web-commercial-dashboard";
const ITER = 250000;
async function encryptData(buf, pw) {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const base = await crypto.subtle.importKey("raw", new TextEncoder().encode(pw), "PBKDF2", false, ["deriveKey"]);
  const key = await crypto.subtle.deriveKey({ name: "PBKDF2", salt, iterations: ITER, hash: "SHA-256" },
    base, { name: "AES-GCM", length: 256 }, false, ["encrypt"]);
  const ct = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, buf));
  const blob = new Uint8Array(28 + ct.length);
  blob.set(salt, 0); blob.set(iv, 16); blob.set(ct, 28);
  let bin = ""; for (let i = 0; i < blob.length; i++) bin += String.fromCharCode(blob[i]);
  return btoa(btoa(bin));   // outer btoa: file content is itself base64 text (matches dataenc.mjs which writes base64 text)
}

export default {
  async fetch(req, env) {
    const origin = env.ALLOW_ORIGIN || "*";
    const cors = {
      "Access-Control-Allow-Origin": origin,
      "Access-Control-Allow-Methods": "POST,OPTIONS",
      "Access-Control-Allow-Headers": "content-type",
    };
    if (req.method === "OPTIONS") return new Response(null, { headers: cors });
    if (req.method !== "POST") return new Response("POST only", { status: 405, headers: cors });
    try {
      const form = await req.formData();
      const files = form.getAll("file").filter((f) => typeof f !== "string");
      if (!files.length) return json({ error: "no file" }, 400, cors);

      const gh = (path, method, body) =>
        fetch(`https://api.github.com/repos/${REPO}/${path}`, {
          method,
          headers: {
            Authorization: `Bearer ${env.GH_TOKEN}`,
            "User-Agent": "dash-worker",
            Accept: "application/vnd.github+json",
          },
          body: body ? JSON.stringify(body) : undefined,
        });

      if (!env.DASH_PW) return json({ error: "DASH_PW not set on worker" }, 500, cors);
      const enc = (p) => p.split("/").map(encodeURIComponent).join("/");
      const allow = new Set(["官网大盘.xlsx", "国家+付费.xlsx", "引流app.xlsx"]);
      const done = [];
      for (const f of files) {
        const name = f.name;
        if (!allow.has(name)) return json({ error: "文件名必须是 官网大盘.xlsx / 国家+付费.xlsx / 引流app.xlsx,收到:" + name }, 400, cors);
        const buf = new Uint8Array(await f.arrayBuffer());
        const content = await encryptData(buf, env.DASH_PW);   // -> GitHub content(base64 of the .enc text)
        const p = `ci/data/${name}.enc`;
        let sha;
        const cur = await gh(`contents/${enc(p)}`, "GET");
        if (cur.ok) sha = (await cur.json()).sha;
        const put = await gh(`contents/${enc(p)}`, "PUT", { message: `upload ${name} (encrypted) via dashboard`, content, sha });
        if (!put.ok) return json({ error: "commit failed", detail: await put.text() }, 500, cors);
        done.push(name);
      }
      const disp = await gh("dispatches", "POST", { event_type: "rebuild" });
      if (!disp.ok) return json({ error: "dispatch failed", detail: await disp.text() }, 500, cors);
      return json({ ok: true, files: done.length, names: done }, 200, cors);
    } catch (e) {
      return json({ error: e.message }, 500, cors);
    }
  },
};
function json(o, status, cors) {
  return new Response(JSON.stringify(o), { status, headers: { ...cors, "content-type": "application/json" } });
}
