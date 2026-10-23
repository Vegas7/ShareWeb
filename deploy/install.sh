#!/usr/bin/env bash
# 安装或更新 ShareWeb (Debian 12/13)。在仓库根目录运行:  sudo bash deploy/install.sh
# 可重复执行: 已有的 .env、数据库和已存文件不会被覆盖, 只更新代码并重启服务。
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "请用 sudo 运行"; exit 1; }
SRC=$(cd "$(dirname "$0")/.." && pwd)
APP=/opt/shareweb

apt-get install -y -q python3 python3-venv rsync curl >/dev/null
id -u shareweb >/dev/null 2>&1 || useradd --system --home "$APP" --shell /usr/sbin/nologin shareweb

mkdir -p "$APP"/{data,database,logs,geoip}
# 代码整体同步 (--delete: 仓库里删掉的文件部署目录也删), 数据目录不动
rsync -a --delete --exclude __pycache__ "$SRC/app/" "$APP/app/"
rsync -a --delete "$SRC/web/" "$APP/web/"
install -m 644 "$SRC/requirements.txt" "$APP/requirements.txt"
install -m 755 "$SRC/deploy/update-geoip.sh" "$APP/geoip/update-geoip.sh"

if [ ! -f "$APP/.env" ]; then
  install -m 600 "$SRC/.env.example" "$APP/.env"
  NEW_ENV=1
fi

[ -x "$APP/venv/bin/python" ] || python3 -m venv "$APP/venv"
"$APP/venv/bin/pip" install -q --upgrade pip
"$APP/venv/bin/pip" install -q -r "$APP/requirements.txt"
chown -R shareweb:shareweb "$APP"
chmod 600 "$APP/.env"

install -m 644 "$SRC"/deploy/systemd/shareweb*.{service,timer} /etc/systemd/system/
systemctl daemon-reload
systemctl enable -q shareweb.service shareweb-cleanup.timer shareweb-geoip.timer
# 首次安装时下载 IP 地理位置库 (失败不影响主程序, 只是访客列表没有国家信息)
[ -f "$APP/geoip/dbip-country-lite.mmdb" ] || systemctl start shareweb-geoip.service || true

if [ "${NEW_ENV:-0}" = "1" ]; then
  echo ">> 已生成 $APP/.env —— 请先修改管理员密码和域名, 再执行: sudo systemctl restart shareweb"
fi
systemctl restart shareweb.service
sleep 2
echo ">> 健康检查: $(curl -s http://127.0.0.1:8000/healthz || echo '失败, 查看: journalctl -u shareweb -n 50')"
echo ">> 反向代理: 参考 deploy/Caddyfile.example"
