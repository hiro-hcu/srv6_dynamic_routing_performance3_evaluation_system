# SRv6 動的経路制御 性能評価システム

5G と Data Network の End-to-End における QoS ベーストラフィックエンジニアリングを実現するための、Docker ベース SRv6（Segment Routing over IPv6）動的経路制御システムです。

---

## 📖 研究背景

### 5G ネットワークと QoS 制御の課題

第五世代移動通信システム（5G）では、多様化するサービス要求に対応するため、単一の物理インフラ上で柔軟にネットワークを構築する技術の検討が進められています。5G の主な特徴として以下が挙げられます：

| 特徴 | 説明 |
|------|------|
| **eMBB** (enhanced Mobile Broadband) | 高速大容量通信 |
| **URLLC** (Ultra-Reliable and Low Latency Communications) | 高信頼・低遅延通信 |
| **mMTC** (massive Machine Type Communications) | 多数同時接続通信 |

これらの要求を満たすために、5G では **ネットワークスライシング**、**エッジコンピューティング**、**5G New Radio** など様々な技術が導入されています。特にネットワークスライシングは、物理ネットワークを仮想的に分割し、サービスごとに異なる帯域幅・遅延・信頼性といった通信要件を満たすネットワークを動的に提供する仕組みです。

### 現状の課題

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        End-to-End 通信の課題                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [UE] ──── [5G RAN] ──── [5G Core] ──── [Data Network] ──── [Server]      │
│              │              │                  │                            │
│              ▼              ▼                  ▼                            │
│         ┌────────┐    ┌─────────┐       ┌───────────┐                      │
│         │QoS制御 │    │スライス │       │ベストエフォート│  ← 課題          │
│         │  可能  │    │  制御   │       │ (BGP/OSPF) │                      │
│         └────────┘    └─────────┘       └───────────┘                      │
│                                                                             │
│   5G 側では QoS に基づくスライス制御・フロー制御が可能                        │
│   Data Network では従来型ルーティングプロトコル（BGP/OSPF）が主流             │
│   → アプリケーションの通信要件を考慮した経路制御ができない                    │
│   → 5G の QoS 制御能力を End-to-End で活用できていない                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 研究目的

本研究は、**Data Network においても 5G の QoS 情報を活用し、通信要件に応じた経路制御を実現する**ことで、5G と Data Network の End-to-End において QoS ベースのトラフィックエンジニアリングの実現を目的としています。

具体的には：
1. **SRv6 による QoS 対応経路制御**: IPv6 ベースのセグメントルーティング技術（SRv6）を用いて、複数の QoS に対応する SRv6 SID を動的に割り当てる仕組みを設計・実装
2. **ISP 網を想定したトポロジ**: 格子状モデルのネットワークトポロジを前提として評価環境を構築
3. **性能評価**: Data Network で 5G の QoS を反映した SRv6 経路制御を適用した場合の End-to-End 通信品質への効果を評価

---

## 🎯 本システムの位置付け

本システムは、上記の研究目的を達成するための**実験・評価プラットフォーム**として開発されました。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    本システムが実現する QoS 対応経路制御                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [UPF] ──── [r1] ═══════════════════════════════════ [r16] ──── [Server]  │
│     │         ║  SRv6 動的経路制御ネットワーク (16ルータ)   ║         │     │
│     │         ║                                              ║         │     │
│     │         ║   ┌─────────────────────────────────────┐   ║         │     │
│     │         ║   │ QoS フローラベル → SRv6 経路マッピング │   ║         │     │
│     │         ║   │  • 高優先度 (0xfffc4) → 最適経路      │   ║         │     │
│     │         ║   │  • 中優先度 (0xfffc6) → 代替経路      │   ║         │     │
│     │         ║   │  • 低優先度 (default) → 標準経路      │   ║         │     │
│     │         ║   └─────────────────────────────────────┘   ║         │     │
│     │         ╚══════════════════════════════════════════════╝         │     │
│     │                                                                   │     │
│   5G QoS                        Data Network                        アプリ  │
│   情報付与                    (SRv6 経路制御)                      ケーション│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### システムの特徴

| 特徴 | 説明 |
|------|------|
| **QoS 連携** | 5G のフローラベル情報を活用した経路選択 |
| **動的経路制御** | リアルタイムトラフィック監視に基づく最適経路計算 |
| **マルチテーブル** | 優先度別の独立したルーティングテーブル管理 |
| **ISP 網モデル** | 16 台ルータによる格子状トポロジで実環境を模擬 |
| **完全コンテナ化** | Docker による再現可能な実験環境 |

