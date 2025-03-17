#!/bin/bash

# Очистка существующих адресов
ip addr flush dev eth0

# Освобождаем предыдущий адрес (если есть)
dhclient -r -v eth0

# Запрашиваем новый адрес
dhclient -v eth0

# Выводим полученные настройки
ip addr show eth0
ip route show
cat /etc/resolv.conf

# Бесконечный цикл, чтобы контейнер не завершался
while true; do sleep 1; done