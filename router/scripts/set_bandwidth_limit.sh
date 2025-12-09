#!/bin/bash

echo "=== Setting 1Gbps bandwidth limit on all interfaces ==="

# ホスト名を取得
HOSTNAME=$(hostname)
echo "Configuring bandwidth limit for: $HOSTNAME"

# 1Gbps = 1000Mbit
BANDWIDTH="1000mbit"

# lo以外の全インターフェースに帯域制限を設定
for iface in $(ip link show | grep -E '^[0-9]+:' | cut -d: -f2 | cut -d@ -f1 | tr -d ' ' | grep -v '^lo$'); do
    echo "Setting $BANDWIDTH limit on $iface"
    
    # 既存のqdisc設定を削除（エラーを無視）
    tc qdisc del dev $iface root 2>/dev/null || true
    
    # HTB (Hierarchical Token Bucket) qdiscを設定
    tc qdisc add dev $iface root handle 1: htb default 10
    
    # 1Gbpsのクラスを作成（burst/cburstを大きくしてパケットロスを防止）
    # burst 256k: 約170パケット分のバーストを許容（1Gbpsで約2msのバースト許容時間）
    tc class add dev $iface parent 1: classid 1:10 htb rate $BANDWIDTH ceil $BANDWIDTH burst 256k cburst 256k
    
    echo "✓ $iface: $BANDWIDTH limit applied (burst 256k)"
done

echo ""
echo "=== Bandwidth limit configuration complete ==="
echo "All interfaces (except lo) are limited to $BANDWIDTH"

# 設定の確認
echo ""
echo "=== Current tc qdisc settings ==="
for iface in $(ip link show | grep -E '^[0-9]+:' | cut -d: -f2 | cut -d@ -f1 | tr -d ' ' | grep -v '^lo$'); do
    echo "Interface: $iface"
    tc qdisc show dev $iface 2>/dev/null || echo "  No qdisc configured"
done
