#!/usr/bin/env python3
"""
Phase 3 Extended: SRv6 Multi-Table Real-time Manager (Optimized)
RRDデータ統合 + リアルタイム監視 + 動的経路選択
最適化版: クラス構造の整理、重複コードの削除
"""

import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import subprocess
import sys
import math
import time
import paramiko
import logging
import warnings
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import os

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
warnings.filterwarnings('ignore', message='.*Glyph.*missing from.*font.*')

# ============================================================================
# 設定変数
# ============================================================================
HISTORY_SAVE_DIR = "srv6_evaluation3_udp/trial3"
MEASUREMENT_DURATION_MINUTES = 52

# ============================================================================
# 定数定義
# ============================================================================
MAX_BANDWIDTH_05G = 62_500_000   # 0.5Gbps in Bytes/s
MAX_BANDWIDTH_1G = 125_000_000   # 1Gbps in Bytes/s
MIN_WEIGHT = 0.0001
WEIGHT_MULTIPLIERS = [3.0, 2.0, 1.0]  # 高優先度、中優先度、低優先度


@dataclass
class TableRoute:
    """テーブル経路情報"""
    table_name: str
    priority: str
    path: List[int]
    segments: List[str]
    interfaces: List[str]
    output_interface: str
    cost: float
    description: str


@dataclass
class PathChangeEvent:
    """経路変更イベント"""
    timestamp: str
    table_name: str
    old_path: Optional[List[int]]
    new_path: List[int]
    old_segments: Optional[List[str]]
    new_segments: List[str]
    old_interface: Optional[str]
    new_interface: str
    reason: str


