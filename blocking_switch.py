#!/usr/bin/env python3
from ryu.base import app_manager
#from ryu.app import simple_switch_13
from ryu.controller import ofp_event, handler
from ryu.ofproto import ofproto_v1_3

from ryu.lib.packet import packet, ipv4, in_proto, ether_types, icmp, ethernet

import array
from simple_switch_13 import SimpleSwitch13
from detector import ICMP_Tracker
import time

# table 0 -> table 5 -> table 10
FILTER_TABLE = 5
FORWARD_TABLE = 10


class BlockingSwitch(SimpleSwitch13):
    def __init__(self, *args, **kwargs):
        super(BlockingSwitch, self).__init__(*args, **kwargs)
        self._tracker = ICMP_Tracker()
        self._icmp_brake_timestamp = 0


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

        is_flood = self._tracker.icmp_sent(src)
        time_since_last_block = time.time() - self._icmp_brake_timestamp
        if ping:
            # Ping detected, somebody's flooding, and icmp blocking rule probably
            # expired by now.
            if is_flood and time_since_last_block > 10:
                print('flood detected, blocking all ICMP traffic...')
                self.apply_filter_table_rules(datapath)
                self._icmp_brake_timestamp = time.time()



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


    def apply_filter_table_rules(self, datapath):
        '''
        Apply "drop all ICMP" rule to FORWRAD_TABLE

        Params:
            datapath (ryu.controller.controller.Datapath): ???

        Returns:
            nothing
        '''
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Create a rule matching all ICMP packets.
        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                ip_proto=in_proto.IPPROTO_ICMP)

        # Use that rule to create a flowtable-modifying object
        # NOTE: in a FILTERING table, if a rule matches a packet, then the packet
        #       is dropped
        mod = parser.OFPFlowMod(datapath=datapath, table_id=FILTER_TABLE,
                                priority=10000, match=match,
                                hard_timeout=10)

        # send that mod object to the switch
        datapath.send_msg(mod)


    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        '''
        Whoever calls this function gets to add their rules (match) to the
        flowtable.
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
