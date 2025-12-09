#!/bin/bash

echo "=== Setting bandwidth limits based on link configuration ==="

# ホスト名を取得
HOSTNAME=$(hostname)
echo "Configuring bandwidth limit for: $HOSTNAME"

# 帯域幅設定
BANDWIDTH_1G="1000mbit"
BANDWIDTH_05G="500mbit"

# ネットワーク名からIPv6サブネットへのマッピング（docker-compose.ymlより）
# 1.0G リンク: r1-r2, r1-r3, r2-r4, r2-r5, r3-r5, r3-r6, r11-r14, r12-r14, r12-r15, r13-r15, r14-r16, r15-r16
# 0.5G リンク: r4-r7, r4-r8, r5-r8, r5-r9, r6-r9, r6-r10, r7-r11, r8-r11, r8-r12, r9-r12, r9-r13, r10-r13

# 1.0Gリンクのサブネット
SUBNETS_1G=(
    "fd01:1::"    # r1-r2
    "fd01:16::"   # r1-r3
    "fd01:2::"    # r2-r4
    "fd01:4::"    # r2-r5
    "fd01:17::"   # r3-r5
    "fd01:15::"   # r3-r6
    "fd01:9::"    # r11-r14
    "fd01:c::"    # r12-r14
    "fd01:d::"    # r12-r15
    "fd01:f::"    # r13-r15
    "fd01:a::"    # r14-r16
    "fd01:e::"    # r15-r16
)

# 0.5Gリンクのサブネット
SUBNETS_05G=(
    "fd01:3::"    # r4-r7
    "fd01:6::"    # r4-r8
    "fd01:5::"    # r5-r8
    "fd01:12::"   # r5-r9
    "fd01:18::"   # r6-r9
    "fd01:14::"   # r6-r10
    "fd01:8::"    # r7-r11
    "fd01:7::"    # r8-r11
    "fd01:b::"    # r8-r12
    "fd01:11::"   # r9-r12
    "fd01:10::"   # r9-r13
    "fd01:13::"   # r10-r13
)

# インターフェースのIPv6アドレスからサブネットを取得する関数
get_subnet() {
    local ip=$1
    # IPv6アドレスの先頭部分（/64サブネット）を抽出
    echo "$ip" | sed 's/::[^:]*$/::/'
}

# サブネットが1.0Gリンクかチェック
is_1g_link() {
    local subnet=$1
    for s in "${SUBNETS_1G[@]}"; do
        if [[ "$subnet" == "$s" ]]; then
            return 0
        fi
    done
    return 1
}

# サブネットが0.5Gリンクかチェック
is_05g_link() {
    local subnet=$1
    for s in "${SUBNETS_05G[@]}"; do
        if [[ "$subnet" == "$s" ]]; then
            return 0
        fi
    done
    return 1
}

# lo以外の全インターフェースに帯域制限を設定
for iface in $(ip link show | grep -E '^[0-9]+:' | cut -d: -f2 | cut -d@ -f1 | tr -d ' ' | grep -v '^lo$'); do
    # インターフェースのIPv6アドレスを取得
    ipv6_addr=$(ip -6 addr show dev "$iface" 2>/dev/null | grep 'inet6 fd01:' | awk '{print $2}' | cut -d'/' -f1 | head -1)
    
    if [[ -z "$ipv6_addr" ]]; then
        echo "Skipping $iface: No fd01:: IPv6 address found"
        continue
    fi
    
    # サブネットを取得
    subnet=$(get_subnet "$ipv6_addr")
    
    # 帯域幅を決定
    if is_1g_link "$subnet"; then
        BANDWIDTH="$BANDWIDTH_1G"
        LINK_TYPE="1.0G"
    elif is_05g_link "$subnet"; then
        BANDWIDTH="$BANDWIDTH_05G"
        LINK_TYPE="0.5G"
    else
        echo "Skipping $iface ($ipv6_addr): Unknown subnet $subnet"
        continue
    fi
    
    echo "Setting $BANDWIDTH limit on $iface ($ipv6_addr) - $LINK_TYPE link"
    
    # 既存のqdisc設定を削除（エラーを無視）
    tc qdisc del dev $iface root 2>/dev/null || true
    
    # HTB (Hierarchical Token Bucket) qdiscを設定
    tc qdisc add dev $iface root handle 1: htb default 10
    
    # 帯域クラスを作成（burst/cburstを大きくしてパケットロスを防止）
    tc class add dev $iface parent 1: classid 1:10 htb rate $BANDWIDTH ceil $BANDWIDTH burst 256k cburst 256k
    
    echo "✓ $iface: $BANDWIDTH limit applied (burst 256k) - $LINK_TYPE"
done

echo ""
echo "=== Bandwidth limit configuration complete ==="
echo "Link bandwidth configuration:"
echo "  1.0G: r1-r2, r1-r3, r2-r4, r2-r5, r3-r5, r3-r6"
echo "  0.5G: r4-r7, r4-r8, r5-r8, r5-r9, r6-r9, r6-r10"
echo "  0.5G: r7-r11, r8-r11, r8-r12, r9-r12, r9-r13, r10-r13"
echo "  1.0G: r11-r14, r12-r14, r12-r15, r13-r15, r14-r16, r15-r16"

# 設定の確認
echo ""
echo "=== Current tc qdisc settings ==="
for iface in $(ip link show | grep -E '^[0-9]+:' | cut -d: -f2 | cut -d@ -f1 | tr -d ' ' | grep -v '^lo$'); do
    echo "Interface: $iface"
    tc qdisc show dev $iface 2>/dev/null || echo "  No qdisc configured"
done
