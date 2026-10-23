I18N.add({
  en: {
    'admin.pageTitle': 'Admin · ShareWeb', 'admin.title': 'Admin', 'admin.subtitle': 'Administrators only', 'admin.logout': 'Log out',
    'admin.loginTitle': 'Admin login', 'admin.pwPh': 'Admin password', 'admin.login': 'Log in', 'admin.loginFailed': 'Login failed',
    'admin.statShares': 'Active shares', 'admin.statFiles': 'Files', 'admin.statBytes': 'Storage used', 'admin.statBlacklist': 'Blacklist',
    'admin.statUploads': 'Uploads today', 'admin.statDownloads': 'Downloads today', 'admin.cleanupDesc': 'Only stored file shares are deleted, and this cannot be undone. Text shares and locked files are not affected.',
    'admin.cleanup7': 'Delete files older than 7 days', 'admin.cleanup14': 'Delete files older than 14 days', 'admin.cleanupAll': 'Delete all files',
    'admin.confirmAll': 'Delete all stored files? This cannot be undone.', 'admin.confirmDays': 'Delete files created more than {n} days ago?',
    'admin.working': 'Working…', 'admin.cleaned': 'Deleted {n} files, freed {size}.', 'admin.cleanFailed': 'Cleanup failed: {msg}',
    'admin.blAddTitle': 'Add to blacklist', 'admin.ipPh': 'IP address', 'admin.reasonPh': 'Reason', 'admin.blAdd': 'Add',
    'admin.requestFailed': 'Request failed',
    'admin.filesTitle': 'Files', 'admin.filesSummary': '{n} files · {size}', 'admin.filesEmpty': 'No stored files',
    'admin.filesLoadFailed': 'Failed to load files: {msg}', 'admin.selectAll': 'Select all', 'admin.selected': '{n} selected',
    'admin.deleteSelected': 'Delete selected', 'admin.confirmSelected': 'Delete the {n} selected files? This cannot be undone.',
    'admin.fileUploaded': 'Uploaded {d}', 'admin.fileExpires': 'expires {d}', 'admin.fileDownloads': '{n} downloads', 'admin.fileCode': 'code {c}',
    'admin.tagExpired': 'Expired', 'admin.tagGithub': 'GitHub',
    'admin.sortBy': 'Sort by', 'admin.sortDate': 'Date', 'admin.sortSize': 'Size', 'admin.sortType': 'Type', 'admin.sortName': 'Name',
    'admin.sortAsc': 'Ascending (click for descending)', 'admin.sortDesc': 'Descending (click for ascending)',
    'admin.lock': 'Lock', 'admin.unlock': 'Unlock', 'admin.tagLocked': '🔒 Locked',
    'admin.fileLockedExpiry': 'never expires (locked; originally {d})',
    'admin.lockedDone': 'Locked {n} files. They won\'t expire or be deleted until unlocked.',
    'admin.unlockedDone': 'Unlocked {n} files. Their original expiry applies again.',
    'admin.lockFailed': 'Failed: {msg}',
    'admin.confirmSelectedSkip': 'Delete the {n} selected files? {m} locked files will be skipped. This cannot be undone.',
    'admin.cleanedSkipped': 'Deleted {n} files, freed {size}. Skipped {m} locked files.',
    'admin.allLocked': 'All selected files are locked. Unlock them first to delete.',
    'admin.visTitle': 'Visitors & blocklist', 'admin.visSummary': '{n} IPs · {b} blocked', 'admin.visEmpty': 'No visitors recorded yet',
    'admin.visEmptyBlocked': 'No blocked IPs', 'admin.visLoadFailed': 'Failed to load visitors: {msg}',
    'admin.visBlock': 'Block', 'admin.visAllow': 'Allow', 'admin.visFilterAll': 'All', 'admin.visFilterBlocked': 'Blocked',
    'admin.visSortLast': 'Last seen', 'admin.visSortHits': 'Requests', 'admin.visSortFirst': 'First seen', 'admin.visSortIp': 'IP', 'admin.visSortCountry': 'Country',
    'admin.visTagBlocked': 'Blocked', 'admin.visTagMe': 'Your IP', 'admin.visHits': '{n} requests',
    'admin.visFirst': 'first {d}', 'admin.visLast': 'last {d}', 'admin.visNeverSeen': 'not seen (added manually)',
    'admin.visReason': 'Reason: {r}', 'admin.visUnknownGeo': 'Unknown location', 'admin.visPrivate': 'Private / local network',
    'admin.visBlocked': 'Blocked {n} IPs.', 'admin.visBlockedSelf': 'Blocked {n} IPs. Skipped your own IP ({ip}) so you don\'t lock yourself out.',
    'admin.visAllowed': 'Allowed {n} IPs.', 'admin.visFailed': 'Failed: {msg}', 'admin.visCredit': 'IP location data',
    'admin.navOverview': 'Overview', 'admin.navFiles': 'Files', 'admin.navSecurity': 'Security', 'admin.navAdvanced': 'Advanced',
    'admin.trendTitle': 'Uploads & downloads', 'admin.trendUploads': 'Uploads', 'admin.trendDownloads': 'Downloads',
    'admin.days7': '7 days', 'admin.days14': '14 days', 'admin.days30': '30 days', 'admin.chartFailed': 'Failed to load chart data: {msg}',
    'admin.typesTitle': 'Storage by type', 'admin.typesSub': 'Active shares, by size', 'admin.typesEmpty': 'No active shares',
    'admin.typeCount': '{n} items', 'admin.tipSize': 'Size', 'admin.tipShare': 'Share', 'admin.tipCount': 'Items',
    'admin.cat.video': 'Video', 'admin.cat.image': 'Images', 'admin.cat.audio': 'Audio', 'admin.cat.archive': 'Archives',
    'admin.cat.document': 'Documents', 'admin.cat.app': 'Apps', 'admin.cat.text': 'Text', 'admin.cat.other': 'Other',
    'admin.diskTitle': 'Disk space', 'admin.diskSub': '{total} disk', 'admin.diskFree': 'free', 'admin.diskShares': 'ShareWeb files',
    'admin.diskOther': 'System & other', 'admin.diskAvail': 'Free', 'admin.diskWarn': 'Getting full', 'admin.diskDanger': 'Almost full',
    'admin.geoTitle': 'Visitors by country', 'admin.geoSub': 'Unique IPs recorded in the visitor log', 'admin.geoEmpty': 'No visitors recorded yet',
    'admin.geoIps': '{n} IPs', 'admin.geoUnknown': 'Unknown', 'admin.geoOther': 'Other countries',
    'admin.limitTitle': 'Max file size', 'admin.limitDesc': 'The largest single file visitors can upload. Takes effect immediately; files already stored are not affected.',
    'admin.limitNone': 'No limit', 'admin.limitCustom': 'Custom', 'admin.save': 'Save',
    'admin.limitCurrent': 'Currently in effect: {v}', 'admin.limitCapacity': 'Free disk space is {free}, so the largest file the server can actually take right now is about {cap} ({reserve} is always kept free).',
    'admin.limitNoneNote': 'With no limit, file size is only bounded by free disk space.',
    'admin.limitOverCap': 'This is more than the disk can currently hold; uploads larger than about {cap} will still fail.',
    'admin.limitInvalid': 'Enter a whole number between 1 MB and 1 TB.', 'admin.limitSaved': 'Saved. New uploads use this limit now.',
    'admin.limitUnchanged': 'No changes to save.',
    'admin.evictTitle': 'Free up space automatically',
    'admin.evictDesc': 'When the disk doesn\'t have room for a file being uploaded, delete the oldest files first until there is enough space. Locked files and text shares are never deleted.',
    'admin.evictConfirm': 'Once on, the oldest files will be permanently deleted whenever the disk runs out of space for an upload. This cannot be undone. Turn it on?',
    'admin.evictPool': 'Files that can be deleted automatically: {n} ({size}).',
    'admin.evictMax': 'With this on, the largest file the server can take is about {cap}.',
    'admin.evictOn': 'Turned on.', 'admin.evictOff': 'Turned off.',
    'admin.limitEvictNote': 'Anything beyond free disk space will be freed by deleting the oldest files during upload (up to about {cap} in total).',
  },
  zh: {
    'admin.pageTitle': '管理后台 · ShareWeb', 'admin.title': '管理后台', 'admin.subtitle': '仅供管理员使用', 'admin.logout': '登出',
    'admin.loginTitle': '管理员登录', 'admin.pwPh': '管理员密码', 'admin.login': '登录', 'admin.loginFailed': '登录失败',
    'admin.statShares': '当前共享', 'admin.statFiles': '文件数量', 'admin.statBytes': '文件占用空间', 'admin.statBlacklist': '黑名单',
    'admin.statUploads': '今日上传', 'admin.statDownloads': '今日下载', 'admin.cleanupDesc': '仅清除已保存的文件共享，操作不可恢复；文本共享和已锁定的文件不受影响。',
    'admin.cleanup7': '清除 7 天前的文件', 'admin.cleanup14': '清除 14 天前的文件', 'admin.cleanupAll': '清除所有文件',
    'admin.confirmAll': '清除所有已保存文件？此操作不可恢复。', 'admin.confirmDays': '清除创建时间超过 {n} 天的文件？',
    'admin.working': '处理中…', 'admin.cleaned': '已清除 {n} 个文件，释放 {size}。', 'admin.cleanFailed': '清除失败：{msg}',
    'admin.blAddTitle': '手动加入黑名单', 'admin.ipPh': 'IP 地址', 'admin.reasonPh': '原因', 'admin.blAdd': '加入',
    'admin.requestFailed': '请求失败',
    'admin.filesTitle': '文件管理', 'admin.filesSummary': '共 {n} 个文件 · {size}', 'admin.filesEmpty': '暂无文件',
    'admin.filesLoadFailed': '文件列表加载失败：{msg}', 'admin.selectAll': '全选', 'admin.selected': '已选 {n} 个',
    'admin.deleteSelected': '删除所选', 'admin.confirmSelected': '删除所选的 {n} 个文件？此操作不可恢复。',
    'admin.fileUploaded': '上传于 {d}', 'admin.fileExpires': '到期 {d}', 'admin.fileDownloads': '下载 {n} 次', 'admin.fileCode': '提取码 {c}',
    'admin.tagExpired': '已过期', 'admin.tagGithub': 'GitHub',
    'admin.sortBy': '排序', 'admin.sortDate': '日期', 'admin.sortSize': '大小', 'admin.sortType': '类型', 'admin.sortName': '名称',
    'admin.sortAsc': '正序（点击切换为倒序）', 'admin.sortDesc': '倒序（点击切换为正序）',
    'admin.lock': '锁定', 'admin.unlock': '解锁', 'admin.tagLocked': '🔒 已锁定',
    'admin.fileLockedExpiry': '不过期（已锁定，原定 {d} 到期）',
    'admin.lockedDone': '已锁定 {n} 个文件，解锁前不会过期或被清除。',
    'admin.unlockedDone': '已解锁 {n} 个文件，恢复原定的到期时间。',
    'admin.lockFailed': '操作失败：{msg}',
    'admin.confirmSelectedSkip': '删除所选的 {n} 个文件？其中 {m} 个已锁定，将被跳过。此操作不可恢复。',
    'admin.cleanedSkipped': '已清除 {n} 个文件，释放 {size}；跳过 {m} 个已锁定的文件。',
    'admin.allLocked': '所选文件均已锁定，请先解锁再删除。',
    'admin.visTitle': '访客与黑名单', 'admin.visSummary': '共 {n} 个 IP · 已封禁 {b} 个', 'admin.visEmpty': '暂无访客记录',
    'admin.visEmptyBlocked': '暂无被封禁的 IP', 'admin.visLoadFailed': '访客列表加载失败：{msg}',
    'admin.visBlock': '封禁', 'admin.visAllow': '解封', 'admin.visFilterAll': '全部', 'admin.visFilterBlocked': '仅封禁',
    'admin.visSortLast': '最近访问', 'admin.visSortHits': '访问次数', 'admin.visSortFirst': '首次访问', 'admin.visSortIp': 'IP', 'admin.visSortCountry': '国家',
    'admin.visTagBlocked': '已封禁', 'admin.visTagMe': '当前 IP', 'admin.visHits': '{n} 次请求',
    'admin.visFirst': '首次 {d}', 'admin.visLast': '最近 {d}', 'admin.visNeverSeen': '未访问过（手动添加）',
    'admin.visReason': '原因：{r}', 'admin.visUnknownGeo': '未知地区', 'admin.visPrivate': '内网 / 本机地址',
    'admin.visBlocked': '已封禁 {n} 个 IP。', 'admin.visBlockedSelf': '已封禁 {n} 个 IP；已跳过你当前的 IP（{ip}），以免把自己挡在外面。',
    'admin.visAllowed': '已解封 {n} 个 IP。', 'admin.visFailed': '操作失败：{msg}', 'admin.visCredit': 'IP 位置数据',
    'admin.navOverview': '总览', 'admin.navFiles': '文件管理', 'admin.navSecurity': '安全设置', 'admin.navAdvanced': '高级设置',
    'admin.trendTitle': '上传与下载', 'admin.trendUploads': '上传', 'admin.trendDownloads': '下载',
    'admin.days7': '7 天', 'admin.days14': '14 天', 'admin.days30': '30 天', 'admin.chartFailed': '图表数据加载失败：{msg}',
    'admin.typesTitle': '按类型的存储占用', 'admin.typesSub': '当前有效的共享，按占用大小', 'admin.typesEmpty': '暂无有效共享',
    'admin.typeCount': '{n} 个', 'admin.tipSize': '大小', 'admin.tipShare': '占比', 'admin.tipCount': '数量',
    'admin.cat.video': '视频', 'admin.cat.image': '图片', 'admin.cat.audio': '音频', 'admin.cat.archive': '压缩包',
    'admin.cat.document': '文档', 'admin.cat.app': '安装包', 'admin.cat.text': '文本', 'admin.cat.other': '其他',
    'admin.diskTitle': '磁盘空间', 'admin.diskSub': '磁盘总容量 {total}', 'admin.diskFree': '可用', 'admin.diskShares': 'ShareWeb 文件',
    'admin.diskOther': '系统及其他', 'admin.diskAvail': '可用空间', 'admin.diskWarn': '空间偏紧', 'admin.diskDanger': '空间即将用尽',
    'admin.geoTitle': '访客来源', 'admin.geoSub': '访客记录中的独立 IP 数，按国家/地区', 'admin.geoEmpty': '暂无访客记录',
    'admin.geoIps': '{n} 个 IP', 'admin.geoUnknown': '未知', 'admin.geoOther': '其他国家/地区',
    'admin.limitTitle': '单文件大小上限', 'admin.limitDesc': '访客可上传的单个文件最大大小。保存后立即生效，已保存的文件不受影响。',
    'admin.limitNone': '不限制', 'admin.limitCustom': '自定义', 'admin.save': '保存',
    'admin.limitCurrent': '当前生效：{v}', 'admin.limitCapacity': '磁盘剩余 {free}，服务器目前实际能接收的单个文件最大约 {cap}（始终保留 {reserve} 不写满）。',
    'admin.limitNoneNote': '不限制时，单个文件大小只受磁盘剩余空间约束。',
    'admin.limitOverCap': '所选上限超过了磁盘当前能容纳的大小，超过约 {cap} 的文件仍会上传失败。',
    'admin.limitInvalid': '请输入 1 MB 到 1 TB 之间的整数。', 'admin.limitSaved': '已保存，新上传立即按此上限执行。',
    'admin.limitUnchanged': '没有需要保存的修改。',
    'admin.evictTitle': '空间不足时自动清理',
    'admin.evictDesc': '上传文件时如果磁盘剩余空间不够，按上传时间从最旧的文件开始删除，直到腾出足够的空间。已锁定的文件和文本共享不会被删除。',
    'admin.evictConfirm': '开启后，磁盘空间不足以存放正在上传的文件时，会自动永久删除最旧的文件，无法恢复。确定开启？',
    'admin.evictPool': '目前可被自动删除的文件：{n} 个，共 {size}。',
    'admin.evictMax': '开启后，服务器最多能接收约 {cap} 的单个文件。',
    'admin.evictOn': '已开启。', 'admin.evictOff': '已关闭。',
    'admin.limitEvictNote': '超出磁盘剩余空间的部分，会在上传时自动删除最旧的文件来腾出（总共最多约 {cap}）。',
  },
});
const t = I18N.t, S = I18N.span, setKey = I18N.setKey;
const $ = s => document.querySelector(s);

