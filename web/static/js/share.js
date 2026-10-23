I18N.add({
  en: {
    'share.pageTitle': 'Shared content · ShareWeb',
    'share.textName': 'Text content',
    'share.validUntil': 'Valid until {d}',
    'share.textTitle': 'Text share ✓',
    'share.clickSelect': 'Click to select all',
    'share.sha': 'SHA-256 checksum',
    'share.clickToCopy': 'Click to copy',
    'share.copyText': 'Copy all text',
    'share.copiedText': 'Text copied ✓',
    'share.imageTitle': 'Image share ✓',
    'share.copyImage': '📋 Copy image to clipboard',
    'share.copiedImage': 'Image copied ✓',
    'share.noImageClipboard': 'This browser can\'t copy images. Use "Download directly", or long-press / right-click the image to copy it.',
    'share.videoTitle': 'Video share ✓',
    'share.audioTitle': 'Audio share ✓',
    'share.fileTitle': 'File share ✓',
    'share.fileMeta': '{size} · Valid until {d} · Downloaded {n} times',
    'share.download': '⬇️ Download directly',
    'share.mediaFallback': 'This format can\'t be played in the browser (common for <b>.mkv / .avi / .wmv / .flv</b>, or <b>.mov / .mp4</b> encoded with <b>H.265/HEVC</b>).<br>Download it and play it with a local player such as <b>VLC / PotPlayer</b>.',
    'enc.title': '🔒 Encrypted retrieval (anti-blocking)',
    'enc.desc': 'For restricted networks or content inspection. Requires the decryption script from code 0000',
    'enc.textBtn': '📋 Copy encrypted text',
    'enc.copyKey': 'Copy key',
    'enc.howTitle': 'How to restore (no download):',
    'enc.step1': 'On the home page, enter code <b>0000</b> to get the decryption script <code>.bat</code> (just copy the code, no download needed).',
    'enc.step2': 'Save the copied <b>encrypted text as a <code>.txt</code></b> file.',
    'enc.step3': 'Drag the <code>.txt</code> onto the <code>.bat</code> and paste the <b>key</b>. The file is restored and its SHA-256 verified automatically.',
    'enc.generating': 'Generating…',
    'enc.fetching': 'Fetching and encrypting data…',
    'enc.encoding': 'Encoding…',
    'enc.done': 'Done. Copy the encrypted text below, save it as a .txt file, then restore it with the script from code 0000.',
    'enc.generated': 'Generated ✓',
    'enc.failed': 'Generation failed: {msg}',
    'enc.fetchFailed': 'request failed',
    'enc.copyAll': 'Copy all encrypted text',
    'enc.parts': 'The content is large and has been split into {n} parts. Copy them <b>in order</b> and paste them one after another into the same .txt file:',
    'enc.part': 'Part {i} / {n}',
    'enc.copyPart': 'Copy this part',
    'gh.title': '🌐 Download via GitHub',
    'gh.desc': 'Download the real file from a GitHub domain, bypassing "this site is not on the allowlist" blocking',
    'gh.tag': 'Mirror',
    'gh.btn': 'Download via GitHub',
    'gh.open': 'Open download',
    'gh.note': 'This is a short-lived direct link that expires in a few minutes. Click the button again once it expires.',
    'gh.loading': 'Fetching…',
    'gh.preparing': 'Preparing… large files can take a minute or two',
    'gh.renamed': 'GitHub doesn\'t keep non-English characters in large file names, so this file will download as "{name}". Rename it back to "{orig}" afterwards.',
    'gh.unavailable': 'Unavailable, please try again later',
    'gh.done': 'Link ready ✓',
    'gh.failed': 'Failed: {msg}',
  },
  zh: {
    'share.pageTitle': '共享内容 · ShareWeb',
    'share.textName': '文本内容',
    'share.validUntil': '有效至 {d}',
    'share.textTitle': '文字共享 ✓',
    'share.clickSelect': '点击可全选',
    'share.sha': 'SHA-256 校验码',
    'share.clickToCopy': '点击复制',
    'share.copyText': '复制全部文字',
    'share.copiedText': '已复制文字 ✓',
    'share.imageTitle': '图片共享 ✓',
    'share.copyImage': '📋 复制图片到剪贴板',
    'share.copiedImage': '已复制图片 ✓',
    'share.noImageClipboard': '此浏览器不支持复制图片，请用“直接下载”，或长按/右键复制。',
    'share.videoTitle': '视频共享 ✓',
    'share.audioTitle': '音频共享 ✓',
    'share.fileTitle': '文件共享 ✓',
    'share.fileMeta': '{size} · 有效至 {d} · 已下载 {n} 次',
    'share.download': '⬇️ 直接下载',
    'share.mediaFallback': '此格式无法在浏览器直接在线播放（常见于 <b>.mkv / .avi / .wmv / .flv</b>，或 <b>H.265/HEVC</b> 编码的 <b>.mov / .mp4</b>）。<br>请用下面的<b>下载</b>模块保存后，用本地播放器（如 <b>VLC / PotPlayer</b>）观看。',
    'enc.title': '🔒 加密获取（防拦截）',
    'enc.desc': '用于受限网络 / 内容检测环境，需配合 0000 页的解密脚本',
    'enc.textBtn': '📋 复制加密文本',
    'enc.copyKey': '复制密钥',
    'enc.howTitle': '如何还原（免下载）：',
    'enc.step1': '回到首页用提取码 <b>0000</b> 拿到解密脚本 <code>.bat</code>（脚本代码复制即可，无需下载）。',
    'enc.step2': '把复制到的<b>加密文本另存为一个 <code>.txt</code></b> 文件。',
    'enc.step3': '把 <code>.txt</code> 拖到 <code>.bat</code> 上，粘贴<b>密钥</b>，自动还原并校验 SHA-256。',
    'enc.generating': '正在生成…',
    'enc.fetching': '正在获取并加密数据…',
    'enc.encoding': '正在编码…',
    'enc.done': '完成。请复制下面的加密文本，另存为 .txt 后用 0000 页脚本还原。',
    'enc.generated': '已生成 ✓',
    'enc.failed': '生成失败：{msg}',
    'enc.fetchFailed': '获取失败',
    'enc.copyAll': '复制全部加密文本',
    'enc.parts': '内容较大，分为 {n} 块，请<b>按顺序</b>复制并依次粘贴到同一个 .txt 文件中：',
    'enc.part': '第 {i} / {n} 块',
    'enc.copyPart': '复制此块',
    'gh.title': '🌐 通过 GitHub 下载',
    'gh.desc': '从 GitHub 域名下载真实文件，绕过「本站域名不在白名单」的拦截',
    'gh.tag': '镜像',
    'gh.btn': '通过 GitHub 下载',
    'gh.open': '打开下载',
    'gh.note': '链接为短时效直链，几分钟后失效；失效后可再次点击上方按钮。',
    'gh.loading': '正在获取…',
    'gh.preparing': '正在准备…大文件可能需要一两分钟',
    'gh.renamed': 'GitHub 不保留大文件名中的中文等字符，下载后的文件名为“{name}”，请自行改回“{orig}”。',
    'gh.unavailable': '暂不可用，请稍后重试',
    'gh.done': '已获取 ✓',
    'gh.failed': '获取失败：{msg}',
  },
});
const t = I18N.t, S = I18N.span, H = I18N.htmlSpan, setKey = I18N.setKey;

