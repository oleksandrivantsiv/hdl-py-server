#!/usr/bin/python

import time
import argparse
from hdlclient import floor_heatings

def parse_cmd_arguments():

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-m", "--mode", type=str, help="Mode that should be set")
    arguments = arg_parser.parse_args()

    return arguments


def set_mode(mode):
    off_devices = [
        floor_heatings.cabinet_fh,
        floor_heatings.living_room_fh,
        floor_heatings.cabinet_rad,
        floor_heatings.living_room_rad,
    ]

    normal_devices = [
        floor_heatings.hall_fh,
        floor_heatings.bad_room_rad,
        floor_heatings.bad_room_vent,
        floor_heatings.child_rad,
    ]

    for dev in off_devices:
        dev.execute_op("off", mode, 6, 6, 6, 6)

    for dev in normal_devices:
        dev.execute_op("on", mode, 23, 23, 20, 20)

    floor_heatings.bath_room_fh.execute_op("on", mode, 35, 35, 35, 35)
    floor_heatings.bath_room_rad.execute_op("on", mode, 35, 35, 35, 35)
    floor_heatings.vault_rad.execute_op("on", mode, 20, 20, 18, 18)


if __name__ == '__main__':
    args = parse_cmd_arguments()

    if args.mode == "at-home":
        for i in xrange(3):
    	    set_mode("normal")
            time.sleep(1)
    elif args.mode == "away":
        for i in xrange(3):
    	    set_mode("away")
            time.sleep(1)
    else:
        raise RuntimeError("Wrong mode: %s" % mode)
