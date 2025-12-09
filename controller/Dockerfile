FROM python:3.9-slim

RUN apt update && apt install -y snmp gcc libsnmp-dev iputils-ping net-tools ssh openssh-client rrdtool cron vim mrtg librrd-dev librrds-perl && \
    pip install easysnmp paramiko networkx matplotlib

WORKDIR /opt/app

# startup.shスクリプトを作成
RUN echo '#!/bin/bash' > /startup.sh && \
    echo 'set -e' >> /startup.sh && \
    echo '# ログディレクトリの確実な作成とパーミッション設定' >> /startup.sh && \
    echo 'mkdir -p /opt/app/mrtg/mrtg_file' >> /startup.sh && \
    echo 'chmod 755 /opt/app/mrtg/mrtg_file' >> /startup.sh && \
    echo '# RRDファイルを作成' >> /startup.sh && \
    echo 'if [ -f /opt/app/mrtg/rrdtool_shell/create_rrd.sh ]; then' >> /startup.sh && \
    echo '  chmod +x /opt/app/mrtg/rrdtool_shell/create_rrd.sh' >> /startup.sh && \
    echo '  /opt/app/mrtg/rrdtool_shell/create_rrd.sh' >> /startup.sh && \
    echo 'fi' >> /startup.sh && \
    echo '# SRv6システム初期化を実行' >> /startup.sh && \
    echo 'echo "SRv6システム初期化開始..."' >> /startup.sh && \
    echo 'if [ -f /opt/app/init_setup.py ]; then' >> /startup.sh && \
    echo '  python3 /opt/app/init_setup.py &' >> /startup.sh && \
    echo '  echo "初期化スクリプトをバックグラウンドで開始しました"' >> /startup.sh && \
    echo 'else' >> /startup.sh && \
    echo '  echo "警告: 初期化スクリプトが見つかりません"' >> /startup.sh && \
    echo 'fi' >> /startup.sh && \
    echo '# crontabを設定' >> /startup.sh && \
    echo "echo '* * * * * env LANG=C /usr/bin/mrtg /opt/app/mrtg/mrtg_kurage.conf' | crontab -" >> /startup.sh && \
    echo '# cronをフォアグラウンドで開始' >> /startup.sh && \
    echo 'cron -f' >> /startup.sh && \
    chmod +x /startup.sh

ENTRYPOINT ["/startup.sh"]
