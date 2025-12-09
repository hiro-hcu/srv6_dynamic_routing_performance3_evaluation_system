#!/bin/bash
set -e

echo "Starting r16 router with SSH support..."

# SRv6設定を適用
echo "Setting up SRv6..."
/usr/local/bin/srv6_setup.sh

# 帯域制限を適用
echo "Setting up bandwidth limits..."
/usr/local/bin/set_bandwidth_limit.sh


# MACアドレスを設定（external-server側インターフェース）
# SRv6セットアップ後にIPアドレスが設定されてから実行
echo "Setting MAC address for external-server interface..."
sleep 2  # インターフェースの初期化を待つ
for iface in /sys/class/net/*; do
    ifname=$(basename $iface)
    if ip -6 addr show dev $ifname 2>/dev/null | grep -q "fd03:1::11"; then
        echo "Found external-server interface: $ifname"
        ip link set $ifname address 2e:7f:2d:e9:34:b8 2>/dev/null && \
            echo "MAC address set to 2e:7f:2d:e9:34:b8 on $ifname" || \
            echo "Warning: Could not set MAC address on $ifname"
        break
    fi
done

# SNMPサービスを開始
echo "Starting SNMP service..."
service snmpd start

# SSHサービスを開始
echo "Starting SSH service..."
service ssh start

# SSH設定の確認
echo "SSH service status:"
service ssh status

echo "SSH is listening on:"
ss -tlnp | grep :22 || echo "SSH port not found"

echo "r16 router startup complete!"
echo "SSH access: ssh root@fd02:1::11 (password: @k@n@3>ki)"

# コンテナを継続実行
tail -f /dev/null