// GitHub 没有 emoji, 用官方 mark (octicon mark-github), 颜色跟随按钮文字。
const GITHUB_ICON = '<svg class="btn-icon" viewBox="0 0 16 16" aria-hidden="true"><path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8Z"/></svg>';

const token = decodeURIComponent(location.pathname.split('/').pop());
const box = document.querySelector('#shareState');

// 按钮临时显示 "已复制" 等状态, 2 秒后恢复; 用文案 key 而不是文字, 期间切换语言也能正确显示。
// 同一时间只保留一个「已复制」: 点了另一个时, 上一个立即恢复, 不等超时。
let lastFlash = null;
function takeFlash(el, reset) {
  if (lastFlash && lastFlash.el !== el) lastFlash.reset();
  lastFlash = { el, reset };
}
function flash(btn, key, restoreKey) {
  const reset = () => { clearTimeout(btn._flash); setKey(btn, restoreKey); if (lastFlash && lastFlash.el === btn) lastFlash = null; };
  takeFlash(btn, reset);
  setKey(btn, key);
  clearTimeout(btn._flash);
  btn._flash = setTimeout(reset, 2000);
}
// SHA-256: 与首页上传结果同款 —— 标题行 (左标题 / 右「点击复制」) + 透明的校验码, 点击即复制
function shaBlock(sha) {
  return `<div class="copy-block share-sha"><div class="copy-head"><span class="copy-label">${S('share.sha')}</span><span class="copy-hint" data-i18n="share.clickToCopy">${esc(t('share.clickToCopy'))}</span></div><button type="button" class="copy-sha" id="copyShaBtn">${esc(sha || '-')}</button></div>`;
}
function bindSha(sha) {
  const el = document.querySelector('#copyShaBtn');
  const hint = el.closest('.copy-block').querySelector('.copy-hint');
  el.onclick = async () => {
    const reset = () => { clearTimeout(el._flash); el.classList.remove('copied'); setKey(hint, 'share.clickToCopy'); hint.classList.remove('done'); if (lastFlash && lastFlash.el === el) lastFlash = null; };
    takeFlash(el, reset);
    await copy(sha || '');
    el.classList.add('copied'); setKey(hint, 'common.copied'); hint.classList.add('done');
    clearTimeout(el._flash);
    el._flash = setTimeout(reset, 2000);
  };
}
function abToB64(buf) {
  const bytes = new Uint8Array(buf);
  let binary = '';
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) {
    binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunk));
  }
  return btoa(binary);
}
function splitString(str, size) {
  if (str.length <= size) return [str];
  const out = [];
  for (let i = 0; i < str.length; i += size) out.push(str.slice(i, i + size));
  return out;
}
setKey(box, 'common.loading');