@dataclass
class SRv6Config:
    """SRv6統合設定クラス"""
    # SSH接続設定
    r1_host: str = "fd02:1::2"
    r16_host: str = "fd02:1::11"
    ssh_port: int = 22
    ssh_user: str = "root"
    ssh_password: str = "@k@n@3>ki"
    device: str = "eth1"
    timeout: int = 15
    
    # ルーティング設定
    route_prefix: str = "fd03:1::/64"
    return_route_prefix: str = "fd00:1::/64"
    
    # テーブル定義
    tables: List[Dict[str, str]] = field(default_factory=lambda: [
        {"name": "rt_table1", "priority": "高優先度", "description": "高優先度"},
        {"name": "rt_table2", "priority": "中優先度", "description": "中優先度"},
        {"name": "rt_table3", "priority": "低優先度", "description": "低優先度"}
    ])

    # RRDファイルパス
    RRD_PATHS: Dict[Tuple[int, int], str] = field(default_factory=lambda: {
        (1, 2): '/opt/app/mrtg/mrtg_file/r1-r2.rrd',
        (1, 3): '/opt/app/mrtg/mrtg_file/r1-r3.rrd',
        (2, 4): '/opt/app/mrtg/mrtg_file/r2-r4.rrd',
        (2, 5): '/opt/app/mrtg/mrtg_file/r2-r5.rrd',
        (3, 5): '/opt/app/mrtg/mrtg_file/r3-r5.rrd',
        (3, 6): '/opt/app/mrtg/mrtg_file/r3-r6.rrd',
        (4, 7): '/opt/app/mrtg/mrtg_file/r4-r7.rrd',
        (4, 8): '/opt/app/mrtg/mrtg_file/r4-r8.rrd',
        (5, 8): '/opt/app/mrtg/mrtg_file/r5-r8.rrd',
        (5, 9): '/opt/app/mrtg/mrtg_file/r5-r9.rrd',
        (6, 9): '/opt/app/mrtg/mrtg_file/r6-r9.rrd',
        (6, 10): '/opt/app/mrtg/mrtg_file/r6-r10.rrd',
        (7, 11): '/opt/app/mrtg/mrtg_file/r7-r11.rrd',
        (8, 11): '/opt/app/mrtg/mrtg_file/r8-r11.rrd',
        (8, 12): '/opt/app/mrtg/mrtg_file/r8-r12.rrd',
        (9, 12): '/opt/app/mrtg/mrtg_file/r9-r12.rrd',
        (9, 13): '/opt/app/mrtg/mrtg_file/r9-r13.rrd',
        (10, 13): '/opt/app/mrtg/mrtg_file/r10-r13.rrd',
        (11, 14): '/opt/app/mrtg/mrtg_file/r11-r14.rrd',
        (12, 14): '/opt/app/mrtg/mrtg_file/r12-r14.rrd',
        (12, 15): '/opt/app/mrtg/mrtg_file/r12-r15.rrd',
        (13, 15): '/opt/app/mrtg/mrtg_file/r13-r15.rrd',
        (14, 16): '/opt/app/mrtg/mrtg_file/r14-r16.rrd',
        (15, 16): '/opt/app/mrtg/mrtg_file/r15-r16.rrd',
    })

    # セグメントマッピング（往路・復路統合）
    SEGMENT_MAP: Dict[str, Dict[int, Dict[int, Tuple[str, str]]]] = field(default_factory=lambda: {
        "forward": {
            1: {2: ("fd01:1::12", "eth1"), 3: ("fd01:16::12", "eth2")},
            2: {4: ("fd01:2::12", "eth2"), 5: ("fd01:4::12", "eth3")},
            3: {5: ("fd01:17::12", "eth0"), 6: ("fd01:15::12", "eth0")},
            4: {2: ("fd01:2::11", "eth2"), 7: ("fd01:3::12", "eth2"), 8: ("fd01:6::12", "eth2")},
            5: {2: ("fd01:4::11", "eth2"), 3: ("fd01:17::11", "eth2"), 8: ("fd01:5::12", "eth3"), 9: ("fd01:12::12", "eth3")},
            6: {3: ("fd01:15::11", "eth3"), 9: ("fd01:18::12", "eth3"), 10: ("fd01:14::12", "eth3")},
            7: {4: ("fd01:3::11", "eth3"), 11: ("fd01:8::12", "eth3")},
            8: {4: ("fd01:6::11", "eth3"), 5: ("fd01:5::11", "eth3"), 11: ("fd01:7::12", "eth3"), 12: ("fd01:b::12", "eth3")},
            9: {5: ("fd01:12::11", "eth3"), 6: ("fd01:18::11", "eth3"), 12: ("fd01:11::12", "eth3"), 13: ("fd01:10::12", "eth3")},
            10: {6: ("fd01:14::11", "eth3"), 13: ("fd01:13::12", "eth3")},
            11: {7: ("fd01:8::11", "eth3"), 8: ("fd01:7::11", "eth3"), 14: ("fd01:9::12", "eth3")},
            12: {8: ("fd01:b::11", "eth3"), 9: ("fd01:11::11", "eth3"), 14: ("fd01:c::12", "eth3"), 15: ("fd01:d::12", "eth3")},
            13: {9: ("fd01:10::11", "eth3"), 10: ("fd01:13::11", "eth3"), 15: ("fd01:f::12", "eth3")},
            14: {11: ("fd01:9::11", "eth3"), 12: ("fd01:c::11", "eth3"), 16: ("fd01:a::12", "eth3")},
            15: {12: ("fd01:d::11", "eth3"), 13: ("fd01:f::11", "eth3"), 16: ("fd01:e::12", "eth3")},
        },
        "return": {
            16: {15: ("fd01:e::11", "eth1"), 14: ("fd01:a::11", "eth2")},
            15: {16: ("fd01:e::12", "eth3"), 13: ("fd01:f::11", "eth1"), 12: ("fd01:d::11", "eth2")},
            14: {16: ("fd01:a::12", "eth3"), 12: ("fd01:c::11", "eth3"), 11: ("fd01:9::11", "eth3")},
            13: {15: ("fd01:f::12", "eth3"), 10: ("fd01:13::11", "eth3"), 9: ("fd01:10::11", "eth3")},
            12: {15: ("fd01:d::12", "eth3"), 14: ("fd01:c::12", "eth3"), 9: ("fd01:11::11", "eth3"), 8: ("fd01:b::11", "eth3")},
            11: {14: ("fd01:9::12", "eth3"), 8: ("fd01:7::11", "eth3"), 7: ("fd01:8::11", "eth3")},
            10: {13: ("fd01:13::12", "eth3"), 6: ("fd01:14::11", "eth3")},
            9: {13: ("fd01:10::12", "eth3"), 12: ("fd01:11::12", "eth3"), 6: ("fd01:18::11", "eth3"), 5: ("fd01:12::11", "eth3")},
            8: {12: ("fd01:b::12", "eth3"), 11: ("fd01:7::12", "eth3"), 5: ("fd01:5::11", "eth3"), 4: ("fd01:6::11", "eth3")},
            7: {11: ("fd01:8::12", "eth3"), 4: ("fd01:3::11", "eth3")},
            6: {10: ("fd01:14::12", "eth3"), 9: ("fd01:18::12", "eth3"), 3: ("fd01:15::11", "eth0")},
            5: {9: ("fd01:12::12", "eth3"), 8: ("fd01:5::12", "eth3"), 3: ("fd01:17::11", "eth0"), 2: ("fd01:4::11", "eth3")},
            4: {8: ("fd01:6::12", "eth3"), 7: ("fd01:3::12", "eth3"), 2: ("fd01:2::11", "eth2")},
            3: {6: ("fd01:15::12", "eth3"), 5: ("fd01:17::12", "eth3"), 1: ("fd01:16::11", "eth2")},
            2: {5: ("fd01:4::12", "eth3"), 4: ("fd01:2::12", "eth3"), 1: ("fd01:1::11", "eth1")},
        }
    })

    # エッジ定義（トポロジ）
    EDGES: List[Tuple[int, int, int]] = field(default_factory=lambda: [
        (1, 2, MAX_BANDWIDTH_1G), (1, 3, MAX_BANDWIDTH_1G),
        (2, 4, MAX_BANDWIDTH_1G), (2, 5, MAX_BANDWIDTH_1G),
        (3, 5, MAX_BANDWIDTH_1G), (3, 6, MAX_BANDWIDTH_1G),
        (4, 7, MAX_BANDWIDTH_05G), (4, 8, MAX_BANDWIDTH_05G),
        (5, 8, MAX_BANDWIDTH_05G), (5, 9, MAX_BANDWIDTH_05G),
        (6, 9, MAX_BANDWIDTH_05G), (6, 10, MAX_BANDWIDTH_05G),
        (7, 11, MAX_BANDWIDTH_05G), (8, 11, MAX_BANDWIDTH_05G),
        (8, 12, MAX_BANDWIDTH_05G), (9, 12, MAX_BANDWIDTH_05G),
        (9, 13, MAX_BANDWIDTH_05G), (10, 13, MAX_BANDWIDTH_05G),
        (11, 14, MAX_BANDWIDTH_1G), (12, 14, MAX_BANDWIDTH_1G),
        (12, 15, MAX_BANDWIDTH_1G), (13, 15, MAX_BANDWIDTH_1G),
        (14, 16, MAX_BANDWIDTH_1G), (15, 16, MAX_BANDWIDTH_1G),
    ])


