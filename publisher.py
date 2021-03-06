#!/usr/bin/env python3

from datetime import datetime
from decimal import Decimal, getcontext
import logging
import os
import shutil
from statistics import mean
import sys

MALFUNCTION_THRESHOLD_PM25 = 500 # Limit is 999.9
MALFUNCTION_THRESHOLD_PM10 = 500 # Limit is 1999.9

logging.basicConfig(level=os.getenv('LOGGING_LEVEL', 'INFO'))

logger = logging.getLogger(__name__)

# Copy web folder
shutil.copytree('web/', '.gh-pages/', dirs_exist_ok=True)

# Compute hourly averages
getcontext().prec = 3

def message_date(message):
    return datetime.fromtimestamp(int(message.body.split(',')[0]))

def run(command):
    errno = os.system(command)
    if errno != 0:
        raise RuntimeError(f"Command {command} returned {errno}")


class Message:

    def __init__(self, ts, pm25, pm10):
        self.ts = int(ts)
        self.pm25 = Decimal(pm25)
        self.pm10 = Decimal(pm10)

    @property
    def datetime(self):
        return datetime.fromtimestamp(int(self.ts))

    @property
    def datehour(self):
        return self.datetime.replace(minute=0, second=0, microsecond=0)

current_hour = None

with open('.state/data.csv', 'r') as datafile, open('.gh-pages/hourly.csv', 'w') as hourlyfile:
    pm25 = []
    pm10 = []
    hourlyfile.write('ts,pm25,pm10\n')
    for line in datafile:
        msg = Message(*line.split(','))
        if current_hour is None:
            current_hour = msg.datehour
        if msg.pm25 < MALFUNCTION_THRESHOLD_PM25:
            pm25.append(msg.pm25)
        if msg.pm10 < MALFUNCTION_THRESHOLD_PM10:
            pm10.append(msg.pm10)

        if msg.datehour != current_hour:
            if pm25 and pm10:
                hourlyfile.write('{},{},{}\n'.format(int(datetime.timestamp(msg.datehour)), mean(pm25), mean(pm10)))
                logger.info('{},{},{}'.format(msg.datehour, mean(pm25), mean(pm10)))
            else:
                logger.warn('No data points where found. Possible reading malfunction.')
            current_hour = msg.datehour
            pm25 = []
            pm10 = []


# Publish also collected gov data if it exists
if os.path.exists('.state/data_gov.csv'):
    with open('.state/data_gov.csv', 'r') as source_file, open('.gh-pages/data_gov.csv', 'w') as output_file:
        output_file.write('ts,pm25,pm10\n')
        output_file.write(source_file.read())
