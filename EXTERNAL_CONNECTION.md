# 外部ノード接続機能（Macvlan版）

このドキュメントでは、Macvlanを使用してSRv6システムに外部ノード（UPF/Server）を接続する方法について説明します。

## 🌐 外部PC接続のメリット

### **実環境での研究価値**
- **リアルな遅延**: 物理ネットワークでの実際のレイテンシ測定
- **実用性検証**: 複数PC間での実際のアプリケーション通信
- **スケーラビリティ**: 複数の外部ノードとの同時接続
- **パフォーマンス評価**: 実際のハードウェアでの性能測定
- **物理IF直接接続**: Macvlanによる低オーバーヘッド通信

### **アーキテクチャ（Macvlan版）**
```
External UPF (fd01:1::100)
    ↓
Physical IF (enp2s0f1)
    ↓ Macvlan (bridge mode)
├─ macvlan-upf (Host: fd01:1::100)
└─ R1 eth0 (Container: fd01:1::2, MAC: 2e:7f:2d:e9:34:b7)
    ↓
SRv6 Network (fd01:2::/64 - fd01:9::/64)
    ↓
R6 eth0 (Container: fd03:1::1, MAC: 2e:7f:2d:e9:34:b8)
    ↓ Macvlan (bridge mode)
├─ macvlan-server (Host: fd03:1::100)
└─ Physical IF (enp2s0f0)
    ↓
External Server (fd03:1::200)
```

### **Macvlanの利点**
- **直接物理IF接続**: Bridgeドライバーでは不可能だった物理インターフェースへの直接接続
- **低レイテンシ**: Bridgeレイヤーを経由しないため、オーバーヘッドが少ない
- **独立MACアドレス**: 各コンテナが独自のMACアドレスを持ち、物理ネットワーク上で独立したデバイスとして見える
- **L2透過性**: VLANタグやその他のL2フレーム処理が可能

## 🚀 セットアップ手順

### **前提条件**
- ホストPC: 2つ以上の物理ネットワークインターフェース（例: enp2s0f1, enp2s0f0）
- 外部ノード: IPv6対応のLinux環境
- 全てのPC: root権限でのネットワーク設定が可能
- Docker & Docker Compose インストール済み

### **クイックスタート（推奨）**

最も簡単な方法は、統合起動スクリプトを使用することです：

```bash
cd srv6_dynamic_routing_prototype_system
sudo ./start.sh
```

`start.sh` は以下を自動実行します：
1. Macvlanインターフェース作成（`scripts/setup_host_macvlan.sh`）
2. UPF側ルーティング設定（`scripts/setup_upf_host.sh`）
3. Server側ルーティング設定（`scripts/setup_server_host.sh`）
4. Dockerコンテナ起動（`docker-compose up -d`）

### **手動セットアップ（詳細制御が必要な場合）**

#### **1. 物理インターフェース名の確認**

```bash
# 利用可能なインターフェース確認
ip link show

# 例: enp2s0f1 (UPF側), enp2s0f0 (Server側) を使用
```

インターフェース名が異なる場合は以下を編集：
- `docker-compose.yml` の `networks.external-upf.driver_opts.parent`
- `docker-compose.yml` の `networks.external-server.driver_opts.parent`
- `scripts/setup_host_macvlan.sh` の `UPF_PARENT`, `SERVER_PARENT`

#### **2. ホスト側Macvlanインターフェース作成**

```bash
sudo ./scripts/setup_host_macvlan.sh
```

このスクリプトは以下を実行します：
- `macvlan-upf` インターフェース作成（親: enp2s0f1）
- `macvlan-server` インターフェース作成（親: enp2s0f0）
- IPv6アドレス設定（fd01:1::100/64, fd03:1::100/64）

#### **3. ルーティング設定**

```bash
# UPF側ルーティング
sudo ./scripts/setup_upf_host.sh

# Server側ルーティング
sudo ./scripts/setup_server_host.sh
```

または統合スクリプトで一括実行：
```bash
sudo ./scripts/setup_all.sh
```

#### **4. Dockerコンテナ起動**

