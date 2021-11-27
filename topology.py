#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info



class Topology(Topo):
    "Single switch connected to n hosts."
    def build(self):
        s1 = self.addSwitch('s1', failMode='secure')
        s2 = self.addSwitch('s2', failMode='secure')
        h1 = self.addHost('h1', mac="00:00:00:00:00:01", ip="192.168.1.1/24")
        h2 = self.addHost('h2', mac="00:00:00:00:00:02", ip="192.168.1.2/24")
        h3 = self.addHost('h3', mac="00:00:00:00:00:03", ip="192.168.1.3/24")
        h4 = self.addHost('h4', mac="00:00:00:00:00:04", ip="192.168.1.4/24")

        self.addLink(s1, s2)
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s2)
        

if __name__ == '__main__':
    setLogLevel('info')
    topology = Topology()
    c1 = RemoteController('c1', ip= '127.0.0.1')
    network = Mininet (topo=topology, controller=c1)

    info('*** Starting network\n')
    network.start()
    #network.pingAll()
    CLI(network)
    network.stop()


