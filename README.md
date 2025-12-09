# SRv6 Dynamic Routing Performance Evaluation System

A comprehensive Docker-based SRv6 (Segment Routing over IPv6) dynamic routing system designed for **performance evaluation research**. Features a 16-router mesh topology with real-time traffic monitoring, multi-table routing, and automatic path orchestration capabilities.

## 🌟 Key Features

- **🚀 Dynamic Path Orchestration**: Real-time optimal path calculation based on network conditions
- **🔄 Bidirectional Control**: Independent forward (r1→r16) and return (r16→r1) path management with synchronized flow label handling
- **📊 Multi-Table Routing**: QoS-aware routing with 3 priority tiers (high/medium/low) using fwmark-based classification
- **⚡ Real-time Monitoring**: MRTG-based traffic analysis with 60-second RRD data polling across 27 monitored links
- **🧠 Intelligent Switching**: Automatic path switching based on link utilization thresholds
- **🔧 Auto-Configuration**: Automated Phase 1 & 2 setup on container startup (nftables + routing tables + fwmark rules)
- **📈 Performance Analytics**: RRD-based edge weight calculation and NetworkX shortest path optimization
- **🐳 Full Containerization**: Complete Docker-based deployment with 16 routers + controller
- **🌐 External Node Support**: Macvlan-based connection for real-world UPF/Server integration
- **⚡ 1Gbps Bandwidth Control**: HTB-based traffic shaping with optimized burst settings on all router interfaces
- **✅ Verified Flow Label Mapping**: 0xfffc4 → mark 4, 0xfffc6 → mark 6, default → mark 9 across r1/r16

## 📅 Last Updated
- **2025-12-01**: Added 1Gbps bandwidth limiting with HTB (burst 15k optimization for high throughput)
- **2025-11-04**: Fixed flow label → mark mapping verification

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                 SRv6 Dynamic Routing Performance Evaluation System               │
│                                                                                  │
│  16-Router Mesh Topology (4x4 Grid)                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                             │ │
│  │   UPF ─── r1 ─── r2 ─── r4 ─── r7 ───┐                                     │ │
│  │  (ext)     │      │      │      │     │                                     │ │
│  │            │      │      │      │     │                                     │ │
│  │            r3 ─── r5 ─── r8 ─── r11 ──┼─── r14 ──┐                          │ │
│  │            │      │      │      │     │          │                          │ │
│  │            │      │      │      │     │          │                          │ │
│  │            r6 ─── r9 ─── r12 ───┼─────┘          r16 ─── Server             │ │
│  │            │      │      │      │                │       (ext)              │ │
│  │            │      │      │      │                │                          │ │
│  │            r10 ── r13 ── r15 ───┴──────────────────┘                         │ │
│  │                                                                             │ │
│  │  All Links: 1Gbps bandwidth limit (HTB, burst 15k)                          │ │
│  │  Monitoring: 27 links with RRD data collection (60s intervals)              │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │                    Controller System (fd02:1::20)                          │  │
│  │  ┌──────────────────┐  ┌──────────────────────────────────────────────┐   │  │
│  │  │ Auto Init        │  │    Real-time Components                       │   │  │
│  │  │ (on startup)     │  │  ┌────────────┐  ┌──────────────────────────┐│   │  │
│  │  │ ┌──────────────┐ │  │  │ MRTG       │  │ Phase3 RT Manager        ││   │  │
│  │  │ │ Phase1       │ │  │  │ Poller     │  │ - Bidirectional Control  ││   │  │
│  │  │ │ - r1 tables  │ │  │  │ (60s)      │  │ - Multi-table Management ││   │  │
│  │  │ │ - r16 tables │◄┼──┼──┤ 27 Links   │◄─┤ - Dynamic Path Switching ││   │  │
│  │  │ │ - fwmark→tbl │ │  │  │ RRD Data   │  │ - SRv6 Route Updates     ││   │  │
│  │  │ └──────────────┘ │  │  └────────────┘  └──────────────────────────┘│   │  │
│  │  │ ┌──────────────┐ │  │                                               │   │  │
│  │  │ │ Phase2       │ │  │   Flow Label → Mark Mapping:                  │   │  │
│  │  │ │ - r1 nftables│ │  │   0xfffc4 → mark 4 → rt_table1 (High)        │   │  │
│  │  │ │ - r16 nftables│ │ │   0xfffc6 → mark 6 → rt_table2 (Medium)      │   │  │
│  │  │ │ - flowlabel  │ │  │   default → mark 9 → rt_table3 (Low)         │   │  │
│  │  │ │   →mark(4/6/9)│ │  │                                               │   │  │
│  │  │ └──────────────┘ │  └──────────────────────────────────────────────┘   │  │
│  │  └──────────────────┘                                                      │  │
│  └────────────────────────────────────────────────────────────────────────────┘  │
│           │ SSH Auto-Config              │ RT Updates                            │
│           ▼                              ▼                                       │
│  ┌─────────────────┐           ┌─────────────────┐                               │
│  │ r1 (Ingress)    │           │ r16 (Egress)    │                               │
│  │ fd02:1::2       │           │ fd02:1::11      │                               │
│  │ ┌─────────────┐ │           │ ┌─────────────┐ │                               │
│  │  │ nftables    │ │           │ │ nftables    │ │                               │
│  │  │ flowlabel→  │ │           │ │ flowlabel→  │ │                               │
│  │  │ mark 4/6/9  │ │           │ │ mark 4/6/9  │ │                               │
│  │  └─────────────┘ │           │ └─────────────┘ │                               │
│  │ ┌─────────────┐ │           │ ┌─────────────┐ │                               │
│  │ │ rt_table1/2/3│ │          │ │ rt_table_1/2/3│ │                              │
│  │ │ (Priority)  │ │           │ │ (Priority)  │ │                               │
│  │ │ fwmark 4/6/9│ │           │ │ fwmark 4/6/9│ │                               │
│  │ │ → SRv6 routes│ │          │ │ → SRv6 routes│ │                               │
│  │ └─────────────┘ │           │ └─────────────┘ │                               │
│  └─────────────────┘           └─────────────────┘                               │
└──────────────────────────────────────────────────────────────────────────────────┘

