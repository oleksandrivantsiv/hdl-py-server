#!/usr/bin/python

import crc16
import time
import binascii
import codecs
import threading
from scapy.all import *


class HDLComponent(object):

    preamble = b"c0a8011448444c4d495241434c45"

    def __init__(self):
        self.iface = "wlp2s0"
        self.ip_address = None
        self.udp_port = 6000
        # 16 bit
        self.leading_code = 0xaaaa
        # 8 bit (13-128)
        # Base data length without content
        self.header_length = 11
        # 8 bit (0-254)
        self.orig_subnet_id = 0xfc
        # 8 bit (0-254)
        self.orig_device_id = 0xfc
        # 16 bit (0-0xffff)
        self.orig_device_type = 0xfffc
        # 8 bit (0-254)
        self.target_subnet_id = 0
        # 8 bit (0-254)
        self.target_device_id = 0
        
        self.sniffer = None

    def content(self):
        raise NotImplemented()

    def bytes_to_hex(self, b):
        return binascii.hexlify(bytes(b))

    def raw_data(self, oper_code, content):
        b = []

        b.append((self.leading_code >> 8) & 0xff)
        b.append(self.leading_code & 0xff)
        b.append((self.header_length + len(content)) & 0xff)
        b.append(self.orig_subnet_id & 0xff)
        b.append(self.orig_device_id & 0xff)
        b.append((self.orig_device_type >> 8) & 0xff)
        b.append(self.orig_device_type & 0xff)
        b.append((oper_code >> 8) & 0xff)
        b.append(oper_code & 0xff)
        b.append(self.target_subnet_id & 0xff)
        b.append(self.target_device_id & 0xff)

        b += content

        s = self.bytes_to_hex(b[2:])
        
        crc = crc16.crc16xmodem(codecs.decode(s, 'hex'))

        b.append((crc >> 8) & 0xff)
        b.append(crc & 0xff)

        return binascii.unhexlify(self.preamble + self.bytes_to_hex(b))

    def set_ip_address(self, ip):
        self.ip_address = ip
    
    def set_udp_port(self, port):
        self.udp_port = int(port)

    def send_packet(self, oper_code, content):
        raw_data = self.raw_data(oper_code, content)
        pack = Ether(src="cc:2f:71:91:2e:54", dst="ff:ff:ff:ff:ff:ff")/IP(src="192.168.88.183", dst=self.ip_address)/UDP(sport=self.udp_port, dport=self.udp_port)/Raw(raw_data)
        sendp(pack, iface=self.iface, count=1, verbose=False)
    
    def run_sniffer(self):
        stop_event = threading.Event()
        
        start = time.time()
        
        def recv(*args, **kwargs):
            if time.time() - start > 1:
                stop_event.set()

            if self.receive(*args, **kwargs):
                stop_event.set()

        sniff(prn=recv, iface=self.iface, 
              stop_filter=lambda p: stop_event.is_set(), 
              filter="udp and port {}".format(self.udp_port), 
              timeout=1)

    def send_receive(self, oper_code, content):
        self.sniffer = threading.Thread(target=self.run_sniffer)
        self.sniffer.start()
        time.sleep(0.1)
        self.send_packet(oper_code, content)

    def validate_op(self, op):
        raise NotImplemented()

    def execute_op(self, op):
        raise NotImplemented()
    
    def update(self):
        raise NotImplemented()
    
    def receive(self, packet):
        raise NotImplemented()
    
    def get_status(self):
        raise NotImplemented()
    
    def wait(self):
        if self.sniffer:
            self.sniffer.join()
        self.sniffer = None


class HDLRelay(HDLComponent):

    operations = {
        "on":  100,
        "off": 0
    }

    def __init__(self, subnet_id, device_id, channel):
        super(HDLRelay, self).__init__()

        # 16 bit (0-0xffff)
        self.oper_code = 0x0031
        self.update_oper_code = 0x0033
        self.target_subnet_id = subnet_id
        self.target_device_id = device_id
        self.channel = channel & 0xff
        self.status = "off"

    def content(self):
        return self.cnt

    def validate_op(self, op):
        return op in self.operations

    def execute_op(self, op):
        cnt = []
        cnt.append(self.channel)
        cnt.append(self.operations[op])
        # Padding
        cnt.append(0)
        cnt.append(0)

        self.send_packet(self.oper_code, cnt)
        self.status = op

    def receive(self, packet):
        payload = bytes(packet[UDP].payload)
        b = binascii.hexlify(payload)
        data = b[len(self.preamble):]
        
        hdl_data = list(binascii.unhexlify(data))
        
        if hdl_data[3] != self.target_subnet_id:
            return False
        if hdl_data[4] != self.target_device_id:
            return False
        if hdl_data[7] != 0:
            return False
        if hdl_data[8] != 0x34:
            return False

        content = hdl_data[self.header_length:]
        if content[0] != 0x0c:
            return False
        
        channels = content[1:]
        
        c = channels[self.channel - 1]
        for command, code in self.operations.items():
            if c == code:
                self.status = command
                break

        return True
    
    def get_status(self):
        return {
            "status": self.status,
            }

    def update(self):
        if not self.target_subnet_id and not self.target_device_id and not self.channel:
            return
        
        self.send_receive(self.update_oper_code, [])

