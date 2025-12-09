# phase3_realtime_multi_table.py - 可視化機能追加

## 新機能

### 1. トポロジ可視化
- NetworkXとmatplotlibを使用した格子状トポロジの表示
- リアルタイムでグラフが更新される

### 2. エッジの重み表示
- 各エッジに利用率（0-100%）を表示
- RRDデータから取得した実際のトラフィック情報を反映

### 3. 3つの経路の視覚化
- **高優先度経路**: 赤色、太線
- **中優先度経路**: オレンジ色、中線
- **低優先度経路**: 緑色、細線
- 各経路のノードリストとコストを凡例に表示

### 4. 60秒間隔での自動更新
- デフォルトで60秒間隔で重みを更新
- `--interval`オプションで間隔をカスタマイズ可能

## 使用方法

### 可視化を有効にして実行

```bash
# 双方向モード（可視化あり、60秒間隔で更新）
python3 phase3_realtime_multi_table.py --mode bidirectional --visualize --interval 60

# 双方向モード（可視化あり、1回のみ実行）
python3 phase3_realtime_multi_table.py --mode bidirectional --visualize --once

# 分析モード（可視化あり、経路計算のみ）
python3 phase3_realtime_multi_table.py --mode analyze --visualize
```

### 可視化なしで実行（従来通り）

```bash
# 双方向モード（可視化なし）
python3 phase3_realtime_multi_table.py --mode bidirectional --interval 60

# 1回のみ実行
python3 phase3_realtime_multi_table.py --mode bidirectional --once
```

## コマンドラインオプション

| オプション | デフォルト | 説明 |
|----------|----------|------|
| `--mode` | bidirectional | 実行モード (bidirectional/forward/analyze) |
| `--visualize` | False | トポロジ可視化を有効化 |
| `--interval` | 60 | 更新間隔（秒） |
| `--once` | False | 1回のみ実行 |
| `--src` | 1 | 送信元ノード |
| `--dst` | 16 | 宛先ノード |

## トポロジレイアウト

```
r1  -- r2  -- r4  -- r7
|      |      |      |
r3  -- r5  -- r8  -- r11
|      |      |      |
r6  -- r9  -- r12 -- r14
|      |      |      |
r10 -- r13 -- r15 -- r16
```

## 可視化ウィンドウの操作

- **Ctrl+C**: プログラムを終了
- ウィンドウは60秒ごとに自動的に更新されます
- 各エッジのラベルに利用率（%）が表示されます
- 選択された3つの経路が色分けして表示されます

## 注意事項

1. **matplotlibのバックエンド**: TkAggを使用しているため、X11フォワーディングまたはGUI環境が必要です
2. **SSH接続**: controllerコンテナからr1とr16への接続が必要です
3. **RRDファイル**: `/opt/app/mrtg/mrtg_file/`に有効なRRDファイルが必要です
4. **更新間隔**: RRDの更新間隔に合わせて60秒を推奨

## トラブルシューティング

### 可視化ウィンドウが表示されない
```bash
# X11フォワーディングの確認
echo $DISPLAY

# SSH接続時に -X オプションを使用
ssh -X user@host
```

### matplotlibエラー
```bash
# TkAggバックエンドが利用できない場合
# 別のバックエンド（Agg）に変更
# コード内の matplotlib.use('TkAgg') を matplotlib.use('Agg') に変更
```
