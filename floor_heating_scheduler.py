#!/usr/bin/python

import time
import argparse
from hdlclient import floor_heatings
import time


workdays = ["mon", "tue", "wed", "thu", "fri"]
weekends = ["sat", "sun"]


off_devices = [
    floor_heatings.cabinet_fh,
    floor_heatings.cabinet_rad,
    floor_heatings.living_room_rad,
]


def main(*arg, **kwargs):
    day, month, date, time_now, year = time.ctime().lower().split()
    hour = int(time_now.split(":")[0])

    at_home_hours = []
    away_hours = []
    if day in workdays:
        at_home_hours.append(6)
        at_home_hours.append(18)
        away_hours.append(9)
        away_hours.append(0)
    else:
        at_home_hours.append(6)
        away_hours.append(0)

    mode = None
    if hour in at_home_hours:
        mode = "normal"
    elif hour in away_hours:
        mode = "away"

    if mode:
        floor_heatings.vault_rad.execute_op("on", mode, 20, 20, 18, 18)
    
        floor_heatings.hall_fh.execute_op("on", mode, 23, 23, 18, 18)
        floor_heatings.living_room_fh.execute_op("on", mode, 23, 23, 18, 18)
    
        floor_heatings.bad_room_rad.execute_op("on", mode, 22, 22, 22, 22)
        floor_heatings.bad_room_vent.execute_op("on", mode, 22, 22, 22, 22)
        floor_heatings.child_rad.execute_op("on", mode, 22, 22, 22, 22)
    
        floor_heatings.bath_room_fh.execute_op("on", mode, 35, 35, 35, 35)
        floor_heatings.bath_room_rad.execute_op("on", mode, 35, 35, 35, 35)

    if hour == 1:
       for dev in off_devices:
           dev.execute_op("off", "normal", 6, 6, 6, 6)

    if hour == 22:
        # Turn off bad room radiator before go to sleep
        floor_heatings.bad_room_vent.execute_op("off", "away", 22, 22, 22, 22)


if __name__ == '__main__':
    for i in range(3):
        main()