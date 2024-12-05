#!/bin/bash

# 1
interface=$(ip route get 1 | awk '{print $5; exit}')
if [ -z "$interface" ]; then
  interface=$(ip -o link show up | awk '$2 != "lo:" {print $2; exit}')
  interface=${interface%:}
fi
if [ -z "$interface" ]; then
  interface=$(ifconfig -s | awk 'NR>1 {print $1; exit}')
fi

if [ -z "$interface" ]; then
  echo "Ошибка: Не удалось определить сетевой интерфейс."
  exit 1
fi

output_file="interface_info.txt"
echo "=== Информация о сетевом интерфейсе $interface ===" > $output_file

mac_address=$(ip link show $interface | grep -oE 'link/ether [0-9a-f:]{17}' | awk '{print $2}')
echo "MAC-адрес: $mac_address" >> $output_file

ifconfig $interface | grep -E 'RX packets|TX packets' >> $output_file

ip link show $interface | grep -E 'mtu|qdisc' >> $output_file

cat $output_file
echo "Вся информация о сетевом интерфейсе сохранена в $output_file"


# 2
echo "Сканирование локальной сети..."
arp-scan -l | grep -oE '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' > local_ips.txt
echo "Список IP-адресов сохранен в local_ips.txt"


# 3
echo "Информация о шлюзе:"

gateway_ip=$(ip route get 1 | awk '{print $3}')
gateway_interface=$(ip route get 1 | awk '{print $5}')

gateway_name=$(getent hosts $gateway_ip | awk '{print $2}')

# router_name=$(sudo nmap -sn $gateway_ip | awk '/Nmap scan report for/{print $5}')  

gateway_mac=$(ip neigh show | grep $gateway_ip | awk '{print $5}')
router_name=$(ip neigh show | grep $gateway_mac | awk '{print $3}')

echo "IP шлюза: $gateway_ip (интерфейс: $gateway_interface)"
echo "Имя шлюза (DNS): $gateway_name"
echo "Имя роутера (ARP/nmap): $router_name"

echo "Информация сохранена в gateway_info.txt" > gateway_info.txt
echo "IP шлюза: $gateway_ip (интерфейс: $gateway_interface)" >> gateway_info.txt
echo "Имя шлюза (DNS): $gateway_name" >> gateway_info.txt
echo "Имя роутера (ARP/nmap): $router_name" >> gateway_info.txt


# 4 и 5
mail_server="linux.org"
echo "Трассировка маршрута до $mail_server:"

traceroute $mail_server > traceroute_info.txt
cat traceroute_info.txt

echo "Информация о маршруте сохранена в traceroute_info.txt"

echo "Проверка доступности узлов:"
grep -oE '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' traceroute_info.txt | while read ip; do
  ping -c 1 -W 1 $ip > /dev/null 2>&1
  if [ $? -eq 0 ]; then
    echo "$ip доступен"
  else
    echo "$ip недоступен"
  fi
done


exit 0