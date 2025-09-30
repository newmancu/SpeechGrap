#!/bin/bash
sudo systemctl stop linux_display.service && echo "stoped"

sudo chmod +x ./target/release/linux_display
cp ./target/release/linux_display ./deploy
sudo cp ./target/release/linux_display /usr/local/bin/linux_display

sudo cp ./deploy/linux_display.service /etc/systemd/system/linux_display.service

sudo systemctl daemon-reload
sudo systemctl enable linux_display.service
sudo systemctl start linux_display.service

sudo systemctl status linux_display.service