fetch('/api/share/' + encodeURIComponent(token))
  .then(async r => { if (!r.ok) throw new Error('not_found'); return r.json(); })
  .then(d => {
    // 文本分享没有文件名时, 历史记录里存当前语言的 "文本内容"。
    const filename = d.filename || (d.type === 'text' ? t('share.textName') : 'download.bin');
    const isImage = d.type === 'file' && (d.mime_type || '').toLowerCase().startsWith('image/');
    addHistory({ token: d.token, name: filename, filename, type: d.type || 'file', size: d.size || 0, role: 'receiver' });
    setKey(box, null);
    // 有效期作为 {date} 变量, 切换语言时按新语言重新格式化; 没有则显示 "永久有效"。
    const exp = { date: d.expires_at || '' };
    if (d.type === 'text') { renderText(d, exp); return; }
    if (isImage) { renderImage(d, filename, exp); return; }
    renderFile(d, filename, exp);
  })
  .catch(() => renderExpired());

// 「通过 GitHub 下载」区块: 文件页与图片页共用; 未开启镜像 (或文件太大) 时不显示
function githubBlock(d) {
  if (!d.github) return '';
  return `
      <div class="enc-box">
        <div class="enc-head">
          <div>
            <h3 style="margin:0">${S('gh.title')}</h3>
            <span class="meta">${S('gh.desc')}</span>
          </div>
          <span class="tag">${S('gh.tag')}</span>
        </div>
        <button class="primary wide" id="ghBtn">${GITHUB_ICON}<span id="ghBtnLabel" data-i18n="gh.btn">${esc(t('gh.btn'))}</span></button>
        <div id="ghMsg" class="meta" style="margin-top:8px"></div>
        <div id="ghLinkWrap" class="hidden" style="margin-top:8px">
          <div id="ghRenamed" class="note hidden" style="margin:0 0 8px"></div>
          <div class="history-url"><input class="input" id="ghLink" readonly><a class="primary" id="ghOpen" target="_blank" rel="noopener" data-i18n="gh.open">${esc(t('gh.open'))}</a></div>
          <div class="meta" style="margin-top:6px">${S('gh.note')}</div>
        </div>
      </div>`;
}
function bindGithub(d, filename) {
  if (!d.github) return;
  const ghBtn = document.querySelector('#ghBtn');
  const ghLabel = document.querySelector('#ghBtnLabel');  // 只改文字, 保留 GitHub 图标
  ghBtn.onclick = async () => {
    const msg = document.querySelector('#ghMsg');
    ghBtn.disabled = true; setKey(ghLabel, 'gh.loading'); setKey(msg, null);
    // 大文件首次获取要先传到 GitHub, 超过 3 秒提示一下。
    const slow = setTimeout(() => setKey(ghLabel, 'gh.preparing'), 3000);
    try {
      const r = await fetch(`/api/share/${encodeURIComponent(token)}/github`);
      const j = await r.json();
      if (!r.ok || !j.url) throw new Error(j.detail || t('gh.unavailable'));
      const wrap = document.querySelector('#ghLinkWrap');
      document.querySelector('#ghLink').value = j.url;
      const open = document.querySelector('#ghOpen');
      open.href = j.url;
      const renamed = document.querySelector('#ghRenamed');
      if (j.filename && j.filename !== filename) {
        setKey(renamed, 'gh.renamed', { name: j.filename, orig: filename });
        renamed.classList.remove('hidden');
      } else {
        renamed.classList.add('hidden');
      }
      wrap.classList.remove('hidden');
      window.open(j.url, '_blank', 'noopener');
      clearTimeout(slow);
      setKey(ghLabel, 'gh.done'); ghBtn.disabled = false;
    } catch (e) {
      clearTimeout(slow);
      setKey(msg, 'gh.failed', { msg: e.message });
      ghBtn.disabled = false; setKey(ghLabel, 'gh.btn');
    }
  };
}