Bandwidth Control:
├── All router interfaces: 1Gbps HTB limit (burst 15k, cburst 15k)
├── Optimized for high-throughput testing
└── Automatic configuration on container startup
```

## 📁 Project Structure

```
srv6_dynamic_routing_performance_evaluation_system/
├── 📋 README.md                           # Project documentation
├── 🐳 docker-compose.yml                  # 16-router topology configuration
├── 📖 EXTERNAL_CONNECTION.md              # External UPF/Server connection guide
│
├── 🌐 router/                             # SRv6 router infrastructure
│   ├── Dockerfile                        # Base router image (r2-r15)
│   ├── Dockerfile_r1                     # R1 (ingress) with SSH + nftables
│   ├── Dockerfile_r16                    # R16 (egress) with SSH + nftables
│   ├── scripts/                          # Router initialization
│   │   ├── srv6_setup.sh                 # SRv6 kernel configuration
│   │   ├── set_bandwidth_limit.sh        # 1Gbps HTB bandwidth control
│   │   ├── r1_startup.sh                 # R1 specialized startup
│   │   └── r16_startup.sh                # R16 specialized startup
│   ├── docs/                             # Technical documentation
│   │   ├── advanced-routing-setup.md     # nftables + fwmark guide
│   │   └── srv6-end-functions.md         # SRv6 function reference
│   └── snmpd/
│       └── snmpd.conf                    # SNMP monitoring config
│
└── 🎛️ controller/                         # Control plane system
    ├── Dockerfile                        # Auto-initializing controller
    ├── init_setup.py                     # Automated Phase1&2 setup
    │
    ├── 📊 mrtg/                          # Traffic monitoring
    │   ├── mrtg_kurage.conf              # Link-specific MRTG config
    │   ├── mrtg_kurage.ok                # Status indicator
    │   ├── mrtg_file/                    # RRD data storage (27 link files)
    │   │   ├── r1-r2.rrd, r1-r3.rrd      # Edge router links
    │   │   ├── r2-r4.rrd ... r15-r16.rrd # Mesh network links
    │   │   └── (27 total RRD files)
    │   └── rrdtool_shell/
    │       └── create_rrd.sh             # RRD database initialization
    │
    ├── 📊 presentation/                   # Research presentation materials
    │   ├── README.md                     # Presentation guide
    │   ├── diagrams/                     # System architecture diagrams
    │   ├── docs/                         # Documentation exports
    │   └── scripts/                      # Diagram generation scripts
    │
    └── 🎯 srv6-path-orchestrator/         # Core orchestration system
        ├── function_analysis.md          # System function analysis
        ├── VISUALIZATION_README.md       # Visualization guide
        │
        ├── 🔧 Phase 1&2 Setup Scripts (Auto-executed):
        ├── r1_phase1_table_setup.py      # R1 routing tables + rules
        ├── r1_phase2_nftables_setup.py   # R1 nftables + flow marking
        ├── r16_phase1_table_setup.py     # R16 routing tables + rules  
        ├── r16_phase2_nftables_setup.py  # R16 nftables + flow marking
        │
        └── 🚀 Phase 3 Main System:
            └── phase3_realtime_multi_table.py # Main orchestrator
                                               # - Bidirectional control
                                               # - Real-time monitoring  
                                               # - Dynamic path switching
                                               # - Multi-table management
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose v2.0+
- Linux environment with IPv6 support (tested on Ubuntu 22.04+)
- Root privileges for container networking
- Physical NIC for external connections (optional, for UPF/Server integration)