---

## 🌟 主な機能

### コア機能

| カテゴリ | 機能 | 説明 |
|----------|------|------|
| **経路制御** | 動的経路オーケストレーション | ネットワーク状況に基づくリアルタイム最適経路計算 |
| | 双方向制御 | 往路（r1→r16）と復路（r16→r1）の独立した経路管理 |
| | インテリジェント切り替え | リンク利用率閾値に基づく自動経路切り替え |
| **QoS 対応** | マルチテーブルルーティング | fwmark ベースの 3 段階 QoS 対応（高/中/低優先度） |
| | フローラベル連携 | IPv6 フローラベルによるトラフィック分類 |
| **監視・分析** | リアルタイム監視 | MRTG/RRD による 60 秒間隔のトラフィック収集（24 リンク） |
| | 性能分析 | NetworkX による最短経路最適化 |
| | トポロジ可視化 | ネットワーク状態と選択経路のリアルタイム画像出力 |
| **インフラ** | 完全コンテナ化 | 16 台ルータ + コントローラの Docker デプロイメント |
| | 自動設定 | コンテナ起動時の Phase 1 & 2 自動セットアップ |
| | 外部ノード接続 | Macvlan による実機 UPF/サーバー統合 |
| | 帯域制御 | 全インターフェース 1Gbps HTB トラフィックシェーピング |

---

## 📅 更新履歴

| 日付 | 内容 |
|------|------|
| 2025-12-11 | README 日本語化、研究背景の追加、可視化機能の強化 |
| 2025-12-01 | HTB による 1Gbps 帯域制限追加（高スループット向け burst 15k 最適化） |
| 2025-11-04 | フローラベル → マーク マッピング検証完了 |

---

## 🏗️ システムアーキテクチャ

### ネットワークトポロジ

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                 SRv6 動的経路制御 性能評価システム                                 │
│                                                                                  │
│  16台ルータ メッシュトポロジ (4x4 グリッド)                                        │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                             │ │
│  │   UPF ─── r1 ─── r2 ─── r4 ─── r7 ───┐                                     │ │
│  │  (外部)    │      │      │      │     │                                     │ │
│  │            │      │      │      │     │                                     │ │
│  │            r3 ─── r5 ─── r8 ─── r11 ──┼─── r14 ──┐                          │ │
│  │            │      │      │      │     │          │                          │ │
│  │            │      │      │      │     │          │                          │ │
│  │            r6 ─── r9 ─── r12 ───┼─────┘          r16 ─── Server             │ │
│  │            │      │      │      │                │       (外部)              │ │
│  │            │      │      │      │                │                          │ │
│  │            r10 ── r13 ── r15 ───┴──────────────────┘                         │ │
│  │                                                                             │ │
│  │  全リンク: 1Gbps帯域制限 (HTB, burst 15k)                                    │ │
│  │  監視: 24リンク RRDデータ収集 (60秒間隔)                                      │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### コントローラシステム

コントローラは集中制御プレーンとして、トラフィック監視と動的経路制御を担当します。

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    コントローラシステム (fd02:1::20)                        │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────────────┐    ┌──────────────────────────────────────────┐ │
│  │  自動初期化 (起動時)   │    │     リアルタイムコンポーネント            │ │
│  ├──────────────────────┤    ├──────────────────────────────────────────┤ │
│  │                      │    │                                          │ │
│  │  Phase 1             │    │  MRTG Poller (60秒間隔)                  │ │
│  │  ├─ r1 テーブル設定   │    │  └─ 24リンク RRDデータ収集               │ │
│  │  ├─ r16 テーブル設定  │    │                                          │ │
│  │  └─ fwmark ルール    │◄───┤  Phase 3 リアルタイムマネージャ           │ │
│  │                      │    │  ├─ 双方向経路制御                       │ │
│  │  Phase 2             │    │  ├─ マルチテーブル管理                    │ │
│  │  ├─ r1 nftables      │    │  ├─ 動的経路切り替え                     │ │
│  │  ├─ r16 nftables     │    │  └─ SRv6 ルート更新                      │ │
│  │  └─ flowlabel→mark   │    │                                          │ │
│  │                      │    └──────────────────────────────────────────┘ │
│  └──────────────────────┘                                                  │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  フローラベル → マーク → テーブル マッピング                          │  │
│  ├─────────────────────────────────────────────────────────────────────┤  │
│  │  0xfffc4 (高優先度)  →  mark 4  →  rt_table1  →  最適経路           │  │
│  │  0xfffc6 (中優先度)  →  mark 6  →  rt_table2  →  代替経路           │  │
│  │  default (低優先度)  →  mark 9  →  rt_table3  →  標準経路           │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 プロジェクト構成

