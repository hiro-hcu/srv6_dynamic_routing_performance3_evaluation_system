# SRv6 ルーティング設定ガイド

> **概要**: 本ドキュメントでは、SRv6ネットワークにおける高度なルーティングテーブル設定と End 関数の設定について説明します。

---

## 📋 目次

1. [マルチテーブルルーティング](#-マルチテーブルルーティング)
2. [nftables によるフローラベルマーキング](#-nftables-によるフローラベルマーキング)
3. [SRv6 End 関数設定](#-srv6-end-関数設定)
4. [動作確認](#-動作確認)
5. [トラブルシューティング](#-トラブルシューティング)
6. [参考資料](#-参考資料)

---

## 📊 マルチテーブルルーティング

### カスタムルーティングテーブルの追加

`/etc/iproute2/rt_tables` に以下を追加:

```
101 rt_table1
102 rt_table2
103 rt_table3
```

### fwmark ベースのルーティングルール

| テーブル | fwmark | 優先度 | 用途 |
|----------|--------|--------|------|
| rt_table1 | 4 | 1000 | 高優先度（URLLC相当） |
| rt_table2 | 6 | 1001 | 中優先度（eMBB相当） |
| rt_table3 | 9 | 1002 | 低優先度（mMTC相当） |

### 設定コマンド

```bash
# 基本設定
sudo ip -6 rule add fwmark 4 table rt_table1
sudo ip -6 rule add fwmark 6 table rt_table2
sudo ip -6 rule add fwmark 9 table rt_table3

# 優先度を明示的に指定する場合
sudo ip -6 rule add pref 1000 fwmark 4 table rt_table1
sudo ip -6 rule add pref 1001 fwmark 6 table rt_table2
sudo ip -6 rule add pref 1002 fwmark 9 table rt_table3
```

### 確認コマンド

```bash
# ルール一覧
ip -6 rule list | grep fwmark

# 期待される出力
# 1000: from all fwmark 0x4 lookup rt_table1
# 1001: from all fwmark 0x6 lookup rt_table2
# 1002: from all fwmark 0x9 lookup rt_table3
```

---

## 🏷️ nftables によるフローラベルマーキング

### 概要

IPv6 フローラベルに基づいてパケットにマークを付与し、適切なルーティングテーブルに振り分けます。

### フローラベルマッピング

| フローラベル | fwmark | 対応テーブル | QoS クラス |
|--------------|--------|--------------|------------|
| `0xfffc4` | 4 | rt_table1 | 高優先度 |
| `0xfffc6` | 6 | rt_table2 | 中優先度 |
| デフォルト | 9 | rt_table3 | 低優先度 |

### r1（入口ルータ）の設定

```bash
# mangle テーブル作成
sudo nft add table ip6 mangle

# prerouting チェーン追加
sudo nft 'add chain ip6 mangle prerouting { type filter hook prerouting priority mangle; }'

# フローラベルベースのマーキングルール
sudo nft 'add rule ip6 mangle prerouting ip6 flowlabel 0xfffc4 mark set 4'
sudo nft 'add rule ip6 mangle prerouting ip6 flowlabel 0xfffc6 mark set 6'
sudo nft 'add rule ip6 mangle prerouting mark 0 mark set 9'  # デフォルト
```

### r16（出口ルータ）の設定

```bash
# mangle_r16 テーブル作成
sudo nft add table ip6 mangle_r16

# prerouting チェーン追加
sudo nft 'add chain ip6 mangle_r16 prerouting { type filter hook prerouting priority mangle; }'

# フローラベルベースのマーキングルール
sudo nft 'add rule ip6 mangle_r16 prerouting ip6 flowlabel 0xfffc4 mark set 4'
sudo nft 'add rule ip6 mangle_r16 prerouting ip6 flowlabel 0xfffc6 mark set 6'
sudo nft 'add rule ip6 mangle_r16 prerouting mark 0 mark set 9'  # デフォルト
```

### 確認コマンド

```bash
# r1 のルール確認
sudo nft list table ip6 mangle | grep flowlabel

# r16 のルール確認
sudo nft list table ip6 mangle_r16 | grep flowlabel
```

---

## 🔧 SRv6 End 関数設定

### 概要

SRv6ネットワークでは、中間ノードが **End 関数**（Local SID）を使用してセグメントを処理します。

### ノード役割

| ノード | 役割 | 関数タイプ | 説明 |
|--------|------|------------|------|
| r1 | 入口 | - | パケットをカプセル化 |
| r2〜r15 | 中間 | End | セグメント処理・転送 |
| r16 | 出口 | End.DX6 | デカプセル化・転送 |

### SRv6 関数タイプ

| 関数 | 説明 | 用途 |
|------|------|------|
| **End** | 標準セグメント処理 | 中間ノード |
| **End.DX6** | デカプセル化 + IPv6転送 | 出口ノード |
| **End.DT4/DT6** | デカプセル化 + テーブル検索 | 本システムでは未使用 |

### Local SID 設定一覧

| ルータ | Local SID | 設定コマンド |
|--------|-----------|--------------|
| r2 | `fd01:3::12` | `ip -6 route add fd01:3::12/128 encap seg6local action End dev lo` |
| r2 | `fd01:9::12` | `ip -6 route add fd01:9::12/128 encap seg6local action End dev lo` |
| r3 | `fd01:7::12` | `ip -6 route add fd01:7::12/128 encap seg6local action End dev lo` |
| r4 | `fd01:4::12` | `ip -6 route add fd01:4::12/128 encap seg6local action End dev lo` |
| r5 | `fd01:6::12` | `ip -6 route add fd01:6::12/128 encap seg6local action End dev lo` |
| r6 | `fd01:5::1` | `ip -6 route add fd01:5::1/128 encap seg6local action End.DX6 nh6 fd01:5::12 dev <if>` |

> **Note**: 設定は `srv6_setup.sh` スクリプトによって自動的に適用されます。

### SRv6 パス例

```
r1 → r2 → r4 → r6 → Server の場合:

[1] r1: パケットをカプセル化
    └─ セグメントリスト: [fd01:3::12, fd01:4::12, fd01:5::1]

[2] r2: fd01:3::12 にマッチ
    └─ End 関数処理 → r4 へ転送

[3] r4: fd01:4::12 にマッチ
    └─ End 関数処理 → r6 へ転送

[4] r6: fd01:5::1 にマッチ
    └─ End.DX6 関数でデカプセル化 → Server へ転送

[5] Server: 元の IPv6 パケットを受信
```

---

## ✅ 動作確認

### Local SID 設定確認

```bash
# seg6local ルート確認
ip -6 route show | grep "seg6local"

# 特定 SID の確認
ip -6 route get <SID_ADDRESS>

# 例: r2 の SID 確認
ip -6 route get fd01:3::12
```

### SRv6 機能テスト

| テスト | コマンド | 説明 |
|--------|----------|------|
| 基本接続 | `ping6 -c 3 fd01:5::12` | r1 から r6 への接続 |
| SRv6 経路追加 | `ip -6 route add fd01:5::/64 encap seg6 mode encap segs fd01:3::12,fd01:4::12 dev eth1` | セグメントリスト設定 |
| fwmark 確認 | `ip -6 rule list \| grep fwmark` | マーキングルール |
| 帯域制御確認 | `tc class show dev eth0 \| grep rate` | HTB 設定 |

### デバッグコマンド

```bash
# 全 IPv6 ルート表示
ip -6 route show

# SRv6 ルートのみ
ip -6 route show | grep seg6

# インターフェース確認
ip -6 addr show

# SRv6 トラフィック監視（SRH ヘッダ）
tcpdump -i any -n ip6 and 'ip6[6] = 43'
```

---

## 🔍 トラブルシューティング

### よくある問題と解決策

| 問題 | 原因 | 解決策 |
|------|------|--------|
| SID が設定されない | ホスト名不一致 | ホスト名が r2, r3, r4, r5 等と一致するか確認 |
| Permission denied | 権限不足 | コンテナを `privileged: true` で起動 |
| seg6local 動作しない | カーネルモジュール未ロード | `seg6_local` モジュールの確認 |
| ルート競合 | 既存ルートとの衝突 | `ip -6 route show` で確認・削除 |
| nftables ルールなし | 初期化未完了 | `controller` ログで Phase 2 完了を確認 |

### ログ確認

```bash
# コンテナログ
docker logs <container_name>

# SRv6 関連カーネルメッセージ
dmesg | grep -i seg6

# controller 初期化確認
docker logs controller | grep "✅"
```

### 設定リセット

```bash
# nftables リセット
sudo nft flush table ip6 mangle
sudo nft delete table ip6 mangle

# ルーティングルール削除
sudo ip -6 rule del fwmark 4 table rt_table1
sudo ip -6 rule del fwmark 6 table rt_table2
sudo ip -6 rule del fwmark 9 table rt_table3
```

---

## 📚 参考資料

### RFC & 標準

| 標準 | 説明 |
|------|------|
| [RFC 8754](https://tools.ietf.org/html/rfc8754) | IPv6 Segment Routing Header (SRH) |
| [RFC 8986](https://tools.ietf.org/html/rfc8986) | SRv6 Network Programming |

### Linux 実装

| リソース | 説明 |
|----------|------|
| [Linux SRv6 Guide](https://www.kernel.org/doc/html/latest/networking/seg6-sysctl.html) | カーネル SRv6 実装 |
| [iproute2 seg6](https://man7.org/linux/man-pages/man8/ip-route.8.html) | ip route seg6 コマンド |
| [nftables](https://netfilter.org/projects/nftables/) | パケットフィルタリング |

---

<div align="center">

**ユースケース**

QoS ベースルーティング | トラフィックエンジニアリング | サービス差別化 | SRv6 経路選択

</div>
