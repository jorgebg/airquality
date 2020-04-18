# Air quality

## Architecture

SDS011 →  Raspberry Pi Zero [`airquality.py`] → AWS SQS →  GitHub Actions [`collector.py` →  `processor.py` →  `plot.py`] → GitHub Pages
  
## Installation

### Station

#### Install dependencies

```sh
pip3 install boto3 pyserial
```

Setup [AWS credencials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html).

#### Install airquality.service

Copy `airquality.py` to `/root/airquality.py`.

Copy `airquality.service` to `/etc/systemd/system/airquality.service` and then run:

```sh
systemd install airquality.service
systemctl daemon-reload
```

### Collector

Setup GitHub Actions.
