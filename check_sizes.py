from scapy.all import rdpcap

pkts = rdpcap('captures/dns_flood3.pcap')
sizes = [len(p) for p in pkts]
print('Total packets:', len(pkts))
print('Unique sizes:', sorted(set(sizes)))
print('Max size:', max(sizes))