```bash
sudo docker compose up -d
sudo docker compose ps  # 全コンテナがUpであることを確認
```

### **5. 外部ノード設定**

外部ノード側では手動でネットワーク設定を行います：

#### **UPF設定例（外部物理端末）**
```bash
# IPv6アドレス設定
sudo ip -6 addr add fd01:1::200/64 dev <interface>

# R1へのルート設定
sudo ip -6 route add fd03:1::/64 via fd01:1::2   # Server network via R1 (fd01:1::2)

# 接続確認
ping6 -c 3 fd01:1::2   # R1への接続確認
ping6 -c 3 fd03:1::200 # Server PCへの疎通確認
```

**重要**: 外部UPFからパケットを送信する際、宛先MACアドレスは R1 のMACアドレス (`2e:7f:2d:e9:34:b7`) である必要があります。
- Neighbor Discovery (ND) により自動学習される
- または、静的にARP/NDエントリを設定

#### **Server設定例（外部物理端末）**
```bash
# IPv6アドレス設定  
sudo ip -6 addr add fd03:1::200/64 dev <interface>

# R6へのルート設定
sudo ip -6 route add fd01:1::/64 via fd03:1::1  # UPF network via R6 (fd03:1::1)

# 接続確認
ping6 -c 3 fd03:1::1   # R6への接続確認
ping6 -c 3 fd01:1::200 # UPF PCへの疎通確認
```

**重要**: 外部Serverからパケットを送信する際、宛先MACアドレスは R6 のMACアドレス (`2e:7f:2d:e9:34:b8`) である必要があります。

### **6. Macvlanパケットフローの理解**

#### **受信フロー（外部UPF → R1コンテナ）**

```
ステップ1: 外部UPFからパケット送信
┌─────────────────────────────────────┐
│ 外部UPF (fd01:1::200)               │
│ 宛先: fd03:1::200                   │
└──────────┬──────────────────────────┘
           │ パケット送信
           │ 宛先MAC: 2e:7f:2d:e9:34:b7 (R1のMAC)
           ↓
ステップ2: 物理NICでパケット受信
┌─────────────────────────────────────┐
│ 物理NIC (enp2s0f1)                  │
│ - すべてのパケットを受信            │
│ - 宛先MACアドレスを確認             │
└──────────┬──────────────────────────┘
           │ MACアドレスで振り分け
           │
           ├─ 宛先MAC: aa:bb:cc:dd:ee:01 → macvlan-upf (ホスト用)
           │
           └─ 宛先MAC: 2e:7f:2d:e9:34:b7 → R1 eth0 (コンテナ用) ✓
                      ↓
ステップ3: Macvlan仮想ブリッジで転送
┌─────────────────────────────────────┐
│ Macvlan仮想ブリッジ (bridgeモード)  │
│ - カーネル内でL2スイッチング        │
│ - MACアドレステーブルで転送先を決定 │
└──────────┬──────────────────────────┘
           │ 該当する子IFへ転送
           ↓
ステップ4: R1コンテナのネットワーク名前空間へ
┌─────────────────────────────────────┐
│ R1コンテナ                          │
│ eth0 (fd01:1::2)                    │
│ - パケットを受信                    │
│ - SRv6ルーティングテーブルを参照    │
│ - fd03:1::/64 → 次ホップ決定        │
└─────────────────────────────────────┘
```

#### **送信フロー（R1コンテナ → 外部UPF）**

```
R1コンテナ (eth0)
    │ パケット送信
    │ 送信元MAC: 2e:7f:2d:e9:34:b7
    ↓
Macvlan仮想ブリッジ
    │ 親IFへ転送
    ↓
物理NIC (enp2s0f1)
    │ 物理的に送信
    ↓
外部ネットワーク → 外部UPF
```

#### **Macvlanの制約**

**制約**: 同一親IF上のホスト ⇔ コンテナ間直接通信不可

```
[NG例] ホスト → enp2s0f1 → R1コンテナ
理由: Linuxカーネルの制約で、親IFとその子IF間は直接通信できない
```

**回避方法**: ホスト専用のMacvlan子IFを作成

