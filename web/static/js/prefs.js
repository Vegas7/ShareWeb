// 语言 / 主题偏好。在 <head> 中同步加载: 先设置 lang 与 data-theme, 避免首屏闪烁。
// 页面脚本用 I18N.add({en:{...}, zh:{...}}) 注册自己的文案, I18N.t(key, vars) 取文案。
// 切换语言时不重新渲染页面, 而是就地替换带标记元素的文字 (页面状态如加密文本、播放进度都保留):
//   data-i18n="key"          textContent        data-i18n-html="key"   innerHTML (仅用于自有文案)
//   data-i18n-args='{...}'   上面两者的插值变量  data-i18n-placeholder / data-i18n-title
//   data-i18n-date="ISO"     按当前语言格式化的日期
// 变量值可以是普通值, {date: ISO} (按语言格式化, 空则显示"永久有效"), 或 {key: 'x'} (另一条文案)。
// 动态内容用 I18N.span / I18N.htmlSpan / I18N.dateSpan 生成, 运行中改文字用 I18N.setKey。
// 文件末尾另有各页面共用的小工具 (esc / fmtSize / copy / 本地历史)。
(function () {
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} },
  };
  const root = document.documentElement;
  const dict = { en: {}, zh: {} };
  let lang = store.get('sw-lang') === 'zh' ? 'zh' : 'en';  // 默认英文

  const savedTheme = store.get('sw-theme');
  if (savedTheme === 'light' || savedTheme === 'dark') root.dataset.theme = savedTheme;
  root.lang = lang === 'zh' ? 'zh-CN' : 'en';

  function fmtArg(v) {
    if (v && typeof v === 'object') {
      if ('date' in v) return v.date ? new Date(v.date).toLocaleString(locale()) : t('common.forever');
      if ('key' in v) return t(v.key);
    }
    return v;
  }

  function t(key, vars) {
    let s = dict[lang][key] ?? dict.en[key] ?? key;
    if (vars) s = s.replace(/\{(\w+)\}/g, (m, k) => (k in vars ? fmtArg(vars[k]) : m));
    return s;
  }

  function argsAttr(vars) {
    return vars ? ` data-i18n-args="${esc(JSON.stringify(vars))}"` : '';
  }

  function argsOf(el) {
    try { return el.dataset.i18nArgs ? JSON.parse(el.dataset.i18nArgs) : undefined; } catch (e) { return undefined; }
  }

  // 生成带标记的 <span>, 嵌进页面模板里; 切换语言时由 apply() 就地更新。
  function span(key, vars) { return `<span data-i18n="${key}"${argsAttr(vars)}>${esc(t(key, vars))}</span>`; }
  function htmlSpan(key, vars) { return `<span data-i18n-html="${key}"${argsAttr(vars)}>${t(key, vars)}</span>`; }
  function dateSpan(iso) { return `<span data-i18n-date="${esc(iso || '')}">${esc(fmtArg({ date: iso }))}</span>`; }

  // 运行中修改某个元素的文案 (进度、按钮状态等); key 为 null 时清空并去掉标记。
  function setKey(el, key, vars, html) {
    if (!el) return;
    el.removeAttribute('data-i18n'); el.removeAttribute('data-i18n-html'); el.removeAttribute('data-i18n-args');
    if (!key) { el.textContent = ''; return; }
    el.setAttribute(html ? 'data-i18n-html' : 'data-i18n', key);
    if (vars) el.setAttribute('data-i18n-args', JSON.stringify(vars));
    if (html) el.innerHTML = t(key, vars); else el.textContent = t(key, vars);
  }

  function add(more) {
    for (const l of ['en', 'zh']) Object.assign(dict[l], more[l] || {});
  }

  function locale() { return lang === 'zh' ? 'zh-CN' : 'en-US'; }

  function effectiveTheme() {
    return root.dataset.theme || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  }

  const SUN = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6"/></svg>';
  const MOON = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" aria-hidden="true"><path d="M20.5 14.6A8.5 8.5 0 0 1 9.4 3.5a8.5 8.5 0 1 0 11.1 11.1Z"/></svg>';
  // 「文A」翻译图标 (Material Icons "translate")。图标不随语言变化, 目标语言写在 title / aria-label 里。
  const TRANSLATE = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true"><path d="M12.87 15.07l-2.54-2.51.03-.03c1.74-1.94 2.98-4.17 3.71-6.53H17V4h-7V2H8v2H1v1.99h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.02L4 19l5-5 3.11 3.11.76-2.04zM18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2l-4.5-12zm-2.62 7l1.62-4.33L19.12 17h-3.24z"/></svg>';

  function renderToggles() {
    document.querySelectorAll('[data-prefs]').forEach(slot => {
      if (!slot.firstChild) {
        slot.innerHTML = '<button type="button" class="pref-btn" data-pref="lang">' + TRANSLATE + '</button>'
          + '<button type="button" class="pref-btn" data-pref="theme"></button>';
      }
      const lb = slot.querySelector('[data-pref="lang"]');
      lb.title = t('prefs.lang');
      lb.setAttribute('aria-label', t('prefs.lang'));
      const tb = slot.querySelector('[data-pref="theme"]');
      const dark = effectiveTheme() === 'dark';
      tb.innerHTML = dark ? SUN : MOON;
      tb.title = t(dark ? 'prefs.toLight' : 'prefs.toDark');
      tb.setAttribute('aria-label', tb.title);
    });
  }

  function apply() {
    document.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = t(el.dataset.i18n, argsOf(el)); });
    document.querySelectorAll('[data-i18n-html]').forEach(el => { el.innerHTML = t(el.dataset.i18nHtml, argsOf(el)); });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => { el.placeholder = t(el.dataset.i18nPlaceholder); });
    document.querySelectorAll('[data-i18n-title]').forEach(el => { el.title = t(el.dataset.i18nTitle); });
    document.querySelectorAll('[data-i18n-date]').forEach(el => { el.textContent = fmtArg({ date: el.dataset.i18nDate }); });
    renderToggles();
  }

  function setLang(l) {
    lang = l === 'zh' ? 'zh' : 'en';
    store.set('sw-lang', lang);
    root.lang = lang === 'zh' ? 'zh-CN' : 'en';
    apply();
    document.dispatchEvent(new CustomEvent('langchange', { detail: { lang } }));
  }

  function toggleTheme() {
    const next = effectiveTheme() === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    store.set('sw-theme', next);
    renderToggles();
  }

  document.addEventListener('click', e => {
    const btn = e.target.closest('[data-pref]');
    if (!btn) return;
    if (btn.dataset.pref === 'lang') setLang(lang === 'en' ? 'zh' : 'en');
    else toggleTheme();
  });
  matchMedia('(prefers-color-scheme: dark)').addEventListener?.('change', renderToggles);
  document.addEventListener('DOMContentLoaded', apply);

  // 各页面通用文案; expired.html 没有自己的脚本, 文案也放这里。
  add({
    en: {
      'prefs.lang': 'Switch to Chinese',
      'prefs.toLight': 'Switch to light theme',
      'prefs.toDark': 'Switch to dark theme',
      'common.loading': 'Loading…',
      'common.copied': 'Copied ✓',
      'common.home': 'Back to home',
      'common.backHome': '← Back to home',
      'common.forever': 'Never expires',
      'brand.tagline': 'File Station',
      'nav.home': 'Home',
      'expired.pageTitle': 'Share expired · ShareWeb',
      'expired.title': 'Share expired',
      'expired.desc': 'This link does not exist, has expired, or the file has been cleaned up.',
    },
    zh: {
      'prefs.lang': '切换到英文',
      'prefs.toLight': '切换到亮色主题',
      'prefs.toDark': '切换到暗色主题',
      'common.loading': '加载中…',
      'common.copied': '已复制 ✓',
      'common.home': '返回首页',
      'common.backHome': '← 返回首页',
      'common.forever': '永久有效',
      'brand.tagline': '文件中转站',
      'nav.home': '首页',
      'expired.pageTitle': '共享已失效 · ShareWeb',
      'expired.title': '共享已失效',
      'expired.desc': '该链接不存在、已过期或文件已被自动清理。',
    },
  });

  window.I18N = {
    t, add, apply, setLang, span, htmlSpan, dateSpan, setKey,
    get lang() { return lang; },
    get locale() { return locale(); },
    date(d) { return new Date(d).toLocaleString(locale()); },
    time(d) { return new Date(d).toLocaleTimeString(locale()); },
  };
})();

