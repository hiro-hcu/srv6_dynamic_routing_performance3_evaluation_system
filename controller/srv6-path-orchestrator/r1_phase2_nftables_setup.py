#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Phase 2: SRv6 nftables Setup - Flow Label to Mark Conversion
IPv6 flow labelに基づいてmarkを付与するnftablesルールの設定
"""

import paramiko
import logging
from typing import Tuple, List, Dict
from contextlib import contextmanager

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SRv6NftablesSetup:
    """Phase 2: nftables設定クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # SSH接続設定
        self.ssh_config = {
            'hostname': 'fd02:1::2',  # r1のIPv6アドレス
            'port': 22,
            'username': 'root',
            'password': '@k@n@3>ki',
            'timeout': 15
        }
        
        # nftables設定（memo.txtの内容を基に）
        self.nft_config = {
            'table_name': 'ip6 mangle',
            'chain_name': 'prerouting',
            'chain_config': 'type filter hook prerouting priority mangle;'
        }
        
        # flow label → mark マッピング（デフォルトルート対応）
        # デフォルトルートとして、4と6以外は全て低優先度（mark 9）に振り分け
        self.flow_label_rules = [
            {
                'flow_label': '0xfffc4',
                'mark_value': 4,
                'description': '高優先度フロー → mark 4 → rt_table1',
                'priority': 1  # 高優先度ルール
            },
            {
                'flow_label': '0xfffc6', 
                'mark_value': 6,
                'description': '中優先度フロー → mark 6 → rt_table2',
                'priority': 2  # 中優先度ルール
            },
            {
                'flow_label': None,
                'mark_value': 9,
                'description': 'デフォルトフロー（4,6以外） → mark 9 → rt_table3',
                'priority': 3  # 低優先度ルール（デフォルト）
            }
        ]
    
    @contextmanager
    def ssh_connection(self):
        """SSH接続のコンテキストマネージャー"""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            self.logger.info(f"SSH接続開始: {self.ssh_config['hostname']}:{self.ssh_config['port']}")
            client.connect(**self.ssh_config)
            self.logger.info("r1への SSH接続成功")
            yield client
            
        except Exception as e:
            self.logger.error(f"SSH接続エラー: {e}")
            raise
        finally:
            client.close()
            self.logger.info("SSH接続を終了しました")
    
    def execute_command(self, client: paramiko.SSHClient, command: str) -> Tuple[int, str, str]:
        """SSHコマンド実行"""
        try:
            self.logger.debug(f"実行コマンド: {command}")
            stdin, stdout, stderr = client.exec_command(command)
            
            rc = stdout.channel.recv_exit_status()
            out = stdout.read().decode('utf-8').strip()
            err = stderr.read().decode('utf-8').strip()
            
            self.logger.debug(f"実行結果 RC={rc}")
            if out:
                self.logger.debug(f"STDOUT: {out}")
            if err and rc != 0:
                self.logger.debug(f"STDERR: {err}")
                
            return rc, out, err
            
        except Exception as e:
            self.logger.error(f"コマンド実行エラー: {e}")
            return 1, "", str(e)
    
    def check_nftables_status(self, client: paramiko.SSHClient) -> bool:
        """nftablesの状態確認"""
        self.logger.info("=== nftables状態確認 ===")
        
        # nftコマンドの存在確認
        rc, out, err = self.execute_command(client, "which nft")
        if rc == 0:
            self.logger.info(f"nftツール確認: {out}")
        else:
            self.logger.error(f"nftツールが見つかりません: {err}")
            return False
        
        # nftablesバージョン確認
        rc, out, err = self.execute_command(client, "nft --version")
        if rc == 0:
            self.logger.info(f"nftablesバージョン: {out}")
        else:
            self.logger.warning(f"バージョン確認失敗: {err}")
        
        # カーネルのnftablesサポート確認
        rc, out, err = self.execute_command(client, "lsmod | grep nf_tables")
        if rc == 0:
            self.logger.info("nf_tablesカーネルモジュール:")
            for line in out.split('\n'):
                if line.strip():
                    self.logger.info(f"  {line}")
        else:
            self.logger.info("nf_tablesカーネルモジュール: 未ロードまたは組み込み")
        
        # 現在のnftablesテーブル確認
        rc, out, err = self.execute_command(client, "nft list tables")
        if rc == 0:
            self.logger.info("現在のnftablesテーブル:")
            if out.strip():
                for line in out.split('\n'):
                    if line.strip():
                        self.logger.info(f"  {line}")
            else:
                self.logger.info("  テーブルなし")
        else:
            self.logger.error(f"テーブル一覧取得失敗: {err}")
            return False
        
        # 基本的なnftables機能テスト
        rc, out, err = self.execute_command(client, "nft list ruleset")
        if rc == 0:
            self.logger.info("nftables基本機能: 正常")
            if out.strip():
                self.logger.info("現在のルールセット概要:")
                lines = out.split('\n')[:10]  # 最初の10行のみ表示
                for line in lines:
                    if line.strip():
                        self.logger.info(f"  {line}")
                if len(out.split('\n')) > 10:
                    self.logger.info("  ... (続きは省略)")
            else:
                self.logger.info("  ルールセット: 空")
        else:
            self.logger.error(f"nftables基本機能テスト失敗: {err}")
            return False
        
        return True
    
    def create_nftables_table_and_chain(self, client: paramiko.SSHClient) -> bool:
        """Phase 2-1: nftablesテーブルとチェーンの作成"""
        self.logger.info("=== Phase 2-1: nftablesテーブル・チェーン作成 ===")
        
        # テーブル作成
        cmd_table = f"nft add table {self.nft_config['table_name']}"
        rc, out, err = self.execute_command(client, cmd_table)
        
        if rc == 0:
            self.logger.info(f"✓ テーブル作成成功: {self.nft_config['table_name']}")
        elif "already exists" in err.lower() or "exist" in err.lower():
            self.logger.info(f"テーブル既存: {self.nft_config['table_name']}")
        else:
            self.logger.error(f"✗ テーブル作成失敗: {err}")
            return False
        
        # チェーン作成  
        cmd_chain = (f"nft 'add chain {self.nft_config['table_name']} "
                    f"{self.nft_config['chain_name']} "
                    f"{{ {self.nft_config['chain_config']} }}'")
        rc, out, err = self.execute_command(client, cmd_chain)
        
        if rc == 0:
            self.logger.info(f"✓ チェーン作成成功: {self.nft_config['chain_name']}")
        elif "already exists" in err.lower() or "exist" in err.lower():
            self.logger.info(f"チェーン既存: {self.nft_config['chain_name']}")
        else:
            self.logger.error(f"✗ チェーン作成失敗: {err}")
            return False
        
        return True
    
    def create_flow_label_rules(self, client: paramiko.SSHClient) -> bool:
        """Phase 2-2: Flow label → mark変換ルールの作成（デフォルトルート対応）"""
        self.logger.info("=== Phase 2-2: Flow label → mark変換ルール作成 ===")
        
        success_count = 0
        for rule in self.flow_label_rules:
            # ルール作成コマンド
            if rule['flow_label'] is not None:
                # 特定のflow_labelに対するルール（高優先度・中優先度）
                cmd_rule = (f"nft 'add rule {self.nft_config['table_name']} "
                           f"{self.nft_config['chain_name']} "
                           f"ip6 flowlabel {rule['flow_label']} "
                           f"mark set {rule['mark_value']}'")
            else:
                # デフォルトルール（flow_label指定なし、低優先度）
                # 既にmarkが設定されていない場合のみmark 9を付与
                cmd_rule = (f"nft 'add rule {self.nft_config['table_name']} "
                           f"{self.nft_config['chain_name']} "
                           f"mark 0 "
                           f"mark set {rule['mark_value']}'")
            
            rc, out, err = self.execute_command(client, cmd_rule)
            
            if rc == 0:
                self.logger.info(f"✓ ルール作成成功: {rule['description']}")
                if rule['flow_label'] is not None:
                    self.logger.info(f"  flow_label {rule['flow_label']} → mark {rule['mark_value']}")
                else:
                    self.logger.info(f"  デフォルト（flow_label 4,6以外） → mark {rule['mark_value']}")
                success_count += 1
            elif "already exists" in err.lower() or "exist" in err.lower():
                self.logger.info(f"ルール既存: {rule['description']}")
                success_count += 1
            else:
                self.logger.error(f"✗ ルール作成失敗: {rule['description']} - {err}")
        
        return success_count == len(self.flow_label_rules)
    
    def verify_nftables_setup(self, client: paramiko.SSHClient) -> bool:
        """Phase 2-3: nftables設定の検証（デフォルトルート対応）"""
        self.logger.info("=== Phase 2-3: nftables設定検証 ===")
        
        # テーブル存在確認
        rc, out, err = self.execute_command(client, "nft list tables")
        if self.nft_config['table_name'] in out:
            self.logger.info(f"✓ テーブル確認: {self.nft_config['table_name']}")
        else:
            self.logger.error(f"✗ テーブル未確認: {self.nft_config['table_name']}")
            return False
        
        # チェーンとルール確認
        cmd_show = f"nft list table {self.nft_config['table_name']}"
        rc, out, err = self.execute_command(client, cmd_show)
        
        if rc == 0:
            self.logger.info(f"テーブル {self.nft_config['table_name']} の内容:")
            for line in out.split('\n'):
                if line.strip():
                    self.logger.info(f"  {line}")
            
            # 各ルールの存在確認
            rule_check = True
            for rule in self.flow_label_rules:
                mark_hex = f"0x{rule['mark_value']:08x}"
                
                if rule['flow_label'] is not None:
                    # 特定flow_labelルールの確認（16進数を10進数に変換して確認）
                    flow_label_dec = str(int(rule['flow_label'], 16))
                    if f"flowlabel {flow_label_dec}" in out and f"mark set {mark_hex}" in out:
                        self.logger.info(f"✓ ルール確認: flow_label {rule['flow_label']} (10進: {flow_label_dec}) → mark {rule['mark_value']}")
                    else:
                        self.logger.error(f"✗ ルール未確認: flow_label {rule['flow_label']} (10進: {flow_label_dec}) → mark {rule['mark_value']}")
                        rule_check = False
                else:
                    # デフォルトルールの確認（mark 0の条件付き）
                    if f"mark 0x00000000" in out and f"mark set {mark_hex}" in out:
                        self.logger.info(f"✓ デフォルトルール確認: flow_label 4,6以外 → mark {rule['mark_value']}")
                    else:
                        self.logger.error(f"✗ デフォルトルール未確認: mark {rule['mark_value']}")
                        rule_check = False
            
            return rule_check
        else:
            self.logger.error(f"テーブル内容確認失敗: {err}")
            return False
    
    def test_flow_label_detection(self, client: paramiko.SSHClient) -> bool:
        """Phase 2-4: Flow label検出テスト（オプション）"""
        self.logger.info("=== Phase 2-4: Flow label検出テスト ===")
        
        # nftablesカウンターを使用したテスト準備
        self.logger.info("テスト用カウンターを追加...")
        
        for rule in self.flow_label_rules:
            # カウンター付きテストルール追加
            cmd_test = (f"nft 'add rule {self.nft_config['table_name']} "
                       f"{self.nft_config['chain_name']} "
                       f"ip6 flowlabel {rule['flow_label']} "
                       f"counter comment \"test-{rule['flow_label']}\"'")
            
            rc, out, err = self.execute_command(client, cmd_test)
            if rc == 0:
                self.logger.info(f"✓ テストカウンター追加: {rule['flow_label']}")
            elif "already exists" in err.lower():
                self.logger.info(f"テストカウンター既存: {rule['flow_label']}")
        
        # カウンター状態確認
        rc, out, err = self.execute_command(client, f"nft list table {self.nft_config['table_name']}")
        if rc == 0:
            self.logger.info("テストカウンター付きルール:")
            for line in out.split('\n'):
                if 'counter' in line and 'test-' in line:
                    self.logger.info(f"  {line.strip()}")
        
        return True
    
    def cleanup_nftables(self, client: paramiko.SSHClient) -> bool:
        """nftables設定のクリーンアップ（テスト用）"""
        self.logger.info("=== nftables設定クリーンアップ ===")
        
        # テーブル削除（チェーンとルールも一緒に削除される）
        cmd_delete = f"nft delete table {self.nft_config['table_name']}"
        rc, out, err = self.execute_command(client, cmd_delete)
        
        if rc == 0:
            self.logger.info(f"✓ テーブル削除成功: {self.nft_config['table_name']}")
        elif "No such file" in err or "not found" in err.lower():
            self.logger.info(f"テーブルは存在しませんでした: {self.nft_config['table_name']}")
        else:
            self.logger.warning(f"テーブル削除失敗: {err}")
        
        return True