```
[OK例] ホスト → macvlan-upf → enp2s0f1 → R1コンテナ

ホスト (macvlan-upf: fd01:1::100)
    │ パケット送信
    ↓
Macvlan仮想ブリッジ (同じ親IF配下)
    │ 子IF間での転送が可能
    ↓
R1コンテナ (eth0: fd01:1::2)
```

この方法により、ホストも1つのMacvlan子IFとしてブリッジに参加し、他の子IF（コンテナ）と通信できるようになります。

## 🔍 動作確認

### **ホスト→コンテナ疎通テスト**
```bash
# ホストからR1への疎通確認
ping6 -c 3 fd01:1::2

# ホストからR6への疎通確認
ping6 -c 3 fd03:1::1
```

### **外部端末間通信テスト**
```bash
# UPF → Server
ping6 -c 3 fd03:1::200

# Server → UPF
ping6 -c 3 fd01:1::200
```

### **パケットキャプチャで確認**

#### **R1でのパケット受信確認**
```bash
# R1のeth0でキャプチャ
sudo docker exec r1 tcpdump -i eth0 -nn icmp6

# 外部UPFから ping6 fd03:1::200 を実行
# R1でパケットが観測されることを確認
```

#### **物理IFでのパケット確認**
```bash
# UPF側物理IFでキャプチャ
sudo tcpdump -i enp2s0f1 -nn icmp6

# Server側物理IFでキャプチャ
sudo tcpdump -i enp2s0f0 -nn icmp6
```

### **MACアドレス学習の確認**
```bash
# ホスト側のNeighbor Discoveryキャッシュ確認
ip -6 neigh show dev macvlan-upf
ip -6 neigh show dev macvlan-server

# R1のMACアドレスが正しく学習されているか確認
# fd01:1::2 lladdr 2e:7f:2d:e9:34:b7 REACHABLE
```

### **SRv6動作確認**
```bash
# ホストPCでリアルタイム監視開始
sudo docker exec -it controller python3 /opt/app/srv6-path-orchestrator/phase3_realtime_multi_table.py

# 別ターミナルでトラフィック生成
# UPF側:
ping6 -i 0.1 fd01:5::100

# Server側:
ping6 -i 0.1 fd01:1::100
```

### **期待される動作**
1. **パス変更観察**: トラフィック量に応じて経路が動的に切り替わる
2. **双方向制御**: 往路と復路が独立して最適化される
3. **負荷分散**: 複数テーブル間でのトラフィック分散

## 📊 性能測定

### **スループット測定（iperf3）**
```bash
# Server PC側でサーバー起動
iperf3 -s -B fd03:1::200

# UPF PC側からテスト実行
iperf3 -c fd03:1::200 -6 -t 60

# 双方向テスト
iperf3 -c fd03:1::200 -6 -t 60 --bidir
```

### **遅延測定**
```bash
# RTT測定（100回）
ping6 -c 100 -i 0.01 fd03:1::200

# 統計情報の確認
# rtt min/avg/max/mdev の値を記録
```

### **SRv6パス切り替えの観察**
```bash
# ホストPCでリアルタイム監視開始
sudo docker exec -it controller python3 /opt/app/srv6-path-orchestrator/phase3_realtime_multi_table.py

# 別ターミナルでトラフィック生成
# UPF側: 高負荷トラフィック
ping6 -f fd03:1::200  # flood ping

# Server側からも同時送信
ping6 -f fd01:1::200
```

### **期待される動作**
1. **パス変更観察**: トラフィック量に応じて経路が動的に切り替わる
2. **双方向制御**: 往路と復路が独立して最適化される
3. **負荷分散**: 複数テーブル間でのトラフィック分散
4. **SRv6ヘッダ挿入**: R1でSRv6ヘッダが追加され、R6で削除される

## 🛠️ トラブルシューティング

### **よくある問題**

#### **1. R1/R6に到達できない**

**症状**: ホストから `ping6 fd01:1::2` が失敗する

**確認項目**:
```bash
# Macvlanインターフェースの存在確認
ip link show macvlan-upf
ip link show macvlan-server

# IPv6アドレスの確認
ip -6 addr show macvlan-upf
ip -6 addr show macvlan-server

# コンテナの起動確認
sudo docker compose ps
```

