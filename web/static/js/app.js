I18N.add({
  en:{'index.pageTitle':'ShareWeb · File Station','tab.upload':'Upload','tab.download':'Download','index.dropHintTouch':'Photos, videos or any other file','index.dropTitle':'Drop a file here','index.dropHint':'Or click to choose one, or press <kbd>Ctrl</kbd>+<kbd>V</kbd> to paste text, an image or a file','index.pick':'Choose file','index.or':'or','index.pastePh':'Paste text here to share it','index.textBtn':'Create text share','index.redeemTitle':'Retrieve a share','index.redeemHint':'Enter code <b>0000</b> for instructions','index.redeemBtn':'Retrieve','index.historyTitle':'Local history','index.clear':'Clear all','index.clearGone':'Clear unavailable','index.footer':'Files are deleted automatically after {days} days · Max file size {size}','index.footerNoLimit':'Files are deleted automatically after {days} days · No file size limit','upload.tooLarge':'This file is larger than the {size} limit','upload.noSpace':'Not enough disk space on the server',
    'history.empty':'No records yet','history.untitled':'Shared content','history.sender':'Sent','history.code':'Code','history.text':'Text','history.deleted':'Deleted','history.expired':'Expired','history.goneTip':'This share is no longer available on the server','history.noneGone':'No unavailable entries','history.confirm':'Confirm','history.confirmAllTip':'Click again to remove all {n} entries from this browser\'s history (files on the server are not affected). Click elsewhere to cancel.','history.confirmGoneTip':'Click again to remove {n} deleted or expired entries. Click elsewhere to cancel.',
    'result.duplicate':'Already on the server ✓','result.done':'Upload complete ✓','result.validUntil':'Valid until {d}','result.code':'Share code','result.link':'Share link','result.clickToCopy':'Click to copy','result.copyFailed':'Copy failed, please copy manually',
    'upload.hashing':'Computing SHA-256…','upload.hashPct':'Computing checksum {p}%','upload.dupFound':'An identical file is already on the server','upload.hashFailed':'Could not compute SHA-256, uploading without resume support…','upload.resumePct':'Resuming upload {p}%','upload.retrying':'Connection lost, retrying in {s}s ({p}% uploaded)','upload.interrupted':'Upload interrupted at {p}%. Choose the same file again to continue from there','upload.checksum':'Checksum mismatch: the file changed during the upload. Please upload it again','upload.uploading':'Uploading…','upload.pct':'Uploading {p}%','upload.failed':'Upload failed: {msg}','net.error':'Network error','text.failed':'Failed to create the share',
    'redeem.need4':'Enter the 4-digit code','redeem.cooldown':'Too many failed attempts. Try again after {t}','redeem.blacklisted':'Your IP has been blacklisted','redeem.wrong':'Wrong code ({n} failed attempts)'},
  zh:{'index.pageTitle':'ShareWeb · 文件中转站','tab.upload':'上传','tab.download':'下载','index.dropHintTouch':'照片、视频或任意文件','index.dropTitle':'拖放文件到这里','index.dropHint':'也可以点击选择，或直接 <kbd>Ctrl</kbd>+<kbd>V</kbd> 粘贴文字、图片或文件','index.pick':'选择文件','index.or':'或','index.pastePh':'文字分享直接粘贴到这里','index.textBtn':'生成文字共享','index.redeemTitle':'提取共享内容','index.redeemHint':'提取码 <b>0000</b> 获取使用方法','index.redeemBtn':'提取','index.historyTitle':'本地历史','index.clear':'清空','index.clearGone':'清除已失效','index.footer':'文件默认保留 {days} 天后自动清理 · 单文件上限 {size}','index.footerNoLimit':'文件默认保留 {days} 天后自动清理 · 单文件大小不限','upload.tooLarge':'文件超过单文件上限 {size}','upload.noSpace':'服务器磁盘空间不足',
    'history.empty':'暂无记录','history.untitled':'共享内容','history.sender':'发送者','history.code':'提取码','history.text':'文字','history.deleted':'已删除','history.expired':'已过期','history.goneTip':'该分享已不在服务器上','history.noneGone':'没有已失效的记录','history.confirm':'确认','history.confirmAllTip':'再点一次删除本浏览器中的全部 {n} 条记录（不影响服务器上的文件），点击其他地方取消。','history.confirmGoneTip':'再点一次删除 {n} 条已删除或已过期的记录，点击其他地方取消。',
    'result.duplicate':'服务器已有相同文件 ✓','result.done':'上传完成 ✓','result.validUntil':'有效至 {d}','result.code':'共享码','result.link':'分享链接','result.clickToCopy':'点击复制','result.copyFailed':'复制失败，请手动复制',
    'upload.hashing':'正在计算 SHA-256…','upload.hashPct':'计算校验码 {p}%','upload.dupFound':'发现服务器已有相同文件','upload.hashFailed':'无法计算 SHA-256，改为普通上传（不支持断点续传）…','upload.resumePct':'断点续传 {p}%','upload.retrying':'网络中断，{s} 秒后重试（已上传 {p}%）','upload.interrupted':'上传中断（已上传 {p}%），重新选择同一个文件即可从断点继续','upload.checksum':'校验失败：文件在上传过程中被修改，请重新上传','upload.uploading':'上传中…','upload.pct':'上传 {p}%','upload.failed':'上传失败：{msg}','net.error':'网络错误','text.failed':'生成失败',
    'redeem.need4':'请输入4位数字提取码','redeem.cooldown':'提取失败次数过多，请于 {t} 后重试','redeem.blacklisted':'当前IP已被加入黑名单','redeem.wrong':'提取码错误，已失败 {n} 次'}
});
const t=I18N.t,S=I18N.span,D=I18N.dateSpan,setKey=I18N.setKey;
const $=s=>document.querySelector(s);const input=$('#fileInput'),pick=$('#pickBtn'),drop=$('#dropzone'),paste=$('#pasteArea'),textBtn=$('#textShareBtn');
async function getHistory(){const db=await openDB();return new Promise((resolve,reject)=>{const r=db.transaction('items').objectStore('items').getAll();r.onsuccess=()=>resolve(r.result.sort((a,b)=>b.added_at.localeCompare(a.added_at)));r.onerror=()=>reject(r.error)})}
let historyGone=new Map(),historyCount=0;
function updateHistoryButtons(){const g=$('#clearGone');g.disabled=historyGone.size===0;if(g.dataset.armed)return;g.dataset.i18nTitle=historyGone.size?'':'history.noneGone';g.title=historyGone.size?'':t('history.noneGone');$('#clearHistory').disabled=historyCount===0}
// 列表在卡片里滚动; 上 / 下方还有内容时给对应边缘加渐隐
const historyBox=$('#history');
function updateHistoryFade(){const h=historyBox;h.classList.toggle('more-above',h.scrollTop>1);h.classList.toggle('more-below',h.scrollTop+h.clientHeight<h.scrollHeight-1)}
historyBox.addEventListener('scroll',updateHistoryFade,{passive:true});
// 列表高度: 尽量让整页一屏显示完。默认上下排列, 列表占满屏幕剩下的高度; 屏幕够宽、但上下排列时列表连约三条记录
// 都放不下 (约 240px, 如笔记本、1080p 显示器) 才改成左右两栏, 列表与左边卡片底部对齐。
// 是否两栏每次都按上下排列实际量一遍再决定 (同一次脚本执行内完成, 不会闪); 屏幕高度取 100svh (手机地址栏收起/展开时不变);
// 超宽屏整页放大 (app.css 里的 zoom) 时量到的是放大后的像素, 换算回 CSS 像素
const HISTORY_MIN=110,SINGLE_COL_MIN=240,TWO_COL_MIN_W=860,svhProbe=document.createElement('div');
svhProbe.style.cssText='position:fixed;top:0;left:0;width:0;height:100vh;height:100svh;visibility:hidden;pointer-events:none';document.body.appendChild(svhProbe);
function fitHistory(){
  const z=parseFloat(getComputedStyle(document.documentElement).zoom)||1;
  const viewH=Math.min(svhProbe.getBoundingClientRect().height||innerHeight,innerHeight);
  const grid=$('.home-grid'),h=historyBox,main=$('main.container');
  grid.classList.remove('two-col');
  const ms=getComputedStyle(main);
  let avail=viewH-(main.getBoundingClientRect().height+(parseFloat(ms.marginTop)+parseFloat(ms.marginBottom))*z-h.getBoundingClientRect().height);
  if(innerWidth/z>=TWO_COL_MIN_W&&avail/z<SINGLE_COL_MIN){
    grid.classList.add('two-col');
    const cs=getComputedStyle(h.closest('.card'));
    avail=$('#mainCard').getBoundingClientRect().bottom-h.getBoundingClientRect().top-(parseFloat(cs.paddingBottom)+parseFloat(cs.borderBottomWidth))*z;
  }
  h.style.maxHeight=Math.max(HISTORY_MIN,Math.floor(avail/z))+'px';
  updateHistoryFade();
}
addEventListener('resize',fitHistory);
// 上传进度 / 结果出现等让左边卡片变高时也重新算
// (下一帧再算: fitHistory 自己会临时改变卡片大小, 在回调里直接算会触发 ResizeObserver 的循环警告)
if(window.ResizeObserver)new ResizeObserver(()=>requestAnimationFrame(fitHistory)).observe($('#mainCard'));
fitHistory();  // 首次绘制前就定好一栏还是两栏, 避免闪一下
document.fonts?.ready.then(fitHistory);
async function renderHistory(){const box=$('#history');const items=await getHistory();historyGone=new Map();historyCount=items.length;updateHistoryButtons();if(!items.length){box.innerHTML=`<p class="muted">${S('history.empty')}</p>`;fitHistory();return}box.innerHTML=items.map(x=>{
  // 发送和提取的记录同一个样式: 文件名点开分享页, 下面一行是提取码和链接 (点击复制)。
  // 旧版本提取的记录没存提取码, 先不显示, 等 markHistoryStatus 从服务器补上
  const name=x.name||x.filename?esc(x.name||x.filename):S('history.untitled'),title=esc(x.name||x.filename||'');
  const url=x.url||`${location.origin}/share/${encodeURIComponent(x.token||'')}`;
  const meta=x.role==='sender'?S('history.sender'):x.type==='file'?esc(fmtSize(x.size)):S('history.text');
  return `<div class="history-item" data-token="${esc(x.token||'')}"><div class="history-line"><a class="history-link history-name" title="${title}" href="/share/${encodeURIComponent(x.token||'')}">${name}</a><span class="history-status"></span><span class="meta history-meta">${meta} · ${D(x.added_at)}</span></div><div class="history-share"><div class="copy-inline history-code${x.code?'':' hidden'}"><button type="button" class="copy-box history-code-box" data-copy="${esc(x.code||'')}" data-i18n-title="result.clickToCopy" title="${esc(t('result.clickToCopy'))}">${esc(x.code||'')}</button><span class="copy-hint" data-i18n="result.clickToCopy">${esc(t('result.clickToCopy'))}</span></div><div class="copy-inline history-url-line"><button type="button" class="copy-box history-link-box" title="${esc(url)}" data-copy="${esc(url)}">${esc(url)}</button><span class="copy-hint" data-i18n="result.clickToCopy">${esc(t('result.clickToCopy'))}</span></div></div></div>`;
}).join('');box.querySelectorAll('[data-copy]').forEach(b=>b.onclick=()=>copyWithFeedback(b));fitHistory();markHistoryStatus(items)}
// 本地历史只存在本机浏览器里, 服务器删文件不会影响它; 这里向服务器查一下, 把已删除/已过期的条目标出来 (查询失败则保持原样)。
// 旧记录 (提取过的) 没存提取码: 用服务器返回的补上显示, 并写回本地历史, 下次直接有
function fillHistoryCodes(items,codes){
  const fill=items.filter(x=>!x.code&&codes[x.token]);if(!fill.length)return;
  fill.forEach(x=>{x.code=codes[x.token];const el=document.querySelector(`#history .history-item[data-token="${CSS.escape(x.token)}"] .history-code`);if(!el)return;const b=el.querySelector('[data-copy]');b.dataset.copy=x.code;b.textContent=x.code;el.classList.remove('hidden')});
  openDB().then(db=>txDone(db,tx=>{const st=tx.objectStore('items');fill.forEach(x=>st.put(x))})).catch(()=>{});
}
async function markHistoryStatus(items){const tokens=items.map(x=>x.token).filter(Boolean).slice(0,200);if(!tokens.length)return;try{const r=await fetch('/api/share-status',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tokens})});if(!r.ok)return;const {status,codes={}}=await r.json();fillHistoryCodes(items,codes);items.forEach(x=>{const s=status[x.token];if(s==='deleted'||s==='expired')historyGone.set(x.token,x.key||x.token)});updateHistoryButtons();document.querySelectorAll('#history .history-item[data-token]').forEach(el=>{const s=status[el.dataset.token];if(s!=='deleted'&&s!=='expired')return;el.classList.add('gone');el.dataset.i18nTitle='history.goneTip';el.title=t('history.goneTip');el.querySelector('.history-status').innerHTML=`<span class="tag ${s==='deleted'?'gone':'warn'}">${S(s==='deleted'?'history.deleted':'history.expired')}</span>`});updateHistoryFade()}catch(e){}}
let lastResult=null;
function renderResult(){if(!lastResult)return;const {data,duplicate}=lastResult;const r=$('#result');r.classList.remove('hidden');const digits=String(data.code||'').split('').map(d=>`<span class="cbox">${esc(d)}</span>`).join('');r.innerHTML=`<div class="result-box centered"><h2>${S(duplicate?'result.duplicate':'result.done')}</h2><p class="result-file">${esc(data.filename)}</p><p class="meta result-meta">${fmtSize(data.size)} · ${S('result.validUntil',{d:{date:data.expires_at}})}</p><div class="copy-block"><div class="copy-head"><span class="copy-label">${S('result.code')}</span><span class="copy-hint" data-i18n="result.clickToCopy">${esc(t('result.clickToCopy'))}</span></div><button type="button" class="copy-code-group" data-copy="${esc(data.code)}" aria-label="${esc(data.code)}">${digits}</button></div><div class="copy-block"><div class="copy-head"><span class="copy-label">${S('result.link')}</span><span class="copy-hint" data-i18n="result.clickToCopy">${esc(t('result.clickToCopy'))}</span></div><div class="copy-box copy-link" role="button" tabindex="0" title="${esc(data.url)}" data-copy="${esc(data.url)}">${esc(data.url)}</div></div><div class="result-divider"></div><div class="copy-block result-sha"><div class="copy-head"><span class="copy-label">SHA-256</span><span class="copy-hint" data-i18n="result.clickToCopy">${esc(t('result.clickToCopy'))}</span></div><button type="button" class="copy-sha" data-copy="${esc(data.sha256)}">${esc(data.sha256)}</button></div></div>`;r.querySelectorAll('[data-copy]').forEach(b=>{b.onclick=()=>copyWithFeedback(b);if(b.getAttribute('role')==='button')b.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();copyWithFeedback(b)}}})}
// 点击复制的统一反馈: 元素边框变绿, 对应的提示文字 (紧随其后, 或所在区块标题行里的) 变成「已复制 ✓」, 2 秒后恢复。
// 同一时间只保留一个「已复制」状态: 点了另一个时, 上一个立即恢复 (走 0.2s 的颜色过渡), 不等它自己超时。
let lastCopied=null;
function resetCopied(b){if(!b)return;clearTimeout(b._t);if(b._hint){setKey(b._hint,'result.clickToCopy');b._hint.classList.remove('done','fail')}b.classList.remove('copied');if(lastCopied===b)lastCopied=null}
async function copyWithFeedback(b){if(lastCopied&&lastCopied!==b)resetCopied(lastCopied);lastCopied=b;const ok=await copy(b.dataset.copy);const n=b.nextElementSibling;const hint=n&&n.classList.contains('copy-hint')?n:(b.closest('.copy-block')?.querySelector('.copy-hint')||null);b._hint=hint;if(lastCopied!==b)return;if(hint){setKey(hint,ok?'common.copied':'result.copyFailed');hint.classList.toggle('done',ok);hint.classList.toggle('fail',!ok)}b.classList.add('copied');clearTimeout(b._t);b._t=setTimeout(()=>resetCopied(b),2000)}
async function showResult(data,{duplicate=false}={}){lastResult={data,duplicate};renderResult();await addHistory({token:data.token,name:data.filename,type:data.type||'file',size:data.size,role:'sender',code:data.code,url:data.url});await renderHistory()}
function setProgress(p,key,args){$('#progressBar').style.width=p+'%';setKey($('#progressText'),key,{p:Math.floor(p),...args})}
let uploadSeq=0;
async function upload(file){if(!file)return;const seq=++uploadSeq;$('#progressWrap').classList.remove('hidden');if(uploadLimit&&file.size>uploadLimit){setProgress(0,'upload.tooLarge',{size:fmtLimit(uploadLimit)});return}setProgress(0,'upload.hashing');let sha=null;
  // 又选了别的文件时停止计算这一个 (onProgress 里抛出即中断 sha256File)
  try{sha=await sha256File(file,(done,total)=>{if(seq!==uploadSeq)throw new Error('cancelled');setProgress(total?done/total*100:0,'upload.hashPct')})}catch(e){}
  if(seq!==uploadSeq)return;if(sha)uploadResumable(file,sha,seq);else{setKey($('#progressText'),'upload.hashFailed');uploadWhole(file)}}