```
srv6_dynamic_routing_performance_evaluation_system/
├── 📋 README.md                           # プロジェクトドキュメント
├── 🐳 docker-compose.yml                  # 16台ルータトポロジ設定
├── 📖 EXTERNAL_CONNECTION.md              # 外部UPF/サーバー接続ガイド
│
├── 🌐 router/                             # SRv6ルータインフラ
│   ├── Dockerfile                        # 基本ルータイメージ (r2-r15)
│   ├── Dockerfile_r1                     # R1 (イングレス) SSH + nftables対応
│   ├── Dockerfile_r16                    # R16 (イーグレス) SSH + nftables対応
│   ├── scripts/                          # ルータ初期化スクリプト
│   │   ├── srv6_setup.sh                 # SRv6カーネル設定
│   │   ├── set_bandwidth_limit.sh        # 1Gbps HTB帯域制御
│   │   ├── r1_startup.sh                 # R1専用起動スクリプト
│   │   └── r16_startup.sh                # R16専用起動スクリプト
│   ├── docs/                             # 技術ドキュメント
│   │   ├── advanced-routing-setup.md     # nftables + fwmarkガイド
│   │   └── srv6-end-functions.md         # SRv6関数リファレンス
│   └── snmpd/
│       └── snmpd.conf                    # SNMP監視設定
│
└── 🎛️ controller/                         # 制御プレーンシステム
    ├── Dockerfile                        # 自動初期化対応コントローラ
    ├── init_setup.py                     # 自動Phase1&2セットアップ
    │
    ├── 📊 mrtg/                          # トラフィック監視
    │   ├── mrtg_kurage.conf              # リンク別MRTG設定
    │   ├── mrtg_file/                    # RRDデータストレージ (24リンクファイル)
    │   └── rrdtool_shell/
    │       └── create_rrd.sh             # RRDデータベース初期化
    │
    ├── 📊 presentation/                   # 研究発表資料
    │   ├── README.md                     # プレゼンテーションガイド
    │   ├── diagrams/                     # システムアーキテクチャ図
    │   └── scripts/                      # ダイアグラム生成スクリプト
    │
    └── 🎯 srv6-path-orchestrator/         # コアオーケストレーションシステム
        ├── function_analysis.md          # システム機能分析
        ├── VISUALIZATION_README.md       # 可視化ガイド
        │
        ├── 🔧 Phase 1&2 セットアップスクリプト (自動実行):
        ├── r1_phase1_table_setup.py      # R1ルーティングテーブル + ルール
        ├── r1_phase2_nftables_setup.py   # R1 nftables + フローマーキング
        ├── r16_phase1_table_setup.py     # R16ルーティングテーブル + ルール
        ├── r16_phase2_nftables_setup.py  # R16 nftables + フローマーキング
        │
        └── 🚀 Phase 3 メインシステム:
            └── phase3_realtime_multi_table.py # メインオーケストレータ
```

---

## 🚀 クイックスタート

### 前提条件

| 要件 | 詳細 |
|------|------|
| Docker | Docker Engine 20.10+ および Docker Compose v2.0+ |
| OS | IPv6 対応 Linux（Ubuntu 22.04 以上で動作確認済み） |
| 権限 | コンテナネットワーキングのための root 権限 |
| NIC | 外部接続用物理 NIC（オプション、UPF/サーバー統合用） |

### 1. クローンとデプロイ

```bash
# リポジトリのクローン
git clone https://github.com/hiro-hcu/srv6_dynamic_routing_performance_evaluation_system.git
cd srv6_dynamic_routing_performance_evaluation_system

# 自動初期化付きで全コンテナをデプロイ
sudo docker compose up -d

# 完全再ビルド（更新後推奨）
sudo docker compose down && sudo docker compose build --no-cache && sudo docker compose up -d
```

### 2. システム状態の確認

```bash
# 17コンテナが起動中であることを確認（16ルータ + 1コントローラ）
sudo docker ps

# 初期化の進捗を監視
sudo docker logs -f controller
```

**期待される出力:**
```
INFO - SRv6システム初期化開始...
INFO - ✅ SSH準備完了 (r1: fd02:1::2, r16: fd02:1::11)
INFO - ✅ r1_phase1_table_setup.py 実行成功
INFO - ✅ r1_phase2_nftables_setup.py 実行成功
INFO - ✅ r16_phase1_table_setup.py 実行成功
INFO - ✅ r16_phase2_nftables_setup.py 実行成功
# INFO - 🎉 初期化完了: システムは運用可能です
```