**解決策**:
```bash
# Macvlan設定をやり直す
sudo ./scripts/cleanup_host.sh
sudo ./scripts/setup_host_macvlan.sh
```

#### **2. 外部端末からR1/R6に到達できない**

**症状**: 外部UPFから `ping6 fd01:1::2` が失敗する

**確認項目**:
```bash
# 物理IFでパケットが届いているか確認
sudo tcpdump -i enp2s0f1 -nn icmp6

# MACアドレスが正しいか確認
# 宛先MACが R1のMAC (2e:7f:2d:e9:34:b7) であることを確認
```

**原因**:
- 宛先MACアドレスが物理IFのMACになっている
- Neighbor Discovery (ND) でR1のMACが学習されていない

**解決策**:
```bash
# 外部端末側でNDキャッシュをクリア
sudo ip -6 neigh flush dev <interface>

# R1に向けてpingを実行（ND学習を促す）
ping6 -c 3 fd01:1::2

# NDキャッシュを確認
ip -6 neigh show dev <interface>
# fd01:1::2 lladdr 2e:7f:2d:e9:34:b7 が表示されればOK
```

#### **3. 外部端末間通信ができない**

**症状**: UPF → Server の通信が失敗する

**確認項目**:
```bash
# 外部端末側ルーティング確認
ip -6 route show

# R1でのSRv6テーブル確認
sudo docker exec r1 ip -6 route show table rt_table1
sudo docker exec r1 ip -6 route show table rt_table2

# R6でのSRv6テーブル確認
sudo docker exec r6 ip -6 route show table rt_table_1
sudo docker exec r6 ip -6 route show table rt_table_2
```

**解決策**:
```bash
# UPF側ルーティングを再設定
sudo ./scripts/setup_upf_host.sh

# Server側ルーティングを再設定
sudo ./scripts/setup_server_host.sh

# SRv6コントローラーの再起動
sudo docker restart controller
```

#### **4. パケットが転送されない**

**確認項目**:
```bash
# IPv6転送が有効か確認
sysctl net.ipv6.conf.all.forwarding
# 1 であることを確認

# ホスト側の転送設定
sysctl net.ipv6.conf.enp2s0f1.forwarding
sysctl net.ipv6.conf.enp2s0f0.forwarding

# nftables/iptablesルール確認
sudo docker exec r1 nft list table ip6 mangle
```

**解決策**:
```bash
# IPv6転送を有効化
sudo sysctl -w net.ipv6.conf.all.forwarding=1
sudo sysctl -w net.ipv6.conf.enp2s0f1.forwarding=1
sudo sysctl -w net.ipv6.conf.enp2s0f0.forwarding=1
```

#### **5. Macvlan子IF間通信ができない（同一ホスト上）**

**症状**: ホストの `macvlan-upf` から R1 への通信は成功するが、逆が失敗する

**原因**: Macvlanの制約により、親IF経由の通信は片方向のみサポートされることがある

**解決策**: これは正常な動作です。外部端末からの通信を優先してください。

## � システム管理

### **停止方法**
```bash
# コンテナ停止
sudo docker compose down

# ホスト側ネットワーク設定のクリーンアップ
sudo ./scripts/cleanup_host.sh
```

### **再起動**
```bash
# 完全な再起動
sudo docker compose down
sudo ./scripts/cleanup_host.sh
sudo ./start.sh
```

### **ログ確認**
```bash
# 全コンテナのログ
sudo docker compose logs -f

# 特定コンテナのログ
sudo docker compose logs -f r1
sudo docker compose logs -f controller

# SRv6パスオーケストレーターのログ
sudo docker exec controller cat /opt/app/logs/srv6_orchestrator.log
```

### **設定変更時の手順**

#### **物理インターフェース名を変更する場合**
1. `docker-compose.yml` を編集:
   ```yaml
   networks:
     external-upf:
       driver_opts:
         parent: <新しいIF名>  # enp2s0f1 → 新IF名
   ```

