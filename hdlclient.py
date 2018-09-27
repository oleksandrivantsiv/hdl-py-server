#!/usr/bin/python

import crc16
import binascii
from scapy.all import *


class HDLComponent(object):

    preamble = "c0a8011448444c4d495241434c45"

    def __init__(self):
        # 16 bit
        self.leading_code = 0xaaaa
        # 8 bit (13-128)
        # Base data length without content
        self.length = 11
        # 8 bit (0-254)
        self.orig_subnet_id = 0xfc
        # 8 bit (0-254)
        self.orig_device_id = 0xfc
        # 16 bit (0-0xffff)
        self.orig_device_type = 0xfffc
        # 16 bit (0-0xffff)
        self.oper_code = 0
        # 8 bit (0-254)
        self.target_subnet_id = 0
        # 8 bit (0-254)
        self.target_device_id = 0

    def content(self):
        raise NotImplemented()

    def bytes_to_hex(self, b):
        return "".join(map(lambda val: "%02x" % val, b))

    def crc(self):
        b = self.bytes()
        # CRC is cal
        s = self.bytes_to_hex(b[2:])
        print("crc", s)
        print("crc", crc16.crc16xmodem(s.decode("hex")), hex(crc16.crc16xmodem(s.decode("hex"))))
        return crc16.crc16xmodem(s.decode("hex"))

    def bytes(self):
        b = []
        content = self.content()

        b.append((self.leading_code >> 8) & 0xff)
        b.append(self.leading_code & 0xff)
        b.append(self.length & 0xff)
        b.append(self.orig_subnet_id & 0xff)
        b.append(self.orig_device_id & 0xff)
        b.append((self.orig_device_type >> 8) & 0xff)
        b.append(self.orig_device_type & 0xff)
        b.append((self.oper_code >> 8) & 0xff)
        b.append(self.oper_code & 0xff)
        b.append(self.target_subnet_id & 0xff)
        b.append(self.target_device_id & 0xff)

        b += content

        return b

    def raw_data(self):
        b = self.bytes()
        crc = self.crc()

        b.append((crc >> 8) & 0xff)
        b.append(crc & 0xff)

        print("new ", self.preamble + self.bytes_to_hex(b))

        return binascii.unhexlify(self.preamble + self.bytes_to_hex(b))

    def _send_packet(self, raw_data):
        pack = Ether(src="cc:2f:71:91:2e:54", dst="ff:ff:ff:ff:ff:ff")/IP(src="192.168.88.183", dst="192.168.88.255")/UDP(sport=6000, dport=6000)/Raw(raw_data)
        sendp(pack, iface="wlp2s0", count=1)

    def validate_op(self, op):
        raise NotImplemented()

    def execute_op(self, op):
        raise NotImplemented()


class HDLRelay(HDLComponent):

    operations = {
        "on":  100,
        "off": 0
    }

    def __init__(self, subnet_id, device_id, channel):
        super(HDLRelay, self).__init__()

        self.oper_code = 0x0031
        self.target_subnet_id = subnet_id
        self.target_device_id = device_id
        self.cnt = []
        self.cnt.append(channel & 0xff)
        self.cnt.append(0)
        self.cnt.append(0)
        self.cnt.append(0)
        self.length += len(self.cnt)

    def content(self):
        return self.cnt

    def validate_op(self, op):
        return op in self.operations

    def execute_op(self, op):
        self.cnt[1] = self.operations[op]
        self._send_packet(self.raw_data())

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

        self.oper_code = 0x1c5c
        self.target_subnet_id = subnet_id
        self.target_device_id = device_id
        
        self.temp_type = self.temperature_map["cels"]
        self.status = self.status_map["on"]
        self.mode = self.mode_map["normal"]
        self.normal_temp = 23
        self.day_temp = 23
        self.night_temp = 20
        self.away_temp = 20

        self.cnt = []
        self.cnt.append(channel & 0xff)
        self.cnt.append(0)
        self.cnt.append(0)
        self.cnt.append(0)
        self.cnt.append(0)
        self.cnt.append(0)
        self.cnt.append(0)
        self.cnt.append(0)
        # Padding
        self.cnt.append(0)
        self.cnt.append(0)
        self.length += len(self.cnt)

    def content(self):
        return self.cnt

    def validate_op(self, op):
        return op in self.operations

    def execute_op(self, status, mode, normal_temp=None, day_temp=None, night_temp=None, away_temp=None):
        self.cnt[1] = self.status_map[status]
        self.cnt[2] = self.temp_type
        self.cnt[3] = self.mode_map[mode]
        self.cnt[4] = normal_temp if normal_temp else self.normal_temp
        self.cnt[5] = day_temp if day_temp else self.day_temp
        self.cnt[6] = night_temp if night_temp else self.night_temp
        self.cnt[7] = away_temp if away_temp else self.away_temp
        self._send_packet(self.raw_data())


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
    #"living_room_vent": HDLFloorHeating(1, 32, 3), 
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
        print request_path
        request = request_path.split("/")
        print("request lenght", len(request))
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