### 3. 帯域制御の確認
```bash
# 任意のルータでHTB設定を確認（burst 15kが表示されるはず）
sudo docker exec r1 tc class show dev eth0

# 期待される出力:
# class htb 1:10 root prio 0 rate 1Gbit ceil 1Gbit burst 15125b cburst 15125b
```

### 4. 設定検証コマンド
```bash
# nftables設定の確認 (r1)
sudo docker exec -it r1 nft list table ip6 mangle
# 期待: flowlabel 0xfffc4 → mark 4, 0xfffc6 → mark 6

# ルーティングルールの確認 (r16)
sudo docker exec -it r16 ip -6 rule list
# 期待: fwmark 0x4/0x6/0x9 lookup rt_table_1/2/3

# ルーティングテーブルの確認
sudo docker exec -it r1 ip -6 route show table rt_table1
sudo docker exec -it r16 ip -6 route show table rt_table_1
```

### 5. リアルタイムオーケストレーション開始 (Phase 3)
```bash
# 双方向リアルタイム管理（継続モード）
sudo docker exec -it controller python3 /opt/app/srv6-path-orchestrator/phase3_realtime_multi_table.py

# 可視化機能付きで実行
sudo docker exec -it controller bash -c "cd /opt/app/srv6-path-orchestrator && python3 phase3_realtime_multi_table.py --mode bidirectional --visualize"

# テスト用の単発実行
sudo docker exec -it controller python3 /opt/app/srv6-path-orchestrator/phase3_realtime_multi_table.py --once

# 期待される出力:
# INFO - 🚀 双方向テーブル更新開始
# INFO - Edge r1 <-> r2: 9.633 Mbps (利用率: 0.0154)
# INFO - 往路最適経路: r1 → r2 → r4 → r7 → r11 → r14 → r16
# INFO - 復路最適経路: r16 → r14 → r11 → r7 → r4 → r2 → r1
# INFO - ✅ 双方向テーブル更新成功
```

## 🌐 外部PC接続（高度な使用法）

実機UPF/サーバーノードとの実環境テスト用:

### システムモード
- **コンテナモード**: 自己完結型テスト環境（デフォルト）
- **外部ノードモード**: Macvlanによる実機接続

### 外部PC設定
```bash
# 外部ネットワークはdocker-compose.ymlで事前設定済み:
# - external-upf: fd00:1::/64 (enp2s0f1経由macvlan)
# - external-server: fd03:1::/64 (enp2s0f0経由macvlan)

# UPF PC設定:
sudo ip -6 addr add fd00:1::1/64 dev <interface>
sudo ip -6 route add fd03:1::/64 via fd00:1::12  # r1経由

# サーバーPC設定:
sudo ip -6 addr add fd03:1::2/64 dev <interface>
sudo ip -6 route add fd00:1::/64 via fd03:1::11  # r16経由
```

📖 **詳細ガイド**: [EXTERNAL_CONNECTION.md](EXTERNAL_CONNECTION.md) を参照してください。

---

## ⚡ 性能最適化

### 帯域制御 (HTB)
全ルータインターフェースは自動的に1Gbps帯域制限で設定されます:

```bash
# 適用される設定 (set_bandwidth_limit.sh):
tc qdisc add dev $iface root handle 1: htb default 10
tc class add dev $iface parent 1: classid 1:10 htb rate 1000mbit ceil 1000mbit burst 15k cburst 15k
```

### ホストレベル最適化（推奨）
最大スループットテスト向けに、以下のホスト最適化を適用:

```bash
# NICリングバッファの拡張（サポートされている場合）
sudo ethtool -G enp2s0f0 rx 8192 tx 8192
sudo ethtool -G enp2s0f1 rx 8192 tx 8192

# カーネルソケットバッファの増加
sudo sysctl -w net.core.rmem_max=16777216
sudo sysctl -w net.core.wmem_max=16777216
sudo sysctl -w net.core.netdev_max_backlog=30000

# 設定確認
tc class show dev eth0  # burst 15125b が表示されるはず
```

---

## 🎯 システムフェーズ概要

本システムは 3 つのフェーズで構成されています。Phase 1 と Phase 2 はコンテナ起動時に自動実行され、Phase 3 は手動または自動で実行します。

### Phase 1: インフラセットアップ（自動実行）

ルーティングテーブルとルールの初期設定を行います。

| 項目 | 内容 |
|------|------|
| **ルーティングテーブル** | `rt_table1`, `rt_table2`, `rt_table3` を QoS 階層用に作成 |
| **ルール設定** | `fwmark` ベースのルーティングルールを設定 |
| **対象ルータ** | r1（イングレス）と r16（イーグレス） |