// 调用管理接口; 传了 body 时以 JSON 发送 (默认 POST)
async function api(url, body, method = 'POST') {
  const opt = body === undefined ? {} : { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) };
  const r = await fetch(url, opt);
  const d = await r.json().catch(() => ({}));
  if (!r.ok) {
    // 服务器返回的错误信息原样显示; 没有时用本地文案 (记下 key, 切换语言时可就地更新)。
    const err = new Error(d.detail || d.error || t('admin.requestFailed'));
    if (!d.detail && !d.error) err.i18nKey = 'admin.requestFailed';
    throw err;
  }
  return d;
}

function renderStats(d) {
  $('#activeShares').textContent = d.active_shares ?? 0;
  $('#fileCount').textContent = d.file_count ?? 0;
  $('#fileBytes').textContent = fmtSize(d.file_bytes);
  $('#todayUploads').textContent = d.today_uploads ?? 0;
  $('#todayDownloads').textContent = d.today_downloads ?? 0;
  $('#blacklistCount').textContent = d.blacklist ?? 0;
}

// ---- 访客与黑名单: 列表 + 勾选封禁/解封 ----
let visItems = [];
const visSelected = new Set();
const visState = (() => {
  try { const v = JSON.parse(localStorage.getItem('sw-admin-vis')); if (v && v.key && v.dir && v.filter) return v; } catch (e) {}
  return { key: 'last', dir: 'desc', filter: 'all' };
})();
// IP 排序: IPv4 在前按数值比较, IPv6 其后按文本
const ipKey = ip => ip.includes(':') ? [1, ip] : [0, ip.split('.').reduce((a, n) => a * 256 + Number(n), 0)];
const VIS_SORTERS = {
  last: (a, b) => (a.last_seen || '').localeCompare(b.last_seen || ''),
  first: (a, b) => (a.first_seen || '').localeCompare(b.first_seen || ''),
  hits: (a, b) => (a.hits || 0) - (b.hits || 0),
  ip: (a, b) => { const x = ipKey(a.ip), y = ipKey(b.ip); return x[0] - y[0] || (x[0] ? x[1].localeCompare(y[1]) : x[1] - y[1]); },
  country: (a, b) => (a.geo?.country_code || '~').localeCompare(b.geo?.country_code || '~') || VIS_SORTERS.ip(a, b),
};
function visView() {
  const sign = visState.dir === 'asc' ? 1 : -1;
  const cmp = VIS_SORTERS[visState.key] || VIS_SORTERS.last;
  return visItems.filter(x => visState.filter !== 'blocked' || x.blocked).sort((a, b) => sign * cmp(a, b) || VIS_SORTERS.ip(a, b));
}
function saveVis() { try { localStorage.setItem('sw-admin-vis', JSON.stringify(visState)); } catch (e) {} }
// 国家名随界面语言就地切换 (数据里同时带中英文名)
function geoName(g) { return I18N.lang === 'zh' ? (g.country_zh || g.country_en) : (g.country_en || g.country_zh); }
function geoHtml(x) {
  const g = x.geo || {};
  if (!g.country_code && !g.asn) {
    const priv = /^(10\.|127\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|::1$|f[cd])/i.test(x.ip);
    return S(priv ? 'admin.visPrivate' : 'admin.visUnknownGeo');
  }
  const parts = [];
  if (g.country_code) parts.push(`<span class="geo-name" data-en="${esc(g.country_en || '')}" data-zh="${esc(g.country_zh || '')}">${esc(geoName(g))}</span> (${esc(g.country_code)})`);
  if (g.asn) parts.push(`AS${g.asn}${g.as_org ? ' ' + esc(g.as_org) : ''}`);
  return parts.join(' · ');
}
document.addEventListener('langchange', () => {
  document.querySelectorAll('.geo-name').forEach(el => { el.textContent = (I18N.lang === 'zh' ? el.dataset.zh : el.dataset.en) || el.dataset.en || el.dataset.zh; });
});
function updateVisSelection() {
  const boxes = [...document.querySelectorAll('#visRows input[data-ip]')];
  boxes.forEach(b => b.closest('.file-row').classList.toggle('selected', b.checked));
  const visible = new Set(boxes.map(b => b.dataset.ip));
  const n = [...visSelected].filter(ip => visible.has(ip)).length;
  const all = $('#visSelectAll');
  all.checked = boxes.length > 0 && n === boxes.length;
  all.indeterminate = n > 0 && n < boxes.length;
  all.disabled = boxes.length === 0;
  $('#blockSelected').disabled = n === 0;
  $('#allowSelected').disabled = n === 0;
  if (n) setKey($('#visSelCount'), 'admin.selected', { n }); else setKey($('#visSelCount'), null);
}
function renderVisitors(items) {
  if (items) {
    visItems = items;
    const ips = new Set(items.map(x => x.ip));
    [...visSelected].forEach(ip => { if (!ips.has(ip)) visSelected.delete(ip); });
  }
  const blockedN = visItems.filter(x => x.blocked).length;
  setKey($('#visSummary'), 'admin.visSummary', { n: visItems.length, b: blockedN });
  const view = visView();
  // 筛选后看不到的条目不保留勾选, 避免误操作
  const shown = new Set(view.map(x => x.ip));
  [...visSelected].forEach(ip => { if (!shown.has(ip)) visSelected.delete(ip); });
  const box = $('#visRows');
  if (!view.length) {
    box.innerHTML = `<div class="file-empty muted">${S(visState.filter === 'blocked' ? 'admin.visEmptyBlocked' : 'admin.visEmpty')}</div>`;
    updateVisSelection();
    return;
  }
  box.innerHTML = view.map(x => `
    <div class="file-row" title="${esc(x.user_agent || '')}">
      <input type="checkbox" data-ip="${esc(x.ip)}" ${visSelected.has(x.ip) ? 'checked' : ''} aria-label="${esc(x.ip)}">
      <div class="file-main">
        <div class="file-top">
          <span><span class="vis-ip">${esc(x.ip)}</span>${x.blocked ? `<span class="tag gone">${S('admin.visTagBlocked')}</span>` : ''}${x.is_me ? `<span class="tag me">${S('admin.visTagMe')}</span>` : ''}</span>
          <span class="vis-hits">${S('admin.visHits', { n: x.hits || 0 })}</span>
        </div>
        <div class="meta">${geoHtml(x)}</div>
        <div class="meta">${x.last_seen ? `${S('admin.visLast', { d: { date: x.last_seen } })} · ${S('admin.visFirst', { d: { date: x.first_seen } })}${x.last_path ? ` · <code>${esc(x.last_path)}</code>` : ''}` : S('admin.visNeverSeen')}${x.blocked && x.block_reason ? ` · ${S('admin.visReason', { r: x.block_reason })}` : ''}</div>
      </div>
    </div>`).join('');
  updateVisSelection();
}
function renderVisControls() {
  $('#visSortKey').value = visState.key;
  $('#visFilter').value = visState.filter;
  const b = $('#visSortDir');
  b.innerHTML = visState.dir === 'asc' ? ARROW_UP : ARROW_DOWN;
  const key = visState.dir === 'asc' ? 'admin.sortAsc' : 'admin.sortDesc';
  b.dataset.i18nTitle = key; b.title = t(key); b.setAttribute('aria-label', t(key));
}
async function loadVisitors() {
  try {
    const d = await api('/api/admin/visitors');
    renderVisitors(d.items || []);
  } catch (e) {
    $('#visRows').innerHTML = '';
    setKey($('#visSummary'), 'admin.visLoadFailed', { msg: e.message });
  }
}
async function blockOrAllow(block, ips, reason) {
  if (!ips.length) return;
  try {
    const d = await api(block ? '/api/admin/visitors/block' : '/api/admin/visitors/allow', reason ? { ips, reason } : { ips });
    if (block && d.skipped_self) setKey($('#visMsg'), 'admin.visBlockedSelf', { n: d.blocked, ip: visItems.find(x => x.is_me)?.ip || '' });
    else if (block) setKey($('#visMsg'), 'admin.visBlocked', { n: d.blocked });
    else setKey($('#visMsg'), 'admin.visAllowed', { n: d.allowed });
    visSelected.clear();
  } catch (e) {
    setKey($('#visMsg'), 'admin.visFailed', { msg: e.message });
  }
  load().catch(() => {});
}
$('#visRows').addEventListener('change', e => {
  const cb = e.target.closest('input[data-ip]');
  if (!cb) return;
  if (cb.checked) visSelected.add(cb.dataset.ip); else visSelected.delete(cb.dataset.ip);
  updateVisSelection();
});
$('#visRows').addEventListener('click', e => {
  if (e.target.closest('a, input')) return;
  const cb = e.target.closest('.file-row')?.querySelector('input[data-ip]');
  if (!cb) return;
  cb.checked = !cb.checked;
  cb.dispatchEvent(new Event('change', { bubbles: true }));
});
$('#visSelectAll').addEventListener('change', e => {
  document.querySelectorAll('#visRows input[data-ip]').forEach(cb => {
    cb.checked = e.target.checked;
    if (cb.checked) visSelected.add(cb.dataset.ip); else visSelected.delete(cb.dataset.ip);
  });
  updateVisSelection();
});
$('#visSortKey').addEventListener('change', e => { visState.key = e.target.value; saveVis(); renderVisitors(); });
$('#visFilter').addEventListener('change', e => { visState.filter = e.target.value; saveVis(); renderVisitors(); });
$('#visSortDir').addEventListener('click', () => { visState.dir = visState.dir === 'asc' ? 'desc' : 'asc'; saveVis(); renderVisControls(); renderVisitors(); });
$('#blockSelected').onclick = () => blockOrAllow(true, [...visSelected]);
$('#allowSelected').onclick = () => blockOrAllow(false, [...visSelected]);

