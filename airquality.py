#!/usr/bin/env python3

import logging
import os
import time

import boto3
import serial

VERSION_ID = 'v0.2'
GROUP_ID = os.getenv('AQ_GROUP_ID', VERSION_ID)

logger = logging.getLogger(__name__)

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName='airquality.fifo')


ser = serial.Serial('/dev/ttyUSB0')

while True:
    time.sleep(10 - time.time() % 10)  # Run every 10 seconds
    timestamp = str(int(time.time()))
    data = []
    for index in range(0,10):
        datum = ser.read()
        data.append(datum)

    pmtwofive = int.from_bytes(b''.join(data[2:4]), byteorder='little') / 10
    pmten = int.from_bytes(b''.join(data[4:6]), byteorder='little') / 10

    msg = '{},{},{}'.format(timestamp, pmtwofive, pmten)
    logger.info(msg)
    response = queue.send_message(
        MessageBody=msg,
        MessageGroupId=GROUP_ID,
        MessageDeduplicationId=timestamp
    )
    failed = response.get('Failed')
    if failed:
        logger.error('Failed: {failed}')