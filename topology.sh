echo "see http://localhost:8080/home/topology.html once the topology is loaded"
sudo mn --controller=remote,ip=127.0.0.1 --mac -i 10.1.1.0/24 --topo=tree,depth=2,fanout=2

