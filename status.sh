#!/bin/bash
uptime
vcgencmd measure_temp | sed -e 's/temp=/ Temperature: /'
systemctl status modecam.service
