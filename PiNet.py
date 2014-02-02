#!/usr/bin/python

"""
    Author: 
	github: @luke666
	twitter: @luke__666

    PiNet checks the network connection of a Raspberry Pi by sending ICMP echo requests to IP addresses in Internet and WAN
    and then blinking/lighting one of the three LEDs according to reachable area / address.

    The LEDs are connected to Raspberry Pi GPIO pins 11 (GPIO17), 13 (GPIO 27 on board rev. 2) and 15 (GPIO 22).
    Each LED is then connected to pin 14 (GND) over an 820R resistor. Schemes and instructions can be found on Internet.  

    If the script can reach IP addresses defined in "netIP" list (or at least one of them), the green LED blinks for
    each successfully reached IP address and then remains lit for defined "timeOut" until next check.

    If none of "netIP" addresses can be reached, the script tries to reach "wanIP" addresses. If the script can reach them
    (or at least one of them), the yellow LED blinks for each successfully reached IP address and then remains lit
    for defined "timeOut" until next check.

    If the script can't reach any "netIP" and "wanIP" address the red LED lights for defined "timeOut" until next check.
"""

import os
import time
import signal
import sys
import RPi.GPIO as GPIO


### ping command, sends three pings
pingCmd = "ping -c 3 "


### Edit the IP addresses as needed
netIP = ["8.8.8.8", "208.67.222.222", "77.75.72.3"]     # These are: Google DNS, OpenDNS DNS, and www.seznam.cz
wanIP = ["10.107.4.1", "10.107.0.5", "89.248.240.28"]   # These are hkfree.org DNS, igw1.hkfree.org, igw.hkfree.org


### Time in seconds between each check: 60 = 1 minute, 300 = 5 minutes, 600 = 10 minutes etc.
timeOut = 300


### Functions


def pingProbe(area):
    """ pings all IP addresses from given area and returns score of successfully reached IPs """
    score = len(area)   # Score is the amount of IP addresses defined in area. We lower the score each time we don't get a reply from IP.
    for ip in area:     # Ping each IP in area. Successful ping returns 0, failed ping lowers the score.
        if os.system(pingCmd + ip) != 0:
            score = score - 1
    return score


def blinkLED(color, score):
    """ blinks the LED according to the color we pick in the program cycle and score returned by pingProbe() """

    if color == "green":
        for i in range(0,score):
            GPIO.output(15, True)
            time.sleep(0.3)
            GPIO.output(15, False)
            time.sleep(0.8)
        GPIO.output(15, True)

    elif color == "yellow":
        for i in range(0,score):
            GPIO.output(13, True)
            time.sleep(0.3)
            GPIO.output(13, False)
            time.sleep(0.8)
        GPIO.output(13, True)

    else:
        if color == "red":
            GPIO.output(11, True)


def lightsDown():
    """ switch off all three LEDs """
    GPIO.output(11, False)
    GPIO.output(13, False)
    GPIO.output(15, False)


### check if we have at least two IPs defined

if len(netIP) == 0:
    print("Please define at least one IP in netIP list")
    sys.exit()

elif len(wanIP) == 0:
    print("Please define at least one IP in wanIP list.") 
    sys.exit()

### Initialize GPIO and pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)

while True:

    try:
        lightsDown()

        netTest = pingProbe(netIP)
        if netTest != 0:
            blinkLED("green", netTest)

        else:
            wanTest = pingProbe(wanIP)
            if wanTest != 0:
                blinkLED("yellow", wanTest)
            else:
                blinkLED("red", "error")

        time.sleep(timeOut)

    except (KeyboardInterrupt, SystemExit):
        print("Exiting...")
        lightsDown()
        GPIO.cleanup()
        sys.exit()