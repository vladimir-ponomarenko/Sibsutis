#!/usr/bin/python
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def create_topology():
    net = Mininet(controller=Controller, switch=OVSKernelSwitch)

    info('*** Добавление контроллера\n')
    c0 = net.addController('c0')

    info('*** Добавление коммутаторов\n')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')

    info('*** Добавление хостов\n')
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')
    h4 = net.addHost('h4', ip='10.0.0.4/24')

    info('*** Создание соединений\n')
    net.addLink(s1, s2)
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s2)
    net.addLink(h4, s2)

    info('*** Запуск сети\n')
    net.build()
    c0.start()
    s1.start([c0])
    s2.start([c0])

    info('*** Запуск CLI\n')
    CLI(net)

    info('*** Остановка сети\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_topology()