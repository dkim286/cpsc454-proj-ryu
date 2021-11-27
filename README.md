# CPSC 454 group project 

## Group members

- Rachelle Chanthavong 
- Danny Diep 
- Austin Kim 

## Prerequisites 

- [Flowmanager](https://github.com/martimy/flowmanager) -- optional, if we want to show off the topology. 
- [Ryu framework](https://github.com/faucetsdn/ryu) -- mandatory. This project depends on it.
- Mininet -- mandatory. This project depends on it.

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

For convenience, this terminal window will be referred to as **topology terminal** in step 3.

#### Option 1: Use the `topology.sh` script 

Simply run the script: 

```
$ ./topology.sh
```

#### Option 2: Use the `topology.py` program 

Simply run the program: 

```
$ ./topology.py
```

### Step 3: Demonstrate the ICMP flood trigger 

At this point, you can open up a browser to http://localhost:8080/home/topology.html to show the current topology. 
You may have to perform `pingall` in **topology terminal** for the nodes to show up. 

In **topology terminal**, start the flood attack: 

```
mininet> h1 python3 flood.py h2 
```

This will cause `h1` to launch a ping flood attack on `h2`. 

Observe the output in **controller terminal**. Once you see `flood detected, blocking all ICMP traffic...` message pop up, that means all ICMP traffic are *blocked* globally for 10 seconds. 

In **topology terminal**, hit `ctrl+c` to stop the flood attack. Immediately, start a normal pinging process: 

```
mininet> h1 ping h2 
```

Wait out the remainder of the 10-second ban. The packets will start arriving again once the block is lifted. 
