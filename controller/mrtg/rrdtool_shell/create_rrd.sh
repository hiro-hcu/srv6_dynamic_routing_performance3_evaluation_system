#!/bin/bash

# エラー時に即時終了
set -e

# 1Gbpsインターフェース向けのRRDファイルを作成
# DS:ds0:COUNTER:120:0:125000000 → 125,000,000 bytes/s = 1,000,000,000 bits/s = 1Gbps

# r1-r2.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r1-r2.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

# r1-r3.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r1-r3.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

# r2-r4.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r2-r4.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

# r2-r5.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r2-r5.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

# r3-r5.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r3-r5.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

# r3-r6.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r3-r6.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

# r4-r7.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r4-r7.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

# r4-r8.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r4-r8.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

# r5-r8.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r5-r8.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

# r5-r9.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r5-r9.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

# r6-r9.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r6-r9.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

# r6-r10.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r6-r10.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

# r7-r11.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r7-r11.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

# r8-r11.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r8-r11.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

# r8-r12.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r8-r12.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

# r9-r12.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r9-r12.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

# r9-r13.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r9-r13.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

# r10-r13.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r10-r13.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

# r11-r14.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r11-r14.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

# r12-r14.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r12-r14.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

# r12-r15.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r12-r15.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

# r13-r15.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r13-r15.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

# r14-r16.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r14-r16.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

# r15-r16.rrd を作成
rrdtool create /opt/app/mrtg/mrtg_file/r15-r16.rrd \
    --step 60 \
    DS:ds0:COUNTER:120:0:125000000 \
    DS:ds1:COUNTER:120:0:125000000 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:MAX:0.5:1:1440

echo "RRD files created successfully."