// ---- 文件管理: 列表 + 勾选删除 ----
const selected = new Set();

function updateSelection() {
  const boxes = [...document.querySelectorAll('#fileList input[data-id]')];
  boxes.forEach(b => b.closest('.file-row').classList.toggle('selected', b.checked));
  const n = selected.size;
  const all = $('#selectAll');
  all.checked = boxes.length > 0 && n === boxes.length;
  all.indeterminate = n > 0 && n < boxes.length;
  all.disabled = boxes.length === 0;
  $('#deleteSelected').disabled = n === 0;
  $('#lockSelected').disabled = n === 0;
  $('#unlockSelected').disabled = n === 0;
  if (n) setKey($('#selCount'), 'admin.selected', { n }); else setKey($('#selCount'), null);
}

// 排序: 在浏览器里排, 选择记在本机 (localStorage 不可用时用默认: 日期倒序)
let fileItems = [];
const sortState = (() => {
  try { const v = JSON.parse(localStorage.getItem('sw-admin-sort')); if (v && v.key && v.dir) return v; } catch (e) {}
  return { key: 'date', dir: 'desc' };
})();
// 名称: 符号 → 数字 → 英文 A-Z (不分大小写) → 中文等其它文字 (中文按拼音), 与中文版 Windows 资源管理器一致。
// 浏览器的 Intl.Collator 不支持调整文字顺序 (zh 会把汉字排在英文前), 所以先按首字符分组再比较。
const collator = new Intl.Collator('zh-CN', { numeric: true, sensitivity: 'base' });
const nameGroup = s => {
  const ch = s.trim().charAt(0);
  if (!/[\p{L}\p{N}]/u.test(ch)) return 0;
  if (/\p{N}/u.test(ch)) return 1;
  if (/[a-z]/i.test(ch)) return 2;
  return 3;
};
const nameCompare = (a, b) => nameGroup(a) - nameGroup(b) || collator.compare(a, b);
const extOf = n => { const i = n.lastIndexOf('.'); return i > 0 ? n.slice(i + 1).toLowerCase() : ''; };
const SORTERS = {
  date: (a, b) => (a.created_at || '').localeCompare(b.created_at || ''),
  size: (a, b) => (a.size || 0) - (b.size || 0),
  type: (a, b) => nameCompare(extOf(a.filename), extOf(b.filename)) || nameCompare(a.filename, b.filename),
  name: (a, b) => nameCompare(a.filename, b.filename),
};
function sortedItems() {
  const cmp = SORTERS[sortState.key] || SORTERS.date;
  const sign = sortState.dir === 'asc' ? 1 : -1;
  return [...fileItems].sort((a, b) => sign * cmp(a, b) || (b.id - a.id));
}
const ARROW_DOWN = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v14M6 13l6 6 6-6"/></svg>';
const ARROW_UP = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5M6 11l6-6 6 6"/></svg>';
function renderSortControls() {
  $('#sortKey').value = sortState.key;
  const b = $('#sortDir');
  b.innerHTML = sortState.dir === 'asc' ? ARROW_UP : ARROW_DOWN;
  const key = sortState.dir === 'asc' ? 'admin.sortAsc' : 'admin.sortDesc';
  b.dataset.i18nTitle = key; b.title = t(key); b.setAttribute('aria-label', t(key));
}
function saveSort() { try { localStorage.setItem('sw-admin-sort', JSON.stringify(sortState)); } catch (e) {} }
$('#sortKey').addEventListener('change', e => { sortState.key = e.target.value; saveSort(); renderFiles(); });
$('#sortDir').addEventListener('click', () => { sortState.dir = sortState.dir === 'asc' ? 'desc' : 'asc'; saveSort(); renderSortControls(); renderFiles(); });
document.addEventListener('langchange', () => { const b = $('#sortDir'); b.setAttribute('aria-label', b.title); });
renderSortControls();

