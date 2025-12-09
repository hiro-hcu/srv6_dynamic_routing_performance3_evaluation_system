# SRv6 System Presentation Materials

研究会発表用のSRv6動的ルーティングプロトタイプシステムに関する図表と資料

## 📁 ディレクトリ構成

```
presentation/
├── diagrams/           # 生成された図表ファイル
├── scripts/           # 図表生成用Pythonスクリプト
└── docs/             # プレゼンテーション用文書
```

## 📊 利用可能な図表

### アーキテクチャ図
- `detailed_architecture_diagram.png` - システム全体の詳細アーキテクチャ図
- `simplified_architecture_diagram.png` - 発表用簡略化アーキテクチャ図

### データフロー図
- `improved_comprehensive_data_flow_diagram.png` - **推奨**: 改良版包括的データフロー図
- `clean_simplified_data_flow_diagram.png` - **推奨**: クリーンな簡略化データフロー図

### プロトコルスタック図
- `organized_protocol_stack_diagram.png` - **推奨**: 整理版プロトコルスタック図

## 🎯 研究会発表での推奨使用順序

### 1. システム概要説明
- **使用図**: `clean_simplified_data_flow_diagram.png`
- **内容**: 3つの主要データフローの概要
- **時間**: 2-3分

### 2. システムアーキテクチャ説明  
- **使用図**: `detailed_architecture_diagram.png`
- **内容**: システム全体の構成と各コンポーネントの役割
- **時間**: 3-4分

### 3. 詳細技術説明
- **使用図**: `improved_comprehensive_data_flow_diagram.png`
- **内容**: データフローの詳細とシステム統合
- **時間**: 4-5分

### 4. プロトコル技術詳細
- **使用図**: `organized_protocol_stack_diagram.png`  
- **内容**: SRv6プロトコルスタックとヘッダー構造
- **時間**: 2-3分

## 🛠️ 図表の再生成方法

### アーキテクチャ図の生成
```bash
# controllerコンテナ内で実行
sudo docker compose exec controller python3 /opt/app/presentation/scripts/presentation_architecture_diagram.py
```

### データフロー図の生成
```bash
# controllerコンテナ内で実行
sudo docker compose exec controller python3 /opt/app/presentation/scripts/improved_data_flow_diagram.py
```

## 📋 各図表の特徴

### アーキテクチャ図
- **詳細版**: 全コンポーネント、IPv6アドレス、技術スタック情報
- **簡略版**: 3層構造での概要説明

### データフロー図
- **改良版包括的**: レイアウト改善、文字重なり解消、全データフローの詳細表示
- **クリーン簡略版**: 主要3フローのシンプル表示、プレゼンテーション最適化

### プロトコルスタック図
- **整理版**: 層別分離、SRv6詳細の2列配置、見やすさ向上

## 🎨 図表の品質仕様

- **解像度**: 300 DPI (印刷対応)
- **フォーマット**: PNG (透明背景対応)
- **サイズ**: プレゼンテーション最適化済み
- **カラー**: フルカラー、色覚障害配慮済み

## 💡 発表のコツ

1. **段階的説明**: 簡単→詳細の順で進める
2. **質疑応答準備**: 詳細図で技術的質問に対応
3. **時間配分**: 各図表2-5分で説明
4. **聴衆配慮**: 専門レベルに応じて図表選択

## 📝 更新履歴

- 2025/09/20: プレゼンテーション用ディレクトリ作成
- 2025/09/20: 改良版データフロー図追加（レイアウト改善）
- 2025/09/20: アーキテクチャ図初版作成
- 2025/09/20: プロトコルスタック図追加

---

**作成者**: GitHub Copilot  
**対象システム**: SRv6 Dynamic Routing Prototype System  
**発表対象**: 研究会プレゼンテーション