### Phase 2: トラフィック分類（自動実行）

nftables によるフローラベル → fwmark 変換を設定します。

| フローラベル | マーク | テーブル | 優先度 |
|-------------|--------|----------|--------|
| `0xfffc4` (1048516) | mark 4 | rt_table1 | 高 |
| `0xfffc6` (1048518) | mark 6 | rt_table2 | 中 |
| その他（デフォルト） | mark 9 | rt_table3 | 低 |

- **双方向対応**: 往路（r1）と復路（r16）で独立した分類
- **自動実行**: `init_setup.py` によりコンテナ起動時に実行

### Phase 3: リアルタイムオーケストレーション（手動/自動）

動的経路制御のメインシステムです。

| 機能 | 説明 |
|------|------|
| **トラフィック監視** | RRD ベースのリンク利用率分析（60 秒間隔、24 リンク） |
| **動的経路計算** | NetworkX Dijkstra 最短経路による最適経路計算 |
| **双方向制御** | r1→r16（往路）と r16→r1（復路）の同時管理 |
| **SRv6 カプセル化** | 計算された経路に基づく動的 SID リスト生成 |
| **ルート更新** | SSH（paramiko）による自動ルートインストール |
| **マルチテーブル** | 優先度別に独立した経路最適化 |
| **可視化** | ネットワークトポロジと選択経路のリアルタイム画像出力 |

---

## 📊 技術実装

### nftables + fwmark 統合

```bash
# Phase 2: フローラベル検出 (nftables)
# mangleテーブルを作成し、IPv6フローラベルに基づいてマークを設定
nft 'add table ip6 mangle'
nft 'add chain ip6 mangle prerouting { type filter hook prerouting priority mangle; }'
nft 'add rule ip6 mangle prerouting ip6 flowlabel 0xfffc4 mark set 0x4'  # 高優先度
nft 'add rule ip6 mangle prerouting ip6 flowlabel 0xfffc6 mark set 0x6'  # 中優先度
nft 'add rule ip6 mangle prerouting mark set 0x9'                        # デフォルト（低優先度）

# Phase 1: ルーティングルール適用 (fwmarkベースのテーブル選択)
ip -6 rule add pref 1000 fwmark 0x4 table rt_table1  # 高優先度
ip -6 rule add pref 1001 fwmark 0x6 table rt_table2  # 中優先度
ip -6 rule add pref 1002 fwmark 0x9 table rt_table3  # 低優先度（デフォルト）

# Phase 3: SRv6ルートインストール（動的、テーブル別）
# 例: rt_table1での往路 r1→r2→r4→r7→r11→r14→r16
ip -6 route add fd03:1::/64 encap seg6 mode encap \
    segs fd01:1::12,fd01:2::12,fd01:3::12,fd01:8::12,fd01:9::12,fd01:a::12 dev eth1 table rt_table1
```

### パケット処理フロー

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        パケット処理フロー                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  flowlabel 0xfffc4 (高優先度) を持つユーザーパケット
      │
      ▼
  ┌─────────────────────────────────┐
  │   nftables mangle prerouting    │
  │   flowlabel 0xfffc4 を検出      │
  └─────────────────────────────────┘
      │
      ▼
  ┌─────────────────────────────────┐
  │   パケットに fwmark=4 を付与     │
  └─────────────────────────────────┘
      │
      ▼
  ┌─────────────────────────────────┐
  │   ip -6 rule lookup             │
  │   fwmark 4 がマッチ             │
  └─────────────────────────────────┘
      │
      ▼
  ┌─────────────────────────────────┐
  │   ルーティングテーブル           │
  │   rt_table1 を選択              │
  └─────────────────────────────────┘
      │
      ▼
  ┌─────────────────────────────────┐
  │   SRv6 カプセル化               │
  │   最適経路用 SID リストを付与    │
  └─────────────────────────────────┘
      │
      ▼
  次ホップへ転送
```

### リアルタイム監視パイプライン

| コンポーネント | 処理内容 |
|----------------|----------|
| **MRTG** | 60 秒間隔の SNMP ポーリング → RRD ストレージ（24 リンク） |
| **Phase 3 マネージャ** | RRD フェッチ → トラフィック分析 → グラフエッジ重み更新 |
| **経路計算** | NetworkX Dijkstra 最短経路 → 複数経路オプション生成 |
| **ルートインストーラ** | SSH（paramiko） → r1/r16 へのライブルート更新 |
| **双方向制御** | 往路と復路の独立した最適化 |

---

## 🔗 ネットワークトポロジとアドレッシング

### 16 台ルータ メッシュトポロジ

ISP の網を想定した 4x4 格子状モデルです。

```
レイヤー1 (エッジ):     r1 ─────────────────────────────────────── r16
                       │                                           │
