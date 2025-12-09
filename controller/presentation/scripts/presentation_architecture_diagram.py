#!/usr/bin/env python3
"""
研究会発表用 SRv6システム全体アーキテクチャ図生成スクリプト
詳細なコンポーネント、プロトコル、データフローを含む包括的な図を作成
"""

import matplotlib
matplotlib.use('Agg')  # ヘッドレス環境用バックエンド設定
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np
import os

# 日本語フォント設定
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10

def create_detailed_architecture_diagram():
    """詳細なシステムアーキテクチャ図を作成"""
    
    # 図のサイズを大きく設定
    fig, ax = plt.subplots(1, 1, figsize=(20, 14))
    
    # 背景色設定
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#f8f9fa')
    
    # 軸の設定
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 14)
    ax.axis('off')
    
    # タイトル
    ax.text(10, 13.5, 'SRv6 Dynamic Routing Prototype System Architecture', 
            fontsize=18, fontweight='bold', ha='center')
    ax.text(10, 13, 'Research Presentation - Detailed Component Overview', 
            fontsize=12, ha='center', style='italic')
    
    # ===============================
    # 1. Application Layer (上部)
    # ===============================
    
    # Client側
    client_box = FancyBboxPatch((0.5, 11), 3, 1.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#e3f2fd', edgecolor='#1976d2', linewidth=2)
    ax.add_patch(client_box)
    ax.text(2, 11.75, 'Client Container', fontweight='bold', ha='center')
    ax.text(2, 11.4, 'Ubuntu 22.04', ha='center', fontsize=9)
    ax.text(2, 11.1, 'IPv6: fd01:1::11', ha='center', fontsize=8, family='monospace')
    
    # Server側
    server_box = FancyBboxPatch((16.5, 11), 3, 1.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#e8f5e8', edgecolor='#388e3c', linewidth=2)
    ax.add_patch(server_box)
    ax.text(18, 11.75, 'Server Container', fontweight='bold', ha='center')
    ax.text(18, 11.4, 'Ubuntu 22.04', ha='center', fontsize=9)
    ax.text(18, 11.1, 'IPv6: fd01:5::12', ha='center', fontsize=8, family='monospace')
    
    # ===============================
    # 2. SRv6 Network Layer (中央)
    # ===============================
    
    # ネットワーク全体の背景
    network_bg = FancyBboxPatch((1, 6.5), 18, 4, 
                               boxstyle="round,pad=0.2", 
                               facecolor='#fff3e0', edgecolor='#f57c00', linewidth=2)
    ax.add_patch(network_bg)
    ax.text(10, 10.2, 'SRv6 Network Infrastructure', fontweight='bold', ha='center', fontsize=14)
    
    # ルーター配置（実際のトポロジーに合わせて）
    router_positions = {
        'r1': (3, 9),
        'r2': (7, 9),
        'r3': (3, 7.5),
        'r4': (11, 9),
        'r5': (7, 7.5),
        'r6': (15, 9)
    }
    
    router_ips = {
        'r1': 'fd02:1::2',
        'r2': 'fd02:1::3', 
        'r3': 'fd02:1::4',
        'r4': 'fd02:1::5',
        'r5': 'fd02:1::6',
        'r6': 'fd02:1::7'
    }
    
    # ルーター描画
    for router, (x, y) in router_positions.items():
        # ルーターボックス
        router_box = FancyBboxPatch((x-0.6, y-0.4), 1.2, 0.8, 
                                   boxstyle="round,pad=0.05", 
                                   facecolor='#fff9c4', edgecolor='#f9a825', linewidth=1.5)
        ax.add_patch(router_box)
        ax.text(x, y+0.1, router.upper(), fontweight='bold', ha='center', fontsize=10)
        ax.text(x, y-0.15, router_ips[router], ha='center', fontsize=7, family='monospace')
    
    # ネットワーク接続線
    connections = [
        ('r1', 'r2', 'fd01:2::/64'),
        ('r1', 'r3', 'fd01:8::/64'),
        ('r2', 'r4', 'fd01:3::/64'),
        ('r2', 'r5', 'fd01:9::/64'),
        ('r3', 'r5', 'fd01:7::/64'),
        ('r4', 'r6', 'fd01:4::/64'),
        ('r5', 'r6', 'fd01:6::/64')
    ]
    
    for r1, r2, subnet in connections:
        x1, y1 = router_positions[r1]
        x2, y2 = router_positions[r2]
        
        # 接続線
        ax.plot([x1, x2], [y1, y2], 'b-', linewidth=2, alpha=0.7)
        
        # サブネット情報
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x, mid_y + 0.2, subnet, fontsize=7, ha='center', 
                bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
    
    # Client-r1, r6-Server接続
    ax.plot([2, 3], [11, 9.4], 'g-', linewidth=3, alpha=0.8)
    ax.plot([15, 18], [9.4, 11], 'g-', linewidth=3, alpha=0.8)
    
    # ===============================
    # 3. Control & Monitoring Layer (下部)
    # ===============================
    
    # Controller全体背景
    controller_bg = FancyBboxPatch((1, 3), 18, 3, 
                                  boxstyle="round,pad=0.2", 
                                  facecolor='#f3e5f5', edgecolor='#7b1fa2', linewidth=2)
    ax.add_patch(controller_bg)
    ax.text(10, 5.7, 'Control & Monitoring Layer', fontweight='bold', ha='center', fontsize=14)
    
    # MRTG監視システム
    mrtg_box = FancyBboxPatch((2, 4.5), 4, 1, 
                             boxstyle="round,pad=0.1", 
                             facecolor='#ffebee', edgecolor='#d32f2f', linewidth=1.5)
    ax.add_patch(mrtg_box)
    ax.text(4, 5.2, 'MRTG Monitoring', fontweight='bold', ha='center')
    ax.text(4, 4.9, 'SNMP v2c Protocol', ha='center', fontsize=9)
    ax.text(4, 4.65, 'RRD Data Collection', ha='center', fontsize=8)
    
    # Path Orchestrator
    orchestrator_box = FancyBboxPatch((7, 4.5), 6, 1, 
                                     boxstyle="round,pad=0.1", 
                                     facecolor='#e8eaf6', edgecolor='#3f51b5', linewidth=1.5)
    ax.add_patch(orchestrator_box)
    ax.text(10, 5.2, 'SRv6 Path Orchestrator', fontweight='bold', ha='center')
    ax.text(10, 4.9, 'NetworkX Topology Management', ha='center', fontsize=9)
    ax.text(10, 4.65, 'Dynamic Route Optimization', ha='center', fontsize=8)
    
    # Container管理
    docker_box = FancyBboxPatch((14, 4.5), 4, 1, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#e0f2f1', edgecolor='#00796b', linewidth=1.5)
    ax.add_patch(docker_box)
    ax.text(16, 5.2, 'Container Management', fontweight='bold', ha='center')
    ax.text(16, 4.9, 'Docker Compose', ha='center', fontsize=9)
    ax.text(16, 4.65, 'Orchestration Layer', ha='center', fontsize=8)
    
    # データストレージ
    storage_box = FancyBboxPatch((2, 3.3), 4, 0.8, 
                                boxstyle="round,pad=0.1", 
                                facecolor='#fafafa', edgecolor='#616161', linewidth=1.5)
    ax.add_patch(storage_box)
    ax.text(4, 3.8, 'RRD Database', fontweight='bold', ha='center')
    ax.text(4, 3.5, 'Time-series Traffic Data', ha='center', fontsize=8)
    
    # 設定ファイル
    config_box = FancyBboxPatch((7, 3.3), 6, 0.8, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#fafafa', edgecolor='#616161', linewidth=1.5)
    ax.add_patch(config_box)
    ax.text(10, 3.8, 'Configuration Management', fontweight='bold', ha='center')
    ax.text(10, 3.5, 'SRv6 Tables, SNMP Config, Network Topology', ha='center', fontsize=8)
    
    # ログ・分析
    analysis_box = FancyBboxPatch((14, 3.3), 4, 0.8, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#fafafa', edgecolor='#616161', linewidth=1.5)
    ax.add_patch(analysis_box)
    ax.text(16, 3.8, 'Analytics & Logging', fontweight='bold', ha='center')
    ax.text(16, 3.5, 'Performance Metrics', ha='center', fontsize=8)
    
    # ===============================
    # 4. データフロー矢印
    # ===============================
    
    # SNMP監視フロー
    for router, (x, y) in router_positions.items():
        # ルーターからMRTGへのSNMPデータフロー
        ax.annotate('', xy=(4, 4.5), xytext=(x, y-0.4),
                   arrowprops=dict(arrowstyle='->', color='red', alpha=0.6, lw=1))
    
    # Path OrchestratorからルーターへのSSH制御フロー
    for router, (x, y) in router_positions.items():
        ax.annotate('', xy=(x, y+0.4), xytext=(10, 4.5),
                   arrowprops=dict(arrowstyle='->', color='blue', alpha=0.6, lw=1))
    
    # Client-Server通信フロー
    ax.annotate('', xy=(16.5, 11.75), xytext=(3.5, 11.75),
               arrowprops=dict(arrowstyle='->', color='green', alpha=0.8, lw=3))
    
    # ===============================
    # 5. Protocol & Technology Labels
    # ===============================
    
    # プロトコル情報ボックス
    protocol_box = FancyBboxPatch((1, 0.5), 18, 2, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#f5f5f5', edgecolor='#424242', linewidth=1)
    ax.add_patch(protocol_box)
    ax.text(10, 2.2, 'Technology Stack & Protocols', fontweight='bold', ha='center', fontsize=12)
    
    # 左側：ネットワーク技術
    ax.text(1.5, 1.8, '● Network Technologies:', fontweight='bold', fontsize=10)
    ax.text(1.7, 1.6, '• SRv6 (Segment Routing over IPv6)', fontsize=9)
    ax.text(1.7, 1.4, '• Native Linux Kernel Implementation', fontsize=9)
    ax.text(1.7, 1.2, '• iproute2 based routing (no daemons)', fontsize=9)
    ax.text(1.7, 1.0, '• IPv6 only network infrastructure', fontsize=9)
    ax.text(1.7, 0.8, '• Docker bridge networks', fontsize=9)
    
    # 中央：監視・制御プロトコル
    ax.text(7, 1.8, '● Monitoring & Control:', fontweight='bold', fontsize=10)
    ax.text(7.2, 1.6, '• SNMP v2c for traffic monitoring', fontsize=9)
    ax.text(7.2, 1.4, '• SSH for remote configuration', fontsize=9)
    ax.text(7.2, 1.2, '• RRD for time-series data storage', fontsize=9)
    ax.text(7.2, 1.0, '• NetworkX for topology management', fontsize=9)
    ax.text(7.2, 0.8, '• MRTG for real-time visualization', fontsize=9)
    
    # 右側：システム基盤
    ax.text(13.5, 1.8, '● System Infrastructure:', fontweight='bold', fontsize=10)
    ax.text(13.7, 1.6, '• Docker containerization', fontsize=9)
    ax.text(13.7, 1.4, '• Python 3.9 control plane', fontsize=9)
    ax.text(13.7, 1.2, '• Ubuntu 22.04 router OS', fontsize=9)
    ax.text(13.7, 1.0, '• Paramiko SSH automation', fontsize=9)
    ax.text(13.7, 0.8, '• Matplotlib visualization', fontsize=9)
    
    # ===============================
    # 6. Legend & Key Features
    # ===============================
    
    # 矢印の凡例
    ax.text(0.5, 12.5, 'Data Flow Legend:', fontweight='bold', fontsize=10)
    ax.plot([0.7, 1.2], [12.2, 12.2], 'r-', linewidth=2)
    ax.text(1.4, 12.2, 'SNMP Monitoring', fontsize=9, va='center')
    ax.plot([0.7, 1.2], [12.0, 12.0], 'b-', linewidth=2)
    ax.text(1.4, 12.0, 'SSH Control', fontsize=9, va='center')
    ax.plot([0.7, 1.2], [11.8, 11.8], 'g-', linewidth=3)
    ax.text(1.4, 11.8, 'SRv6 Traffic', fontsize=9, va='center')
    
    # Key Features
    ax.text(16, 12.5, 'Key Features:', fontweight='bold', fontsize=10)
    ax.text(16, 12.2, '✓ Real-time traffic monitoring', fontsize=9)
    ax.text(16, 12.0, '✓ Dynamic path optimization', fontsize=9)
    ax.text(16, 11.8, '✓ Container-based deployment', fontsize=9)
    
    plt.tight_layout()
    
    # ファイル保存（controllerコンテナ内のパス）
    output_path = '/opt/app/presentation/diagrams/detailed_architecture_diagram.png'
    
    # ディレクトリが存在しない場合は作成
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print(f"詳細アーキテクチャ図を保存しました: {output_path}")
    
    return fig, ax

def create_simplified_presentation_diagram():
    """発表用簡略化アーキテクチャ図"""
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#fafafa')
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # タイトル
    ax.text(8, 9.5, 'SRv6 Dynamic Routing System Overview', 
            fontsize=16, fontweight='bold', ha='center')
    
    # 3層アーキテクチャ
    layers = [
        {'name': 'Application Layer', 'y': 7.5, 'color': '#e3f2fd', 'edge': '#1976d2'},
        {'name': 'SRv6 Network Layer', 'y': 5, 'color': '#fff3e0', 'edge': '#f57c00'},
        {'name': 'Control & Monitoring Layer', 'y': 2.5, 'color': '#f3e5f5', 'edge': '#7b1fa2'}
    ]
    
    for layer in layers:
        layer_box = FancyBboxPatch((1, layer['y']-0.8), 14, 1.6, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=layer['color'], 
                                  edgecolor=layer['edge'], linewidth=2)
        ax.add_patch(layer_box)
        ax.text(8, layer['y'], layer['name'], 
                fontweight='bold', fontsize=14, ha='center')
    
    # Application Layer詳細
    ax.text(3, 7.5, 'Client\n(fd01:1::11)', ha='center', fontsize=11, 
            bbox=dict(boxstyle="round", facecolor='white', alpha=0.8))
    ax.text(13, 7.5, 'Server\n(fd01:5::12)', ha='center', fontsize=11,
            bbox=dict(boxstyle="round", facecolor='white', alpha=0.8))
    
    # Network Layer詳細
    ax.text(8, 5.5, 'r1 -- r2 -- r4 -- r6', ha='center', fontsize=12, family='monospace')
    ax.text(8, 4.7, '|     |           |', ha='center', fontsize=12, family='monospace')
    ax.text(8, 4.5, 'r3 -- r5 ---------+', ha='center', fontsize=12, family='monospace')
    ax.text(8, 4.2, 'SRv6-enabled Linux Routers', ha='center', fontsize=10, style='italic')
    
    # Control Layer詳細
    control_components = ['MRTG\nMonitoring', 'Path\nOrchestrator', 'Docker\nManagement']
    x_positions = [4, 8, 12]
    
    for comp, x in zip(control_components, x_positions):
        ax.text(x, 2.5, comp, ha='center', fontsize=10,
                bbox=dict(boxstyle="round", facecolor='white', alpha=0.8))
    
    # データフロー矢印
    ax.annotate('', xy=(13, 6.7), xytext=(3, 6.7),
               arrowprops=dict(arrowstyle='->', color='green', lw=3))
    ax.text(8, 6.9, 'SRv6 Traffic Flow', ha='center', fontsize=10, color='green')
    
    # 保存（controllerコンテナ内のパス）
    output_path = '/opt/app/presentation/diagrams/simplified_architecture_diagram.png'
    
    # ディレクトリが存在しない場合は作成
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print(f"簡略化アーキテクチャ図を保存しました: {output_path}")
    
    return fig, ax

if __name__ == "__main__":
    print("SRv6システム研究会発表用アーキテクチャ図を生成中...")
    
    # 詳細版
    print("\n1. 詳細アーキテクチャ図生成中...")
    detailed_fig, detailed_ax = create_detailed_architecture_diagram()
    
    # 簡略版
    print("\n2. 簡略化アーキテクチャ図生成中...")
    simplified_fig, simplified_ax = create_simplified_presentation_diagram()
    
    print("\n✅ アーキテクチャ図の生成が完了しました！")
    print("📁 保存場所: /opt/app/presentation/diagrams/")
    print("   - detailed_architecture_diagram.png (詳細版)")
    print("   - simplified_architecture_diagram.png (簡略版)")
    print("\n🎯 研究会発表でご活用ください！")
    
    # 図を表示（環境によっては無効）
    try:
        plt.show()
    except:
        print("図の表示はスキップされました（GUI環境が利用できません）")