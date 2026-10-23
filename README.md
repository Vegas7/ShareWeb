# ShareWeb

一个自托管的文件中转站：拖入文件或粘贴文字，得到一个 4 位提取码和分享链接，对方输入提取码或打开链接即可下载。

## 功能

- **文件 / 文字分享**：流式上传（不经过临时目录），上传前在浏览器里算 SHA-256，服务器已有相同文件时直接复用。
- **提取码**：4 位数字；输错有冷却，多次输错自动拉黑。提取码 `0000` 打开使用说明页。
- **加密下载**：每个分享有独立的 AES-256 密钥，可下载加密后的 `.dat`，或在网页里生成加密文本复制带走，
  用说明页提供的 Windows 脚本还原并校验 SHA-256，适合内容检测较严的网络环境。
- **GitHub 镜像（可选）**：把文件同步到一个 GitHub 私有仓库，提供短时效的 GitHub 下载直链。
- **在线预览**：图片直接显示，音视频在线播放。
- **本地历史**：首页列出本机上传 / 收到过的分享，并标出已过期或已删除的条目。
- **管理后台** `/admin`：
  - 总览：统计数字、每日上传 / 下载趋势、按类型的存储占用、磁盘空间、访客来源国家
  - 文件管理：排序、批量删除、锁定（锁定的文件不过期、不会被清理）
  - 安全设置：访客 IP 列表（含国家与运营商），封禁 / 解封
  - 高级设置：单文件大小上限（500 MB / 1 GB / 4 GB / 不限 / 自定义），磁盘不足时自动删除最旧的文件
- 中文 / English 界面，亮色 / 暗色主题。

## 目录结构

```
app/                  后端 (FastAPI)
  main.py             路由
  services.py         分享的创建、提取、删除、清理
  storage.py          上传落盘
  app_settings.py     后台可修改的设置 (单文件上限、自动清理)
  database.py         SQLite 表结构
  crypto.py           加密下载容器 (AES-256-CBC)
  github_mirror.py    GitHub 镜像
  geoip.py            访客 IP 地理位置 (本地 DB-IP Lite 库)
web/                  前端 (原生 HTML / CSS / JS, 无构建步骤)
  static/js/prefs.js  语言 / 主题切换与各页面共用的小工具
deploy/
  install.sh          安装 / 更新脚本
  systemd/            服务与定时任务
  Caddyfile.example   反向代理示例
  update-geoip.sh     每月更新 IP 地理位置库
.env.example          配置示例
```

## 部署

需要 Debian 12/13（其他 Linux 发行版自行调整 `deploy/install.sh`）和 Python 3.11+。

```bash
git clone https://github.com/Vegas7/ShareWeb.git
cd ShareWeb
sudo bash deploy/install.sh
```

脚本会把代码装到 `/opt/shareweb`、创建 `shareweb` 系统用户和虚拟环境、安装 systemd 服务（主程序监听 `127.0.0.1:8000`）。
首次运行会生成 `/opt/shareweb/.env`，**改好管理员密码和域名**后重启：

```bash
sudo systemctl restart shareweb
```

再参考 `deploy/Caddyfile.example` 配置反向代理（Caddy 会自动申请 HTTPS 证书）。

**更新**：`git pull` 后再执行一次 `sudo bash deploy/install.sh`。`.env`、数据库和已存文件不会被覆盖。

运行时数据都在 `/opt/shareweb` 下：`data/`（已存文件）、`database/share.db`、`logs/`、`geoip/`。

## 本地开发

```bash
python3 -m venv venv && venv/bin/pip install -r requirements.txt
mkdir -p data database logs
SHAREWEB_BASE_DIR=$PWD SHAREWEB_ADMIN_PASSWORD=dev venv/bin/uvicorn app.main:app --reload
```

打开 http://localhost:8000 ，后台在 http://localhost:8000/admin （密码 `dev`）。
前端改完刷新即可，没有构建步骤；改了 JS / CSS 记得把 HTML 里对应的 `?v=` 版本号加一，避免浏览器用旧缓存。

## 分支

- `main`：线上正在用的版本
- `preview`：新界面风格（Liquid Glass）的试验分支

## 第三方资源

- IP 地理位置：[DB-IP Lite](https://db-ip.com)（CC BY 4.0），部署时下载，不随仓库分发
- 提取码数字字体：[Tilt Neon](https://fonts.google.com/specimen/Tilt+Neon)（SIL Open Font License 1.1），仅含 0–9 子集
- GitHub 图标：[Octicons](https://github.com/primer/octicons)（MIT）
