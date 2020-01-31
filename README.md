# modecam
Motion detection camera, based on Raspberry Pi

## use system.d
To start modecam directly on boot, add the following to be used with systemd

```
cp systemd/modecam.service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart modecam.service
sudo systemctl status  modecam.service
```
