# Advanced SRv6 Routing Table Configuration

This document describes advanced routing table configuration for multi-table routing with QoS support.

## Custom Routing Tables Setup

Add custom routing tables to `/etc/iproute2/rt_tables`:

```
101 rt_table1
102 rt_table2
103 rt_table3
```

## Rule-based Routing with fwmark

Configure packet marking based routing:

```bash
# Basic fwmark-based routing
sudo ip -6 rule add fwmark 1 table rt_table1
sudo ip -6 rule add fwmark 2 table rt_table2
sudo ip -6 rule add fwmark 3 table rt_table3

# With priority preferences (table1: high, table2: medium, table3: low)
sudo ip -6 rule add pref 1000 fwmark 1 table rt_table1
sudo ip -6 rule add pref 1001 fwmark 2 table rt_table2
sudo ip -6 rule add pref 1002 fwmark 3 table rt_table3
```

## NFTables Configuration for Flow Label Based Marking

Set up packet marking based on IPv6 flow labels:

```bash
# Create mangle table
sudo nft add table ip6 mangle

# Add prerouting chain
sudo nft 'add chain ip6 mangle prerouting { type filter hook prerouting priority mangle; }'

# Add flow label based marking rules
sudo nft 'add rule ip6 mangle prerouting ip6 flowlabel 0xfffc1 mark set 1'
sudo nft 'add rule ip6 mangle prerouting ip6 flowlabel 0xfffc2 mark set 2'
sudo nft 'add rule ip6 mangle prerouting ip6 flowlabel 0xfffc3 mark set 3'
```

## Use Cases

This configuration enables:
- QoS-aware routing based on flow labels
- Traffic engineering with multiple routing tables
- Service differentiation through packet marking
- Advanced SRv6 path selection