# Flow Incremental Load Test (filt)

**DIRE WARNING**:
------------
THIS IS A NETWORK STRESS TOOL - DO NOT USE THIS
PROGRAM UNLESS YOU KNOW WHAT YOU ARE DOING AND
ARE AUTHORISED TO DO IT. THE LOAD GENERATED MAY
CAUSE NETWORK PERFORMANCE ISSUES!!!!!!!

This code is used to stress test a network by
incrementally increasing a new flows/second load.

Do not use this code on production networks - it
is proof of concept code and carries no warrantee
whatsoever. You have been warned.

May need to install scapy if not already installed

Uses raw socket to improve packet sending performance

Will only send traffic if has entry in ARP table for
destination. You may want to consider adding a static
ARP if the destination does not exist, example:

```
arp -i eth1 -s 10.1.3.254 00:01:02:03:04:05
```