### 1. Clone and Deploy
```bash
git clone https://github.com/hiro-hcu/srv6_dynamic_routing_performance_evaluation_system.git
cd srv6_dynamic_routing_performance_evaluation_system

# Deploy all containers with automatic initialization
sudo docker compose up -d

# For fresh rebuild (recommended after updates)
sudo docker compose down && sudo docker compose build --no-cache && sudo docker compose up -d
```

### 2. Verify System Status
```bash
# Check all 17 containers are running (16 routers + 1 controller)
sudo docker ps

# Monitor initialization progress
sudo docker logs -f controller

# Expected output:
# INFO - SRv6システム初期化開始...
# INFO - ✅ SSH準備完了 (r1: fd02:1::2, r16: fd02:1::11)
# INFO - ✅ r1_phase1_table_setup.py 実行成功
# INFO - ✅ r1_phase2_nftables_setup.py 実行成功
# INFO - ✅ r16_phase1_table_setup.py 実行成功
# INFO - ✅ r16_phase2_nftables_setup.py 実行成功
# INFO - 🎉 初期化完了: システムは運用可能です
```

### 3. Verify Bandwidth Control
```bash
# Check HTB settings on any router (should show burst 15k)
sudo docker exec r1 tc class show dev eth0

# Expected output:
# class htb 1:10 root prio 0 rate 1Gbit ceil 1Gbit burst 15125b cburst 15125b
```

### 4. Verification Commands
```bash
# Verify nftables configuration (r1)
sudo docker exec -it r1 nft list table ip6 mangle
# Expected: flowlabel 0xfffc4 → mark 4, 0xfffc6 → mark 6

# Verify routing rules (r16)
sudo docker exec -it r16 ip -6 rule list
# Expected: fwmark 0x4/0x6/0x9 lookup rt_table_1/2/3

# Check routing tables
sudo docker exec -it r1 ip -6 route show table rt_table1
sudo docker exec -it r16 ip -6 route show table rt_table_1
```

### 5. Start Real-time Orchestration (Phase 3)
```bash
# Run bidirectional real-time management (continuous mode)
sudo docker exec -it controller python3 /opt/app/srv6-path-orchestrator/phase3_realtime_multi_table.py

# Alternative: One-time execution for testing
sudo docker exec -it controller python3 /opt/app/srv6-path-orchestrator/phase3_realtime_multi_table.py --once

# Expected output:
# INFO - 🚀 双方向テーブル更新開始
# INFO - Edge r1 <-> r2: 9.633 bps
# INFO - 往路最適経路: r1 → r2 → r4 → r7 → r11 → r14 → r16
# INFO - 復路最適経路: r16 → r14 → r11 → r7 → r4 → r2 → r1
# INFO - ✅ 双方向テーブル更新成功
```

## 🌐 External PC Connection (Advanced)

For real-world testing with physical UPF/Server nodes:

### System Modes
- **Container Mode**: Self-contained testing environment (default)
- **External Node Mode**: Macvlan-based connection to real hardware