class HDLFloorHeating(HDLComponent):
    """
    Data Format:
      Status: 1 byte
      Temp: 1 byte
      Mode: 1 byte
      Normal temp: 1 byte
      Day temp: 1 byte
      Night temp: 1 byte
      Away temp: 1 byte
    """

    status_map = {
        "on":  1,
        "off": 0
    }

    temperature_map = {
        "cels": 0,
        "fahr": 1
    }

    mode_map = {
        "normal": 1,
        "day": 2,
        "night": 3,
        "away": 4,
        "timer": 5,
    }

    def __init__(self, subnet_id, device_id, channel):
        super(HDLFloorHeating, self).__init__()

        # 16 bit (0-0xffff)
        self.oper_code = 0x1c5c
        self.update_oper_code = 0x1c5e
        self.target_subnet_id = subnet_id
        self.target_device_id = device_id
        self.channel = channel & 0xff
        
        self.temp_type = "cels"
        self.status = "on"
        self.mode = "normal"
        self.normal_temp = 23
        self.day_temp = 23
        self.night_temp = 20
        self.away_temp = 20
        self.current_temp = 0

    def content(self):
        return self.cnt

    def validate_op(self, op):
        return op in self.operations

    def execute_op(self, status, mode, normal_temp=None, day_temp=None, night_temp=None, away_temp=None):
        self.status = status
        self.mode = mode
        self.normal_temp = normal_temp
        self.day_temp = day_temp
        self.night_temp = night_temp
        self.away_temp = away_temp
        
        cnt = []
        cnt.append(self.channel)
        cnt.append(self.status_map[status])
        cnt.append(self.temperature_map[self.temp_type])
        cnt.append(self.mode_map[mode])
        cnt.append(self.normal_temp)
        cnt.append(self.day_temp)
        cnt.append(self.night_temp)
        cnt.append(self.away_temp)
        # Padding
        cnt.append(0)
        cnt.append(0)
        
        print(cnt)

        self.send_packet(self.oper_code, cnt)

    def receive(self, packet):
        payload = bytes(packet[UDP].payload)
        b = binascii.hexlify(payload)
        data = b[len(self.preamble):]
        
        hdl_data = list(binascii.unhexlify(data))
        
        if hdl_data[3] != self.target_subnet_id:
            return False
        if hdl_data[4] != self.target_device_id:
            return False
        if hdl_data[7] != 0x1c:
            return False
        if hdl_data[8] != 0x5f:
            return False

        content = hdl_data[self.header_length:]
        
        # Check channel number,
        if content[0] != self.channel:
            return False
        
        for status, code in self.status_map.items():
            if content[1] & 0x7 == code:
                self.status = status
                break
        
        for temp_type, code in self.temperature_map.items():
            if content[2] == code:
                self.temp_type = temp_type
                break
        
        for mode, code in self.mode_map.items():
            if content[3] == code:
                self.mode = mode
                break
        
        self.normal_temp = content[4]
        self.day_temp = content[5]
        self.night_temp = content[6]
        self.away_temp = content[7]
        
        self.current_temp = content[9]

        return True

    def update(self):
        cnt = []
        cnt.append(self.channel)

        self.send_receive(self.update_oper_code, cnt)
    
    def get_status(self):
        return {
            "status": self.status,
            "temp_type": self.temp_type,
            "mode": self.mode,
            "normal_temp": self.normal_temp,
            "day_temp": self.day_temp,
            "night_temp": self.night_temp,
            "away_temp": self.away_temp,
            "current_temp": self.current_temp
            }


# Zone: list of channels
class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