function renderFiles(items) {
  if (items) fileItems = items;
  items = sortedItems();
  const box = $('#fileRows');
  // 刷新后只保留仍存在的勾选
  const ids = new Set(items.map(x => String(x.id)));
  [...selected].forEach(id => { if (!ids.has(id)) selected.delete(id); });
  const total = items.reduce((a, x) => a + (x.size || 0), 0);
  setKey($('#filesSummary'), 'admin.filesSummary', { n: items.length, size: fmtSize(total) });
  if (!items.length) {
    box.innerHTML = `<div class="file-empty muted">${S('admin.filesEmpty')}</div>`;
    updateSelection();
    return;
  }
  box.innerHTML = items.map(x => `
    <div class="file-row">
      <input type="checkbox" data-id="${x.id}" ${selected.has(String(x.id)) ? 'checked' : ''} aria-label="${esc(x.filename)}">
      <div class="file-main">
        <div class="file-top">
          <span><a class="file-name" href="/share/${encodeURIComponent(x.token)}" target="_blank" rel="noopener">${esc(x.filename)}</a>${x.locked ? `<span class="tag lock">${S('admin.tagLocked')}</span>` : ''}${x.expired ? `<span class="tag warn">${S('admin.tagExpired')}</span>` : ''}${x.github ? `<span class="tag">${S('admin.tagGithub')}</span>` : ''}</span>
          <span class="file-size">${fmtSize(x.size)}</span>
        </div>
        <div class="meta">${S('admin.fileUploaded', { d: { date: x.created_at } })} · ${x.locked ? S('admin.fileLockedExpiry', { d: { date: x.expires_at || '' } }) : S('admin.fileExpires', { d: { date: x.expires_at || '' } })} · ${S('admin.fileDownloads', { n: x.download_count })} · ${S('admin.fileCode', { c: x.code || '-' })}</div>
      </div>
    </div>`).join('');
  updateSelection();
}

