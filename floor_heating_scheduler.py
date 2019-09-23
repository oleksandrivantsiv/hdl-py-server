#!/usr/bin/python

import time
import argparse
from hdlclient import floor_heatings
import time


class Scheduler(object):

    workdays = ["mon", "tue", "wed", "thu", "fri"]
    weekends = ["sat", "sun"]

    def __init__(self, dev, temp, athome=None, away=None, off=None):
        self.dev = dev
        self.temp = temp
        self.athome_time = athome if athome else {}
        self.away_time = away if away else {}
        self.off_time = off if off else {}

    def execute(self, day, hour):
        if day in self.athome_time and hour in self.athome_time[day]:
            self.dev.execute_op("on", "normal", *self.temp)

        if day in self.away_time :
            if hour in self.away_time[day]:
                self.dev.execute_op("on", "away", *self.temp)
        else:
            if day in self.athome_time and hour not in self.athome_time[day]:
                self.dev.execute_op("on", "away", *self.temp)

        if day in self.off_time and hour in self.off_time[day]:
            self.dev.execute_op("off", "normal", *self.temp)


schedulers_winter = [
    Scheduler(dev=floor_heatings.cabinet_fh, temp=(22, 22, 20, 20),
              athome={
                  "mon": range(6, 9) + range(18, 24),
                  "tue": range(6, 9) + range(18, 24),
                  "wed": range(6, 9) + range(18, 24),
                  "thu": range(6, 9) + range(18, 24),
                  "fri": range(6, 9) + range(18, 24),
                  "sat": range(8, 24),
                  "sun": range(8, 24),
                  }, 
              ),
    Scheduler(dev=floor_heatings.cabinet_rad, temp=(6, 6, 6, 6),
              off={
                  "mon": range(0, 24),
                  "tue": range(0, 24),
                  "wed": range(0, 24),
                  "thu": range(0, 24),
                  "fri": range(0, 24),
                  "sat": range(0, 24),
                  "sun": range(0, 24),
                  }),
    Scheduler(dev=floor_heatings.living_room_rad, temp=(23, 23, 20, 20),
              athome={
                  "mon": range(6, 9) + range(18, 24),
                  "tue": range(6, 9) + range(18, 24),
                  "wed": range(6, 9) + range(18, 24),
                  "thu": range(6, 9) + range(18, 24),
                  "fri": range(6, 9) + range(18, 24),
                  "sat": range(8, 24),
                  "sun": range(8, 24),
                  }),
    Scheduler(dev=floor_heatings.living_room_vent, temp=(6, 6, 6, 6),
              off={
                  "mon": range(0, 24),
                  "tue": range(0, 24),
                  "wed": range(0, 24),
                  "thu": range(0, 24),
                  "fri": range(0, 24),
                  "sat": range(0, 24),
                  "sun": range(0, 24),
                  }),
    Scheduler(dev=floor_heatings.vault_rad, temp=(20, 20, 18, 18),
              athome={
                  "mon": range(6, 9) + range(18, 24),
                  "tue": range(6, 9) + range(18, 24),
                  "wed": range(6, 9) + range(18, 24),
                  "thu": range(6, 9) + range(18, 24),
                  "fri": range(6, 9) + range(18, 24),
                  "sat": range(8, 24),
                  "sun": range(8, 24),
                  }),
    Scheduler(dev=floor_heatings.hall_fh, temp=(23, 23, 20, 20),
              athome={
                  "mon": range(6, 9) + range(18, 24),
                  "tue": range(6, 9) + range(18, 24),
                  "wed": range(6, 9) + range(18, 24),
                  "thu": range(6, 9) + range(18, 24),
                  "fri": range(6, 9) + range(18, 24),
                  "sat": range(8, 24),
                  "sun": range(8, 24),
                  }),
    Scheduler(dev=floor_heatings.living_room_fh, temp=(23, 23, 20, 20),
              athome={
                  "mon": range(6, 9) + range(18, 24),
                  "tue": range(6, 9) + range(18, 24),
                  "wed": range(6, 9) + range(18, 24),
                  "thu": range(6, 9) + range(18, 24),
                  "fri": range(6, 9) + range(18, 24),
                  "sat": range(8, 24),
                  "sun": range(8, 24),
                  }),
    Scheduler(dev=floor_heatings.bad_room_rad, temp=(23, 23, 23, 23),
              athome={
                  "mon": range(6, 9) + range(18, 24),
                  "tue": range(6, 9) + range(18, 24),
                  "wed": range(6, 9) + range(18, 24),
                  "thu": range(6, 9) + range(18, 24),
                  "fri": range(6, 9) + range(18, 24),
                  "sat": range(8, 24),
                  "sun": range(8, 24),
                  }),
    Scheduler(dev=floor_heatings.bad_room_vent, temp=(22, 22, 22, 22),
              athome={
                  "mon": range(6, 22),
                  "tue": range(6, 22),
                  "wed": range(6, 22),
                  "thu": range(6, 22),
                  "fri": range(6, 22),
                  "sat": range(6, 22),
                  "sun": range(6, 22),
                  }, 
              off={
                  "mon": range(22, 24) + range(0, 6),
                  "tue": range(22, 24) + range(0, 6),
                  "wed": range(22, 24) + range(0, 6),
                  "thu": range(22, 24) + range(0, 6),
                  "fri": range(22, 24) + range(0, 6),
                  "sat": range(22, 24) + range(0, 6),
                  "sun": range(22, 24) + range(0, 6),
                  }),
    Scheduler(dev=floor_heatings.child_rad, temp=(22, 22, 22, 22),
              athome={
                  "mon": range(6, 9) + range(18, 24),
                  "tue": range(6, 9) + range(18, 24),
                  "wed": range(6, 9) + range(18, 24),
                  "thu": range(6, 9) + range(18, 24),
                  "fri": range(6, 9) + range(18, 24),
                  "sat": range(8, 24),
                  "sun": range(8, 24),
                  }),
    Scheduler(dev=floor_heatings.bath_room_fh, temp=(23, 23, 20, 20),
              athome={
                  "mon": range(6, 9) + range(18, 24),
                  "tue": range(6, 9) + range(18, 24),
                  "wed": range(6, 9) + range(18, 24),
                  "thu": range(6, 9) + range(18, 24),
                  "fri": range(6, 9) + range(18, 24),
                  "sat": range(8, 24),
                  "sun": range(8, 24),
              }),
    Scheduler(dev=floor_heatings.bath_room_rad, temp=(6, 6, 6, 6),
              athome={
                  "mon": range(6, 9) + range(18, 24),
                  "tue": range(6, 9) + range(18, 24),
                  "wed": range(6, 9) + range(18, 24),
                  "thu": range(6, 9) + range(18, 24),
                  "fri": range(6, 9) + range(18, 24),
                  "sat": range(8, 24),
                  "sun": range(8, 24),
              }),
    ]

