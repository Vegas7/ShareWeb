I18N.add({
  en: {
    'special.pageTitle': 'Instructions · ShareWeb',
    'sp.title': '✨ How to use ShareWeb',
    'sp.basicTitle': '📤 Basics',
    'sp.basic1': '<b>Upload</b>: drop a file or paste text on the home page to get a <b>share link</b> and a <b>4-digit code</b>.',
    'sp.basic2': '<b>Share</b>: send the link or the code to the recipient.',
    'sp.basic3': '<b>Receive</b>: open the link, or enter the code on the home page. Text and images are shown right on the page and can be copied in one click, no download needed.',
    'sp.blockedTitle': '🚫 Downloads blocked? Use "encrypted text · no download"',
    'sp.blockedDesc': 'If your computer or network blocks downloads, the file can skip downloading entirely: on the file page click <b>"Copy encrypted text"</b>, <b>save the copied content as a .txt file</b> (creating a local file from the clipboard is not a download), then restore it with the script below.',
    'sp.blocked1': 'On the file page click <b>"Copy encrypted text"</b>, and <b>copy the key shown on the page</b>.',
    'sp.blocked2': 'Save the script below as <code>ShareWeb-Decrypt.bat</code>.',
    'sp.blocked3': '<b>Drag the saved <code>.txt</code> onto the .bat</b> to run it.',
    'sp.blocked4': 'When prompted, <b>paste the key</b>. The script restores the original file and verifies its SHA-256.',
    'sp.tip': '<b>Tip:</b> the script uses the PowerShell built into Windows. No internet or installation required. The restored file is saved in the same folder as the <code>.txt</code> / <code>.dat</code>.',
    'sp.scriptTitle': '🛠️ Decryption script (Windows · save as .bat)',
    'sp.scriptDesc': 'Copy all of the code, save it as <code>ShareWeb-Decrypt.bat</code>, then drag the saved <code>.txt</code> onto it.',
    'sp.copyCode': 'Copy all code',
  },
  zh: {
    'special.pageTitle': '使用说明 · ShareWeb',
    'sp.title': '✨ ShareWeb 使用说明',
    'sp.basicTitle': '📤 基本用法',
    'sp.basic1': '<b>上传</b>：在首页拖放文件 / 粘贴文字，得到<b>分享链接</b>和<b>4 位提取码</b>。',
    'sp.basic2': '<b>分享</b>：把链接或提取码发给接收者。',
    'sp.basic3': '<b>接收</b>：打开链接，或在首页输入提取码即可获取。文字与图片直接在页面显示、可一键复制，无需下载。',
    'sp.blockedTitle': '🚫 下载被拦截？用「加密文本 · 免下载」',
    'sp.blockedDesc': '如果所在电脑/网络会拦截下载动作，文件可以完全不走下载：在文件页点 <b>「复制加密文本」</b>，把复制到的内容<b>另存为一个 .txt 文件</b>（从剪贴板新建本地文件不算下载），再用下面的脚本还原。',
    'sp.blocked1': '文件页点 <b>「复制加密文本」</b>，并<b>复制页面上的密钥</b>。',
    'sp.blocked2': '把下面的脚本保存为 <code>ShareWeb-Decrypt.bat</code>。',
    'sp.blocked3': '把保存好的 <code>.txt</code> <b>拖到该 .bat 上</b>运行。',
    'sp.blocked4': '按提示 <b>粘贴密钥</b>，脚本自动还原原文件并校验 SHA-256。',
    'sp.tip': '<b>提示：</b>脚本用 Windows 自带 PowerShell，无需联网、无需安装。还原文件会保存在 <code>.txt</code> / <code>.dat</code> 所在的同一文件夹里。',
    'sp.scriptTitle': '🛠️ 解密脚本（Windows · 另存为 .bat）',
    'sp.scriptDesc': '复制全部代码，保存为 <code>ShareWeb-Decrypt.bat</code>，然后把保存好的 <code>.txt</code> 拖进去运行。',
    'sp.copyCode': '复制全部代码',
  },
});
const t = I18N.t, S = I18N.span, H = I18N.htmlSpan;
const $ = s => document.querySelector(s);
const box = $('#specialState');
box.removeAttribute('data-i18n');

