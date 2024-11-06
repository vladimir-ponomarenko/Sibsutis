#!/bin/bash

# Функции для форматирования вывода 
print_header() {
  echo -e "\033[1;34m$1\033[0m"
  echo "========================================"
}

print_item() {
  printf "  \033[1;32m•\033[0m %-25s %s\n" "$1:" "$2"
}

# Дата и информация о пользователе 
print_header "Дата и информация о пользователе"
print_item "Дата" "$(date)"
print_item "Имя учетной записи" "$(whoami)"
print_item "Доменное имя ПК" "$(hostname)"
echo

# Информация об ОС и ядре 
print_header "Информация об ОС и ядре"
os_name=$(cat /etc/*-release | grep "PRETTY_NAME" | cut -d '"' -f 2)
os_version=$(cat /etc/*-release | grep "VERSION_ID" | cut -d '"' -f 2)
kernel_version=$(uname -r)
kernel_architecture=$(uname -m)
print_item "Название ОС" "$os_name"
print_item "Версия ОС" "$os_version"
print_item "Версия ядра" "$kernel_version"
print_item "Архитектура ядра" "$kernel_architecture"
echo

# Информация о процессоре 
print_header "Информация о процессоре(ах)"

# Информация о сокетах из /proc/cpuinfo
sockets=$(cat /proc/cpuinfo | awk '/physical id/ {print $NF}' | sort -nu | wc -l)

for ((s = 0; s < sockets; s++)); do
  print_header "  Сокет $((s + 1))"

  cpu_info=$(cat /proc/cpuinfo | awk -v socket="$s" '$1 == "physical" && $4 == socket {p = 1} p' | awk  '
    BEGIN { core = 1 }
    /model name/ { model = $4 " " $5 " " $6 " " $7 " " $8 " " $9 }
    /cpu MHz/ { freqs[core++] = $4 } 
    /cache size/ { caches[$2] = $4 } 
    END {
      printf "  • Модель процессора: %s\n", model
      for (i = 1; i <= length(freqs); i++) { 
        printf "  • Тактовая частота ядра %d: %.3f MHz\n", i, freqs[i]
      }
      for (level in caches) {
        printf "  • Кэш %s: %s\n", level, caches[level]
      }
    }
  ')

  echo "$cpu_info"
done


# Информация об оперативной памяти
print_header "Информация об оперативной памяти"
RAM_all=$(LC_ALL=C free -h | grep "Mem" | tr -s ' ' '\t' | awk '{print $2}')
RAM_used=$(LC_ALL=C free -h | grep "Mem" | tr -s ' ' '\t' | awk '{print $3}')
RAM_available=$(LC_ALL=C free -h | grep "Mem" | tr -s ' ' '\t' | awk '{print $7}')
print_item "Всего" "$RAM_all"
print_item "Использовано" "$RAM_used"
print_item "Доступно" "$RAM_available"
echo

# Информация о сетевых интерфейсах 
print_header "Информация о сетевых интерфейсах"
for iface in $(ip -o link show | awk -F': ' '{print $2}'); do
  print_item "Интерфейс" "$iface"
  mac=$(ip link show "$iface" | awk '/link\/ether/ {print $2}')
  print_item "MAC адрес" "$mac"

  i=1
  for ip in $(ip addr show "$iface" | awk '/inet / {print $2}'); do
    print_item "IP адрес $i" "$ip"
    i=$((i+1))
  done

  rx_bytes_start=$(cat /sys/class/net/"$iface"/statistics/rx_bytes)
  tx_bytes_start=$(cat /sys/class/net/"$iface"/statistics/tx_bytes)
  sleep 1
  rx_bytes_end=$(cat /sys/class/net/"$iface"/statistics/rx_bytes)
  tx_bytes_end=$(cat /sys/class/net/"$iface"/statistics/tx_bytes)
  rx_speed=$(( ($rx_bytes_end - $rx_bytes_start) * 8 / 1000 ))
  tx_speed=$(( ($tx_bytes_end - $tx_bytes_start) * 8 / 1000 ))
  print_item "rx" "$rx_bytes_start Кбит"
  print_item "tx" "$tx_bytes_start Кбит"
  print_item "Скорость приема" "$rx_speed Кбит/с"
  print_item "Скорость передачи" "$tx_speed Кбит/с"
  echo
done

# Информация о системных разделах 
print_header "Информация о системных разделах"
df -h -T | tail -n +2 | while read line; do
  filesystem=$(echo "$line" | awk '{print $1}')
  type=$(echo "$line" | awk '{print $2}')
  size=$(echo "$line" | awk '{print $3}')
  used=$(echo "$line" | awk '{print $4}')
  available=$(echo "$line" | awk '{print $5}')
  use_percentage=$(echo "$line" | awk '{print $6}')
  mountpoint=$(echo "$line" | awk '{print $7}')
  print_item "Файловая система" "$filesystem"
  print_item "Тип" "$type"
  print_item "Размер" "$size"
  print_item "Использовано" "$used"
  print_item "Доступно" "$available"
  print_item "Использование" "$use_percentage"
  print_item "Точка монтирования" "$mountpoint"
  echo
done