async function loadFiles() {
  try {
    const d = await api('/api/admin/files');
    renderFiles(d.items || []);
  } catch (e) {
    $('#fileRows').innerHTML = '';
    setKey($('#filesSummary'), 'admin.filesLoadFailed', { msg: e.message });
  }
}

$('#fileList').addEventListener('change', e => {
  const cb = e.target.closest('input[data-id]');
  if (!cb) return;
  if (cb.checked) selected.add(cb.dataset.id); else selected.delete(cb.dataset.id);
  updateSelection();
});
// 点击整行即可勾选 (点文件名链接除外)
$('#fileList').addEventListener('click', e => {
  if (e.target.closest('a, input')) return;
  const cb = e.target.closest('.file-row')?.querySelector('input[data-id]');
  if (!cb) return;
  cb.checked = !cb.checked;
  cb.dispatchEvent(new Event('change', { bubbles: true }));
});
$('#selectAll').addEventListener('change', e => {
  document.querySelectorAll('#fileList input[data-id]').forEach(cb => {
    cb.checked = e.target.checked;
    if (cb.checked) selected.add(cb.dataset.id); else selected.delete(cb.dataset.id);
  });
  updateSelection();
});
$('#deleteSelected').onclick = async () => {
  const ids = [...selected].map(Number);
  if (!ids.length) return;
  const lockedN = fileItems.filter(x => x.locked && selected.has(String(x.id))).length;
  if (lockedN === ids.length) { setKey($('#cleanupMsg'), 'admin.allLocked'); return; }
  const ask = lockedN ? t('admin.confirmSelectedSkip', { n: ids.length, m: lockedN }) : t('admin.confirmSelected', { n: ids.length });
  if (!confirm(ask)) return;
  const btn = $('#deleteSelected');
  btn.disabled = true;
  setKey($('#cleanupMsg'), 'admin.working');
  try {
    const d = await api('/api/admin/files/delete', { ids });
    // 被跳过的锁定文件保持勾选, 其余清空
    [...selected].forEach(id => { if (!fileItems.some(x => String(x.id) === id && x.locked)) selected.delete(id); });
    if (d.skipped_locked) setKey($('#cleanupMsg'), 'admin.cleanedSkipped', { n: d.removed, size: fmtSize(d.removed_bytes), m: d.skipped_locked });
    else setKey($('#cleanupMsg'), 'admin.cleaned', { n: d.removed, size: fmtSize(d.removed_bytes) });
  } catch (e) {
    setKey($('#cleanupMsg'), 'admin.cleanFailed', { msg: e.message });
  }
  load().catch(() => {});
};

async function setLocked(locked) {
  const ids = [...selected].map(Number);
  if (!ids.length) return;
  try {
    const d = await api('/api/admin/files/lock', { ids, locked });
    setKey($('#cleanupMsg'), locked ? 'admin.lockedDone' : 'admin.unlockedDone', { n: d.changed });
  } catch (e) {
    setKey($('#cleanupMsg'), 'admin.lockFailed', { msg: e.message });
  }
  load().catch(() => {});
}
$('#lockSelected').onclick = () => setLocked(true);
$('#unlockSelected').onclick = () => setLocked(false);

const TZ = new Date().getTimezoneOffset();

// 刷新全部数据; 统计接口失败 (未登录 / 会话过期) 时抛出
async function load() {
  renderStats(await api('/api/admin/stats?tz=' + TZ));
  await Promise.all([loadVisitors(), loadFiles(), loadOverview(), loadSettings()]);
}

function showPanel(on) {
  $('#loginCard').classList.toggle('hidden', on);
  $('#panel').classList.toggle('hidden', !on);
  $('#logout').classList.toggle('hidden', !on);
}

// 打开页面时: 已登录就直接显示后台, 否则显示登录框
async function checkAuth() {
  try {
    await load();
    showPanel(true);
  } catch (e) {
    showPanel(false);
  }
}

