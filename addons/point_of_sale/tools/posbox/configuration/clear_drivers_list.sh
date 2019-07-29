#!/usr/bin/env bash

logger -t posbox_clear_server_configuration "Clearing the drivers list"
sudo mount -o remount,rw /
sudo rm -rf /home/pi/eagle/addons/hw_drivers/drivers/*
sudo mount -o remount,ro /
