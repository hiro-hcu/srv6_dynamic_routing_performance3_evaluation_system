# SRv6 End Function Configuration

This document describes the SRv6 End function (Local SID) configuration for intermediate nodes in the network.

## Overview

In the SRv6 network topology, nodes r2, r3, r4, and r5 act as intermediate nodes and require End function configuration to process SRv6 segments properly.

## Local SID Configuration

### Router-specific Local SIDs

| Router | Local SIDs | Function Type | Description |
|--------|------------|---------------|-------------|
| r2 | `fd01:3::12`, `fd01:9::12` | End | Processes segments for r2→r4 and r2→r5 paths |
| r3 | `fd01:7::12` | End | Processes segments for r3→r5 path |
| r4 | `fd01:4::12` | End | Processes segments for r4→r6 path |
| r5 | `fd01:6::12` | End | Processes segments for r5→r6 path |
| r6 | `fd01:5::1` | End.DX6 | Egress node - decapsulates and forwards to server network |
| r1 | (none) | - | Ingress edge node - encapsulates packets |

### Configuration Commands

The End functions are automatically configured by the `srv6_setup.sh` script based on the hostname:

```bash
# r2 configuration
ip -6 route add fd01:3::12/128 encap seg6local action End dev lo
ip -6 route add fd01:9::12/128 encap seg6local action End dev lo

# r3 configuration  
ip -6 route add fd01:7::12/128 encap seg6local action End dev lo

# r4 configuration
ip -6 route add fd01:4::12/128 encap seg6local action End dev lo

# r5 configuration
ip -6 route add fd01:6::12/128 encap seg6local action End dev lo

# r6 configuration (egress node)
ip -6 route add fd01:5::1/128 encap seg6local action End.DX6 nh6 fd01:5::12 dev <server_interface>
```

## Testing and Verification

### Check Local SID Configuration

```bash
# Check seg6local routes
ip -6 route show | grep "seg6local"

# Check specific SID
ip -6 route get <SID_ADDRESS>

# Example for r2
ip -6 route get fd01:3::12
ip -6 route get fd01:9::12

# Example for r6 (egress)
ip -6 route get fd01:5::1
```

### Verify SRv6 Functionality

```bash
# From r1, test connectivity with SRv6 encapsulation
ping6 -c 3 fd01:5::12 -I eth0

# Test SRv6 path with segments (requires route configuration)
ip -6 route add fd01:5::/64 encap seg6 mode encap segs fd01:3::12,fd01:4::12 dev eth1
```

### Debug Commands

```bash
# Show all IPv6 routes
ip -6 route show

# Show SRv6-specific routes
ip -6 route show | grep seg6

# Check interface configuration
ip -6 addr show

# Monitor SRv6 traffic (if supported)
tcpdump -i any -n ip6 and 'ip6[6] = 43'
```

## Architecture

```
SRv6 Path Example: r1 → r2 → r4 → r6 → server

1. r1 encapsulates packet with segment list: [fd01:3::12, fd01:4::12, fd01:5::1]
2. r2 receives packet, matches fd01:3::12 → End function processes → forwards to r4
3. r4 receives packet, matches fd01:4::12 → End function processes → forwards to r6
4. r6 receives packet, matches fd01:5::1 → End.DX6 function decapsulates → forwards to server
5. Server receives original IPv6 packet
```

### SRv6 Function Types

- **End**: Standard segment processing for intermediate nodes
- **End.DX6**: Decapsulation and IPv6 forwarding for egress nodes
- **End.DT4/DT6**: Decapsulation with table lookup (not used in this setup)

## Troubleshooting

### Common Issues

1. **SID not configured**: Check if hostname matches expected values (r2, r3, r4, r5)
2. **Permission denied**: Ensure container runs with `privileged: true`
3. **Module not loaded**: Verify `seg6_local` kernel module is loaded
4. **Route conflicts**: Check for conflicting routes with `ip -6 route show`

### Log Analysis

```bash
# Check container logs
docker logs <container_name>

# Check system logs for SRv6-related messages
dmesg | grep -i seg6
```

## References

- [RFC 8754: IPv6 Segment Routing Header (SRH)](https://tools.ietf.org/html/rfc8754)
- [Linux SRv6 Implementation](https://www.kernel.org/doc/html/latest/networking/seg6-sysctl.html)
- [iproute2 seg6 commands](https://man7.org/linux/man-pages/man8/ip-route.8.html)