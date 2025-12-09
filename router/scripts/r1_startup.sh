#!/bin/bash
set -e

echo "Starting r1 router with SSH support..."

# SRv6設定を適用
echo "Setting up SRv6..."
/usr/local/bin/srv6_setup.sh

# 帯域制限を適用
echo "Setting up bandwidth limits..."
/usr/local/bin/set_bandwidth_limit.sh


# MACアドレスを設定（external-upf側インターフェース）
# SRv6セットアップ後にIPアドレスが設定されてから実行
echo "Setting MAC address for external-upf interface..."
sleep 2  # インターフェースの初期化を待つ
for iface in /sys/class/net/*; do
    ifname=$(basename $iface)
    if ip -6 addr show dev $ifname 2>/dev/null | grep -q "fd00:1::12"; then
        echo "Found external-upf interface: $ifname"
        ip link set $ifname address 2e:7f:2d:e9:34:b7 2>/dev/null && \
            echo "MAC address set to 2e:7f:2d:e9:34:b7 on $ifname" || \
            echo "Warning: Could not set MAC address on $ifname"
        
        # 静的NDエントリを追加（UPF: fd00:1::1, MAC: a0:36:9f:e1:ea:72）
        echo "Adding static ND entry for UPF (fd00:1::1)..."
        ip -6 neigh add fd00:1::1 lladdr a0:36:9f:e1:ea:72 dev $ifname nud permanent 2>/dev/null && \
            echo "Static ND entry added: fd00:1::1 -> a0:36:9f:e1:ea:72 on $ifname" || \
            echo "Warning: Could not add static ND entry (may already exist)"
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

echo "r1 router startup complete!"
echo "SSH access: ssh root@fd02:1::2 (password: @k@n@3>ki)"

# コンテナを継続実行
tail -f /dev/null