### External PC Setup
```bash
# External networks are pre-configured in docker-compose.yml:
# - external-upf: fd00:1::/64 (via enp2s0f1 macvlan)
# - external-server: fd03:1::/64 (via enp2s0f0 macvlan)

# UPF PC configuration:
sudo ip -6 addr add fd00:1::1/64 dev <interface>
sudo ip -6 route add fd03:1::/64 via fd00:1::12  # via r1

# Server PC configuration:
sudo ip -6 addr add fd03:1::2/64 dev <interface>
sudo ip -6 route add fd00:1::/64 via fd03:1::11  # via r16
```

📖 **Detailed Guide**: See [EXTERNAL_CONNECTION.md](EXTERNAL_CONNECTION.md) for complete setup instructions.

---

## ⚡ Performance Optimization

### Bandwidth Control (HTB)
All router interfaces are automatically configured with 1Gbps bandwidth limits:

```bash
# Applied settings (set_bandwidth_limit.sh):
tc qdisc add dev $iface root handle 1: htb default 10
tc class add dev $iface parent 1: classid 1:10 htb rate 1000mbit ceil 1000mbit burst 15k cburst 15k
```

### Host-Level Optimizations (Recommended)
For maximum throughput testing, apply these host optimizations:

```bash
# Expand NIC ring buffers (if supported)
sudo ethtool -G enp2s0f0 rx 8192 tx 8192
sudo ethtool -G enp2s0f1 rx 8192 tx 8192

# Increase kernel socket buffers
sudo sysctl -w net.core.rmem_max=16777216
sudo sysctl -w net.core.wmem_max=16777216
sudo sysctl -w net.core.netdev_max_backlog=30000

# Verify settings
tc class show dev eth0  # Should show burst 15125b
```

## 🎯 System Phases Overview

### Phase 1: Infrastructure Setup (Auto-executed)
- **Routing Tables**: Creates `rt_table1`, `rt_table2`, `rt_table3` for QoS tiers
- **Rule Configuration**: Sets up `fwmark`-based routing rules
- **Targets**: Both r1 (ingress) and r16 (egress) routers

### Phase 2: Traffic Classification (Auto-executed)  
- **nftables Setup**: IPv6 flow label → firewall mark conversion
- **Flow Mapping**: 
  - `0xfffc4` (1048516) → mark **4** → High Priority (rt_table1)
  - `0xfffc6` (1048518) → mark **6** → Medium Priority (rt_table2) 
  - デフォルト（上記以外） → mark **9** → Low Priority (rt_table3)
- **Bidirectional**: Independent forward (r1) and return (r16) classification
- **Automatic**: Executes during container startup via `init_setup.py`

### Phase 3: Real-time Orchestration (Manual/Automated)
- **Traffic Monitoring**: RRD-based link utilization analysis (60-second intervals, 27 monitored links)
- **Dynamic Paths**: Automatic optimal path calculation using NetworkX shortest path
- **Bidirectional Control**: Simultaneous r1→r16 (forward) and r16→r1 (return) path management
- **SRv6 Encapsulation**: Dynamic SID list generation based on calculated paths
- **Route Updates**: SSH-based automated route installation to r1 and r16
- **Multi-Table**: 3-priority system with independent path optimization per table

## 📊 Technical Implementation

### nftables + fwmark Integration
```bash
# Phase 2: Flow Label Detection (nftables)
# Creates mangle table and sets marks based on IPv6 flow labels
nft 'add table ip6 mangle'
nft 'add chain ip6 mangle prerouting { type filter hook prerouting priority mangle; }'
nft 'add rule ip6 mangle prerouting ip6 flowlabel 0xfffc4 mark set 0x4'  # 高優先度
nft 'add rule ip6 mangle prerouting ip6 flowlabel 0xfffc6 mark set 0x6'  # 中優先度
nft 'add rule ip6 mangle prerouting mark set 0x9'                        # デフォルト（低優先度）

# Phase 1: Routing Rule Application (fwmark-based table selection)
ip -6 rule add pref 1000 fwmark 0x4 table rt_table1  # High priority
ip -6 rule add pref 1001 fwmark 0x6 table rt_table2  # Medium priority
ip -6 rule add pref 1002 fwmark 0x9 table rt_table3  # Low priority (default)

# Phase 3: SRv6 Route Installation (dynamic, per-table)
# Example: Forward path r1→r2→r4→r6 in rt_table1
ip -6 route add fd03:1::/64 encap seg6 mode encap \
    segs fd01:2::12,fd01:3::12,fd01:4::12 dev eth1 table rt_table1

# Example: Return path r6→r4→r2→r1 in rt_table_1
ip -6 route add fd00:1::/64 encap seg6 mode encap \
    segs fd01:4::11,fd01:3::11,fd01:2::11 dev eth2 table rt_table_1
```