function renderExpired() {
  box.className = 'center';
  box.innerHTML = `
    <div style="padding:20px 0;">
      <div class="drop-icon">⏳</div>
      <h2 class="danger" style="margin-top:10px">${S('expired.title')}</h2>
      <p class="muted">${S('expired.desc')}</p>
      <a class="primary accent button" style="margin-top:12px;" href="/">${S('common.home')}</a>
    </div>`;
}

function renderText(d, exp) {
  box.className = '';
  box.innerHTML = `
    <div class="result-box" style="margin-top:0;">
      <h2>${S('share.textTitle')}</h2>
      <p><span class="meta">${S('share.validUntil', { d: exp })}</span></p>
      <div id="textContent" class="text-content" data-i18n-title="share.clickSelect" title="${esc(t('share.clickSelect'))}">${esc(d.text || '')}</div>
      ${shaBlock(d.sha256)}
      <button class="primary accent wide" id="copyTextBtn" data-i18n="share.copyText">${esc(t('share.copyText'))}</button>
    </div>`;
  bindSha(d.sha256);
  document.querySelector('#copyTextBtn').onclick = e => { copy(d.text || ''); flash(e.currentTarget, 'share.copiedText', 'share.copyText'); };
  const tBox = document.querySelector('#textContent');
  tBox.onclick = () => { const sel = window.getSelection(), rg = document.createRange(); rg.selectNodeContents(tBox); sel.removeAllRanges(); sel.addRange(rg); };
}

