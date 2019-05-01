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

        if day in self.away_time and hour in self.away_time[day]:
            self.dev.execute_op("on", "away", *self.temp)
        
        if day in self.off_time and hour in self.off_time[day]:
            self.dev.execute_op("off", "normal", *self.temp)


schedulers = [
    Scheduler(dev=floor_heatings.cabinet_fh, temp=(23, 23, 20, 20),
              athome={
                  "mon": (6, 18),
                  "tue": (6, 18),
                  "wed": (6, 18),
                  "thu": (6, 18),
                  "fri": (6, 18),
                  "sat": (8,),
                  "sun": (8,),
                  }, 
              away={
                  "mon": (0, 9),
                  "tue": (0, 9),
                  "wed": (0, 9),
                  "thu": (0, 9),
                  "fri": (0, 9),
                  "sat": (0,),
                  "sun": (0,),
                  }),
    Scheduler(dev=floor_heatings.cabinet_rad, temp=(6, 6, 6, 6),
              off={
                  "mon": (1, ),
                  "tue": (1, ),
                  "wed": (1, ),
                  "thu": (1, ),
                  "fri": (1, ),
                  "sat": (1, ),
                  "sun": (1, ),
                  }),
    Scheduler(dev=floor_heatings.living_room_rad, temp=(23, 23, 20, 20),
              athome={
                  "mon": (6, 18),
                  "tue": (6, 18),
                  "wed": (6, 18),
                  "thu": (6, 18),
                  "fri": (6, 18),
                  "sat": (8,),
                  "sun": (8,),
                  }, 
              away={
                  "mon": (0, 9),
                  "tue": (0, 9),
                  "wed": (0, 9),
                  "thu": (0, 9),
                  "fri": (0, 9),
                  "sat": (0,),
                  "sun": (0,),
                  }),
    Scheduler(dev=floor_heatings.living_room_vent, temp=(6, 6, 6, 6),
              off={
                  "mon": (1, ),
                  "tue": (1, ),
                  "wed": (1, ),
                  "thu": (1, ),
                  "fri": (1, ),
                  "sat": (1, ),
                  "sun": (1, ),
                  }),
    Scheduler(dev=floor_heatings.vault_rad, temp=(20, 20, 18, 18),
              athome={
                  "mon": (6, 18),
                  "tue": (6, 18),
                  "wed": (6, 18),
                  "thu": (6, 18),
                  "fri": (6, 18),
                  "sat": (8,),
                  "sun": (8,),
                  }, 
              away={
                  "mon": (0, 9),
                  "tue": (0, 9),
                  "wed": (0, 9),
                  "thu": (0, 9),
                  "fri": (0, 9),
                  "sat": (0,),
                  "sun": (0,),
                  }),
    Scheduler(dev=floor_heatings.hall_fh, temp=(23, 23, 20, 20),
              athome={
                  "mon": (6, 18),
                  "tue": (6, 18),
                  "wed": (6, 18),
                  "thu": (6, 18),
                  "fri": (6, 18),
                  "sat": (8,),
                  "sun": (8,),
                  }, 
              away={
                  "mon": (0, 9),
                  "tue": (0, 9),
                  "wed": (0, 9),
                  "thu": (0, 9),
                  "fri": (0, 9),
                  "sat": (0,),
                  "sun": (0,),
                  }),
    Scheduler(dev=floor_heatings.living_room_fh, temp=(23, 23, 20, 20),
              athome={
                  "mon": (6, 18),
                  "tue": (6, 18),
                  "wed": (6, 18),
                  "thu": (6, 18),
                  "fri": (6, 18),
                  "sat": (8,),
                  "sun": (8,),
                  }, 
              away={
                  "mon": (0, 9),
                  "tue": (0, 9),
                  "wed": (0, 9),
                  "thu": (0, 9),
                  "fri": (0, 9),
                  "sat": (0,),
                  "sun": (0,),
                  }),
    Scheduler(dev=floor_heatings.bad_room_rad, temp=(23, 23, 23, 23),
              athome={
                  "mon": (6, 18),
                  "tue": (6, 18),
                  "wed": (6, 18),
                  "thu": (6, 18),
                  "fri": (6, 18),
                  "sat": (8,),
                  "sun": (8,),
                  }, 
              away={
                  "mon": (0, 9),
                  "tue": (0, 9),
                  "wed": (0, 9),
                  "thu": (0, 9),
                  "fri": (0, 9),
                  "sat": (0,),
                  "sun": (0,),
                  }),
    Scheduler(dev=floor_heatings.bad_room_vent, temp=(22, 22, 22, 22),
              athome={
                  "mon": (6,),
                  "tue": (6,),
                  "wed": (6,),
                  "thu": (6,),
                  "fri": (6,),
                  "sat": (8,),
                  "sun": (8,),
                  }, 
              off={
                  "mon": (22, ),
                  "tue": (22, ),
                  "wed": (22, ),
                  "thu": (22, ),
                  "fri": (22, ),
                  "sat": (22, ),
                  "sun": (22, ),
                  }),
    Scheduler(dev=floor_heatings.child_rad, temp=(22, 22, 22, 22),
              athome={
                  "mon": (6, 18),
                  "tue": (6, 18),
                  "wed": (6, 18),
                  "thu": (6, 18),
                  "fri": (6, 18),
                  "sat": (8,),
                  "sun": (8,),
                  }, 
              away={
                  "mon": (0, 9),
                  "tue": (0, 9),
                  "wed": (0, 9),
                  "thu": (0, 9),
                  "fri": (0, 9),
                  "sat": (0,),
                  "sun": (0,),
                  }),
    Scheduler(dev=floor_heatings.bath_room_fh, temp=(23, 23, 20, 20),
              athome={
                  "mon": (6, 18),
                  "tue": (6, 18),
                  "wed": (6, 18),
                  "thu": (6, 18),
                  "fri": (6, 18),
                  "sat": (8,),
                  "sun": (8,),
                  }, 
              away={
                  "mon": (0, 9),
                  "tue": (0, 9),
                  "wed": (0, 9),
                  "thu": (0, 9),
                  "fri": (0, 9),
                  "sat": (0,),
                  "sun": (0,),
                  }),
    Scheduler(dev=floor_heatings.bath_room_rad, temp=(6, 6, 6, 6),
              athome={
                  "mon": (6, 18),
                  "tue": (6, 18),
                  "wed": (6, 18),
                  "thu": (6, 18),
                  "fri": (6, 18),
                  "sat": (8,),
                  "sun": (8,),
                  }, 
              away={
                  "mon": (0, 9),
                  "tue": (0, 9),
                  "wed": (0, 9),
                  "thu": (0, 9),
                  "fri": (0, 9),
                  "sat": (0,),
                  "sun": (0,),
                  }),
    ]


def main(*arg, **kwargs):
    day, month, date, time_now, year = time.ctime().lower().split()
    hour = int(time_now.split(":")[0])

    for sched in schedulers:
        sched.execute(day, hour)


if __name__ == '__main__':
    for i in range(3):
        main()