2. `scripts/setup_host_macvlan.sh` を編集:
   ```bash
   UPF_PARENT="<新しいIF名>"
   SERVER_PARENT="<新しいIF名>"
   ```

3. システムを再起動:
   ```bash
   sudo docker compose down
   sudo ./scripts/cleanup_host.sh
   sudo ./start.sh
   ```

#### **IPアドレス範囲を変更する場合**
1. `docker-compose.yml` のサブネット設定を変更
2. 各スクリプトのIPアドレスを変更
3. 外部端末の設定も変更
4. システムを再起動

## 📈 研究活用例

### **学術研究での応用**
- **トラフィックエンジニアリング**: 実際のネットワーク負荷での経路最適化
- **QoS評価**: 異なる優先度での実performance比較
- **スケーラビリティ検証**: 複数外部ノードでの同時通信
- **レイテンシ分析**: 物理ネットワークでの実遅延測定
- **SRv6性能評価**: Macvlanによる低オーバーヘッド環境での測定

### **パフォーマンス指標**
- **スループット**: iperf3による帯域幅測定（Macvlanの低レイテンシ効果）
- **遅延**: ping6によるRTT測定（物理IF直接接続の効果）
- **パケットロス**: 長時間pingでの損失率
- **経路切替時間**: SRv6ログからの切替遅延分析
- **MACアドレス学習時間**: ND学習にかかる時間の測定

### **実験シナリオ例**

#### **シナリオ1: 動的負荷分散**
```bash
# UPF側から複数フロー生成
for i in {1..5}; do
  ping6 -f fd03:1::200 &
done

# コントローラーログで経路変更を観察
sudo docker exec controller tail -f /opt/app/logs/srv6_orchestrator.log
```

#### **シナリオ2: 双方向トラフィック**
```bash
# 双方向同時通信
# UPF → Server
iperf3 -c fd03:1::200 -6 -t 60 -P 4 &

# Server → UPF  
iperf3 -c fd01:1::200 -6 -t 60 -P 4 -R &
```

#### **シナリオ3: レイテンシ変動測定**
```bash
# 経路切り替え時のレイテンシ変動測定
ping6 -i 0.01 fd03:1::200 | tee latency.log

# 別ターミナルで負荷生成（経路切り替えをトリガー）
ping6 -f fd03:1::200
```

## 📚 技術詳細

### **Macvlan vs Bridge**

| 項目 | Bridge | Macvlan |
|-----|--------|---------|
| 物理IF接続 | ❌ 不可 | ✅ 可能 |
| レイテンシ | 高い（Bridge経由） | 低い（直接接続） |
| MACアドレス | 共有 | 独立 |
| 設定複雑度 | 簡単 | 中程度 |
| ホスト⇔コンテナ | 制約なし | 専用子IF必要 |
| ユースケース | 開発環境 | **本番/実験環境** |

### **ネットワーク構成詳細**

#### **アドレス設計**
```
UPF側ネットワーク (fd01:1::/64):
  - R1 コンテナ: fd01:1::2
  - ホスト macvlan-upf: fd01:1::100
  - 外部UPF: fd01:1::200 (例)

Server側ネットワーク (fd03:1::/64):
  - R6 コンテナ: fd03:1::1
  - ホスト macvlan-server: fd03:1::100
  - 外部Server: fd03:1::200 (例)

内部SRv6ネットワーク (fd01:2::/64 - fd01:9::/64):
  - R1-R2: fd01:2::/64
  - R2-R4: fd01:3::/64
  - R4-R6: fd01:4::/64
  - R5-R6: fd01:6::/64
  - R3-R5: fd01:7::/64
  - R1-R3: fd01:8::/64
  - R2-R5: fd01:9::/64
```

#### **MACアドレス固定の理由**
- **安定性**: コンテナ再起動時もMACが変わらない
- **ND学習**: 外部端末が一度学習すれば永続的に使用可能
- **デバッグ**: MACアドレスベースのトラブルシューティングが容易

この外部ノード接続機能（Macvlan版）により、コンテナ環境から実環境へとSRv6システムを拡張し、より実用的で低レイテンシな研究環境を構築できます。