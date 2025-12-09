#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Phase 1: SRv6 Table Setup - Basic Implementation
r1でのルーティングテーブル作成とルール設定
"""

import paramiko
import logging
from typing import Tuple
from contextlib import contextmanager

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SRv6TableSetup:
    """Phase 1: 基本的なテーブル設定クラス"""
    
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
        
        # テーブル設定（phase3と整合性を保つ）
        self.tables = [
            {'id': 100, 'name': 'rt_table1'},
            {'id': 101, 'name': 'rt_table2'},
            {'id': 102, 'name': 'rt_table3'}
        ]
        
        # ルール設定（memo.txtの内容を基に）
        self.rules = [
            {'mark': 4, 'table': 'rt_table1', 'priority': 50},
            {'mark': 6, 'table': 'rt_table2', 'priority': 60},
            {'mark': 9, 'table': 'rt_table3', 'priority': 90}
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
    
    def setup_routing_tables(self, client: paramiko.SSHClient) -> bool:
        """Phase 1-1: ルーティングテーブルの作成"""
        self.logger.info("=== Phase 1-1: ルーティングテーブル作成 ===")
        
        # 現在の/etc/iproute2/rt_tablesの内容を確認
        rc, out, err = self.execute_command(client, "cat /etc/iproute2/rt_tables")
        if rc == 0:
            self.logger.info("現在のrt_tablesの内容:")
            for line in out.split('\n'):
                if line.strip():
                    self.logger.info(f"  {line}")
        
        # 各テーブルを追加
        success_count = 0
        for table in self.tables:
            # テーブルが既に存在するかチェック
            if table['name'] in out:
                self.logger.info(f"テーブル {table['name']} は既に存在します")
                success_count += 1
                continue
            
            # テーブル追加
            cmd = f"echo '{table['id']} {table['name']}' >> /etc/iproute2/rt_tables"
            rc, out_add, err_add = self.execute_command(client, cmd)
            
            if rc == 0:
                self.logger.info(f"✓ テーブル追加成功: {table['id']} {table['name']}")
                success_count += 1
            else:
                self.logger.error(f"✗ テーブル追加失敗: {table['name']} - {err_add}")
        
        # 追加後の確認
        rc, out, err = self.execute_command(client, "cat /etc/iproute2/rt_tables")
        if rc == 0:
            self.logger.info("更新後のrt_tablesの内容:")
            for line in out.split('\n'):
                if any(table['name'] in line for table in self.tables):
                    self.logger.info(f"  {line}")
        
        return success_count == len(self.tables)
    
    def setup_routing_rules(self, client: paramiko.SSHClient) -> bool:
        """Phase 1-2: ルーティングルールの設定"""
        self.logger.info("=== Phase 1-2: ルーティングルール設定 ===")
        
        # 現在のルールを確認
        rc, out, err = self.execute_command(client, "ip -6 rule show")
        if rc == 0:
            self.logger.info("現在のIPv6ルール:")
            for line in out.split('\n'):
                if line.strip():
                    self.logger.info(f"  {line}")
        
        # 各ルールを追加
        success_count = 0
        for rule in self.rules:
            # ルールが既に存在するかチェック
            rule_exists = False
            if f"fwmark 0x{rule['mark']}" in out and rule['table'] in out:
                self.logger.info(f"ルール mark={rule['mark']} table={rule['table']} は既に存在します")
                success_count += 1
                continue
            
            # ルール追加
            cmd = (f"ip -6 rule add pref {rule['priority']} "
                  f"fwmark {rule['mark']} table {rule['table']}")
            rc, out_add, err_add = self.execute_command(client, cmd)
            
            if rc == 0:
                self.logger.info(f"✓ ルール追加成功: mark={rule['mark']} -> table={rule['table']} (pref={rule['priority']})")
                success_count += 1
            elif "File exists" in err_add or "exists" in err_add.lower():
                self.logger.info(f"✓ ルール既存: mark={rule['mark']} -> table={rule['table']}")
                success_count += 1
            else:
                self.logger.error(f"✗ ルール追加失敗: {rule} - {err_add}")
        
        # 追加後のルール確認
        rc, out, err = self.execute_command(client, "ip -6 rule show")
        if rc == 0:
            self.logger.info("更新後のIPv6ルール（関連部分）:")
            for line in out.split('\n'):
                if any(rule['table'] in line for rule in self.rules):
                    self.logger.info(f"  {line}")
        
        return success_count == len(self.rules)
    
    def verify_table_setup(self, client: paramiko.SSHClient) -> bool:
        """Phase 1-3: テーブル設定の検証"""
        self.logger.info("=== Phase 1-3: テーブル設定検証 ===")
        
        # テーブル存在確認
        rc, out, err = self.execute_command(client, "cat /etc/iproute2/rt_tables")
        table_check = True
        for table in self.tables:
            if f"{table['id']} {table['name']}" in out:
                self.logger.info(f"✓ テーブル確認: {table['name']}")
            else:
                self.logger.error(f"✗ テーブル未確認: {table['name']}")
                table_check = False
        
        # ルール存在確認
        rc, out, err = self.execute_command(client, "ip -6 rule show")
        rule_check = True
        for rule in self.rules:
            if f"fwmark 0x{rule['mark']}" in out and rule['table'] in out:
                self.logger.info(f"✓ ルール確認: mark={rule['mark']} -> {rule['table']}")
            else:
                self.logger.error(f"✗ ルール未確認: mark={rule['mark']} -> {rule['table']}")
                rule_check = False
        
        return table_check and rule_check
    
    def cleanup_tables(self, client: paramiko.SSHClient) -> bool:
        """テーブル設定のクリーンアップ（テスト用）"""
        self.logger.info("=== テーブル設定クリーンアップ ===")
        
        # ルール削除
        for rule in self.rules:
            cmd = f"ip -6 rule del fwmark {rule['mark']} table {rule['table']}"
            rc, out, err = self.execute_command(client, cmd)
            if rc == 0:
                self.logger.info(f"✓ ルール削除: mark={rule['mark']}")
            elif "No such file" in err or "not found" in err.lower():
                self.logger.info(f"ルールは存在しませんでした: mark={rule['mark']}")
            else:
                self.logger.warning(f"ルール削除失敗: {err}")
        
        return True

def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Phase 1: SRv6テーブル設定")
    parser.add_argument("--setup", action="store_true", help="テーブル設定の実行")
    parser.add_argument("--verify", action="store_true", help="設定の検証")
    parser.add_argument("--cleanup", action="store_true", help="設定のクリーンアップ")
    
    args = parser.parse_args()
    
    setup = SRv6TableSetup()
    
    try:
        with setup.ssh_connection() as client:
            if args.setup:
                logger.info("Phase 1: SRv6テーブル設定開始")
                
                # Step 1: テーブル作成
                if setup.setup_routing_tables(client):
                    logger.info("✅ テーブル作成完了")
                    
                    # Step 2: ルール設定
                    if setup.setup_routing_rules(client):
                        logger.info("✅ ルール設定完了")
                        
                        # Step 3: 検証
                        if setup.verify_table_setup(client):
                            logger.info("🎯 Phase 1完了: 全ての設定が正常です")
                        else:
                            logger.error("❌ 設定検証に失敗")
                    else:
                        logger.error("❌ ルール設定に失敗")
                else:
                    logger.error("❌ テーブル作成に失敗")
            
            elif args.verify:
                setup.verify_table_setup(client)
            
            elif args.cleanup:
                setup.cleanup_tables(client)
            
            else:
                logger.info("使用法: --setup, --verify, --cleanup のいずれかを指定してください")
    
    except Exception as e:
        logger.error(f"実行エラー: {e}")

if __name__ == "__main__":
    main()