schedulers_summer = [
    Scheduler(dev=floor_heatings.cabinet_fh, temp=(23, 23, 20, 20),
              off={
                  "mon": range(0, 24),
                  "tue": range(0, 24),
                  "wed": range(0, 24),
                  "thu": range(0, 24),
                  "fri": range(0, 24),
                  "sat": range(0, 24),
                  "sun": range(0, 24),
                  }),
    Scheduler(dev=floor_heatings.cabinet_rad, temp=(6, 6, 6, 6),
              off={
                  "mon": range(0, 24),
                  "tue": range(0, 24),
                  "wed": range(0, 24),
                  "thu": range(0, 24),
                  "fri": range(0, 24),
                  "sat": range(0, 24),
                  "sun": range(0, 24),
                  }),
    Scheduler(dev=floor_heatings.living_room_rad, temp=(23, 23, 20, 20),
              off={
                  "mon": range(0, 24),
                  "tue": range(0, 24),
                  "wed": range(0, 24),
                  "thu": range(0, 24),
                  "fri": range(0, 24),
                  "sat": range(0, 24),
                  "sun": range(0, 24),
                  }),
    Scheduler(dev=floor_heatings.living_room_vent, temp=(6, 6, 6, 6),
              off={
                  "mon": range(0, 24),
                  "tue": range(0, 24),
                  "wed": range(0, 24),
                  "thu": range(0, 24),
                  "fri": range(0, 24),
                  "sat": range(0, 24),
                  "sun": range(0, 24),
                  }),
    Scheduler(dev=floor_heatings.vault_rad, temp=(30, 30, 18, 18),
              athome={
                  "mon": range(0, 2),
                  "tue": range(0, 2),
                  "wed": range(0, 2),
                  "thu": range(0, 2),
                  "fri": range(0, 2),
                  "sat": range(0, 2),
                  "sun": range(0, 2),
                  }, 
              off={
                  "mon": range(2, 24),
                  "tue": range(2, 24),
                  "wed": range(2, 24),
                  "thu": range(2, 24),
                  "fri": range(2, 24),
                  "sat": range(2, 24),
                  "sun": range(2, 24),
                  }),
    Scheduler(dev=floor_heatings.hall_fh, temp=(23, 23, 20, 20),
              off={
                  "mon": range(0, 24),
                  "tue": range(0, 24),
                  "wed": range(0, 24),
                  "thu": range(0, 24),
                  "fri": range(0, 24),
                  "sat": range(0, 24),
                  "sun": range(0, 24),
                  }),
    Scheduler(dev=floor_heatings.living_room_fh, temp=(23, 23, 20, 20),
              off={
                  "mon": range(0, 24),
                  "tue": range(0, 24),
                  "wed": range(0, 24),
                  "thu": range(0, 24),
                  "fri": range(0, 24),
                  "sat": range(0, 24),
                  "sun": range(0, 24),
                  }),
    Scheduler(dev=floor_heatings.bad_room_rad, temp=(23, 23, 23, 23),
              athome={
                  "mon": range(6, 9) + range(18, 24),
                  "tue": range(6, 9) + range(18, 24),
                  "wed": range(6, 9) + range(18, 24),
                  "thu": range(6, 9) + range(18, 24),
                  "fri": range(6, 9) + range(18, 24),
                  "sat": range(8, 24),
                  "sun": range(8, 24),
                  }),
    Scheduler(dev=floor_heatings.bad_room_vent, temp=(22, 22, 22, 22),
              off={
                  "mon": range(0, 24),
                  "tue": range(0, 24),
                  "wed": range(0, 24),
                  "thu": range(0, 24),
                  "fri": range(0, 24),
                  "sat": range(0, 24),
                  "sun": range(0, 24),
                  }),
    Scheduler(dev=floor_heatings.child_rad, temp=(22, 22, 22, 22),
              athome={
                  "mon": range(0, 24),
                  "tue": range(0, 24),
                  "wed": range(0, 24),
                  "thu": range(0, 24),
                  "fri": range(0, 24),
                  "sat": range(0, 24),
                  "sun": range(0, 24),
                  }),
    Scheduler(dev=floor_heatings.bath_room_fh, temp=(30, 30, 20, 20),
              athome={
                  "mon": range(20, 22),
                  "tue": range(20, 22),
                  "wed": range(20, 22),
                  "thu": range(20, 22),
                  "fri": range(20, 22),
                  "sat": range(20, 22),
                  "sun": range(20, 22),
                  }, 
              off={
                  "mon": range(22, 24) + range(0, 20),
                  "tue": range(22, 24) + range(0, 20),
                  "wed": range(22, 24) + range(0, 20),
                  "thu": range(22, 24) + range(0, 20),
                  "fri": range(22, 24) + range(0, 20),
                  "sat": range(22, 24) + range(0, 20),
                  "sun": range(22, 24) + range(0, 20),
                  }),
    Scheduler(dev=floor_heatings.bath_room_rad, temp=(30, 30, 6, 6),
              athome={
                  "mon": range(0, 2) + range(4, 6),
                  "tue": range(0, 2) + range(4, 6),
                  "wed": range(0, 2) + range(4, 6),
                  "thu": range(0, 2) + range(4, 6),
                  "fri": range(0, 2) + range(4, 6),
                  "sat": range(0, 2) + range(4, 6),
                  "sun": range(0, 2) + range(4, 6),
                  }, 
              off={
                  "mon": range(2, 4) + range(6, 24),
                  "tue": range(2, 4) + range(6, 24),
                  "wed": range(2, 4) + range(6, 24),
                  "thu": range(2, 4) + range(6, 24),
                  "fri": range(2, 4) + range(6, 24),
                  "sat": range(2, 4) + range(6, 24),
                  "sun": range(2, 4) + range(6, 24),
                  }),
    ]


schedulers = schedulers_winter

def main(*arg, **kwargs):
    day, month, date, time_now, year = time.ctime().lower().split()
    hour = int(time_now.split(":")[0])

    for sched in schedulers:
        sched.execute(day, hour)


if __name__ == '__main__':
    for i in range(3):
        main()