// 算不出 SHA-256 时的后备: 整个文件一次传完, 不能续传
function uploadWhole(file){const fd=new FormData();fd.append('file',file);const xhr=new XMLHttpRequest();xhr.open('POST','/api/upload');xhr.upload.onprogress=e=>{if(e.lengthComputable)setProgress(e.loaded/e.total*100,'upload.pct')};xhr.onload=()=>{if(xhr.status===200)showResult(JSON.parse(xhr.responseText));else uploadFailed(xhr.status,xhr.responseText)};xhr.onerror=()=>setKey($('#progressText'),'net.error');xhr.send(fd)}
function uploadFailed(status,msg){if(status===413)setKey($('#progressText'),'upload.tooLarge',{size:uploadLimit?fmtLimit(uploadLimit):'?'});else if(status===507)setKey($('#progressText'),'upload.noSpace');else if(status===422)setKey($('#progressText'),'upload.checksum');else setKey($('#progressText'),'upload.failed',{msg:msg||status})}

// ---- 断点续传 ----
// 先用 SHA-256 和大小向服务器建立 (或找回) 上传会话, 再按 8 MB 一块从前往后传。网络断开时自动重试,
// 多次失败才停下; 之后重新选择同一个文件, 哈希和大小一致就从服务器已收到的位置继续 (会话保留 24 小时)。
// 会话 id 存在本机 localStorage 里; 收齐后服务器会再核对一次 SHA-256。
const CHUNK=8*1024*1024,MAX_RETRY=8;
const resumeKey=(sha,size)=>`shareweb.upload.${sha}.${size}`;
function lsGet(k){try{return localStorage.getItem(k)}catch(e){return null}}
function lsSet(k,v){try{v==null?localStorage.removeItem(k):localStorage.setItem(k,v)}catch(e){}}
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function initUpload(file,sha,uploadId){const res=await fetch('/api/upload/init',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sha256:sha,size:file.size,filename:file.name,content_type:file.type||null,upload_id:uploadId})});return {status:res.status,data:await res.json().catch(()=>({}))}}
function putChunk(id,offset,blob,onProgress){return new Promise((resolve,reject)=>{const xhr=new XMLHttpRequest();xhr.open('PUT',`/api/upload/${id}?offset=${offset}`);xhr.upload.onprogress=e=>onProgress(e.loaded);xhr.onload=()=>{let data={};try{data=JSON.parse(xhr.responseText)}catch(e){}resolve({status:xhr.status,data})};xhr.onerror=()=>reject(new Error('network'));xhr.send(blob)})}
async function uploadResumable(file,sha,seq){
  const key=resumeKey(sha,file.size),pct=n=>file.size?n/file.size*100:100;
  let id=null,offset=0,retries=0,renewed=false,label='upload.pct',r;
  for(;;){
    if(seq!==uploadSeq)return;  // 已开始上传别的文件: 放下这个, 以后还能续传
    try{
      if(!id){
        r=await initUpload(file,sha,lsGet(key));
        if(r.status===200&&r.data.exists){lsSet(key,null);setProgress(100,'upload.dupFound');r.data.type='file';await showResult(r.data,{duplicate:true});return}
        if(r.status===200){id=r.data.upload_id;offset=r.data.offset;lsSet(key,id);if(offset)label='upload.resumePct';setProgress(pct(offset),label);continue}
      }else{
        r=await putChunk(id,offset,file.slice(offset,offset+CHUNK),n=>{if(seq===uploadSeq)setProgress(pct(offset+n),label)});
        if(r.status===200){retries=0;if(!r.data.done){offset=r.data.offset;continue}lsSet(key,null);setProgress(100,label);await showResult(r.data);return}
        if(r.status===409){offset=r.data.offset;continue}  // 服务器实际收到的位置与这边不同 (重试时上一块其实已收到)
        // 会话过期被清理, 或其实已经传完只是没收到回应: 重新建立 (已传完的话服务器会直接返回那个文件)
        if(r.status===404&&!renewed){renewed=true;id=null;lsSet(key,null);continue}
      }
      if(r.status>=500&&r.status!==507)throw new Error(r.status);  // 服务器重启等临时故障, 按断网处理
    }catch(e){
      if(++retries>MAX_RETRY){setProgress(pct(offset),'upload.interrupted');return}
      const s=Math.min(2**retries,30);setProgress(pct(offset),'upload.retrying',{s});await sleep(s*1000);continue
    }
    if(r.status===422)lsSet(key,null);
    uploadFailed(r.status,r.data.detail);return
  }
}

