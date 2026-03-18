#!/usr/bin/env python3
from scapy.all import *
from datetime import datetime
import csv

detected_macs = set()
probe_requests = []

def packet_handler(pkt):
    if pkt.haslayer(Dot11ProbeReq):
        mac = pkt.addr2
        timestamp = datetime.now()
        
        # Get SSID if present
        ssid = pkt.info.decode('utf-8', errors='ignore') if pkt.info else '<Broadcast>'
        
        # Get signal strength if available
        try:
            rssi = pkt.dBm_AntSignal
        except:
            rssi = None
        
        # Log the probe request
        probe_data = {
            'timestamp': timestamp,
            'mac': mac,
            'ssid': ssid,
            'rssi': rssi
        }
        probe_requests.append(probe_data)
        
        # Track unique devices
        if mac not in detected_macs:
            detected_macs.add(mac)
            print(f"[{timestamp.strftime('%H:%M:%S')}] NEW DEVICE: {mac}")
            print(f"  Looking for: {ssid}")
            print(f"  Total unique devices: {len(detected_macs)}\n")
        
        # Save to CSV every 20 packets
        if len(probe_requests) % 20 == 0:
            save_to_csv()

def save_to_csv():
    with open('probe_requests.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'mac', 'ssid', 'rssi'])
        writer.writeheader()
        writer.writerows(probe_requests)

print("Starting WiFi Probe Request Sniffer...")
print("Monitoring for devices searching for WiFi networks...")
print("Press Ctrl+C to stop\n")

try:
    sniff(iface="wlan0mon", prn=packet_handler, store=0)
except KeyboardInterrupt:
    print("\n\nStopping sniffer...")
    save_to_csv()
    print(f"\nFinal Statistics:")
    print(f"  Total unique devices detected: {len(detected_macs)}")
    print(f"  Total probe requests captured: {len(probe_requests)}")
    print(f"  Data saved to: probe_requests.csv")