// Windows drag-and-drop AES-256 decryptor. Handles BOTH the encrypted .dat download
// and a base64 .txt saved from the "copy encrypted text" (no-download) flow.
const decryptorBat = `@echo off
setlocal EnableExtensions
chcp 65001 >nul
title ShareWeb Decryptor
color 0b
set "SELF=%~f0"
set "DROP=%~1"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$self=Get-Content -LiteralPath $env:SELF -Raw; $m=[char]35+'===PSBEGIN==='+[char]35; $i=$self.LastIndexOf($m); & ([ScriptBlock]::Create($self.Substring($i+$m.Length))) $env:DROP"
echo.
pause
exit /b
#===PSBEGIN===#
param([string]$InputFile)
$ErrorActionPreference = 'Stop'
try {
  Write-Host '=====================================================' -ForegroundColor Cyan
  Write-Host '   ShareWeb  -  AES-256 File Decryptor' -ForegroundColor Cyan
  Write-Host '=====================================================' -ForegroundColor Cyan
  Write-Host ''

  if (-not $InputFile -or -not (Test-Path -LiteralPath $InputFile)) {
    $InputFile = Read-Host 'Drag the .dat or .txt file here (or paste its full path) and press Enter'
    $InputFile = $InputFile.Trim().Trim('"')
  }
  if (-not (Test-Path -LiteralPath $InputFile)) { throw "File not found: $InputFile" }

  $Key = Read-Host 'Paste the decryption KEY and press Enter'
  $Key = $Key.Trim()
  $keyBytes = [Convert]::FromBase64String($Key)
  if ($keyBytes.Length -ne 32) { throw 'Invalid key (must be a 32-byte base64 key)' }

  # Detect input form: raw SWE1 container (.dat) vs base64 text (.txt).
  $probe = [System.IO.File]::OpenRead($InputFile)
  $m4 = New-Object byte[] 4
  $n = $probe.Read($m4,0,4)
  $isRaw = ($n -eq 4 -and $m4[0] -eq 0x53 -and $m4[1] -eq 0x57 -and $m4[2] -eq 0x45 -and $m4[3] -eq 0x31)
  if ($isRaw) {
    $probe.Position = 0
    $inStream = $probe
    Write-Host '[i] Input: encrypted .dat (binary)' -ForegroundColor DarkGray
  } else {
    $probe.Close()
    $text = [System.IO.File]::ReadAllText($InputFile)
    $text = ($text -replace '\\s','')
    $bytes = [Convert]::FromBase64String($text)
    $inStream = New-Object System.IO.MemoryStream(,$bytes)
    Write-Host '[i] Input: base64 text' -ForegroundColor DarkGray
  }

  try {
    $magic = New-Object byte[] 4
    if ($inStream.Read($magic,0,4) -ne 4) { throw 'Data too short' }
    if (-not ($magic[0] -eq 0x53 -and $magic[1] -eq 0x57 -and $magic[2] -eq 0x45 -and $magic[3] -eq 0x31)) { throw 'Unrecognized data (bad header)' }
    $iv = New-Object byte[] 16
    if ($inStream.Read($iv,0,16) -ne 16) { throw 'Data too short (iv)' }

    $aes = [System.Security.Cryptography.Aes]::Create()
    $aes.Key = $keyBytes; $aes.IV = $iv
    $aes.Mode = [System.Security.Cryptography.CipherMode]::CBC
    $aes.Padding = [System.Security.Cryptography.PaddingMode]::PKCS7
    $dec = $aes.CreateDecryptor()
    $cs = New-Object System.Security.Cryptography.CryptoStream($inStream,$dec,[System.Security.Cryptography.CryptoStreamMode]::Read)

    $hb = New-Object System.Collections.Generic.List[byte]
    $nl = 0
    while ($nl -lt 2) {
      $b = $cs.ReadByte()
      if ($b -lt 0) { throw 'Decryption failed: wrong key or corrupt data' }
      if ($b -eq 10) { $nl++ }
      $hb.Add([byte]$b)
    }
    $header = [System.Text.Encoding]::UTF8.GetString($hb.ToArray())
    $parts = $header -split "\`n"
    $filename = $parts[0].Trim()
    $expectedHash = $parts[1].Trim().ToLower()
    $invalid = [System.IO.Path]::GetInvalidFileNameChars() -join ''
    $filename = ($filename -replace ('[' + [regex]::Escape($invalid) + ']'), '_')
    if ([string]::IsNullOrWhiteSpace($filename)) { $filename = 'restored.bin' }

    $destDir = Split-Path -Parent $InputFile
    $destFile = Join-Path $destDir $filename
    if (Test-Path -LiteralPath $destFile) {
      $stem = [System.IO.Path]::GetFileNameWithoutExtension($filename)
      $ext  = [System.IO.Path]::GetExtension($filename)
      $destFile = Join-Path $destDir ($stem + '_' + (Get-Date -Format 'HHmmss') + $ext)
    }

    Write-Host ('[1/3] Original filename : ' + $filename) -ForegroundColor Cyan
    Write-Host ('[2/3] Expected SHA-256  : ' + $expectedHash) -ForegroundColor Cyan
    Write-Host '[3/3] Decrypting and writing file...' -ForegroundColor Cyan
    $out = [System.IO.File]::Create($destFile)
    try { $cs.CopyTo($out) } finally { $out.Close() }
    $cs.Close()

    $actual = (Get-FileHash -LiteralPath $destFile -Algorithm SHA256).Hash.ToLower()
    Write-Host ''
    Write-Host ('    Saved to: ' + $destFile) -ForegroundColor Cyan
    if ($actual -eq $expectedHash) {
      Write-Host '[SUCCESS] SHA-256 verified. File is intact.' -ForegroundColor Green
    } else {
      Write-Host '[WARNING] SHA-256 MISMATCH! Wrong key or corrupted file.' -ForegroundColor Red
      Write-Host ('    Actual: ' + $actual) -ForegroundColor Yellow
    }
  } finally { $inStream.Close() }
} catch {
  Write-Host ''
  $msg = $_.Exception.Message
  if ($msg -match 'Padding|Illegal char|wrong key|Base64|bad header') { $msg = 'Wrong key or corrupted/incomplete data. Please re-check the KEY and that you copied the FULL text.' }
  Write-Host ('[ERROR] ' + $msg) -ForegroundColor Red
}

`;