$('#login').onclick = async () => {
  setKey($('#loginErr'), null);
  try {
    await api('/api/admin/login', { password: $('#adminPw').value });
  } catch (e) {
    if (e.i18nKey || !e.message) setKey($('#loginErr'), e.i18nKey || 'admin.loginFailed');
    else { setKey($('#loginErr'), null); $('#loginErr').textContent = e.message; }
    return;
  }
  showPanel(true);
  load().catch(() => {});
};

$('#adminPw').addEventListener('keydown', e => { if (e.key === 'Enter') $('#login').click(); });

$('#logout').onclick = async () => {
  await api('/api/admin/logout', {});
  location.reload();
};

// 手动添加: 走同一个封禁接口 (校验 IP 格式, 也不会封到自己)
$('#blAdd').onclick = async () => {
  const ip = $('#blIp').value.trim();
  if (!ip) return;
  await blockOrAllow(true, [ip], $('#blReason').value.trim() || 'manual blacklist');
  $('#blIp').value = '';
  $('#blReason').value = '';
};

document.querySelectorAll('.cleanup-btn').forEach(btn => {
  btn.onclick = async () => {
    const days = btn.dataset.days === 'all' ? null : Number(btn.dataset.days);
    const msg = days === null ? t('admin.confirmAll') : t('admin.confirmDays', { n: days });
    if (!confirm(msg)) return;
    setKey($('#cleanupMsg'), 'admin.working');
    try {
      const d = await api('/api/admin/cleanup', { days });
      setKey($('#cleanupMsg'), 'admin.cleaned', { n: d.removed, size: fmtSize(d.removed_bytes) });
      load().catch(() => {});
    } catch (e) {
      setKey($('#cleanupMsg'), 'admin.cleanFailed', { msg: e.message });
    }
  };
});

// ---- 左侧菜单: 按 #hash 切换视图, 刷新后停留在当前页 ----
// 标签页列表取自页面里的 .admin-view, 新增标签页只需改 HTML (第一个为默认页)
const VIEWS = [...document.querySelectorAll('.admin-view')].map(el => el.dataset.view);
function showView() {
  const v = VIEWS.includes(location.hash.slice(1)) ? location.hash.slice(1) : VIEWS[0];
  document.querySelectorAll('.admin-nav a').forEach(a => {
    const on = a.dataset.view === v;
    a.classList.toggle('active', on);
    if (on) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
  });
  document.querySelectorAll('.admin-view').forEach(el => el.classList.toggle('active', el.dataset.view === v));
  hideTip();
}
window.addEventListener('hashchange', showView);

// ---- 总览图表: 纯 SVG 手绘, 不依赖外部库 ----
let overview = null;
const trendState = (() => {
  try { const v = Number(localStorage.getItem('sw-admin-days')); if ([7, 14, 30].includes(v)) return { days: v }; } catch (e) {}
  return { days: 14 };
})();

const tip = $('#chartTip');
function showTip(html, x, y) {
  tip.innerHTML = html;
  tip.classList.remove('hidden');
  const r = tip.getBoundingClientRect();
  let left = x + 14, top = y + 14;
  if (left + r.width > innerWidth - 8) left = x - r.width - 14;
  if (top + r.height > innerHeight - 8) top = y - r.height - 14;
  tip.style.left = Math.max(8, left) + 'px';
  tip.style.top = Math.max(8, top) + 'px';
}
function hideTip() { tip.classList.add('hidden'); }
const tipRow = (key, label, value) => `<div class="tip-row"><span>${key ? `<i class="key dot ${key}"></i>` : ''}${esc(label)}</span><span>${esc(value)}</span></div>`;

// 坐标轴取整: 最大值向上取到 1/2/5×10^n, 刻度为整数
function niceTicks(max, count = 4) {
  if (max <= 0) return [0, 1];
  const raw = max / count, mag = 10 ** Math.floor(Math.log10(raw));
  const step = Math.max(1, [1, 2, 5, 10].map(m => m * mag).find(s => s >= raw));
  const top = Math.ceil(max / step) * step;
  const out = [];
  for (let v = 0; v <= top + 1e-9; v += step) out.push(v);
  return out;
}
const compact = n => n >= 1e6 ? (n / 1e6).toFixed(1).replace(/\.0$/, '') + 'M' : n >= 1000 ? (n / 1000).toFixed(1).replace(/\.0$/, '') + 'K' : String(n);
const locale = () => I18N.lang === 'zh' ? 'zh-CN' : 'en-US';
const dayLabel = (iso, opts) => new Date(iso + 'T00:00:00').toLocaleDateString(locale(), opts);

