# Air quality monitoring station

## Architecture

| Monitoring Station         | → | Message Queue | → | Data Collector | → | Data Publisher | → | Static Website |
| -                          | - | -             | - | -              | - | -              | - | -              |
| Raspberry Pi Zero + SDS011 |   | AWS SQS       |   | GitHub Actions |   | GitHub Actions |   | GitHub Pages   |

1. The Monitoring Station reads PM2.5 and PM10 from the sensor and sends the metrics to the Message Queue.
2. These messages are collected by the Data Collector.
3. The Data Publisher computes the hourly averages and publishes the data as a static website on GitHub Pages.

## Components setup

### Message Queue

Create an account in AWS and:

1. Create a **[SQS FIFO queue](console.aws.amazon.com/sqs)** named `airquality.fifo`.
2. Create an [user](console.aws.amazon.com/iam) for the **monitor** and give it the following permissions:
    * `SQS:SendMessage`
    * `SQS:GetQueueUrl`
3. Create an [user](console.aws.amazon.com/iam) for the **collector** and give it the following permissions:
    * `SQS:DeleteMessage`
    * `SQS:GetQueueUrl`
    * `SQS:ReceiveMessage`


### Monitoring Station

Composed by [SDS011](http://inovafitness.com/en/a/chanpinzhongxin/95.html) and [Raspberry Pi Zero](https://www.raspberrypi.org/products/raspberry-pi-zero-w/) with a Debian-based distribution (I use [DietPi](https://dietpi.com/)).

1. Setup AWS credentials
    * Setup monitor [AWS credencials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html) for the monitor IAM.

2. Install dependencies
    * Run `pip3 install boto3 pyserial`

3. Install the service
    * Copy `monitor/airquality.py` to `/root/airquality.py`.
    * Copy `monitor/airquality.service` to `/etc/systemd/system/airquality.service`.
    * Run `systemd install airquality.service && systemctl daemon-reload`

It sends a message every 10 seconds, so it fits AWS SQS free tier.

### Data Collector

It collects the data sent to the queue every 15 minutes and stores it in a git branch named `state`. The branch must be checked out as a git worktree under `.state` folder.

It's implemented on GitHub actions. Setup the following [secrets](https://help.github.com/en/actions/configuring-and-managing-workflows/creating-and-storing-encrypted-secrets):
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

### Data Publisher

It computes the hourly averages and publishes the results as a static website on GitHub Pages. The data and the website are stored into a branch named `gh-pages`. The branch must be checked out as a git worktree under `.gh-tree` folder.

The chart is built with [Plotly](https://plotly.com/javascript/).

## Git worktrees

Collected and published data are stored on different branches that are managed as [git worktrees](https://git-scm.com/docs/git-worktree). They are handled by [stateful-action](/jorgebg/stateful-action) on the GitHub workflow.