function renderImage(d, filename, exp) {
  box.className = '';
  const url = `/download/${encodeURIComponent(token)}`;
  box.innerHTML = `
    <div class="result-box" style="margin-top:0;">
      <h2 class="result-title">${S('share.imageTitle')}</h2>
      <p>
        <strong style="font-size:18px;word-break:break-all;">${esc(filename)}</strong><br>
        <span class="meta">${S('share.fileMeta', { size: fmtSize(d.size), d: exp, n: d.download_count ?? 0 })}</span>
      </p>
      <img src="${url}?inline=1" alt="${esc(filename)}" style="max-width:100%;border-radius:12px;border:1px solid var(--card-border);display:block;margin:10px 0">
      ${shaBlock(d.sha256)}
      <a class="primary accent wide button" id="dlBtn" href="${url}" download="${esc(filename)}" data-i18n="share.download">${esc(t('share.download'))}</a>
      <button class="primary wide" id="copyImgBtn" data-i18n="share.copyImage">${esc(t('share.copyImage'))}</button>
      <div id="imgMsg" class="meta" style="margin-top:8px"></div>
      ${githubBlock(d)}
    </div>`;
  bindSha(d.sha256);
  bindGithub(d, filename);
  document.querySelector('#copyImgBtn').onclick = async e => {
    const btn = e.currentTarget;
    try {
      const blob = await (await fetch(`${url}?inline=1`)).blob();
      let out = blob;
      // clipboard 对 PNG 支持最好；非 PNG 尝试转 PNG
      if (blob.type !== 'image/png' && window.createImageBitmap && document.createElement('canvas').getContext) {
        try {
          const bmp = await createImageBitmap(blob);
          const c = document.createElement('canvas'); c.width = bmp.width; c.height = bmp.height;
          c.getContext('2d').drawImage(bmp, 0, 0);
          out = await new Promise(res => c.toBlob(res, 'image/png'));
        } catch (e) {}
      }
      await navigator.clipboard.write([new ClipboardItem({ [out.type]: out })]);
      flash(btn, 'share.copiedImage', 'share.copyImage');
    } catch (e) {
      setKey(document.querySelector('#imgMsg'), 'share.noImageClipboard');
    }
  };
}

function renderFile(d, filename, exp) {
  box.className = '';
  const downloadUrl = `/download/${encodeURIComponent(token)}`;
  const encUrl = downloadUrl + '?enc=1';
  const mime = (d.mime_type || '').toLowerCase();
  const ext = (filename.split('.').pop() || '').toLowerCase();
  const VIDEO_EXT = ['mp4', 'mov', 'm4v', 'webm', 'ogv'];
  const AUDIO_EXT = ['mp3', 'wav', 'aac', 'flac', 'oga', 'm4a', 'ogg'];
  const isVideo = mime.startsWith('video/') || VIDEO_EXT.includes(ext);
  const isAudio = !isVideo && (mime.startsWith('audio/') || AUDIO_EXT.includes(ext));
  // 不用 <source type=...> 过滤：直接给 src，让浏览器按实际内容尝试解码
  // (否则 .mov=video/quicktime 等会被 Chrome 依据 type 字符串直接判为不支持而根本不尝试)。
  const playerHtml = isVideo
    ? `<video id="mediaEl" controls preload="metadata" playsinline style="width:100%;max-height:70vh;border-radius:12px;background:#000;margin:8px 0"></video><div id="mediaFallback" class="note hidden"></div>`
    : isAudio
    ? `<audio id="mediaEl" controls preload="metadata" style="width:100%;margin:8px 0"></audio><div id="mediaFallback" class="note hidden"></div>`
    : '';
  box.innerHTML = `
    <div class="result-box" style="margin-top:0;">
      <h2 class="result-title">${S(isVideo ? 'share.videoTitle' : isAudio ? 'share.audioTitle' : 'share.fileTitle')}</h2>
      <p>
        <strong style="font-size:18px;word-break:break-all;">${esc(filename)}</strong><br>
        <span class="meta">${S('share.fileMeta', { size: fmtSize(d.size), d: exp, n: d.download_count ?? 0 })}</span>
      </p>
      ${playerHtml}
      ${shaBlock(d.sha256)}
      <a class="primary accent wide button" id="dlBtn" href="${downloadUrl}" download="${esc(filename)}" data-i18n="share.download">${esc(t('share.download'))}</a>

      <div class="enc-box">
        <div class="enc-head">
          <div>
            <h3 style="margin:0">${S('enc.title')}</h3>
            <span class="meta">${S('enc.desc')}</span>
          </div>
          <span class="tag">AES-256</span>
        </div>
        <button class="primary accent wide" id="encTextBtn" data-i18n="enc.textBtn">${esc(t('enc.textBtn'))}</button>
        <div id="keyReveal" class="hidden">
          <div class="keyfield">
            <input class="input" id="keyBox" readonly value="${esc(d.enc_key || '')}">
            <button class="primary" id="copyKeyBtn" style="white-space:nowrap" data-i18n="enc.copyKey">${esc(t('enc.copyKey'))}</button>
          </div>
          <div class="note">
            <b>${S('enc.howTitle')}</b>
            <ol class="steps" style="margin:6px 0 0">
              <li>${H('enc.step1')}</li>
              <li>${H('enc.step2')}</li>
              <li>${H('enc.step3')}</li>
            </ol>
          </div>
        </div>
        <div id="encTextWrap" class="hidden" style="margin-top:12px"></div>
        <div id="encProgress" class="hidden" style="margin-top:10px">
          <div class="progress"><span id="encBar"></span></div>
          <div class="meta" id="encMsg" style="margin-top:6px"></div>
        </div>
      </div>

      ${githubBlock(d)}
    </div>`;

  bindSha(d.sha256);

  const mediaEl = document.querySelector('#mediaEl');
  if (mediaEl) {
    mediaEl.src = downloadUrl + '?inline=1';
    mediaEl.addEventListener('error', () => {
      const fb = document.querySelector('#mediaFallback');
      mediaEl.style.display = 'none';
      if (fb) {
        fb.classList.remove('hidden');
        setKey(fb, 'share.mediaFallback', null, true);
      }
    }, true);
  }

  bindGithub(d, filename);
  document.querySelector('#copyKeyBtn').onclick = e => { copy(d.enc_key || ''); flash(e.currentTarget, 'common.copied', 'enc.copyKey'); };

  document.querySelector('#encTextBtn').onclick = async () => {
    const btn = document.querySelector('#encTextBtn');
    const prog = document.querySelector('#encProgress');
    const bar = document.querySelector('#encBar');
    const msg = document.querySelector('#encMsg');
    const wrap = document.querySelector('#encTextWrap');
    btn.disabled = true; setKey(btn, 'enc.generating');
    prog.classList.remove('hidden'); bar.style.width = '10%'; setKey(msg, 'enc.fetching');
    try {
      const resp = await fetch(encUrl);
      if (!resp.ok) throw new Error(t('enc.fetchFailed'));
      const buf = await resp.arrayBuffer();
      bar.style.width = '70%'; setKey(msg, 'enc.encoding');
      const b64 = abToB64(buf);
      bar.style.width = '100%'; setKey(msg, 'enc.done');
      document.querySelector('#keyReveal').classList.remove('hidden');
      renderEncText(wrap, b64);
      setKey(btn, 'enc.generated');
    } catch (e) {
      setKey(msg, 'enc.failed', { msg: e.message });
      btn.disabled = false; setKey(btn, 'enc.textBtn');
    }
  };
}