class SSHManager:
    """SSH接続管理クラス"""
    
    def __init__(self, config: SRv6Config):
        self.config = config
    
    @contextmanager
    def connect(self, host: str):
        """SSH接続コンテキストマネージャー"""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            client.connect(
                hostname=host,
                port=self.config.ssh_port,
                username=self.config.ssh_user,
                password=self.config.ssh_password,
                timeout=self.config.timeout
            )
            yield client
        except Exception as e:
            logger.error(f"SSH接続エラー ({host}): {e}")
            raise
        finally:
            client.close()
    
    def execute(self, client: paramiko.SSHClient, command: str) -> Tuple[int, str, str]:
        """SSHコマンド実行"""
        try:
            stdin, stdout, stderr = client.exec_command(command)
            rc = stdout.channel.recv_exit_status()
            return rc, stdout.read().decode('utf-8').strip(), stderr.read().decode('utf-8').strip()
        except Exception as e:
            logger.error(f"コマンド実行エラー: {e}")
            return 1, "", str(e)


class NetworkGraph:
    """ネットワークグラフ管理クラス（トポロジ + 経路計算）"""
    
    def __init__(self, config: SRv6Config):
        self.config = config
        self.graph = nx.Graph()
        self._build_topology()
    
    def _build_topology(self):
        """トポロジ構築"""
        self.graph.add_nodes_from(range(1, 17))
        for u, v, max_bw in self.config.EDGES:
            self.graph.add_edge(u, v, weight=MIN_WEIGHT, max_bandwidth=max_bw)
    
    def update_weights_from_rrd(self) -> bool:
        """RRDデータからエッジ重みを更新"""
        update_count = 0
        
        for u, v in self.graph.edges():
            edge_key = (u, v) if (u, v) in self.config.RRD_PATHS else (v, u)
            rrd_path = self.config.RRD_PATHS.get(edge_key)
            max_bandwidth = self.graph[u][v].get('max_bandwidth', MAX_BANDWIDTH_05G)
            
            if rrd_path:
                out_bytes = self._fetch_rrd_data(rrd_path)
                if out_bytes is not None:
                    utilization = max(0.0, min(1.0, out_bytes / max_bandwidth))
                    self.graph[u][v]['weight'] = max(utilization, MIN_WEIGHT)
                    self._log_traffic(u, v, out_bytes, utilization)
                    update_count += 1
                else:
                    self.graph[u][v]['weight'] = MIN_WEIGHT
                    logger.warning(f"Edge r{u} <-> r{v}: RRDデータ取得失敗")
            else:
                self.graph[u][v]['weight'] = MIN_WEIGHT
        
        logger.info(f"エッジ重み更新完了: {update_count}/{len(self.graph.edges())}")
        return update_count > 0
    
    def _fetch_rrd_data(self, rrd_path: str) -> Optional[float]:
        """RRDデータ取得"""
        try:
            result = subprocess.run(
                ['rrdtool', 'fetch', rrd_path, 'AVERAGE', '--start', '-60s'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                return None
            
            for line in reversed(result.stdout.strip().split('\n')[2:]):
                if ':' in line:
                    parts = line.split()
                    if len(parts) >= 3 and parts[2].lower() not in ['-nan', 'nan']:
                        try:
                            val = float(parts[2])
                            if not math.isnan(val):
                                return val
                        except ValueError:
                            continue
            return None
        except Exception as e:
            logger.error(f"RRDデータ取得エラー ({rrd_path}): {e}")
            return None
    
    def _log_traffic(self, u: int, v: int, bytes_per_sec: float, utilization: float):
        """トラフィックログ出力"""
        bps = bytes_per_sec * 8
        if bps >= 1_000_000:
            display = f"{bps / 1_000_000:.2f} Mbps"
        elif bps >= 1_000:
            display = f"{bps / 1_000:.2f} Kbps"
        else:
            display = f"{bps:.2f} bps"
        logger.info(f"Edge r{u} <-> r{v}: {display} (利用率: {utilization:.4f})")
    
    def calculate_paths(self, src: int, dst: int, num_paths: int = 3, verbose: bool = True) -> List[Tuple[List[int], float]]:
        """複数経路計算（Dijkstra法 + 重み倍率適用）"""
        paths = []
        temp_graph = self.graph.copy()
        priorities = ['高', '中', '低']
        
        for i in range(num_paths):
            try:
                path = nx.shortest_path(temp_graph, src, dst, weight='weight')
                cost = nx.shortest_path_length(temp_graph, src, dst, weight='weight')
                paths.append((path, cost))
                
                if verbose:
                    path_str = ' → '.join([f'r{n}' for n in path])
                    logger.info(f"経路{i+1}（優先度: {priorities[i] if i < 3 else '---'}）: {path_str} (総コスト: {cost:.6f})")
                
                # 次の経路用に重み増加
                if i < num_paths - 1:
                    multiplier = WEIGHT_MULTIPLIERS[i]
                    for j in range(len(path) - 1):
                        u, v = path[j], path[j + 1]
                        if temp_graph.has_edge(u, v):
                            temp_graph[u][v]['weight'] *= multiplier
                            
            except nx.NetworkXNoPath:
                logger.warning(f"経路{i+1}の計算失敗: 経路が存在しません")
                break
        
        return paths
    
    def path_to_sid_list(self, path: List[int], is_return: bool = False) -> Tuple[List[str], List[str], str]:
        """経路をSIDリストに変換"""
        direction = "return" if is_return else "forward"
        segment_map = self.config.SEGMENT_MAP[direction]
        sid_list, interface_list = [], []
        
        for i in range(len(path) - 1):
            current, next_node = path[i], path[i + 1]
            if current in segment_map and next_node in segment_map[current]:
                seg, iface = segment_map[current][next_node]
                sid_list.append(seg)
                interface_list.append(iface)
        
        output_interface = interface_list[0] if interface_list else "eth0"
        return sid_list, interface_list, output_interface


class TopologyVisualizer:
    """ネットワークトポロジ可視化クラス"""
    
    def __init__(self, graph: nx.Graph, output_dir: str = "/opt/app/visualization"):
        self.graph = graph
        self.output_dir = output_dir
        self.history_dir = os.path.join(output_dir, HISTORY_SAVE_DIR)
        self.start_time = time.time()
        self.fig = None
        self.ax = None
        
        # 格子状レイアウト
        self.pos = {
            1: (0, 3), 2: (1, 3), 4: (2, 3), 7: (3, 3),
            3: (0, 2), 5: (1, 2), 8: (2, 2), 11: (3, 2),
            6: (0, 1), 9: (1, 1), 12: (2, 1), 14: (3, 1),
            10: (0, 0), 13: (1, 0), 15: (2, 0), 16: (3, 0)
        }
        
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.history_dir, exist_ok=True)
        self._setup_figure()
    
    def _setup_figure(self):
        """図の初期設定"""
        self.fig, self.ax = plt.subplots(figsize=(14, 10))
    
    def visualize(self, paths: List[Tuple[List[int], float]] = None, update_count: int = 0):
        """トポロジと経路を可視化"""
        self.ax.clear()
        
        # ノード描画
        nx.draw_networkx_nodes(self.graph, self.pos, node_color='lightblue', node_size=1000, ax=self.ax)
        nx.draw_networkx_labels(self.graph, self.pos, labels={n: f'r{n}' for n in self.graph.nodes()},
                                font_size=12, font_weight='bold', ax=self.ax)
        
        # 全エッジ描画
        nx.draw_networkx_edges(self.graph, self.pos, edge_color='gray', width=1, alpha=0.3, ax=self.ax)
        
        # エッジラベル
        edge_labels = {(u, v): f'U:{self.graph[u][v].get("weight", 0.0):.4f}' for u, v in self.graph.edges()}
        nx.draw_networkx_edge_labels(self.graph, self.pos, edge_labels=edge_labels, font_size=10, ax=self.ax)
        
        # 選択経路を色分け描画
        if paths:
            colors, labels, widths = ['red', 'orange', 'green'], ['High Priority', 'Medium Priority', 'Low Priority'], [4, 3, 2]
            for idx, (path_nodes, cost) in enumerate(paths[:3]):
                path_edges = [(path_nodes[i], path_nodes[i+1]) for i in range(len(path_nodes)-1)]
                path_str = " -> ".join([f"r{n}" for n in path_nodes])
                nx.draw_networkx_edges(self.graph, self.pos, edgelist=path_edges, edge_color=colors[idx],
                                       width=widths[idx], alpha=0.7, label=f'{labels[idx]}: {path_str} (Cost={cost:.4f})', ax=self.ax)
        
        # タイトル
        elapsed_minutes = int((time.time() - self.start_time) / 60)
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        self.ax.text(0.5, 1.08, f"Elapsed: {elapsed_minutes} minute{'s' if elapsed_minutes != 1 else ''}",
                    transform=self.ax.transAxes, fontsize=18, fontweight='bold', ha='center', va='bottom',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        self.ax.set_title(f'SRv6 Network Topology and Path Selection\n(Update Count: {update_count}, Time: {timestamp})',
                         fontsize=16, fontweight='bold')
        if paths:
            self.ax.legend(loc='upper left', fontsize=11)
        self.ax.axis('off')
        plt.tight_layout()
        
        # 保存
        plt.savefig(os.path.join(self.output_dir, 'topology_latest.png'), dpi=150, bbox_inches='tight')
        plt.savefig(os.path.join(self.history_dir, f"{elapsed_minutes}_minutes.png"), dpi=150, bbox_inches='tight')
    
    def close(self):
        if self.fig:
            plt.close(self.fig)


class SRv6PathManager:
    """SRv6双方向パス管理クラス（統合版）"""
    
    def __init__(self, enable_visualization: bool = False):
        self.config = SRv6Config()
        self.network = NetworkGraph(self.config)
        self.ssh = SSHManager(self.config)
        self.visualizer = TopologyVisualizer(self.network.graph) if enable_visualization else None
        
        self.update_count = 0
        self.calculated_paths = None
        self.current_table_routes = {}
        self.path_history = []
        self.stats = {'total_updates': 0, 'path_changes': 0, 'last_update': None}
        
        logger.info("SRv6パス管理システム初期化完了")
    
    def update_bidirectional_tables(self) -> bool:
        """双方向テーブル統合更新"""
        try:
            logger.info("🚀 双方向テーブル更新開始")
            
            # RRDデータ取得
            if not self.network.update_weights_from_rrd():
                logger.error("トラフィックデータ取得失敗")
                return False
            
            # 往路経路計算
            self.calculated_paths = self.network.calculate_paths(1, 16, 3)
            if not self.calculated_paths:
                logger.error("往路経路計算失敗")
                return False
            
            forward_path = self.calculated_paths[0][0]
            return_path = forward_path[::-1]
            
            logger.info(f"往路最適経路: {' → '.join([f'r{n}' for n in forward_path])}")
            logger.info(f"復路最適経路: {' → '.join([f'r{n}' for n in return_path])}")
            
            # テーブル生成
            forward_routes = self._create_table_routes(is_return=False)
            return_routes = self._create_table_routes(is_return=True)
            
            if not forward_routes or not return_routes:
                logger.error("テーブル生成失敗")
                return False
            
            # 経路変更検出
            changes = self._detect_path_changes(forward_routes)
            if changes:
                self._log_path_changes(changes)
            
            # テーブル更新実行
            forward_success = self._update_tables(forward_routes, is_return=False)
            return_success = self._update_tables(return_routes, is_return=True)
            
            # 統計更新
            self.update_count += 1
            self.stats['total_updates'] += 1
            self.stats['last_update'] = time.strftime('%Y-%m-%d %H:%M:%S')
            
            # 可視化
            if self.visualizer:
                self.visualizer.visualize(paths=self.calculated_paths, update_count=self.update_count)
            
            if forward_success and return_success:
                logger.info(f"✅ 双方向テーブル更新成功（往路: {len(forward_routes)}, 復路: {len(return_routes)}テーブル）")
                return True
            else:
                logger.error(f"❌ 更新失敗 - 往路: {forward_success}, 復路: {return_success}")
                return False
                
        except Exception as e:
            logger.error(f"双方向テーブル更新例外: {e}")
            return False
    
    def _create_table_routes(self, is_return: bool = False) -> List[TableRoute]:
        """テーブルルート生成"""
        if not self.calculated_paths:
            return []
        
        routes = []
        for i, (path, cost) in enumerate(self.calculated_paths):
            if i >= len(self.config.tables):
                break
            
            # 復路の場合はパスを逆順に
            actual_path = path[::-1] if is_return else path
            sid_list, interface_list, output_interface = self.network.path_to_sid_list(actual_path, is_return)
            
            table_name = self.config.tables[i]["name"]
            if is_return:
                table_name = table_name.replace("rt_table", "rt_table_")
            
            path_str = " → ".join([f"r{n}" for n in actual_path])
            routes.append(TableRoute(
                table_name=table_name,
                priority=self.config.tables[i]["priority"],
                path=actual_path,
                segments=sid_list,
                interfaces=interface_list,
                output_interface=output_interface,
                cost=cost,
                description=f"{path_str} (コスト: {cost:.6f})"
            ))
        
        return routes
    
    def _update_tables(self, routes: List[TableRoute], is_return: bool = False) -> bool:
        """テーブル更新実行"""
        host = self.config.r16_host if is_return else self.config.r1_host
        prefix = self.config.return_route_prefix if is_return else self.config.route_prefix
        
        try:
            with self.ssh.connect(host) as client:
                success_count = 0
                for route in routes:
                    # テーブルクリア
                    rc, out, _ = self.ssh.execute(client, f"ip -6 route show table {route.table_name}")
                    if rc == 0 and out.strip():
                        for line in out.strip().split('\n'):
                            parts = line.strip().split()
                            if parts and '::' in parts[0] and '/' in parts[0]:
                                self.ssh.execute(client, f"ip -6 route del {parts[0]} table {route.table_name}")
                    
                    # 新経路追加
                    if route.segments:
                        cmd = (f"ip -6 route add {prefix} encap seg6 mode encap "
                               f"segs {','.join(route.segments)} dev {route.output_interface} table {route.table_name}")
                        rc, _, err = self.ssh.execute(client, cmd)
                        if rc == 0:
                            success_count += 1
                        else:
                            logger.error(f"✗ {route.table_name} 更新失敗: {err}")
                    
                    # 現在の経路を記録
                    if not is_return:
                        self.current_table_routes[route.table_name] = route
                
                return success_count == len(routes)
        except Exception as e:
            logger.error(f"テーブル更新エラー: {e}")
            return False
    
    def _detect_path_changes(self, new_routes: List[TableRoute]) -> List[PathChangeEvent]:
        """経路変更検出"""
        changes = []
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        for new_route in new_routes:
            old_route = self.current_table_routes.get(new_route.table_name)
            
            if old_route is None:
                changes.append(PathChangeEvent(
                    timestamp=timestamp, table_name=new_route.table_name,
                    old_path=None, new_path=new_route.path,
                    old_segments=None, new_segments=new_route.segments,
                    old_interface=None, new_interface=new_route.output_interface,
                    reason="初回設定"
                ))
            elif old_route.path != new_route.path or old_route.output_interface != new_route.output_interface:
                reasons = []
                if old_route.path != new_route.path:
                    reasons.append("経路変更")
                if old_route.output_interface != new_route.output_interface:
                    reasons.append("出力IF変更")
                changes.append(PathChangeEvent(
                    timestamp=timestamp, table_name=new_route.table_name,
                    old_path=old_route.path, new_path=new_route.path,
                    old_segments=old_route.segments, new_segments=new_route.segments,
                    old_interface=old_route.output_interface, new_interface=new_route.output_interface,
                    reason="負荷変動による" + "・".join(reasons)
                ))
        
        return changes
    
    def _log_path_changes(self, changes: List[PathChangeEvent]):
        """経路変更ログ"""
        for change in changes:
            self.path_history.append(change)
            self.stats['path_changes'] += 1
            
            if change.old_path is None:
                logger.info(f"🆕 {change.table_name}: 初回設定 - {' → '.join([f'r{n}' for n in change.new_path])}")
            else:
                logger.info(f"🔄 {change.table_name}: {' → '.join([f'r{n}' for n in change.old_path])} → {' → '.join([f'r{n}' for n in change.new_path])}")
    
    def cleanup(self):
        """クリーンアップ"""
        if self.visualizer:
            self.visualizer.close()


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SRv6双方向リアルタイム多テーブル管理（最適化版）")
    parser.add_argument("--interval", type=int, default=60, help="更新間隔（秒）")
    parser.add_argument("--once", action="store_true", help="1回のみ実行")
    parser.add_argument("--visualize", action="store_true", help="トポロジ可視化を有効化")
    
    args = parser.parse_args()
    
    logger.info("SRv6双方向リアルタイム多テーブル管理開始（最適化版）")
    
    try:
        manager = SRv6PathManager(enable_visualization=args.visualize)
        
        if args.once:
            success = manager.update_bidirectional_tables()
            logger.info("✅ 完了" if success else "❌ 失敗")
            manager.cleanup()
        else:
            logger.info(f"リアルタイム監視開始（間隔: {args.interval}秒, 停止時間: {MEASUREMENT_DURATION_MINUTES}分）")
            measurement_start = time.time()
            
            try:
                while True:
                    elapsed_minutes = (time.time() - measurement_start) / 60
                    if elapsed_minutes >= MEASUREMENT_DURATION_MINUTES:
                        logger.info(f"⏱️ 測定時間 {MEASUREMENT_DURATION_MINUTES}分が経過。終了します。")
                        break
                    
                    start = time.time()
                    success = manager.update_bidirectional_tables()
                    logger.info("✅ 更新完了" if success else "❌ 更新失敗")
                    logger.info(f"⏱️ 経過: {elapsed_minutes:.1f}分 / 残り: {MEASUREMENT_DURATION_MINUTES - elapsed_minutes:.1f}分")
                    
                    sleep_time = max(0, args.interval - (time.time() - start))
                    logger.info(f"次回更新まで {sleep_time:.1f}秒")
                    logger.info("=" * 80)
                    time.sleep(sleep_time)
                
                logger.info("✅ 測定完了")
            except KeyboardInterrupt:
                logger.info("監視停止")
            finally:
                manager.cleanup()
                
    except Exception as e:
        logger.error(f"実行エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
