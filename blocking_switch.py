#!/usr/bin/env python3
from ryu.base import app_manager
#from ryu.app import simple_switch_13
from ryu.controller import ofp_event, handler
from ryu.ofproto import ofproto_v1_3

from ryu.lib.packet import packet, ipv4, in_proto, ether_types, icmp, ethernet

import array
from simple_switch_13 import SimpleSwitch13
from icmp_detector import ICMP_Detector
import time

# table 0 -> table 5 -> table 10
FILTER_TABLE = 5
FORWARD_TABLE = 10

# ban offenders for 10 sec
BAN_TIME = 10


class BlockingSwitch(SimpleSwitch13):
    def __init__(self, *args, **kwargs):
        super(BlockingSwitch, self).__init__(*args, **kwargs)
        self._tracker = ICMP_Detector()
        self._icmp_ban_timers = dict()


    @handler.set_ev_cls(ofp_event.EventOFPSwitchFeatures, handler.CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        '''
        Set up switch features
        '''
        super(BlockingSwitch, self).switch_features_handler(ev)
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # add tables at startup
        self.add_default_table(datapath)
        self.add_filter_table(datapath)
        #self.apply_filter_table_rules(datapath)

    @handler.set_ev_cls(ofp_event.EventOFPPacketIn, handler.MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        '''
        Called whenever a packet enters a switch controlled by this controller.
        '''
        super(BlockingSwitch, self)._packet_in_handler(ev)
        msg = ev.msg
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        ping = pkt.get_protocol(icmp.icmp)
        datapath = msg.datapath
        dst = eth.dst
        src = eth.src

        offenders = self._tracker.tally(src)
        if ping:
            # Ping detected, somebody's flooding, and icmp blocking rule probably
            # expired by now.
            time_elapsed = self._time_since_last_ban(src)
            if offenders != [] and time_elapsed > BAN_TIME:
                # only punish the offender, not the replying victim
                print('flood detected from ',
                    src,
                    ' - blocking all ICMP traffic from that host temporarily...')
                self.apply_filter_table_rules(datapath, src)
                self._icmp_ban_timers[src] = time.time()


    def _time_since_last_ban(self, src):
        '''
        Calculate the time elapsed since src was banned last time.

        Params:
            src(str): MAC address of the host to check for ban timer (01:23:...)

        Returns:
            (int): number of seconds since the last ban, or BAN_TIME+1 seconds if
                   this host hasn't been banned before (e.g. assume that ban has
                   "expred").
        '''
        if src not in self._icmp_ban_timers.keys():
            return BAN_TIME + 1
        else:
            return time.time() - self._icmp_ban_timers[src]



    def add_default_table(self, datapath):
        '''
        Set up pipeline: default table -> filter table
        '''
        # openflow protocol definitions
        ofproto = datapath.ofproto

        # openflow protocol implementations
        parser = datapath.ofproto_parser

        # instruction: "defer to table 5 (filter table)"
        inst = [parser.OFPInstructionGotoTable(FILTER_TABLE)]

        # use the instruction to create a flowtable-modifying object
        mod = parser.OFPFlowMod(datapath=datapath, table_id=0, instructions=inst)

        # send that mod object to the switch
        datapath.send_msg(mod)


    def add_filter_table(self, datapath):
        '''
        set up pipeline: filter table -> forward table
        '''
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionGotoTable(FORWARD_TABLE)]
        mod = parser.OFPFlowMod(datapath=datapath, table_id=FILTER_TABLE,
                                priority=1, instructions=inst)
        datapath.send_msg(mod)


    def apply_filter_table_rules(self, datapath, src_mac='', duration=10):
        '''
        Apply "drop all ICMP from host" rule to FORWRAD_TABLE

        Params:
            datapath (ryu.controller.controller.Datapath): ???

        Returns:
            nothing
        '''
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        if src_mac != '':
            # Create a rule matching all ICMP packets from src_mac.
            match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                    ip_proto=in_proto.IPPROTO_ICMP,
                                    eth_src=src_mac)
        else:
            # block ICMP packets globally
            match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                    ip_proto=in_proto.IPPROTO_ICMP)

        # Use that rule to create a flowtable-modifying object
        # NOTE: in a FILTERING table, if a rule matches a packet, then the packet
        #       is dropped
        mod = parser.OFPFlowMod(datapath=datapath, table_id=FILTER_TABLE,
                                priority=10000, match=match,
                                hard_timeout=duration)

        # send that mod object to the switch
        datapath.send_msg(mod)


    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        '''
        Modify the forwardng table to apply <actions> to any packet that
        satisfies <match> conditions.
        '''
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, table_id=FORWARD_TABLE,
                                    match=match, instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, table_id=FORWARD_TABLE,
                                    instructions=inst)
        datapath.send_msg(mod)