const codeInputs=[...document.querySelectorAll('#codeInputs input')];
function redeemCode(){const code=codeInputs.map(x=>x.value).join('');if(!/^\d{4}$/.test(code)){setKey($('#redeemMsg'),'redeem.need4');return}setKey($('#redeemMsg'),null);fetch('/api/redeem',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code})}).then(async r=>{const d=await r.json();if(r.status===429){setKey($('#redeemMsg'),'redeem.cooldown',{t:{date:d.cooldown_until}});return}if(r.status===403){setKey($('#redeemMsg'),'redeem.blacklisted');return}if(!r.ok){setKey($('#redeemMsg'),'redeem.wrong',{n:d.fail_count||1});return}if(d.special){location.href='/special';return}location.href=d.url}).catch(()=>{setKey($('#redeemMsg'),'net.error')})}
// 提取码四个格子: 点击或切换到任意一格都会选中其中的数字, 直接输入即替换这一位并跳到下一格
// (每格 maxlength=1, 不选中的话已有数字的格子输入不进去)
const lastBox=codeInputs.length-1;
function focusBox(i){const el=codeInputs[i];if(el){el.focus();el.select()}}
codeInputs.forEach((el,i)=>{
  const selectAll=()=>el.select();
  el.addEventListener('focus',selectAll);el.addEventListener('click',selectAll);
  el.addEventListener('keydown',e=>{
    const plain=!e.ctrlKey&&!e.metaKey&&!e.altKey;
    if(/^\d$/.test(e.key)&&plain){e.preventDefault();el.value=e.key;focusBox(Math.min(i+1,lastBox));return}
    if(e.key.length===1&&plain){e.preventDefault();return}  // 字母等其他字符不接受, 也不会把选中的数字删掉
    if(e.key==='Backspace'&&!el.value&&i>0){e.preventDefault();codeInputs[i-1].value='';focusBox(i-1);return}
    if(e.key==='ArrowLeft'&&i>0){e.preventDefault();focusBox(i-1)}
    else if(e.key==='ArrowRight'&&i<lastBox){e.preventDefault();focusBox(i+1)}
    else if(e.key==='Enter'&&i===lastBox)redeemCode();
  });
  // 手机输入法常常拿不到按键 (keydown 里是 Unidentified), 走 input 事件: 只留下刚输入的那个数字;
  // 输入的不是数字时恢复原来的数字, 删除操作则照常清空
  let before='';
  el.addEventListener('beforeinput',()=>{before=el.value});
  el.addEventListener('input',e=>{
    if((e.inputType||'').startsWith('delete')){el.value='';return}
    const d=((e.data||el.value).match(/\d/g)||[]).pop();
    if(!d){el.value=before;el.select();return}
    el.value=d;focusBox(Math.min(i+1,lastBox));
  });
  el.addEventListener('paste',e=>{e.preventDefault();const t=(e.clipboardData?.getData('text')||'').replace(/\D/g,'').slice(0,4);t.split('').forEach((c,j)=>{if(codeInputs[j])codeInputs[j].value=c});if(t)focusBox(Math.min(t.length,lastBox));if(t.length===4)redeemCode()});
});
$('#redeemBtn').onclick=redeemCode;

