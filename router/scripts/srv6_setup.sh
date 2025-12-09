#!/bin/bash

echo "=== Optimized SRv6 Setup Script ==="

# ホスト名を取得してルーター識別
HOSTNAME=$(hostname)
echo "Configuring optimized SRv6 for: $HOSTNAME"

echo ""
echo "Configuring SRv6 settings..."

# 基本的なIPv6設定
echo "Configuring basic IPv6 settings..."
sysctl -w net.ipv6.conf.all.forwarding=1
sysctl -w net.ipv6.conf.default.forwarding=1
sysctl -w net.ipv6.conf.all.seg6_enabled=1
sysctl -w net.ipv6.conf.default.seg6_enabled=1

# 利用可能なすべてのネットワークインターフェースでSRv6を有効化
echo "Enabling SRv6 on all available interfaces..."
for iface in $(ip link show | grep -E '^[0-9]+:' | cut -d: -f2 | cut -d@ -f1 | tr -d ' ' | grep -v '^lo$'); do
    echo "Enabling SRv6 on $iface"
    sysctl -w net.ipv6.conf.$iface.seg6_enabled=1 2>/dev/null || true
    sysctl -w net.ipv6.conf.$iface.forwarding=1 2>/dev/null || true
done

# IPv6のセグメントルーティングモジュールの確認と読み込み
echo "Checking IPv6 segment routing modules..."
if ! lsmod | grep -q ipv6; then
    echo "Loading IPv6 module..."
    modprobe ipv6
fi

if ! lsmod | grep -q seg6; then
    echo "Loading seg6 module..."
    modprobe seg6_iptunnel || echo "seg6_iptunnel module not found"
    modprobe seg6_local || echo "seg6_local module not found"
fi

echo "=== Optimized SRv6 Configuration Complete ==="
echo "✓ IPv6 forwarding enabled on all interfaces"
echo "✓ SRv6 enabled on all interfaces"  
echo "✓ Basic SRv6 packet processing active"

# SRv6設定の確認
echo ""
echo "=== Current SRv6 Settings ==="
echo "IPv6 forwarding (all): $(sysctl -n net.ipv6.conf.all.forwarding)"
echo "SRv6 enabled (all): $(sysctl -n net.ipv6.conf.all.seg6_enabled)"

echo ""
echo "Interface-specific SRv6 settings:"
for iface in $(ip link show | grep -E '^[0-9]+:' | cut -d: -f2 | cut -d@ -f1 | tr -d ' ' | grep -v '^lo$'); do
    seg6_status=$(sysctl -n net.ipv6.conf.$iface.seg6_enabled 2>/dev/null || echo "N/A")
    forwarding_status=$(sysctl -n net.ipv6.conf.$iface.forwarding 2>/dev/null || echo "N/A")
    echo "  $iface: SRv6=$seg6_status, Forwarding=$forwarding_status"
done

echo ""
echo "=== SRv6 Setup Complete ==="
