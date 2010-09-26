#!/usr/bin/python
import os
import sys
import speechd
from collections import deque
import re


# functions
def log(data):
    log_file = open("/tmp/espd.log", "a")
    log_file.write(data + "\n")
    log_file.close()

def set_rate(rate):
    log( "setting rate to " + rate)
    r = int(rate)
    if r > 100:
        r = 100
    if r < -100:
        r = -100

    client.set_rate(r)


# Main



client = speechd.SSIPClient('test')
#     client.set_output_module('festival')
client.set_language('en')
client.set_punctuation(speechd.PunctuationMode.SOME)
client.set_priority(speechd.Priority.MESSAGE)
client.speak("Emacspeak Speech Dispatcher!")


q = deque([])

# Main loop
while 1:
    line = sys.stdin.readline().rstrip()
    log("original: " + line)
    # split out the command from the data
    if re.search("\s+", line):
        cmd, data = re.split("\s+", line, 1)
    else:
        cmd = line
        data = ""
    log ("cmd " + cmd + " data " + data)
    # remove leading left brace if it exists
    data = re.sub(r"^{", "", data)
    # remove trailing right brace if it exists
    data = re.sub(r"}$", "", data)
    log( "data now '" + data + "'")
    data = re.sub(r"\[ ?:.*?\]", "", data)
    log( "rem dtk: '" + data + "'")
    if cmd == "q":
        client.speak(data)
    if cmd == "tts_say":


        client.speak(data)
    if cmd == "s":
        log( "stopping")
        client.stop()
    if cmd == "tts_set_speech_rate":
        set_rate(data)
    if cmd == "l":
        log( "letter " + data)
        data = re.sub("}", "", data) 
        client.char(data)
        # x is for exit.  Not used by emacspeak, helpful for testing.
    if cmd == "x":
        client.close()
        exit()

client.close()