レイヤー2:             r2 ─── r3                             r14 ── r15
                       │       │                              │      │
レイヤー3:             r4 ─── r5 ─── r6                 r11 ── r12 ── r13
                       │       │      │                  │      │      │
レイヤー4:             r7 ─── r8 ─── r9 ─── r10 ────────┴──────┴──────┘
```

### 監視リンク（24 本）

| 区分 | リンク |
|------|--------|
| エッジイングレス | r1-r2, r1-r3 |
| 中間リンク | r2-r4, r2-r5, r3-r5, r3-r6, r4-r7, r4-r8, r5-r8, r5-r9, r6-r9, r6-r10, r7-r11, r8-r11, r8-r12, r9-r12, r9-r13, r10-r13, r11-r14, r12-r14, r12-r15, r13-r15 |
| エッジイーグレス | r14-r16, r15-r16 |

### IP アドレス体系

**管理ネットワーク（SSH & 制御）:**

| ノード | アドレス | 備考 |
|--------|----------|------|
| コントローラ | fd02:1::20 | 制御プレーン |
| r1 | fd02:1::2 | SSH 有効、イングレス |
| r2 | fd02:1::3 | - |
| r3 | fd02:1::4 | - |
| r4 | fd02:1::5 | - |
| r5 | fd02:1::6 | - |
| r6 | fd02:1::7 | - |
| r7 | fd02:1::8 | - |
| r8 | fd02:1::9 | - |
| r9 | fd02:1::a | - |
| r10 | fd02:1::b | - |
| r11 | fd02:1::c | - |
| r12 | fd02:1::d | - |
| r13 | fd02:1::e | - |
| r14 | fd02:1::f | - |
| r15 | fd02:1::10 | - |
| r16 | fd02:1::11 | SSH 有効、イーグレス |

**外部ネットワーク:**

| ネットワーク | プレフィックス | ノード |
|--------------|----------------|--------|
| UPF-R1 | fd00:1::/64 | UPF: fd00:1::1, R1: fd00:1::12 |
| R16-Server | fd03:1::/64 | R16: fd03:1::11, Server: fd03:1::2 |

### 経路例

**高優先度経路 (rt_table1):**

```
UPF → r1 → r2 → r4 → r7 → r11 → r14 → r16 → Server
```

SID リスト例: `[fd01:1::12, fd01:2::12, fd01:3::12, fd01:8::12, fd01:9::12, fd01:a::12]`

**代替経路（トラフィック状況により選択）:**

| 優先度 | 経路 |
|--------|------|
| 中（rt_table2） | r1 → r3 → r5 → r8 → r12 → r15 → r16 |
| 低（rt_table3） | r1 → r3 → r6 → r9 → r13 → r15 → r16 |

---

## 🛠️ 高度な使用法

### 手動フェーズ実行

```bash
# 個別セットアップフェーズの実行
sudo docker exec -it controller python3 /opt/app/srv6-path-orchestrator/r1_phase1_table_setup.py
sudo docker exec -it controller python3 /opt/app/srv6-path-orchestrator/r1_phase2_nftables_setup.py
sudo docker exec -it controller python3 /opt/app/srv6-path-orchestrator/r16_phase1_table_setup.py
sudo docker exec -it controller python3 /opt/app/srv6-path-orchestrator/r16_phase2_nftables_setup.py
```

### リアルタイムオーケストレーションモード

| オプション | コマンド |
|------------|----------|
| 双方向監視（推奨） | `python3 phase3_realtime_multi_table.py --mode bidirectional` |
| 可視化付き | `python3 phase3_realtime_multi_table.py --mode bidirectional --visualize` |
| 往路のみ | `python3 phase3_realtime_multi_table.py --mode forward` |
| 分析のみ | `python3 phase3_realtime_multi_table.py --mode analyze --once` |
| カスタム間隔 | `python3 phase3_realtime_multi_table.py --interval 30` |
```

### 設定パラメータ
`phase3_realtime_multi_table.py` 内で以下のパラメータをカスタマイズ可能:

```python
# 履歴保存先ディレクトリ名（visualization/以下のパス）
HISTORY_SAVE_DIR = "srv6_evaluation3_tcp"

# 測定停止時間（分）- この時間が経過すると自動停止
MEASUREMENT_DURATION_MINUTES = 52
```

