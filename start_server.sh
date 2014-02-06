#!/bin/bash
killall redsibd
killall sib-tcp
redsibd &
sleep 2
sib-tcp &
python initializer.py
# python monopolym3.py
