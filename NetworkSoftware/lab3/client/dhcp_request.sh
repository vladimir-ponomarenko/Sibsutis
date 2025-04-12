#!/bin/bash

echo "Starting tshark capture..."
tshark -i eth0 -w /capture.pcap -f "udp port 67 or udp port 68" &
TSHARK_PID=$!
sleep 2

echo "Running dhclient -r..."
dhclient -r -v eth0

echo "Running dhclient..."
dhclient -v eth0

echo "Waiting for DHCP process to complete..."
sleep 5 

echo "Stopping tshark..."
kill $TSHARK_PID
wait $TSHARK_PID 2>/dev/null

echo "Displaying network info..."
ip addr show eth0
ip route show
cat /etc/resolv.conf

echo "Client script finished. capture.pcap created."
# while true; do sleep 1000; done