function renderTrend() {
  const box = $('#trendChart');
  const data = overview?.trend;
  if (!data) return;
  const W = Math.max(280, box.clientWidth), H = 230;
  const m = { l: 34, r: 30, t: 12, b: 26 };
  const iw = W - m.l - m.r, ih = H - m.t - m.b;
  const ticks = niceTicks(Math.max(...data.map(d => Math.max(d.uploads, d.downloads))));
  const top = ticks[ticks.length - 1];
  const x = i => m.l + (data.length === 1 ? iw / 2 : i * iw / (data.length - 1));
  const y = v => m.t + ih - v / top * ih;
  const line = k => data.map((d, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(d[k]).toFixed(1)}`).join('');
  // x 轴日期: 最多约 7 个, 末尾那天总是显示
  const every = Math.ceil(data.length / Math.max(2, Math.floor(iw / 70)));
  const xl = data.map((d, i) => ((data.length - 1 - i) % every === 0) ? `<text x="${x(i)}" y="${H - 6}" text-anchor="middle">${esc(dayLabel(d.date, { month: 'numeric', day: 'numeric' }))}</text>` : '').join('');
  const yl = ticks.map(v => `<line x1="${m.l}" x2="${W - m.r}" y1="${y(v)}" y2="${y(v)}"/>`).join('');
  const yt = ticks.map(v => `<text x="${m.l - 8}" y="${y(v) + 4}" text-anchor="end">${compact(v)}</text>`).join('');
  // 末端数值标签: 两条线末端离得够远才标, 否则交给图例和悬浮提示
  const last = data[data.length - 1], lx = x(data.length - 1);
  const ends = Math.abs(y(last.uploads) - y(last.downloads)) >= 14
    ? `<text class="lbl" x="${lx + 8}" y="${y(last.uploads) + 4}">${last.uploads}</text><text class="lbl" x="${lx + 8}" y="${y(last.downloads) + 4}">${last.downloads}</text>` : '';
  box.innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="${esc(t('admin.trendTitle'))}">
    <g class="grid">${yl}</g>${yt}${xl}
    <path d="${line('downloads')}" fill="none" stroke="var(--s2)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
    <path d="${line('uploads')}" fill="none" stroke="var(--s1)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
    <circle cx="${lx}" cy="${y(last.downloads)}" r="4" fill="var(--s2)" stroke="var(--card)" stroke-width="2"/>
    <circle cx="${lx}" cy="${y(last.uploads)}" r="4" fill="var(--s1)" stroke="var(--card)" stroke-width="2"/>
    ${ends}
    <g class="hover hidden"><line class="xhair" y1="${m.t}" y2="${m.t + ih}"/><circle class="h2" r="4.5" fill="var(--s2)" stroke="var(--card)" stroke-width="2"/><circle class="h1" r="4.5" fill="var(--s1)" stroke="var(--card)" stroke-width="2"/></g>
    <rect class="hit" x="${m.l}" y="0" width="${iw}" height="${H - m.b}"/>
  </svg>`;
  const svg = box.firstElementChild, hover = svg.querySelector('.hover');
  const move = e => {
    const r = svg.getBoundingClientRect();
    const px = (e.clientX - r.left) * W / r.width;
    const i = Math.max(0, Math.min(data.length - 1, Math.round((px - m.l) / (iw / Math.max(1, data.length - 1)))));
    const d = data[i];
    hover.classList.remove('hidden');
    hover.querySelector('.xhair').setAttribute('x1', x(i)); hover.querySelector('.xhair').setAttribute('x2', x(i));
    hover.querySelector('.h1').setAttribute('cx', x(i)); hover.querySelector('.h1').setAttribute('cy', y(d.uploads));
    hover.querySelector('.h2').setAttribute('cx', x(i)); hover.querySelector('.h2').setAttribute('cy', y(d.downloads));
    showTip(`<b>${esc(dayLabel(d.date, { month: 'short', day: 'numeric', weekday: 'short' }))}</b>${tipRow('s1', t('admin.trendUploads'), d.uploads)}${tipRow('s2', t('admin.trendDownloads'), d.downloads)}`, e.clientX, e.clientY);
  };
  const hit = svg.querySelector('.hit');
  hit.addEventListener('pointermove', move);
  hit.addEventListener('pointerdown', move);
  hit.addEventListener('pointerleave', () => { hover.classList.add('hidden'); hideTip(); });
}

// 量文字宽度, 标签放不下时截断加省略号 (完整名称在悬浮提示里)
const measureCtx = document.createElement('canvas').getContext('2d');
function textWidth(s, size) {
  measureCtx.font = `${size}px ${getComputedStyle(document.body).fontFamily}`;
  return measureCtx.measureText(s).width;
}
function fitText(s, size, max) {
  if (textWidth(s, size) <= max) return s;
  while (s.length > 1 && textWidth(s + '…', size) > max) s = s.slice(0, -1);
  return s + '…';
}

// 横向条形图 (单一系列): rows = [{label, value, text, tip}]
function renderBars(box, rows, emptyKey) {
  if (!rows.length) { box.innerHTML = `<div class="chart-empty muted">${S(emptyKey)}</div>`; return; }
  const W = Math.max(280, box.clientWidth), rowH = 34, bar = 18;
  const labelMax = Math.round(W * 0.3);
  const labelW = Math.min(labelMax, Math.max(...rows.map(r => textWidth(r.label, 13))) + 14);
  const valueW = Math.min(150, Math.max(...rows.map(r => textWidth(r.text, 11.5))) + 12);
  const iw = W - labelW - valueW - 8, max = Math.max(...rows.map(r => r.value)) || 1;
  const H = rows.length * rowH;
  const body = rows.map((r, i) => {
    const y0 = i * rowH + (rowH - bar) / 2, w = Math.max(2, r.value / max * iw), x0 = labelW, rr = Math.min(4, w / 2);
    // 只有末端圆角, 基线一侧是直角
    const path = `M${x0},${y0}H${x0 + w - rr}Q${x0 + w},${y0} ${x0 + w},${y0 + rr}V${y0 + bar - rr}Q${x0 + w},${y0 + bar} ${x0 + w - rr},${y0 + bar}H${x0}Z`;
    return `<g data-i="${i}"><rect class="hit" x="0" y="${i * rowH}" width="${W}" height="${rowH}"/>
      <text class="cat" x="0" y="${y0 + bar / 2 + 4.5}">${esc(fitText(r.label, 13, labelW - 10))}</text>
      <path d="${path}" fill="${r.color || 'var(--s1)'}" pointer-events="none"/>
      <text class="lbl" x="${x0 + w + 8}" y="${y0 + bar / 2 + 4}" pointer-events="none">${esc(r.text)}</text></g>`;
  }).join('');
  box.innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}">${body}</svg>`;
  box.querySelectorAll('g[data-i]').forEach(g => {
    const r = rows[Number(g.dataset.i)];
    const move = e => showTip(r.tip, e.clientX, e.clientY);
    g.addEventListener('pointermove', move);
    g.addEventListener('pointerdown', move);
    g.addEventListener('pointerleave', hideTip);
  });
}

function renderTypes() {
  const types = overview?.types;
  if (!types) return;
  const total = types.reduce((a, x) => a + x.bytes, 0) || 1;
  renderBars($('#typesChart'), types.map(x => {
    const label = t('admin.cat.' + x.category);
    const pct = (x.bytes / total * 100).toFixed(x.bytes / total < 0.01 ? 2 : 1);
    return {
      label, value: x.bytes, text: `${fmtSize(x.bytes)} · ${t('admin.typeCount', { n: x.count })}`,
      tip: `<b>${esc(label)}</b>${tipRow('', t('admin.tipSize'), fmtSize(x.bytes))}${tipRow('', t('admin.tipShare'), pct + '%')}${tipRow('', t('admin.tipCount'), x.count)}`,
    };
  }), 'admin.typesEmpty');
}

function renderGeo() {
  const list = overview?.countries;
  if (!list) return;
  // 前 7 个国家单独显示, 其余合并为「其他」
  const head = list.slice(0, 7), rest = list.slice(7);
  const rows = head.map(c => ({ label: c.code ? (I18N.lang === 'zh' ? (c.zh || c.en) : (c.en || c.zh)) || c.code : t('admin.geoUnknown'), code: c.code, ips: c.ips, hits: c.hits }));
  if (rest.length) rows.push({ label: t('admin.geoOther'), code: '', ips: rest.reduce((a, c) => a + c.ips, 0), hits: rest.reduce((a, c) => a + c.hits, 0), other: true });
  renderBars($('#geoChart'), rows.map(r => ({
    label: r.label, value: r.ips, text: t('admin.geoIps', { n: r.ips }), color: r.other ? 'var(--other)' : undefined,
    tip: `<b>${esc(r.label)}${r.code ? ` (${esc(r.code)})` : ''}</b>${tipRow('', 'IP', r.ips)}${tipRow('', t('admin.visSortHits'), compact(r.hits))}`,
  })), 'admin.geoEmpty');
}

function renderDisk() {
  const d = overview?.disk;
  if (!d) return;
  const other = Math.max(0, d.used - d.shares), pct = v => (v / d.total * 100);
  const usedPct = pct(d.used);
  const state = usedPct >= 90 ? ['danger', 'admin.diskDanger'] : usedPct >= 75 ? ['warn', 'admin.diskWarn'] : null;
  setKey($('#diskSub'), 'admin.diskSub', { total: fmtSize(d.total) });
  $('#diskChart').innerHTML = `
    <div class="disk-big">${esc(fmtSize(d.free))}<small>${S('admin.diskFree')}</small>${state ? `<span class="tag ${state[0] === 'danger' ? 'gone' : 'warn'} disk-state">⚠ ${S(state[1])}</span>` : ''}</div>
    <div class="disk-bar" role="img" aria-label="${esc(t('admin.diskTitle'))} ${usedPct.toFixed(1)}%">
      <span class="s1" style="width:${pct(d.shares)}%" title="${esc(t('admin.diskShares'))}"></span><span class="other" style="width:${pct(other)}%" title="${esc(t('admin.diskOther'))}"></span>
    </div>
    <div class="disk-legend">
      <div><i class="key dot s1"></i>${S('admin.diskShares')}<b>${esc(fmtSize(d.shares))}</b></div>
      <div><i class="key dot other"></i>${S('admin.diskOther')}<b>${esc(fmtSize(other))}</b></div>
      <div><i class="key dot track"></i>${S('admin.diskAvail')}<b>${esc(fmtSize(d.free))}</b></div>
    </div>`;
}

