/**
 * 官网商业化看板 · BI 邮件自动落地(Google Apps Script,每天定时)
 * 作用:找到 Quick BI 推送邮件里的 xlsx 附件 → 提交到私有数据仓库 → 触发看板重建。
 *
 * 部署:
 *  1) 用「能收到 BI 邮件的那个 Google 账号」登录 script.google.com,新建项目,粘贴本文件。
 *  2) 项目设置 → 脚本属性(Script properties)加三条:
 *       GH_TOKEN   = GitHub 细粒度令牌(对以下两个仓库都授权 Contents: Read and write)
 *       DATA_REPO  = luojingyu-max/reelshort-dash-data          (私有,存原始 Excel)
 *       DASH_REPO  = luojingyu-max/reelshort-web-commercial-dashboard (公开,触发重建)
 *  3) 先手动运行一次 setupDailyTrigger()(会让你授权 Gmail / 外部请求),设定每天触发。
 *  4) 再手动运行一次 pullBIExcelDaily() 测试。
 */

function pullBIExcelDaily() {
  const P = PropertiesService.getScriptProperties();
  const TOKEN = P.getProperty('GH_TOKEN');
  const DATA_REPO = P.getProperty('DATA_REPO');
  const DASH_REPO = P.getProperty('DASH_REPO');
  if (!TOKEN || !DATA_REPO || !DASH_REPO) throw new Error('缺少脚本属性 GH_TOKEN / DATA_REPO / DASH_REPO');

  const processed = getOrCreateLabel_('BI-已处理');
  // 最近 3 天、含附件、未处理的 BI 邮件
  const query = 'from:quickbi@service.aliyun.com subject:官网大盘数据邮箱推送 has:attachment newer_than:3d -label:"BI-已处理"';
  const threads = GmailApp.search(query, 0, 10);
  if (!threads.length) { Logger.log('没有待处理的 BI 邮件'); return; }

  let handled = 0;
  for (const thread of threads) {
    const msgs = thread.getMessages();
    let got = false;
    for (let i = msgs.length - 1; i >= 0 && !got; i--) {
      const xlsx = msgs[i].getAttachments().filter(function(a){ return /\.xlsx$/i.test(a.getName()); })[0];
      if (!xlsx) continue;
      const b64 = Utilities.base64Encode(xlsx.getBytes());
      const stamp = Utilities.formatDate(msgs[i].getDate(), 'Etc/GMT', 'yyyy-MM-dd_HHmmss');
      ghPutFile_(TOKEN, DATA_REPO, 'incoming/latest.xlsx', b64, 'BI latest ' + stamp);
      ghPutFile_(TOKEN, DATA_REPO, 'incoming/history/' + stamp + '.xlsx', b64, 'BI ' + stamp);
      got = true; handled++;
    }
    thread.addLabel(processed);
  }
  if (handled) { ghDispatch_(TOKEN, DASH_REPO, 'rebuild'); Logger.log('已处理 ' + handled + ' 封并触发重建'); }
  else Logger.log('匹配到邮件但未找到 xlsx 附件');
}

function getOrCreateLabel_(name){ return GmailApp.getUserLabelByName(name) || GmailApp.createLabel(name); }

function ghHeaders_(token){ return {Authorization:'Bearer '+token, Accept:'application/vnd.github+json', 'User-Agent':'gas-bi'}; }

function ghPutFile_(token, repo, path, contentB64, message) {
  const url = 'https://api.github.com/repos/' + repo + '/contents/' + path.split('/').map(encodeURIComponent).join('/');
  let sha = null;
  const get = UrlFetchApp.fetch(url, {method:'get', muteHttpExceptions:true, headers:ghHeaders_(token)});
  if (get.getResponseCode() === 200) sha = JSON.parse(get.getContentText()).sha;
  const payload = {message: message, content: contentB64};
  if (sha) payload.sha = sha;
  const put = UrlFetchApp.fetch(url, {method:'put', contentType:'application/json', muteHttpExceptions:true, headers:ghHeaders_(token), payload: JSON.stringify(payload)});
  if (put.getResponseCode() >= 300) throw new Error('提交失败 '+path+': '+put.getResponseCode()+' '+put.getContentText());
}

function ghDispatch_(token, repo, eventType) {
  const url = 'https://api.github.com/repos/' + repo + '/dispatches';
  const resp = UrlFetchApp.fetch(url, {method:'post', contentType:'application/json', muteHttpExceptions:true, headers:ghHeaders_(token), payload: JSON.stringify({event_type: eventType})});
  if (resp.getResponseCode() >= 300) throw new Error('触发重建失败: '+resp.getResponseCode()+' '+resp.getContentText());
}

/** 一次性:设置每天 9 点(脚本所在时区)自动运行 */
function setupDailyTrigger() {
  ScriptApp.getProjectTriggers().forEach(function(t){ if (t.getHandlerFunction()==='pullBIExcelDaily') ScriptApp.deleteTrigger(t); });
  ScriptApp.newTrigger('pullBIExcelDaily').timeBased().everyDays(1).atHour(9).create();
  Logger.log('已设置每天 9 点触发');
}
