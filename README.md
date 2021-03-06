# CPSC 454 group project 

## Group members

- [Rachelle Chanthavong](https://github.com/rachpchan)
- [Danny Diep](https://github.com/DannyDiep963)
- Austin Kim 

## Report

The project report can be found under the `docs` folder. ([link](./docs/report.pdf))

Abstract: 

> Conventional firewalls are used to implement network security standards at network borders. 
> However, this can leave clients exposed to cyberattacks that originate within the network to which they are connected. 
> One way to mitigate this issue is to use the flexibility of software-defined networking (SDN) to shape network traffic using a virtual firewall, enhancing network security across the board. 
> In this project, we demonstrate a network-wide virtual firewall that uses the OpenFlow API to apply packet filtering across an entire virtual network in an automated manner.

## Prerequisites 

- [Flowmanager](https://github.com/martimy/flowmanager) -- optional, if we want to show off the topology. 
- [Ryu framework](https://github.com/faucetsdn/ryu) -- mandatory. This project depends on it.
- Mininet -- mandatory. This project depends on it.
- `hping` -- mandatory. Needed for demonstration. 

## Running 

Unlike Pox, the components need to be run in a specific order:
1. Start the controller
2. Start the topology 
3. Demonstrate the ICMP flood trigger

This should be done in two separate terminal windows.

### Step 1: Start the controller

Open up a terminal window and start the controller. 

For convenience, this terminal window will be referred to as **controller terminal** in step 3.
#### Option 1: You already have Flowmanager

If you have Flowmanager cloned somewhere, run:

```
$ cd ~/path-to-this-project
$ ryu-manager --observe-links ~/path-to-flowmanager-dir/flowmanager.py blocking_switch.py 
```

#### Option 2: You want to use `start_switch.sh` (requires Flowmanager)

If you want to use the `start_switch.sh` script, then clone Flowmanager in the `~/sources` directory: 

```
$ mkdir ~/sources 
$ cd ~/sources 
$ git clone https://github.com/martimy/flowmanager
```
...then run the script:

```
$ cd ~/path-to-this-project
$ ./start_switch.sh
```

#### Option 3: You don't care about Flowmanager 

If you don't care about Flowmanager, then run: 
```
$ cd ~/path-to-this-project 
$ ryu-manager blocking_switch.py
```

### Step 2: Start the topology 

In a separate terminal window, start the topology. 

This terminal window will be referred to as **topology terminal** in step 3.

#### Option 1: Use the `topology.sh` script 

Simply run the script: 

```
$ ./topology.sh
```

#### Option 2: Use the `topology.py` program 

Simply, run the program: 

```
$ ./topology.py
```

### Step 3: Demonstrate the ICMP flood trigger 

At this point, *if you have Flowmanager installed and running with the controller*, you can point the browser at http://localhost:8080/home/topology.html to display a diagram of the current topology. 
You may have to perform `pingall` in **topology terminal** for the nodes to show up. 

In **topology terminal**, start the flood attack: 

```
mininet> h1 python3 flood.py h2 
```

This will cause `h1` to launch a ping flood attack on `h2`. 

Observe the output in **controller terminal**. Once the `flood detected, blocking all ICMP traffic...` message pops up, all ICMP traffic are *blocked* for the offending host for 10 seconds. This will also block the victim to prevent replies from flooding the network.

In **topology terminal**, hit `ctrl+c` to stop the flood attack. Then, start the normal pinging process immediately: 

```
mininet> h1 ping h2 
```

Wait out the remainder of the 10-second ban. The packets will start arriving again once the block is lifted. 