### テスト & デバッグ
```bash
# nftablesルールの確認
sudo docker exec -it r1 nft list table ip6 mangle
sudo docker exec -it r16 nft list table ip6 mangle_r16

# ルーティングテーブルの確認
sudo docker exec -it r1 ip -6 route show table rt_table1
sudo docker exec -it r16 ip -6 route show table rt_table_1

# 帯域制御設定の確認
sudo docker exec -it r1 tc qdisc show
sudo docker exec -it r1 tc class show dev eth0

# RRDデータの監視
sudo docker exec -it controller rrdtool fetch /opt/app/mrtg/mrtg_file/r1-r2.rrd AVERAGE --start -60s

# 監視対象リンクの一覧
sudo docker exec -it controller ls /opt/app/mrtg/mrtg_file/*.rrd
```

### 性能テスト
```bash
# iperf3スループットテスト（iperf3のインストールが必要）
# サーバー側:
iperf3 -s -6

# クライアント側:
iperf3 -c fd03:1::2 -6 -t 30 -P 4

# テスト中のtc統計監視
watch -n 1 'sudo docker exec r1 tc -s class show dev eth0'
```

---

## 📊 システム監視と分析

### リアルタイムメトリクス収集

| メトリクス | 説明 |
|------------|------|
| **リンク利用率** | SNMP/RRD によるリンク別トラフィック分析（24 リンク） |
| **経路性能** | ルーティングテーブル別のレイテンシとスループット |
| **ルート変更** | 経路切り替えイベントの自動ログ |
| **負荷分散** | 複数テーブル間のトラフィック分布 |
| **帯域使用量** | 各インターフェースの HTB クラス統計 |

### 期待されるシステム動作

| 状況 | システムの応答 |
|------|----------------|
| r1→r2 の高トラフィック | 代替経路（r1→r3→...）に切り替え |
| リンク輻輳検出 | メッシュ全体で代替経路を活性化 |
| 経路振動 | システムが最適ルートで安定化 |
| 双方向トラフィック | 往路/復路が独立して最適化 |
| マルチホップ要求 | 16 台ルータメッシュで多数の代替経路を提供 |

---

## 🔬 研究応用

### 本システムによる評価項目

本研究では、以下の観点から End-to-End 通信品質への効果を評価します：

| 評価項目 | 内容 |
|----------|------|
| **スループット** | QoS 別経路での帯域利用効率 |
| **レイテンシ** | 動的経路切り替えによる遅延変動 |
| **経路収束時間** | トラフィック変動への応答速度 |
| **負荷分散効果** | マルチテーブルによるトラフィック分離 |

### 学術的ユースケース

| 研究分野 | 活用方法 |
|----------|----------|
| **SRv6 性能評価** | 様々な条件下でのスループット、レイテンシ、経路収束の測定 |
| **トラフィックエンジニアリング** | 16 台ルータメッシュでのマルチパスルーティング最適化 |
| **SDN 統合研究** | 分散データプレーンを持つ集中制御プレーンの評価 |
| **ネットワークシミュレーション** | ルーティングプロトコル研究のためのテストベッド |
| **QoS 研究** | フローラベルベースの分類によるマルチテーブルルーティング |

### 研究プラットフォームとしての特徴

| 特徴 | 説明 |
|------|------|
| **再現可能性** | Docker コンテナ化による一貫した実験環境 |
| **包括的ログ** | 詳細な経路変更と性能ログの自動記録 |
| **柔軟な設定** | ルーティングポリシーの容易な変更 |
| **標準準拠** | 純粋な IPv6 + SRv6 実装 |
| **スケーラブル** | 24 リンク監視を持つ 16 台ルータメッシュ |
| **性能テスト対応** | 1Gbps 帯域制御による実環境に近い評価 |

---

## 🚨 トラブルシューティング

### よくある問題と解決方法

#### 1. コンテナ起動問題

```bash
# 全コンテナの起動確認
sudo docker ps -a

# コンテナログの確認
sudo docker logs r1
sudo docker logs controller

# 特定コンテナの再起動
sudo docker restart r1
```

#### 2. 自動初期化失敗

```bash
# 自動初期化ログの確認
sudo docker logs controller

# 自動初期化失敗時の手動リトライ
sudo docker exec -it controller python3 /opt/app/init_setup.py
```

#### 3. SSH 接続失敗

```bash
# ルータのSSHサービス確認
sudo docker exec -it r1 service ssh status
sudo docker exec -it r16 service ssh status

# 必要に応じてSSHを再起動
sudo docker exec -it r1 service ssh restart
sudo docker exec -it r16 service ssh restart
```

