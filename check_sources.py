from scapy.all import rdpcap, IP

pkts = rdpcap('captures/generic_flood.pcap')
src_ips = set()
for p in pkts:
    if IP in p:
        src_ips.add(p[IP].src)

print('Total packets:', len(pkts))
print('Distinct source IPs:', len(src_ips))
print('Sample of source IPs:', list(src_ips)[:10])