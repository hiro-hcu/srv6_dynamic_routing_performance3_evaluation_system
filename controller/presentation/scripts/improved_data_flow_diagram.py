#!/usr/bin/env python3
"""
SRv6システム データフロー図生成スクリプト（改良版）
レイアウトと可読性を大幅に改善した研究会発表用図
"""

import matplotlib
matplotlib.use('Agg')  # ヘッドレス環境用
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, FancyArrowPatch
import numpy as np
import os

# フォント設定
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 11

def create_improved_comprehensive_data_flow_diagram():
    """改良版包括的データフロー図 - レイアウトを大幅改善"""
    
    fig, ax = plt.subplots(1, 1, figsize=(24, 18))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#fafafa')
    
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 18)
    ax.axis('off')
    
    # タイトル - より大きく、位置調整
    ax.text(12, 17.3, 'SRv6 System Comprehensive Data Flow Diagram', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(12, 16.8, 'Multi-layered Data Communication Analysis - Improved Layout', 
            fontsize=13, ha='center', style='italic')
    
    # ===============================
    # 1. データフロー種別の凡例 - 上部に整理
    # ===============================
    
    legend_bg = FancyBboxPatch((1, 15.5), 22, 1, 
                              boxstyle="round,pad=0.05", 
                              facecolor='#f5f5f5', edgecolor='#424242', linewidth=1)
    ax.add_patch(legend_bg)
    ax.text(12, 16.2, 'Data Flow Types Legend', fontweight='bold', ha='center', fontsize=14)
    
    # 凡例を横一列に配置
    flow_types = [
        {'name': 'User Traffic', 'color': '#4caf50', 'style': '-', 'width': 4},
        {'name': 'SNMP Monitor', 'color': '#f44336', 'style': '--', 'width': 2},
        {'name': 'SSH Control', 'color': '#2196f3', 'style': '-.', 'width': 2},
        {'name': 'RRD Data', 'color': '#ff9800', 'style': ':', 'width': 2},
        {'name': 'Container', 'color': '#9c27b0', 'style': '-', 'width': 1.5}
    ]
    
    x_start = 2.5
    for i, flow in enumerate(flow_types):
        x_pos = x_start + i * 3.8
        ax.plot([x_pos, x_pos + 1.2], [15.8, 15.8], color=flow['color'], 
                linestyle=flow['style'], linewidth=flow['width'])
        ax.text(x_pos + 1.4, 15.8, flow['name'], fontsize=10, va='center')
    
    # ===============================
    # 2. システムコンポーネント配置 - 間隔を広げて整理
    # ===============================
    
    # Client（左上）
    client_box = FancyBboxPatch((1.5, 13), 4, 1.8, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#e3f2fd', edgecolor='#1976d2', linewidth=2)
    ax.add_patch(client_box)
    ax.text(3.5, 14.1, 'Client Container', fontweight='bold', ha='center', fontsize=13)
    ax.text(3.5, 13.7, 'IPv6: fd01:1::11', ha='center', fontsize=10, family='monospace')
    ax.text(3.5, 13.4, 'Tools: iperf3, ping', ha='center', fontsize=9)
    
    # Server（右上）
    server_box = FancyBboxPatch((18.5, 13), 4, 1.8, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#e8f5e8', edgecolor='#388e3c', linewidth=2)
    ax.add_patch(server_box)
    ax.text(20.5, 14.1, 'Server Container', fontweight='bold', ha='center', fontsize=13)
    ax.text(20.5, 13.7, 'IPv6: fd01:5::12', ha='center', fontsize=10, family='monospace')
    ax.text(20.5, 13.4, 'Service Applications', ha='center', fontsize=9)
    
    # SRv6 ルーターネットワーク（中央上部）- 位置調整
    router_positions = {
        'r1': (7, 12),
        'r2': (10.5, 12),
        'r3': (7, 10),
        'r4': (14, 12),
        'r5': (10.5, 10),
        'r6': (17.5, 12)
    }
    
    # ルーター描画 - サイズ統一
    for router, (x, y) in router_positions.items():
        router_box = FancyBboxPatch((x-0.8, y-0.6), 1.6, 1.2, 
                                   boxstyle="round,pad=0.05", 
                                   facecolor='#fff9c4', edgecolor='#f9a825', linewidth=2)
        ax.add_patch(router_box)
        ax.text(x, y+0.2, router.upper(), fontweight='bold', ha='center', fontsize=12)
        ax.text(x, y-0.2, 'SRv6', ha='center', fontsize=9)
    
    # ネットワーク接続線 - 重ならないように調整
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
        ax.plot([x1, x2], [y1, y2], 'b-', linewidth=2, alpha=0.6)
        
        # サブネット情報 - 位置調整
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        # 縦のリンクは右側に、横のリンクは上側にラベル配置
        if abs(x1 - x2) > abs(y1 - y2):  # 横向きリンク
            label_y = mid_y + 0.3
        else:  # 縦向きリンク
            label_y = mid_y
        ax.text(mid_x, label_y, subnet, fontsize=8, ha='center', 
                bbox=dict(boxstyle="round,pad=0.15", facecolor='white', alpha=0.9, edgecolor='none'))
    
    # Client-r1, r6-Server接続 - カーブを追加
    # Client → r1
    ax.annotate('', xy=(7-0.8, 12), xytext=(5.5, 13.9),
               arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=0.2", 
                             color='#4caf50', lw=4, alpha=0.8))
    # r6 → Server
    ax.annotate('', xy=(18.5, 13.9), xytext=(17.5+0.8, 12),
               arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=0.2", 
                             color='#4caf50', lw=4, alpha=0.8))
    
    # ===============================
    # 3. Controller層 - 下部に配置して分離
    # ===============================
    
    # Controller全体背景
    controller_bg = FancyBboxPatch((2, 6.5), 20, 2.5, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='#f3e5f5', edgecolor='#7b1fa2', linewidth=2)
    ax.add_patch(controller_bg)
    ax.text(12, 8.7, 'Controller & Monitoring Layer', fontweight='bold', ha='center', fontsize=15)
    ax.text(12, 8.3, 'Container: fd02:1::10', ha='center', fontsize=11, family='monospace')
    
    # Controller内部コンポーネント - 横並びで整理
    mrtg_box = FancyBboxPatch((3, 7), 4, 1.2, 
                             boxstyle="round,pad=0.1", 
                             facecolor='#ffebee', edgecolor='#d32f2f', linewidth=1.5)
    ax.add_patch(mrtg_box)
    ax.text(5, 7.8, 'MRTG Monitor', fontweight='bold', ha='center', fontsize=12)
    ax.text(5, 7.4, 'SNMP v2c Collection', ha='center', fontsize=10)
    ax.text(5, 7.1, '1-minute intervals', ha='center', fontsize=9)
    
    orchestrator_box = FancyBboxPatch((8.5, 7), 4, 1.2, 
                                     boxstyle="round,pad=0.1", 
                                     facecolor='#e8eaf6', edgecolor='#3f51b5', linewidth=1.5)
    ax.add_patch(orchestrator_box)
    ax.text(10.5, 7.8, 'Path Orchestrator', fontweight='bold', ha='center', fontsize=12)
    ax.text(10.5, 7.4, 'NetworkX Topology', ha='center', fontsize=10)
    ax.text(10.5, 7.1, 'Dynamic Routing', ha='center', fontsize=9)
    
    docker_box = FancyBboxPatch((14, 7), 4, 1.2, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#e0f2f1', edgecolor='#00796b', linewidth=1.5)
    ax.add_patch(docker_box)
    ax.text(16, 7.8, 'Container Mgmt', fontweight='bold', ha='center', fontsize=12)
    ax.text(16, 7.4, 'Docker Compose', ha='center', fontsize=10)
    ax.text(16, 7.1, 'Orchestration', ha='center', fontsize=9)
    
    rrd_box = FancyBboxPatch((19, 7), 2.5, 1.2, 
                            boxstyle="round,pad=0.1", 
                            facecolor='#fff3e0', edgecolor='#f57c00', linewidth=1.5)
    ax.add_patch(rrd_box)
    ax.text(20.25, 7.8, 'RRD DB', fontweight='bold', ha='center', fontsize=12)
    ax.text(20.25, 7.4, 'Time Series', ha='center', fontsize=10)
    ax.text(20.25, 7.1, 'Data Storage', ha='center', fontsize=9)
    
    # ===============================
    # 4. データフロー矢印 - 重ならないように配置
    # ===============================
    
    # 1. ユーザートラフィックフロー（メインパス）
    main_path_points = [
        (7, 12), (10.5, 12), (14, 12), (17.5, 12)
    ]
    
    for i in range(len(main_path_points) - 1):
        x1, y1 = main_path_points[i]
        x2, y2 = main_path_points[i + 1]
        arrow = FancyArrowPatch((x1+0.8, y1), (x2-0.8, y2),
                               arrowstyle='->', mutation_scale=18,
                               color='#4caf50', linewidth=4, alpha=0.8)
        ax.add_patch(arrow)
    
    # 代替パス（点線）
    alt_path_points = [(7, 12), (7, 10), (10.5, 10), (17.5, 12)]
    for i in range(len(alt_path_points) - 1):
        x1, y1 = alt_path_points[i]
        x2, y2 = alt_path_points[i + 1]
        if i == 0:  # r1 → r3
            arrow = FancyArrowPatch((x1, y1-0.6), (x2, y2+0.6),
                                   arrowstyle='->', mutation_scale=12,
                                   color='#4caf50', linewidth=2, alpha=0.5, linestyle='--')
        elif i == 1:  # r3 → r5
            arrow = FancyArrowPatch((x1+0.8, y1), (x2-0.8, y2),
                                   arrowstyle='->', mutation_scale=12,
                                   color='#4caf50', linewidth=2, alpha=0.5, linestyle='--')
        else:  # r5 → r6
            arrow = FancyArrowPatch((x1, y1), (x2, y2-0.6),
                                   arrowstyle='->', mutation_scale=12,
                                   color='#4caf50', linewidth=2, alpha=0.5, linestyle='--')
        ax.add_patch(arrow)
    
    # 2. SNMP監視フロー - カーブで重なりを回避
    snmp_targets = [(7, 12), (10.5, 12), (14, 12), (17.5, 12), (7, 10), (10.5, 10)]
    for i, (x, y) in enumerate(snmp_targets):
        # 各ルーターからMRTGへ
        curve_rad = 0.3 + i * 0.1  # 各線に異なるカーブを適用
        ax.annotate('', xy=(5, 7), xytext=(x, y-0.6),
                   arrowprops=dict(arrowstyle='->', connectionstyle=f"arc3,rad={curve_rad}", 
                                 color='#f44336', lw=1.5, alpha=0.7, linestyle='--'))
    
    # 3. SSH制御フロー - より緩やかなカーブ
    for i, (x, y) in enumerate(snmp_targets):
        curve_rad = -0.2 - i * 0.05
        ax.annotate('', xy=(x, y+0.6), xytext=(10.5, 7),
                   arrowprops=dict(arrowstyle='->', connectionstyle=f"arc3,rad={curve_rad}", 
                                 color='#2196f3', lw=1.5, alpha=0.7, linestyle='-.'))
    
    # 4. データ保存フロー
    ax.annotate('', xy=(19, 7.6), xytext=(7, 7.6),
               arrowprops=dict(arrowstyle='->', color='#ff9800', lw=2, alpha=0.8, linestyle=':'))
    
    # ===============================
    # 5. 詳細情報パネル - 下部に整理
    # ===============================
    
    # 左パネル: トラフィックフロー
    traffic_panel = FancyBboxPatch((1, 2), 7, 4, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='#e8f5e8', edgecolor='#388e3c', linewidth=1.5)
    ax.add_patch(traffic_panel)
    ax.text(4.5, 5.7, 'User Traffic Flow Process', fontweight='bold', ha='center', fontsize=13)
    
    traffic_steps = [
        "1. Client generates IPv6 packets",
        "2. r1 applies SRv6 encapsulation", 
        "3. Segment List Configuration:",
        "   • Primary: [fd01:2::12, fd01:3::12, fd01:4::12]",
        "   • Backup: [fd01:8::12, fd01:7::12, fd01:6::12]",
        "4. Dynamic path selection criteria:",
        "   • Real-time link utilization",
        "   • Historical performance data",
        "   • Network topology changes",
        "5. r6 decapsulates → Server delivery"
    ]
    
    for i, step in enumerate(traffic_steps):
        ax.text(1.3, 5.3 - i*0.35, step, fontsize=10, va='top')
    
    # 中央パネル: 監視制御
    control_panel = FancyBboxPatch((8.5, 2), 7, 4, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='#fff3e0', edgecolor='#f57c00', linewidth=1.5)
    ax.add_patch(control_panel)
    ax.text(12, 5.7, 'Monitoring & Control Details', fontweight='bold', ha='center', fontsize=13)
    
    control_steps = [
        "SNMP Data Collection:",
        "• Target: ifHCInOctets/ifHCOutOctets",
        "• Frequency: Every 60 seconds",
        "• Protocol: SNMPv2c (Community: public)",
        "",
        "SSH Control Operations:",
        "• Routing table modifications",
        "• SRv6 segment updates", 
        "• Interface management",
        "",
        "RRD Processing:",
        "• Time-series storage (5-year retention)",
        "• Traffic trend analysis",
        "• Performance optimization data"
    ]
    
    for i, step in enumerate(control_steps):
        ax.text(8.8, 5.3 - i*0.25, step, fontsize=9, va='top')
    
    # 右パネル: パフォーマンス
    perf_panel = FancyBboxPatch((16, 2), 7, 4, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#f3e5f5', edgecolor='#7b1fa2', linewidth=1.5)
    ax.add_patch(perf_panel)
    ax.text(19.5, 5.7, 'System Performance Metrics', fontweight='bold', ha='center', fontsize=13)
    
    perf_metrics = [
        "Network Performance:",
        "• Throughput: Up to 100 Mbps/link",
        "• Latency: < 10ms inter-router",
        "• Path switch time: < 30 seconds",
        "",
        "Monitoring Capabilities:",
        "• Data resolution: 1-minute intervals",
        "• Historical data: 5-year retention",
        "• Real-time analysis: < 5 seconds",
        "",
        "System Features:",
        "• Container-based deployment",
        "• Automated failover capability",
        "• Dynamic optimization algorithms"
    ]
    
    for i, metric in enumerate(perf_metrics):
        ax.text(16.3, 5.3 - i*0.25, metric, fontsize=9, va='top')
    
    # ===============================
    # 6. フロー説明ラベル
    # ===============================
    
    # メインフローラベル
    ax.text(12, 12.7, 'Primary SRv6 Path', ha='center', fontsize=11, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#4caf50', alpha=0.2))
    
    # 代替フローラベル
    ax.text(9, 9.2, 'Backup Path', ha='center', fontsize=10, 
            bbox=dict(boxstyle="round,pad=0.2", facecolor='#4caf50', alpha=0.1))
    
    plt.tight_layout()
    
    # 保存
    output_path = '/opt/app/presentation/diagrams/improved_comprehensive_data_flow_diagram.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print(f"改良版包括的データフロー図を保存しました: {output_path}")
    return fig, ax

def create_clean_simplified_data_flow_diagram():
    """クリーンな簡略化データフロー図"""
    
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#fafafa')
    
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # タイトル
    ax.text(9, 11.3, 'SRv6 System Data Flow Overview - Clean Layout', 
            fontsize=18, fontweight='bold', ha='center')
    ax.text(9, 10.8, 'Three Key Data Communication Patterns', 
            fontsize=13, ha='center', style='italic')
    
    # 3つの主要データフローを縦に配置
    flows = [
        {
            'title': '1. User Traffic Flow',
            'y': 8.5,
            'color': '#4caf50',
            'icon': '🌐',
            'source': 'Client Container',
            'target': 'Server Container', 
            'path': 'SRv6 Network (r1→r2→r4→r6)',
            'description': 'IPv6 packets with SRv6 segment routing headers\nDynamic path selection based on network conditions'
        },
        {
            'title': '2. Network Monitoring Flow', 
            'y': 5.5,
            'color': '#f44336',
            'icon': '📊',
            'source': 'Router Interfaces',
            'target': 'MRTG → RRD Database',
            'path': 'SNMP v2c Protocol',
            'description': 'Traffic statistics collection every 1 minute\nHistorical data storage for trend analysis'
        },
        {
            'title': '3. System Control Flow',
            'y': 2.5,
            'color': '#2196f3',
            'icon': '🎛️',
            'source': 'Path Orchestrator',
            'target': 'Router Configuration',
            'path': 'SSH Remote Commands',
            'description': 'Dynamic routing table updates\nAutomatic network optimization based on monitoring data'
        }
    ]
    
    for flow in flows:
        # メインボックス
        main_box = FancyBboxPatch((1, flow['y']-1), 16, 2, 
                                 boxstyle="round,pad=0.15", 
                                 facecolor=f"{flow['color']}15", 
                                 edgecolor=flow['color'], linewidth=2)
        ax.add_patch(main_box)
        
        # アイコンとタイトル
        ax.text(2, flow['y']+0.5, flow['icon'], fontsize=20, va='center')
        ax.text(3, flow['y']+0.5, flow['title'], 
                fontweight='bold', fontsize=14, color=flow['color'], va='center')
        
        # フロー矢印と経路
        ax.annotate('', xy=(14, flow['y']), xytext=(4, flow['y']),
                   arrowprops=dict(arrowstyle='->', mutation_scale=25,
                                 color=flow['color'], linewidth=3))
        
        ax.text(9, flow['y']+0.1, flow['path'], ha='center', fontsize=11, 
                fontweight='bold', va='center')
        
        # ソースとターゲット
        ax.text(4, flow['y']-0.3, f"From: {flow['source']}", fontsize=10, va='center')
        ax.text(14, flow['y']-0.3, f"To: {flow['target']}", fontsize=10, va='center', ha='right')
        
        # 説明
        ax.text(9, flow['y']-0.6, flow['description'], ha='center', fontsize=10, 
                va='center', style='italic')
    
    # システム統合効果
    integration_box = FancyBboxPatch((2, 0.2), 14, 1.2, 
                                    boxstyle="round,pad=0.1", 
                                    facecolor='#f5f5f5', edgecolor='#424242', linewidth=1.5)
    ax.add_patch(integration_box)
    ax.text(9, 1, '🔄 Integrated System Benefits', fontweight='bold', ha='center', fontsize=14)
    ax.text(9, 0.6, 'Real-time monitoring enables intelligent path optimization', ha='center', fontsize=11)
    ax.text(9, 0.3, 'Historical analysis supports predictive network management', ha='center', fontsize=11)
    
    # 保存
    output_path = '/opt/app/presentation/diagrams/clean_simplified_data_flow_diagram.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print(f"クリーンな簡略化データフロー図を保存しました: {output_path}")
    return fig, ax

def create_organized_protocol_stack_diagram():
    """整理されたプロトコルスタック図"""
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#fafafa')
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # タイトル
    ax.text(8, 11.5, 'SRv6 Protocol Stack & Processing - Organized View', 
            fontsize=17, fontweight='bold', ha='center')
    ax.text(8, 11, 'Layer-by-layer Data Processing Architecture', 
            fontsize=12, ha='center', style='italic')
    
    # プロトコルスタック層 - 間隔を広げて整理
    layers = [
        {
            'name': 'Application Layer', 
            'y': 9.5, 
            'color': '#e3f2fd', 
            'edge': '#1976d2', 
            'content': 'iperf3, ping, SSH client, SNMP tools',
            'details': 'User applications and network testing tools'
        },
        {
            'name': 'Transport Layer', 
            'y': 8, 
            'color': '#e8f5e8', 
            'edge': '#388e3c', 
            'content': 'TCP (SSH), UDP (SNMP), ICMPv6 (ping)',
            'details': 'Reliable and unreliable data transport'
        },
        {
            'name': 'Network Layer', 
            'y': 6.5, 
            'color': '#fff3e0', 
            'edge': '#f57c00', 
            'content': 'IPv6 Base Header + SRv6 Extension Headers',
            'details': 'Segment Routing over IPv6 implementation'
        },
        {
            'name': 'Data Link Layer', 
            'y': 5, 
            'color': '#f3e5f5', 
            'edge': '#7b1fa2', 
            'content': 'Ethernet frames over Docker bridge networks',
            'details': 'Container network interface abstraction'
        },
        {
            'name': 'Physical Layer', 
            'y': 3.5, 
            'color': '#fafafa', 
            'edge': '#616161', 
            'content': 'Virtual network interfaces (veth pairs)',
            'details': 'Docker container networking infrastructure'
        }
    ]
    
    for layer in layers:
        # メイン層ボックス
        layer_box = FancyBboxPatch((1, layer['y']-0.6), 14, 1.2, 
                                  boxstyle="round,pad=0.05", 
                                  facecolor=layer['color'], 
                                  edgecolor=layer['edge'], linewidth=2)
        ax.add_patch(layer_box)
        
        # 層名
        ax.text(2, layer['y'], layer['name'], fontweight='bold', fontsize=13, va='center')
        
        # プロトコル/技術内容
        ax.text(8, layer['y']+0.15, layer['content'], fontsize=11, va='center', ha='center')
        
        # 詳細説明
        ax.text(8, layer['y']-0.25, layer['details'], fontsize=9, va='center', ha='center', 
                style='italic', alpha=0.8)
    
    # SRv6詳細セクション
    srv6_section = FancyBboxPatch((1, 0.5), 14, 2.5, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#fff9c4', edgecolor='#f9a825', linewidth=2)
    ax.add_patch(srv6_section)
    ax.text(8, 2.7, '🔍 SRv6 Header Structure Details', fontweight='bold', ha='center', fontsize=14)
    
    # SRv6詳細を2列に配置
    srv6_left = [
        "Routing Header Type 4 (SRH):",
        "• Next Header: Protocol following SRH",
        "• Hdr Ext Len: Length of SRH in 8-byte units", 
        "• Routing Type: 4 (indicates SRv6)",
        "• Segments Left: Remaining segments to process"
    ]
    
    srv6_right = [
        "Segment List Example:",
        "• [0] fd01:2::12 (r1→r2 segment)",
        "• [1] fd01:3::12 (r2→r4 segment)",
        "• [2] fd01:4::12 (r4→r6 segment)",
        "• Active segment updated at each hop"
    ]
    
    for i, detail in enumerate(srv6_left):
        ax.text(1.5, 2.3 - i*0.25, detail, fontsize=10, va='top')
    
    for i, detail in enumerate(srv6_right):
        ax.text(8.5, 2.3 - i*0.25, detail, fontsize=10, va='top')
    
    plt.tight_layout()
    
    # 保存
    output_path = '/opt/app/presentation/diagrams/organized_protocol_stack_diagram.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print(f"整理されたプロトコルスタック図を保存しました: {output_path}")
    return fig, ax

if __name__ == "__main__":
    print("SRv6システム データフロー図生成中（改良版）...")
    
    # 改良版包括的データフロー図
    print("\n1. 改良版包括的データフロー図生成中...")
    improved_comprehensive_fig, improved_comprehensive_ax = create_improved_comprehensive_data_flow_diagram()
    
    # クリーンな簡略化データフロー図
    print("\n2. クリーンな簡略化データフロー図生成中...")
    clean_simplified_fig, clean_simplified_ax = create_clean_simplified_data_flow_diagram()
    
    # 整理されたプロトコルスタック図
    print("\n3. 整理されたプロトコルスタック図生成中...")
    organized_protocol_fig, organized_protocol_ax = create_organized_protocol_stack_diagram()
    
    print("\n✅ 改良版データフロー図の生成が完了しました！")
    print("📁 保存場所: /opt/app/presentation/diagrams/")
    print("   - improved_comprehensive_data_flow_diagram.png (改良版包括的)")
    print("   - clean_simplified_data_flow_diagram.png (クリーン簡略版)")
    print("   - organized_protocol_stack_diagram.png (整理版プロトコルスタック)")
    print("\n🎯 レイアウトを大幅改善しました！研究会発表でご活用ください！")
    
    # 図を表示（環境によってはスキップ）
    try:
        plt.show()
    except:
        print("図の表示はスキップされました（GUI環境が利用できません）")