// ---- 各页面共用的小工具 ----
function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]));
}

function fmtSize(bytes) {
  const n = Number(bytes) || 0;
  if (n < 1024) return n + ' B';
  if (n < 1024 ** 2) return (n / 1024).toFixed(1) + ' KB';
  if (n < 1024 ** 3) return (n / 1024 ** 2).toFixed(1) + ' MB';
  if (n < 1024 ** 4) return (n / 1024 ** 3).toFixed(2) + ' GB';
  return (n / 1024 ** 4).toFixed(2) + ' TB';
}

// 复制到剪贴板; 剪贴板 API 不可用时退回到 execCommand。返回是否成功。
async function copy(text) {
  try { await navigator.clipboard.writeText(text); return true; } catch (e) {}
  try {
    const a = document.createElement('textarea');
    a.value = text; a.setAttribute('readonly', ''); a.style.position = 'fixed'; a.style.opacity = '0';
    document.body.appendChild(a); a.select();
    const ok = document.execCommand('copy');
    a.remove();
    return ok;
  } catch (e) { return false; }
}

// 本地历史 (IndexedDB, 只存在本机浏览器里): 首页记录上传, 提取页记录收到的分享
function openDB() {
  return new Promise((resolve, reject) => {
    const r = indexedDB.open('shareweb', 1);
    r.onupgradeneeded = () => { if (!r.result.objectStoreNames.contains('items')) r.result.createObjectStore('items', { keyPath: 'key' }); };
    r.onsuccess = () => resolve(r.result);
    r.onerror = () => reject(r.error);
  });
}
// 读写事务完成后才 resolve
function txDone(db, fn) {
  return new Promise((resolve, reject) => {
    const tx = db.transaction('items', 'readwrite');
    fn(tx);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}
async function addHistory(item) {
  try {
    const db = await openDB();
    await txDone(db, tx => tx.objectStore('items').put({ ...item, key: item.key || item.token, added_at: item.added_at || new Date().toISOString() }));
  } catch (e) {
    console.warn('saving local history failed:', e);  // 隐私模式等禁用 IndexedDB 时不影响主流程
  }
}