### Flow Label → Mark → Table Flow
```
User Packet with flowlabel 0xfffc4 (high priority)
    ↓
[nftables mangle prerouting]
    ↓ (flowlabel 0xfffc4 detected)
Packet marked with fwmark=4
    ↓
[ip -6 rule lookup]
    ↓ (fwmark 4 matches)
Routing table rt_table1 selected
    ↓
[SRv6 encapsulation route in rt_table1]
    ↓
Packet encapsulated with SID list for optimal path
    ↓
Forwarded to next hop
```

### Real-time Monitoring Pipeline
- **MRTG**: 60-second SNMP polling → RRD storage (27 links)
- **Phase3 Manager**: RRD fetch → Traffic analysis → Graph edge weight update
- **Path Calculator**: NetworkX Dijkstra shortest path → Multiple path options
- **Route Installer**: SSH automation (paramiko) → Live route updates to r1/r16
- **Bidirectional**: Independent optimization for forward and return paths

## 🔗 Network Topology & Addressing

### 16-Router Mesh Topology
```
Layer 1 (Edge):     r1 ─────────────────────────────────────── r16
                    │                                           │
Layer 2:            r2 ─── r3                             r14 ── r15
                    │       │                              │      │
Layer 3:            r4 ─── r5 ─── r6                 r11 ── r12 ── r13
                    │       │      │                  │      │      │
Layer 4:            r7 ─── r8 ─── r9 ─── r10 ────────┴──────┴──────┘

Monitored Links (27 total with RRD data):
├── r1-r2, r1-r3 (edge ingress)
├── r2-r4, r2-r5, r3-r5, r3-r6, r4-r7, r4-r8, r5-r8, r5-r9
├── r6-r9, r6-r10, r7-r11, r8-r11, r8-r12, r9-r12, r9-r13
├── r10-r13, r11-r14, r12-r14, r12-r15, r13-r15
└── r14-r16, r15-r16 (edge egress)
```

### IP Addressing Scheme
```
Management Network (SSH & Control):
├── Controller: fd02:1::20
├── r1:  fd02:1::2  (SSH enabled, ingress)
├── r2:  fd02:1::3  
├── r3:  fd02:1::4
├── r4:  fd02:1::5
├── r5:  fd02:1::6
├── r6:  fd02:1::7
├── r7:  fd02:1::8
├── r8:  fd02:1::9
├── r9:  fd02:1::a
├── r10: fd02:1::b
├── r11: fd02:1::c
├── r12: fd02:1::d
├── r13: fd02:1::e
├── r14: fd02:1::f
├── r15: fd02:1::10
└── r16: fd02:1::11 (SSH enabled, egress)

External Networks:
├── UPF-R1:    fd00:1::/64 (macvlan, UPF: fd00:1::1, R1: fd00:1::12)
└── R16-Server: fd03:1::/64 (macvlan, R16: fd03:1::11, Server: fd03:1::2)
```

### Path Examples
**High Priority Path (rt_table1)**: 
- Forward: UPF → r1 → r2 → r4 → r7 → r11 → r14 → r16 → Server
- SID List example: `[fd01:1::12, fd01:2::12, fd01:3::12, ...]`

**Alternative Paths**:
- Via r3: r1 → r3 → r5 → r8 → r12 → r15 → r16
- Via r6: r1 → r3 → r6 → r9 → r13 → r15 → r16

## 🛠️ Advanced Usage

