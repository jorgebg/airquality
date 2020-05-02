#!/usr/bin/env python3

import json
import logging
import os
import subprocess
import sys
import time
import urllib.request
from collections import OrderedDict
from datetime import datetime
from os import path

import boto3
import pytz

logging.basicConfig(level=os.getenv('LOGGING_LEVEL', 'INFO'))

logger = logging.getLogger(__name__)

def message_date(message):
    return datetime.fromtimestamp(int(message.body.split(',')[0]))

def run(command):
    errno = os.system(command)
    if errno != 0:
        raise RuntimeError(f"Command {command} returned {errno}")


queue = boto3.resource('sqs').get_queue_by_name(QueueName='airquality.fifo')

logger.info('Fetching monitor station data')
os.chdir('.state')
with open('data.csv', 'a+', buffering=1) as csvfile:  # Line buffered
    total = 0
    while True:
        messages = queue.receive_messages(
            MaxNumberOfMessages=10,
        )
        if messages:
            info = '{} messages found from {} to {}'.format(len(messages), message_date(messages[0]), message_date(messages[-1]))
            logger.info(info)
            entries = []
            for message in messages:
                logger.info(f'message: {message.body}')
                csvfile.write(message.body + "\n")  # comma-separated list
                entries.append({
                    'Id': message.message_id,
                    'ReceiptHandle': message.receipt_handle,
                })
            run('git add .')
            run(f'git commit -m"{info}"')
            run('git push')
            queue.delete_messages(
                Entries=entries,
            )
            total += len(messages)
        else:
            logger.info('No messages found.')
            if total == 0:
                sys.exit(1)  # Station has stopped working
            break


# Download data from goverment station
tz = pytz.timezone('Europe/Madrid')

if path.exists('data_gov.csv'):
    last_line = subprocess.check_output(['tail', '-1', 'data_gov.csv'])
    last_ts = int(last_line.decode().split(',')[0])
else:
    last_ts = 0
last_date = datetime.fromtimestamp(last_ts, tz=tz)

logger.info(f'Fetching goverment station data since ${last_date}')

url = 'https://idem.madrid.org/geoserver3/proxy?https://gestiona3.madrid.org/mova_rest_servicios/v1/consultas/do?&idApp=5&idConsulta=sigi_azul_semana_particula&first=1&limit=1440&pq1=I:11&pq2=I:4'
try:
    with urllib.request.urlopen(url) as req, open('data_gov.csv', 'a+', buffering=1) as csvfile:
        content = json.load(req)
        rows = []
        for obj in content:
            obj_date = datetime.strptime(obj.get('FECHA'), "%d-%m-%Y %H:%M:%S").astimezone(tz)
            if obj.get('INDICADOR') == 'PM10':
                rows.append((int(time.mktime(obj_date.timetuple())), '', '{0:.2f}'.format(obj.get("VALOR"))))
        rows.sort(key=lambda row: row[0])  # Order by date
        for row in rows:
            if row[0] > last_ts:
                row_str = '{},{},{}'.format(*row)
                logger.info(row_str)
                csvfile.write(row_str + '\n')
except urllib.request.URLError as e:
    logger.warning(f'Unable to download data from goverment station: {e}')