function render() {
  box.className = '';
  box.innerHTML = `
    <div class="result-box" style="margin-top:0;">
      <h2 class="result-title">${S('sp.title')}</h2>

      <div style="text-align:left; margin-bottom:20px;">
        <h3>${S('sp.basicTitle')}</h3>
        <ol class="steps">
          <li>${H('sp.basic1')}</li>
          <li>${H('sp.basic2')}</li>
          <li>${H('sp.basic3')}</li>
        </ol>

        <h3 style="margin-top:20px;">${S('sp.blockedTitle')}</h3>
        <p class="muted" style="font-size:14px">${H('sp.blockedDesc')}</p>
        <ol class="steps">
          <li>${H('sp.blocked1')}</li>
          <li>${H('sp.blocked2')}</li>
          <li>${H('sp.blocked3')}</li>
          <li>${H('sp.blocked4')}</li>
        </ol>
        <div class="note">${H('sp.tip')}</div>
      </div>

      <hr class="sep">

      <h3>${S('sp.scriptTitle')}</h3>
      <p class="faint" style="font-size:12px; margin-bottom:10px;">${H('sp.scriptDesc')}</p>
      <div class="codearea">
        <textarea id="codeArea" class="textpaste" readonly></textarea>
        <button id="copyCodeBtn" class="primary accent" data-i18n="sp.copyCode">${t('sp.copyCode')}</button>
      </div>
      <a class="back" href="/" style="margin-top:16px">${S('common.backHome')}</a>
    </div>`;

  $('#codeArea').value = decryptorBat;
  $('#copyCodeBtn').onclick = async () => {
    await copy(decryptorBat);
    const btn = $('#copyCodeBtn');
    I18N.setKey(btn, 'common.copied');
    clearTimeout(btn._flash);
    btn._flash = setTimeout(() => I18N.setKey(btn, 'sp.copyCode'), 2000);
  };
}
render();