### Manual Phase Execution
```bash
# Run individual setup phases
sudo docker exec -it controller python3 /opt/app/srv6-path-orchestrator/r1_phase1_table_setup.py
sudo docker exec -it controller python3 /opt/app/srv6-path-orchestrator/r1_phase2_nftables_setup.py
sudo docker exec -it controller python3 /opt/app/srv6-path-orchestrator/r16_phase1_table_setup.py
sudo docker exec -it controller python3 /opt/app/srv6-path-orchestrator/r16_phase2_nftables_setup.py
```

### Real-time Orchestration Modes
```bash
# Bidirectional monitoring (recommended)
python3 /opt/app/srv6-path-orchestrator/phase3_realtime_multi_table.py --mode bidirectional

# Forward path only
python3 /opt/app/srv6-path-orchestrator/phase3_realtime_multi_table.py --mode forward

# Traffic analysis only
python3 /opt/app/srv6-path-orchestrator/phase3_realtime_multi_table.py --mode analyze --once

# Custom update interval  
python3 /opt/app/srv6-path-orchestrator/phase3_realtime_multi_table.py --interval 30
```

### Testing & Debugging
```bash
# Verify nftables rules
sudo docker exec -it r1 nft list table ip6 mangle
sudo docker exec -it r16 nft list table ip6 mangle_r16

# Check routing tables
sudo docker exec -it r1 ip -6 route show table rt_table1
sudo docker exec -it r16 ip -6 route show table rt_table_1

# Check bandwidth control settings
sudo docker exec -it r1 tc qdisc show
sudo docker exec -it r1 tc class show dev eth0

# Monitor RRD data
sudo docker exec -it controller rrdtool fetch /opt/app/mrtg/mrtg_file/r1-r2.rrd AVERAGE --start -60s

# List all monitored links
sudo docker exec -it controller ls /opt/app/mrtg/mrtg_file/*.rrd
```

### Performance Testing
```bash
# iperf3 throughput test (requires iperf3 installation)
# On server side:
iperf3 -s -6

# On client side:
iperf3 -c fd03:1::2 -6 -t 30 -P 4

# Monitor tc statistics during test
watch -n 1 'sudo docker exec r1 tc -s class show dev eth0'
```

## 📊 System Monitoring & Analytics

### Real-time Metrics Collection
- **Link Utilization**: Per-link traffic analysis via SNMP/RRD (27 monitored links)
- **Path Performance**: Latency and throughput per routing table
- **Route Changes**: Automatic logging of path switching events
- **Load Distribution**: Traffic distribution across multiple tables
- **Bandwidth Usage**: HTB class statistics for each interface

### Observable Behaviors
```bash
# Expected system responses to traffic:
1. High traffic on r1→r2 → System switches to alternative path (r1→r3→...)
2. Link congestion detected → Alternative paths activated across mesh
3. Path oscillation → System stabilizes on optimal route
4. Bidirectional independence → Forward/return paths optimized separately
5. Multi-hop optimization → 16-router mesh allows many alternative paths
```

## 🔬 Research Applications

### Academic Use Cases
- **SRv6 Performance Evaluation**: Throughput, latency, and path convergence under various conditions
- **Traffic Engineering**: Multi-path routing optimization algorithms with 16-router mesh
- **SDN Integration**: Centralized control plane with distributed data plane
- **Network Simulation**: Realistic testbed for routing protocol research
- **QoS Research**: Multi-table routing with flow label-based classification

### Key Research Features
- **Reproducible Results**: Containerized environment ensures consistency
- **Comprehensive Logging**: Detailed path change and performance logs
- **Flexible Configuration**: Easy modification of routing policies
- **Standards Compliance**: Pure IPv6 + SRv6 implementation
- **Scalable Design**: 16-router mesh with 27 monitored links
- **Performance Testing**: 1Gbps bandwidth control with optimized settings

## 🚨 Troubleshooting

### Common Issues

#### 1. Container Startup Issues
```bash
# Check all containers are running
sudo docker ps -a

# View container logs
sudo docker logs r1
sudo docker logs controller

# Restart specific container
sudo docker restart r1
```

#### 2. Auto-Initialization Failures
```bash
# Check auto-initialization logs
sudo docker logs controller

# Manual retry if auto-init failed
sudo docker exec -it controller python3 /opt/app/init_setup.py
```