function renderOverview() {
  document.querySelectorAll('#trendRange button').forEach(b => b.classList.toggle('active', Number(b.dataset.days) === trendState.days));
  renderTrend(); renderTypes(); renderGeo(); renderDisk();
}
async function loadOverview() {
  try {
    overview = await api(`/api/admin/overview?days=${trendState.days}&tz=${TZ}`);
    renderOverview();
  } catch (e) {
    $('#trendChart').innerHTML = `<div class="chart-empty muted">${S('admin.chartFailed', { msg: e.message })}</div>`;
  }
}
$('#trendRange').addEventListener('click', e => {
  const b = e.target.closest('button[data-days]');
  if (!b) return;
  trendState.days = Number(b.dataset.days);
  try { localStorage.setItem('sw-admin-days', trendState.days); } catch (e) {}
  loadOverview();
});
document.addEventListener('langchange', () => { if (overview) renderOverview(); });
// 宽度变化 (含从隐藏切换到显示) 时按新宽度重画
let resizeTimer;
new ResizeObserver(() => { clearTimeout(resizeTimer); resizeTimer = setTimeout(() => { if (overview) { renderTrend(); renderTypes(); renderGeo(); } }, 60); }).observe($('#trendChart'));

// ---- 高级设置: 单文件大小上限 ----
const PRESETS = ['500', '1024', '4096', '0'];
let adminSettings = null;
const fmtLimit = mb => mb === 0 ? t('admin.limitNone') : mb % 1024 === 0 ? `${mb / 1024} GB` : `${mb} MB`;
function chosenLimitMb() {
  const v = document.querySelector('#limitOptions input:checked')?.value;
  if (v !== 'custom') return Number(v);
  const n = Number($('#limitValue').value);
  if (!Number.isInteger(n) || n < 1) return NaN;
  return n * Number($('#limitUnit').value);
}
function renderLimitInfo() {
  if (!adminSettings) return;
  const s = adminSettings, mb = chosenLimitMb();
  $('#limitCustom').classList.toggle('hidden', document.querySelector('#limitOptions input:checked')?.value !== 'custom');
  const lines = [`<div>${S('admin.limitCurrent', { v: fmtLimit(s.max_upload_mb) })}</div>`,
    `<div>${S('admin.limitCapacity', { free: fmtSize(s.disk.free), cap: fmtSize(s.capacity_bytes), reserve: fmtLimit(s.disk_reserve_bytes / 1048576) })}</div>`];
  // 开启自动清理时, 可腾出的空间也算进最大可接收大小
  const maxCap = s.capacity_bytes + (s.auto_evict ? s.evictable_bytes : 0);
  if (mb === 0) lines.push(`<div>${S('admin.limitNoneNote')}</div>`);
  if (mb >= 0 && (mb === 0 ? Infinity : mb * 1024 * 1024) > s.capacity_bytes) {
    if (mb > 0 && mb * 1024 * 1024 > maxCap) lines.push(`<div class="warn">⚠ ${S('admin.limitOverCap', { cap: fmtSize(maxCap) })}</div>`);
    else if (s.auto_evict) lines.push(`<div>${S('admin.limitEvictNote', { cap: fmtSize(maxCap) })}</div>`);
  }
  $('#limitInfo').innerHTML = lines.join('');
}
function renderEvict() {
  if (!adminSettings) return;
  const s = adminSettings;
  $('#autoEvict').checked = s.auto_evict;
  const lines = [`<div>${S('admin.evictPool', { n: s.evictable_count, size: fmtSize(s.evictable_bytes) })}</div>`];
  if (s.auto_evict) lines.push(`<div>${S('admin.evictMax', { cap: fmtSize(s.capacity_bytes + s.evictable_bytes) })}</div>`);
  $('#evictInfo').innerHTML = lines.join('');
}
function renderSettings() {
  const mb = adminSettings.max_upload_mb, preset = PRESETS.includes(String(mb));
  document.querySelectorAll('#limitOptions input').forEach(r => { r.checked = preset ? r.value === String(mb) : r.value === 'custom'; });
  if (!preset) {
    const gb = mb % 1024 === 0;
    $('#limitUnit').value = gb ? '1024' : '1';
    $('#limitValue').value = gb ? mb / 1024 : mb;
  }
  renderLimitInfo();
  renderEvict();
}
async function loadSettings() {
  try {
    adminSettings = await api('/api/admin/settings');
    renderSettings();
  } catch (e) {
    setKey($('#limitMsg'), 'admin.lockFailed', { msg: e.message });
  }
}
$('#limitOptions').addEventListener('change', () => {
  if (document.querySelector('#limitOptions input:checked')?.value === 'custom' && !$('#limitValue').value) $('#limitValue').focus();
  setKey($('#limitMsg'), null);
  renderLimitInfo();
});
$('#limitValue').addEventListener('input', () => { setKey($('#limitMsg'), null); renderLimitInfo(); });
$('#limitUnit').addEventListener('change', renderLimitInfo);
document.addEventListener('langchange', renderLimitInfo);
$('#limitValue').addEventListener('keydown', e => { if (e.key === 'Enter') $('#limitSave').click(); });
$('#autoEvict').addEventListener('change', async e => {
  const on = e.target.checked;
  if (on && !confirm(t('admin.evictConfirm'))) { e.target.checked = false; return; }
  e.target.disabled = true;
  try {
    adminSettings = await api('/api/admin/settings', { auto_evict: on }, 'PUT');
    // 只刷新开关相关的显示, 不重置上面还没保存的上限选择
    renderEvict(); renderLimitInfo();
    setKey($('#evictMsg'), on ? 'admin.evictOn' : 'admin.evictOff');
  } catch (err) {
    e.target.checked = !on;
    setKey($('#evictMsg'), 'admin.lockFailed', { msg: err.message });
  }
  e.target.disabled = false;
});
document.addEventListener('langchange', renderEvict);

$('#limitSave').onclick = async () => {
  const mb = chosenLimitMb();
  if (!Number.isInteger(mb) || mb < 0 || mb > (adminSettings?.max_upload_mb_cap || 1048576)) { setKey($('#limitMsg'), 'admin.limitInvalid'); return; }
  if (adminSettings && mb === adminSettings.max_upload_mb) { setKey($('#limitMsg'), 'admin.limitUnchanged'); return; }
  const btn = $('#limitSave');
  btn.disabled = true;
  try {
    adminSettings = await api('/api/admin/settings', { max_upload_mb: mb }, 'PUT');
    renderSettings();
    setKey($('#limitMsg'), 'admin.limitSaved');
  } catch (e) {
    setKey($('#limitMsg'), 'admin.lockFailed', { msg: e.message });
  }
  btn.disabled = false;
};

renderVisControls();
showView();
checkAuth();
