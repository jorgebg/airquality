#!/usr/bin/env python3

from datetime import datetime
import logging
import os
import sys

import boto3

logging.basicConfig(level=os.getenv('LOGGING_LEVEL', 'INFO'))

logger = logging.getLogger(__name__)

def message_date(message):
    return datetime.fromtimestamp(int(message.body.split(',')[0]))

def run(command):
    errno = os.system(command)
    if errno != 0:
        raise RuntimeError(f"Command {command} returned {errno}")


queue = boto3.resource('sqs').get_queue_by_name(QueueName='airquality.fifo')


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
