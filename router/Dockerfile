FROM ubuntu:22.04

RUN apt update && apt install -y \
    iproute2 iputils-ping curl net-tools tcpdump \
    kmod \
    snmpd snmp \
    snmp-mibs-downloader 

RUN download-mibs

# SRv6はカーネルレベル（iproute2）で処理
# SRv6設定は起動時のsrv6_setup.shで動的に実行 

# 行頭が mibs : で始まる行を # mibs : に変える
RUN sed -i 's/^mibs\s*:/# &/' /etc/snmp/snmp.conf

# SNMPポートを開ける（Dockerホストと通信する場合）
EXPOSE 161/udp

COPY snmpd/snmpd.conf /etc/snmp/snmpd.conf
COPY scripts/srv6_setup.sh /usr/local/bin/srv6_setup.sh
COPY scripts/set_bandwidth_limit.sh /usr/local/bin/set_bandwidth_limit.sh
RUN chmod +x /usr/local/bin/srv6_setup.sh /usr/local/bin/set_bandwidth_limit.sh

# コンテナ起動時にSRv6設定、帯域制限、SNMPdを起動
CMD /usr/local/bin/srv6_setup.sh && /usr/local/bin/set_bandwidth_limit.sh && service snmpd start && tail -f /dev/null