// ---- 上传 / 下载切换 (记住上次用的是哪个) ----
const modeTabs=[...document.querySelectorAll('#modeSwitch [role=tab]')];
function setMode(mode,{focus=false}={}){
  for(const el of [$('#modeSwitch'),$('.mode-stage'),$('#mainCard')])el.dataset.mode=mode;
  modeTabs.forEach(b=>{const on=b.dataset.mode===mode;b.setAttribute('aria-selected',on);b.tabIndex=on?0:-1});
  $('#panelUpload').inert=mode!=='upload';$('#panelDownload').inert=mode!=='download';
  try{localStorage.setItem('shareweb.mode',mode)}catch(e){}
  // 切到下载时把光标放进第一个空格子 (只在电脑上; 手机上自动弹出键盘反而打扰)
  if(focus&&mode==='download'&&matchMedia('(hover: hover) and (pointer: fine)').matches)focusBox(Math.max(0,codeInputs.findIndex(x=>!x.value)))
}
modeTabs.forEach(b=>{
  b.onclick=()=>setMode(b.dataset.mode,{focus:true});
  b.onkeydown=e=>{if(e.key!=='ArrowLeft'&&e.key!=='ArrowRight')return;e.preventDefault();const next=modeTabs[e.key==='ArrowRight'?1:0];setMode(next.dataset.mode);next.focus()};
});
setMode((()=>{try{return localStorage.getItem('shareweb.mode')}catch(e){return null}})()==='download'?'download':'upload');
requestAnimationFrame(()=>requestAnimationFrame(()=>$('#mainCard').classList.remove('mode-init')));
// 在下载页拖文件进来: 切回上传, 让文件能放到上传区
document.addEventListener('dragenter',e=>{if([...(e.dataTransfer?.types||[])].includes('Files'))setMode('upload')});
pick.onclick=()=>input.click();input.onchange=()=>{upload(input.files[0]);input.value=''};drop.ondragover=e=>{e.preventDefault();drop.classList.add('drag')};drop.ondragleave=()=>drop.classList.remove('drag');drop.ondrop=e=>{e.preventDefault();drop.classList.remove('drag');upload(e.dataTransfer.files[0])};document.addEventListener('paste',onPaste);textBtn.onclick=async()=>{const text=paste.value;if(!text.trim())return;const res=await fetch('/api/text',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})});const data=await res.json();if(!res.ok){alert(data.detail||t('text.failed'));return}data.type='text';await showResult(data);paste.value=''};// 清除按钮两步确认: 第一次点击变成高亮的「确认」, 再点才执行; 点击其他地方 / Esc / 焦点移走 / 3 秒无操作即取消 (鼠标停在按钮上时暂停计时)。
let armedBtn=null,armTimer=0;const ARM_TIMEOUT=3000;
// 只有真正有鼠标悬停的设备才在悬停时暂停计时 (触屏点按后 :hover 会一直粘着)
const canHover=matchMedia('(hover: hover) and (pointer: fine)').matches;
function playAnim(b,cls){b.classList.remove('anim-arm','anim-disarm');void b.offsetWidth;b.classList.add(cls)}
function startArmTimer(){clearTimeout(armTimer);armTimer=setTimeout(disarm,ARM_TIMEOUT)}
function disarm(){clearTimeout(armTimer);if(!armedBtn)return;const b=armedBtn;armedBtn=null;delete b.dataset.armed;b.classList.remove('armed');b.style.minWidth='';setKey(b,b.dataset.label);b.removeAttribute('data-i18n-title');b.title='';playAnim(b,'anim-disarm');updateHistoryButtons()}
function arm(b,tipKey,n){disarm();b.style.minWidth=b.getBoundingClientRect().width+'px';armedBtn=b;b.dataset.armed='1';b.classList.add('armed');setKey(b,'history.confirm');b.removeAttribute('data-i18n-title');b.title=t(tipKey,{n});playAnim(b,'anim-arm');if(!(canHover&&b.matches(':hover')))startArmTimer()}
async function clearKeys(keys){const db=await openDB();await txDone(db,tx=>{const st=tx.objectStore('items');if(keys)keys.forEach(k=>st.delete(k));else st.clear()})}
$('#clearHistory').dataset.label='index.clear';$('#clearGone').dataset.label='index.clearGone';
$('#clearHistory').onclick=async e=>{const b=e.currentTarget;if(!historyCount)return;if(!b.dataset.armed){arm(b,'history.confirmAllTip',historyCount);return}disarm();await clearKeys(null);renderHistory()};
$('#clearGone').onclick=async e=>{const b=e.currentTarget;const keys=[...historyGone.values()];if(!keys.length)return;if(!b.dataset.armed){arm(b,'history.confirmGoneTip',keys.length);return}disarm();await clearKeys(keys);renderHistory()};
document.addEventListener('click',e=>{if(armedBtn&&!armedBtn.contains(e.target))disarm()},true);
document.addEventListener('keydown',e=>{if(e.key==='Escape')disarm()});
['clearHistory','clearGone'].forEach(id=>{const b=$('#'+id);if(!canHover)return;b.addEventListener('mouseenter',()=>{if(armedBtn===b)clearTimeout(armTimer)});b.addEventListener('mouseleave',()=>{if(armedBtn===b)startArmTimer()})});
['clearHistory','clearGone'].forEach(id=>$('#'+id).addEventListener('blur',()=>{if(armedBtn&&armedBtn.id===id)setTimeout(()=>{if(armedBtn&&document.activeElement!==armedBtn)disarm()},0)}));
renderHistory();

