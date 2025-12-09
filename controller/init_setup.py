#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SRv6システム初期化スクリプト
controllerコンテナ起動時にphase1, phase2のセットアップを自動実行
"""

import os
import sys
import time
import logging
import subprocess
from pathlib import Path

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SRv6SystemInitializer:
    """SRv6システム初期化クラス"""
    
    def __init__(self):
        self.base_path = Path("/opt/app/srv6-path-orchestrator")
        self.setup_scripts = [
            "r1_phase1_table_setup.py",
            "r1_phase2_nftables_setup.py", 
            "r16_phase1_table_setup.py",
            "r16_phase2_nftables_setup.py"
        ]
        
        # SSH接続テスト用の設定
        self.ssh_targets = [
            {'name': 'r1', 'host': 'fd02:1::2'},
            {'name': 'r16', 'host': 'fd02:1::11'}
        ]
    
    def wait_for_network_ready(self, max_wait=300):
        """ネットワークとSSHサービスの準備完了を待機"""
        import paramiko
        
        logger.info("ネットワークとSSHサービスの準備完了を待機中...")
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            all_ready = True
            
            for target in self.ssh_targets:
                try:
                    # Paramikoで直接SSH接続テスト（タイムアウト5秒）
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    client.connect(
                        hostname=target['host'],
                        port=22,
                        username='root',
                        password='@k@n@3>ki',
                        timeout=5
                    )
                    client.close()
                    logger.info(f"✅ {target['name']} ({target['host']}) - SSH準備完了")
                        
                except Exception as e:
                    logger.debug(f"⏳ {target['name']} ({target['host']}) - SSH接続待機中: {e}")
                    all_ready = False
            
            if all_ready:
                logger.info("🎉 全てのターゲットのSSH準備完了！")
                return True
                
            time.sleep(10)  # 10秒待機してリトライ
            
        logger.error(f"❌ {max_wait}秒以内にSSH準備が完了しませんでした")
        return False
    
    def run_setup_script(self, script_name):
        """セットアップスクリプトを実行"""
        script_path = self.base_path / script_name
        
        if not script_path.exists():
            logger.error(f"❌ スクリプトが見つかりません: {script_path}")
            return False
            
        logger.info(f"🚀 実行開始: {script_name}")
        
        try:
            # Pythonスクリプトとして実行（--setupオプション付き）
            result = subprocess.run([
                sys.executable, str(script_path), '--setup'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info(f"✅ 実行成功: {script_name}")
                
                # 成功時のログも表示
                if result.stdout.strip():
                    logger.info(f"📄 {script_name} 出力:")
                    for line in result.stdout.strip().split('\n'):
                        logger.info(f"  {line}")
                        
                return True
            else:
                logger.error(f"❌ 実行失敗: {script_name} (RC: {result.returncode})")
                
                if result.stderr.strip():
                    logger.error(f"エラー詳細:")
                    for line in result.stderr.strip().split('\n'):
                        logger.error(f"  {line}")
                        
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ 実行タイムアウト: {script_name}")
            return False
        except Exception as e:
            logger.error(f"❌ 実行エラー: {script_name} - {e}")
            return False
    
    def run_all_setups(self):
        """全セットアップスクリプトを順次実行"""
        logger.info("🎯 SRv6システム初期化開始")
        
        # ネットワーク準備完了を待機
        if not self.wait_for_network_ready():
            logger.error("❌ ネットワーク準備タイムアウト - 初期化を中止")
            return False
        
        # SSH安定化のため追加で20秒待機（確実な接続のため）
        logger.info("SSH安定化のため追加で20秒待機...")
        time.sleep(20)

        success_count = 0
        
        for script in self.setup_scripts:
            if self.run_setup_script(script):
                success_count += 1
                time.sleep(5)  # 各スクリプト間で5秒待機
            else:
                logger.error(f"❌ {script} の実行に失敗しました")
                # 失敗しても続行（部分的なセットアップでも有用）
        
        logger.info(f"📊 セットアップ完了: {success_count}/{len(self.setup_scripts)} 成功")
        
        if success_count == len(self.setup_scripts):
            logger.info("🎉 全セットアップが正常完了しました！")
            return True
        elif success_count > 0:
            logger.warning("⚠️ 一部のセットアップが完了しました")
            return True
        else:
            logger.error("❌ すべてのセットアップが失敗しました")
            return False

def main():
    """メイン関数"""
    initializer = SRv6SystemInitializer()
    
    try:
        success = initializer.run_all_setups()
        if success:
            logger.info("✅ 初期化プロセス完了")
            sys.exit(0)
        else:
            logger.error("❌ 初期化プロセス失敗")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 初期化プロセスが中断されました")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 予期しないエラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()