lights = AttrDict({
    "dining_grp1": HDLRelay(1, 12, 3),
    "dining_grp2": HDLRelay(1, 12, 4),
    "dining_led": HDLRelay(1, 12, 12),
    "dining_vent": HDLRelay(1, 11, 3),

    "living_main": HDLRelay(1, 12, 1),
    "living_led": HDLRelay(1, 11, 9),
    "living_drops": HDLRelay(0,0,0) , # TBD

    "backyard": HDLRelay(0,0,0),  # TBD

    "hall_floar_1_grp1": HDLRelay(0,0,0),  # TBD
    "hall_floar_1_grp2": HDLRelay(0,0,0),  # TBD
    "hall_floar_1_wall": HDLRelay(0,0,0),  # TBD

    "hall_floar_2_grp1": HDLRelay(0,0,0),  # TBD
    "hall_floar_2_grp2": HDLRelay(0,0,0),  # TBD
    "hall_floar_2_led": HDLRelay(0,0,0),  # TBD

    "stairs": HDLRelay(0,0,0),  # TBD

    "bedroom_grp1": HDLRelay(0,0,0),  # TBD
    "bedroom_grp2": HDLRelay(0,0,0),  # TBD
    "bedroom_pendant_right": HDLRelay(0,0,0),  # TBD
    "bedroom_pendant_left": HDLRelay(0,0,0),  # TBD

    "dressing": HDLRelay(0,0,0),  # TBD
    "dressing_bra": HDLRelay(0,0,0),  # TBD
    "dressing_led": HDLRelay(0,0,0),  # TBD

    "kidsroom_grp1": HDLRelay(0,0,0),  # TBD
    "kidsroom_grp2": HDLRelay(0,0,0),  # TBD
    "kidsroom_grp3": HDLRelay(0,0,0),  # TBD
    "kidsroom_bra": HDLRelay(0,0,0),  # TBD
    "kidsroom_bubbles": HDLRelay(0,0,0),  # TBD

    "bathroom_led": HDLRelay(0,0,0),  # TBD
    "bathroom_grp1": HDLRelay(0,0,0),  # TBD
    "bathroom_grp2": HDLRelay(0,0,0),  # TBD
    "bathroom_vent": HDLRelay(0,0,0),  # TBD

    "toilet": HDLRelay(0, 0, 0),  # TBD
    "toilet_vent": HDLRelay(0, 0, 0)  # TBD
})


floor_heatings = AttrDict({
    "cabinet_fh": HDLFloorHeating(1, 31, 1), 
    "living_room_fh": HDLFloorHeating(1, 31, 2), 
    "hall_fh": HDLFloorHeating(1, 31, 3), 
    "bath_room_fh": HDLFloorHeating(1, 31, 4), 
    "bath_room_rad": HDLFloorHeating(1, 31, 5), 
    "vault_rad": HDLFloorHeating(1, 31, 6), 

    "cabinet_rad": HDLFloorHeating(1, 32, 1), 
    "living_room_rad": HDLFloorHeating(1, 32, 2), 
    "living_room_vent": HDLFloorHeating(1, 32, 3), 
    "bad_room_rad": HDLFloorHeating(1, 32, 4), 
    "bad_room_vent": HDLFloorHeating(1, 32, 5), 
    "child_rad": HDLFloorHeating(1, 32, 6), 
})


# channel map dedicated for requests /api/light/<channel>/<operation>
channel_map = {
    "dining": (lights.dining_grp1, lights.dining_grp2),
    "living_room": (lights.living_main,),
}

# scenarios map dedicated for requests /api/light/<sequence_of_on_offs>
scenarios_map = {
    "lets_watch_a_movie": ((lights.living_led, "on"),
                           (lights.living_main, "off"),
                           (lights.dining_grp1, "off"),
                           (lights.dining_grp2, "off")
                           ),
    "lets_cook": ((lights.dining_grp1, "on"),
                  (lights.dining_grp2, "on"),
                  (lights.dining_vent, "on")
                  ),
    "finish_cooking": ((lights.dining_vent, "off"),
                       (lights.dining_grp2, "off")
                       ),
}


class HDLClient(object):

    def process_ifttt(self, request_path):
        request = request_path.split("/")
        if len(request) not in (4, 5):
            raise RuntimeError("Wrong request %s!" % request_path)

        if len(request) == 5:
            _, api, action, scene, operation = request

            if action != "light":
                raise RuntimeError("Unsupported action %s!" % action)

            if scene not in channel_map:
                raise RuntimeError("Unsupported scene %s!" % scene)

            for dev in channel_map[scene]:
                if not dev.validate_op(operation):
                    raise RuntimeError("Unsupported operation %s!" % operation)

            for dev in channel_map[scene]:
                dev.execute_op(operation)

        if len(request) == 4:
            _, api, action, scenario = request

            if action != "light":
                raise RuntimeError("Unsupported action %s!" % action)

            if scenario not in scenarios_map:
                raise RuntimeError("Unsupported scene %s!" % scenario)

            for dev, operation in scenarios_map[scenario]:
                dev.execute_op(operation)