// 单文件上限由管理后台设置, 页脚与上传预检都以服务器当前值为准
let uploadLimit=null;
// 上限展示为整数 GB/MB (1 GB 而不是 1.00 GB)
const fmtLimit=n=>n%1024**3===0?n/1024**3+' GB':n%1024**2===0?n/1024**2+' MB':fmtSize(n);
fetch('/api/config').then(r=>r.json()).then(c=>{uploadLimit=c.max_upload_bytes||null;const el=document.querySelector('[data-i18n="index.footer"]');if(!el)return;const days=c.retention_days||30;if(uploadLimit)setKey(el,'index.footer',{days,size:fmtLimit(uploadLimit)});else setKey(el,'index.footerNoLimit',{days})}).catch(()=>{});

// ---- 粘贴: 焦点不在输入框时接收剪贴板内容 ----
// 文件 / 图片 (截图、复制的图片、在资源管理器或访达里复制的文件) 直接上传, 与拖放相同;
// 文字放进文字框并聚焦, 由用户确认后再生成分享 (避免误粘贴就生成公开链接)。
function isEditable(el){return !!el&&(el.isContentEditable||/^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName))}
// 截图等直接粘贴的图片没有像样的文件名 (Chrome 里叫 image.png), 按粘贴时间命名
const GENERIC_NAME=/^(image|blob|untitled)?(\.\w+)?$/i;
function pasteName(type){const d=new Date(),p=n=>String(n).padStart(2,'0');const ext=((type||'').split('/')[1]||'bin').replace('jpeg','jpg').replace(/[^a-z0-9].*$/i,'');return `paste-${d.getFullYear()}${p(d.getMonth()+1)}${p(d.getDate())}-${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}.${ext}`}
function pastedFile(cd){
  const f=(cd.files&&cd.files[0])||[...(cd.items||[])].find(i=>i.kind==='file')?.getAsFile();
  if(!f)return null;
  return GENERIC_NAME.test(f.name||'')?new File([f],pasteName(f.type),{type:f.type,lastModified:Date.now()}):f;
}
function onPaste(e){
  if(isEditable(e.target)||!e.clipboardData)return;  // 在输入框里粘贴: 交给输入框自己处理
  const cd=e.clipboardData,txt=cd.getData('text/plain'),file=pastedFile(cd);
  // Word / Excel 等复制文字时会同时附带一张同内容的截图, 有文字时以文字为准; 有真实文件名的文件仍按文件上传
  const textWins=txt&&file&&file.name.startsWith('paste-');
  if(file&&!textWins){e.preventDefault();setMode('upload');upload(file);$('#progressWrap').scrollIntoView({block:'nearest',behavior:'smooth'});return}
  if(txt){e.preventDefault();setMode('upload');paste.value=txt;paste.focus();paste.scrollIntoView({block:'center',behavior:'smooth'})}
}