def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Phase 2: SRv6 nftables設定")
    parser.add_argument("--setup", action="store_true", help="nftables設定の実行")
    parser.add_argument("--verify", action="store_true", help="設定の検証")
    parser.add_argument("--test", action="store_true", help="Flow label検出テスト")
    parser.add_argument("--status", action="store_true", help="nftables状態確認")
    parser.add_argument("--cleanup", action="store_true", help="設定のクリーンアップ")
    
    args = parser.parse_args()
    
    setup = SRv6NftablesSetup()
    
    try:
        with setup.ssh_connection() as client:
            if args.setup:
                logger.info("Phase 2: SRv6 nftables設定開始")
                
                # Step 1: テーブル・チェーン作成
                if setup.create_nftables_table_and_chain(client):
                    logger.info("✅ テーブル・チェーン作成完了")
                    
                    # Step 2: Flow labelルール作成
                    if setup.create_flow_label_rules(client):
                        logger.info("✅ Flow labelルール作成完了")
                        
                        # Step 3: 検証
                        if setup.verify_nftables_setup(client):
                            logger.info("🎯 Phase 2完了: nftables設定が正常です")
                            
                            # Step 4: テスト（オプション）
                            setup.test_flow_label_detection(client)
                        else:
                            logger.error("❌ 設定検証に失敗")
                    else:
                        logger.error("❌ Flow labelルール作成に失敗")
                else:
                    logger.error("❌ テーブル・チェーン作成に失敗")
            
            elif args.verify:
                setup.verify_nftables_setup(client)
            
            elif args.test:
                setup.test_flow_label_detection(client)
            
            elif args.status:
                setup.check_nftables_status(client)
            
            elif args.cleanup:
                setup.cleanup_nftables(client)
            
            else:
                logger.info("使用法: --setup, --verify, --test, --status, --cleanup のいずれかを指定してください")
    
    except Exception as e:
        logger.error(f"実行エラー: {e}")

if __name__ == "__main__":
    main()
