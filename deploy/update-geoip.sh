#!/bin/bash
# 下载 DB-IP Lite 国家与 ASN 数据库 (CC BY 4.0, https://db-ip.com), 校验后原子替换。
# 由 shareweb-geoip.timer 每月运行; 当月文件未发布时退回上个月。
set -euo pipefail
DIR=/opt/shareweb/geoip
PY=/opt/shareweb/venv/bin/python
cd "$DIR"
this_month=$(date -u +%Y-%m)
last_month=$(date -u -d "$(date -u +%Y-%m-01) -1 month" +%Y-%m)
for kind in country asn; do
  got=""
  for m in "$this_month" "$last_month"; do
    if curl -fsSL --max-time 600 -o "$kind.mmdb.gz.tmp" "https://download.db-ip.com/free/dbip-$kind-lite-$m.mmdb.gz"; then got=$m; break; fi
  done
  if [ -z "$got" ]; then rm -f "$kind.mmdb.gz.tmp"; echo "download failed: $kind" >&2; exit 1; fi
  gunzip -c "$kind.mmdb.gz.tmp" > "$kind.mmdb.tmp"
  rm -f "$kind.mmdb.gz.tmp"
  # 能打开且能查到公网地址才替换, 避免坏文件覆盖好文件
  "$PY" -c 'import maxminddb,sys; r=maxminddb.open_database(sys.argv[1]); assert r.get("8.8.8.8"), "lookup failed"' "$kind.mmdb.tmp"
  mv -f "$kind.mmdb.tmp" "dbip-$kind-lite.mmdb"
  echo "updated dbip-$kind-lite.mmdb ($got)"
done