#### 4. nftablesルール競合
```bash
# 現在のルールを確認
sudo docker exec -it r1 nft list ruleset | grep -A 20 mangle

# フラッシュして再作成
sudo docker exec -it r1 nft flush table ip6 mangle
sudo docker exec -it controller python3 /opt/app/srv6-path-orchestrator/r1_phase2_nftables_setup.py
```

#### 5. 帯域制御問題
```bash
# tc設定の確認
sudo docker exec -it r1 tc qdisc show
sudo docker exec -it r1 tc class show dev eth0

# burst設定の確認（約15kが表示されるはず）
sudo docker exec -it r1 tc class show dev eth0 | grep burst

# overlimitsの確認（帯域飽和を示す）
sudo docker exec -it r1 tc -s class show dev eth0
```

#### 6. RRDデータ収集問題
```bash
# RRDファイルの存在確認（24ファイルあるはず）
sudo docker exec -it controller ls -la /opt/app/mrtg/mrtg_file/*.rrd | wc -l

# RRDデータフェッチのテスト
sudo docker exec -it controller rrdtool fetch /opt/app/mrtg/mrtg_file/r1-r2.rrd AVERAGE --start -60s
```

### システムリセット
```bash
# 環境の完全リセット
sudo docker compose down
sudo docker system prune -f
sudo docker volume prune -f
sudo docker compose build --no-cache
sudo docker compose up -d

# 自動初期化を待機（30-60秒）
sudo docker logs -f controller
```

### 診断コマンド チートシート

| 目的 | コマンド |
|------|----------|
| nftables 確認（r1） | `sudo docker exec -it r1 nft list table ip6 mangle \| grep flowlabel` |
| nftables 確認（r16） | `sudo docker exec -it r16 nft list table ip6 mangle_r16 \| grep flowlabel` |
| fwmark ルール確認 | `sudo docker exec -it r1 ip -6 rule list \| grep fwmark` |
| 帯域制御確認 | `sudo docker exec -it r1 tc class show dev eth0 \| grep rate` |
| 初期化完了確認 | `sudo docker logs controller \| grep "✅"` |
| E2E テスト（往路） | `ping6 -c 3 fd03:1::2` |
| E2E テスト（復路） | `ping6 -c 3 fd00:1::1` |

---

## 🤝 コントリビューション

1. リポジトリをフォーク
2. 新しいルーティングアルゴリズム用のフィーチャーブランチを作成
3. コンテナ化環境でテスト
4. 性能改善を文書化
5. テスト結果とともにプルリクエストを送信

---

## 📄 ライセンス & 引用

このプロジェクトは SRv6 動的ルーティングシステムの学術研究のために開発されています。

**引用形式（BibTeX）:**

```bibtex
@misc{srv6_performance_evaluation_2025,
  title={SRv6 Dynamic Routing Performance Evaluation System},
  author={[Author]},
  year={2025},
  howpublished={\url{https://github.com/hiro-hcu/srv6_dynamic_routing_performance_evaluation_system}},
  note={Docker-based 16-router SRv6 testbed for 5G QoS-based traffic engineering evaluation}
}
```

---

## 🔍 技術リファレンス

### 標準 & プロトコル

| 標準 | 説明 |
|------|------|
| [RFC 8754](https://tools.ietf.org/html/rfc8754) | IPv6 Segment Routing Header (SRH) |
| [RFC 8986](https://tools.ietf.org/html/rfc8986) | Segment Routing over IPv6 (SRv6) Network Programming |
| [Linux SRv6 Guide](https://www.kernel.org/doc/html/latest/networking/seg6-sysctl.html) | Linux SRv6 Implementation |

### 実装ツール

| ツール | 用途 |
|--------|------|
| [iproute2](https://wiki.linuxfoundation.org/networking/iproute2) | Linux Advanced Routing |
| [nftables](https://netfilter.org/projects/nftables/) | Linux Firewall Framework |
| [tc-htb](https://man7.org/linux/man-pages/man8/tc-htb.8.html) | Hierarchical Token Bucket |
| [MRTG](https://oss.oetiker.ch/mrtg/) | Network Traffic Monitoring |
| [NetworkX](https://networkx.org/) | Network Analysis in Python |

---

<div align="center">

**システム状態**

✅ 本番稼働可能 | 🔄 リアルタイム監視 | 🚀 自動初期化 | ⚡ 1Gbps 帯域制御 | 🌐 16 台メッシュ | 🖼️ 可視化対応

</div>