function renderEncText(wrap, b64) {
  wrap.classList.remove('hidden');
  const LIMIT = 8 * 1024 * 1024; // 单块上限，超过则分块
  if (b64.length <= LIMIT) {
    wrap.innerHTML = `
      <textarea class="textpaste" id="encArea" readonly style="height:150px;font-family:ui-monospace,Consolas,monospace;font-size:12px"></textarea>
      <button class="primary accent wide" id="copyEncBtn" data-i18n="enc.copyAll">${esc(t('enc.copyAll'))}</button>`;
    document.querySelector('#encArea').value = b64;
    document.querySelector('#copyEncBtn').onclick = async e => { const btn = e.currentTarget; await copy(b64); flash(btn, 'common.copied', 'enc.copyAll'); };
  } else {
    const parts = splitString(b64, LIMIT);
    let html = `<p class="meta">${H('enc.parts', { n: parts.length })}</p>`;
    parts.forEach((_, i) => { html += `<div class="row between" style="margin:6px 0"><span class="meta">${S('enc.part', { i: i + 1, n: parts.length })}</span><button class="primary" data-i="${i}" data-i18n="enc.copyPart">${esc(t('enc.copyPart'))}</button></div>`; });
    wrap.innerHTML = html;
    wrap.querySelectorAll('button[data-i]').forEach(b => {
      b.onclick = async () => { await copy(parts[Number(b.dataset.i)]); flash(b, 'common.copied', 'enc.copyPart'); };
    });
  }
}
