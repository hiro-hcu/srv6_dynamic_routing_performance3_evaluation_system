#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Phase 2: SRv6 nftables Setup - r16 Implementation (Return Path)
r16での復路IPv6 flow labelに基づいてmarkを付与するnftablesルールの設定
server (fd01:6::/64) から client への復路フロー制御
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

class SRv6NftablesSetupR16:
    """Phase 2: r16用nftables設定クラス（復路）"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # SSH接続設定（r16用）
        self.ssh_config = {
            'hostname': 'fd02:1::11',  # r16のIPv6アドレス
            'port': 22,
            'username': 'root',
            'password': '@k@n@3>ki',
            'timeout': 15
        }
        
        # nftables設定（復路用）
        self.nft_config = {
            'table_name': 'ip6 mangle_r16',
            'chain_name': 'prerouting_r16',
            'chain_config': 'type filter hook prerouting priority mangle;'
        }
        
        # flow label → mark マッピング（復路用、r16のphase1と対応）
        # デフォルトルートとして、4と6以外は全て低優先度（mark 9）に振り分け
        self.flow_label_rules = [
            {
                'flow_label': '0xfffc4',  # 往路と統一：高優先度フロー
                'mark_value': 4,          # r16復路用mark値
                'description': '復路高優先度フロー → mark 4 → rt_table_1',
                'priority': 1  # 高優先度ルール
            },
            {
                'flow_label': '0xfffc6',  # 往路と統一：中優先度フロー
                'mark_value': 6,          # r16復路用mark値
                'description': '復路中優先度フロー → mark 6 → rt_table_2',
                'priority': 2  # 中優先度ルール
            },
            {
                'flow_label': None,       # デフォルトルール（flow_label指定なし）
                'mark_value': 9,          # r16復路用mark値
                'description': '復路デフォルトフロー（4,6以外） → mark 9 → rt_table_3',
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
            self.logger.info("r16への SSH接続成功")
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
        """nftablesの状態確認（r16）"""
        self.logger.info("=== r16 nftables状態確認 ===")
        
        # nftコマンドの存在確認
        rc, out, err = self.execute_command(client, "which nft")
        if rc == 0:
            self.logger.info(f"nftツール確認: {out}")
        else:
            self.logger.error(f"nftツールが見つかりません: {err}")
            return False
        
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
        
        return True
    
    def create_nftables_table_and_chain(self, client: paramiko.SSHClient) -> bool:
        """Phase 2-1: r16用nftablesテーブルとチェーンの作成"""
        self.logger.info("=== Phase 2-1: r16復路nftablesテーブル・チェーン作成 ===")
        
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
        """Phase 2-2: r16復路Flow label → mark変換ルールの作成（デフォルトルート対応）"""
        self.logger.info("=== Phase 2-2: r16復路Flow label → mark変換ルール作成 ===")
        
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
        """Phase 2-3: r16復路nftables設定の検証（デフォルトルート対応）"""
        self.logger.info("=== Phase 2-3: r16復路nftables設定検証 ===")
        
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
    
    def cleanup_nftables(self, client: paramiko.SSHClient) -> bool:
        """r16復路nftables設定のクリーンアップ（テスト用）"""
        self.logger.info("=== r16復路nftables設定クリーンアップ ===")
        
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
    
    parser = argparse.ArgumentParser(description="Phase 2: r16復路SRv6 nftables設定")
    parser.add_argument("--setup", action="store_true", help="nftables設定の実行")
    parser.add_argument("--verify", action="store_true", help="設定の検証")
    parser.add_argument("--cleanup", action="store_true", help="設定のクリーンアップ")
    
    args = parser.parse_args()
    
    setup = SRv6NftablesSetupR16()
    
    try:
        with setup.ssh_connection() as client:
            if args.setup:
                logger.info("Phase 2: r16復路SRv6 nftables設定開始")
                
                # Step 1: テーブル・チェーン作成
                if setup.create_nftables_table_and_chain(client):
                    logger.info("✅ r16復路テーブル・チェーン作成完了")
                    
                    # Step 2: Flow labelルール作成
                    if setup.create_flow_label_rules(client):
                        logger.info("✅ r16復路Flow labelルール作成完了")
                        
                        # Step 3: 検証
                        if setup.verify_nftables_setup(client):
                            logger.info("🎯 Phase 2完了: r16復路nftables設定が正常です")
                        else:
                            logger.error("❌ r16復路設定検証に失敗")
                    else:
                        logger.error("❌ r16復路Flow labelルール作成に失敗")
                else:
                    logger.error("❌ r16復路テーブル・チェーン作成に失敗")
            
            elif args.verify:
                setup.verify_nftables_setup(client)
            
            elif args.cleanup:
                setup.cleanup_nftables(client)
            
            else:
                logger.info("使用法: --setup, --verify, --cleanup のいずれかを指定してください")
    
    except Exception as e:
        logger.error(f"実行エラー: {e}")

if __name__ == "__main__":
    main()