#### 3. SSH Connection Failures  
```bash
# Check SSH service on routers
sudo docker exec -it r1 service ssh status
sudo docker exec -it r16 service ssh status

# Restart SSH if needed
sudo docker exec -it r1 service ssh restart
sudo docker exec -it r16 service ssh restart
```

#### 4. nftables Rule Conflicts
```bash
# View current rules
sudo docker exec -it r1 nft list ruleset | grep -A 20 mangle

# Flush and recreate
sudo docker exec -it r1 nft flush table ip6 mangle
sudo docker exec -it controller python3 /opt/app/srv6-path-orchestrator/r1_phase2_nftables_setup.py
```

#### 5. Bandwidth Control Issues
```bash
# Check tc settings
sudo docker exec -it r1 tc qdisc show
sudo docker exec -it r1 tc class show dev eth0

# Verify burst settings (should show ~15k)
sudo docker exec -it r1 tc class show dev eth0 | grep burst

# Check for overlimits (indicates bandwidth saturation)
sudo docker exec -it r1 tc -s class show dev eth0
```

#### 6. RRD Data Collection Issues
```bash
# Check RRD file existence (should be 27 files)
sudo docker exec -it controller ls -la /opt/app/mrtg/mrtg_file/*.rrd | wc -l

# Test RRD data fetch
sudo docker exec -it controller rrdtool fetch /opt/app/mrtg/mrtg_file/r1-r2.rrd AVERAGE --start -60s
```

### System Reset
```bash
# Complete environment reset
sudo docker compose down
sudo docker system prune -f
sudo docker volume prune -f
sudo docker compose build --no-cache
sudo docker compose up -d

# Wait for auto-initialization (30-60 seconds)
sudo docker logs -f controller
```

### Diagnostic Commands Cheat Sheet
```bash
# Quick health check
sudo docker exec -it r1 nft list table ip6 mangle | grep flowlabel
sudo docker exec -it r16 nft list table ip6 mangle_r16 | grep flowlabel
sudo docker exec -it r1 ip -6 rule list | grep fwmark
sudo docker exec -it r16 ip -6 rule list | grep fwmark

# Check bandwidth control
sudo docker exec -it r1 tc class show dev eth0 | grep rate

# Verify Phase 1 & 2 completion
sudo docker logs controller | grep "✅"

# Test end-to-end (from external UPF/Server)
ping6 -c 3 fd03:1::2   # UPF → Server
ping6 -c 3 fd00:1::1   # Server → UPF
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branches for new routing algorithms
3. Test in containerized environment
4. Document performance improvements
5. Submit pull requests with test results

## 📄 License & Citation

This project is developed for academic research on SRv6 dynamic routing systems.

```bibtex
@misc{srv6_performance_evaluation_2025,
  title={SRv6 Dynamic Routing Performance Evaluation System},
  author={[Author]},
  year={2025},
  howpublished={\\url{https://github.com/hiro-hcu/srv6_dynamic_routing_performance_evaluation_system}},
  note={Docker-based 16-router SRv6 testbed with 1Gbps bandwidth control and multi-table routing}
}
```

## 🔍 Technical References

### Standards & Protocols
- [RFC 8754: IPv6 Segment Routing Header (SRH)](https://tools.ietf.org/html/rfc8754)
- [RFC 8986: Segment Routing over IPv6 (SRv6) Network Programming](https://tools.ietf.org/html/rfc8986)
- [Linux SRv6 Implementation Guide](https://www.kernel.org/doc/html/latest/networking/seg6-sysctl.html)

### Implementation Tools  
- [iproute2: Linux Advanced Routing](https://wiki.linuxfoundation.org/networking/iproute2)
- [nftables: Linux Firewall Framework](https://netfilter.org/projects/nftables/)
- [tc-htb: Hierarchical Token Bucket](https://man7.org/linux/man-pages/man8/tc-htb.8.html)
- [MRTG: Network Traffic Monitoring](https://oss.oetiker.ch/mrtg/)
- [NetworkX: Network Analysis in Python](https://networkx.org/)

---

**System Status**: ✅ Production Ready | 🔄 Real-time Monitoring Active | 🚀 Auto-Initialization Enabled | ⚡ 1Gbps Bandwidth Control | 🌐 16-Router Mesh Topology
# srv6_dynamic_routing_performance3_evaluation_system
