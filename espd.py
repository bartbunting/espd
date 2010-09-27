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

def set_punctuation(punctlevel):
    if punctlevel == "all":
        client.set_punctuation(speechd.PunctuationMode.ALL)
    elif punctlevel == "some":
        client.set_punctuation(speechd.PunctuationMode.SOME)
    elif punctlevel == "none":
        client.set_punctuation(speechd.PunctuationMode.NONE)
    else:
        log ("unimplemented punctuation level " + punctlevel)


# Main



client = speechd.SSIPClient('espd')
#     client.set_output_module('festival')
client.set_language('en')
client.set_punctuation(speechd.PunctuationMode.SOME)
client.set_cap_let_recogn("icon")
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

    # This tests if we have a q command if we received the entire
    # data.  As the data to the q command is delimited with left and
    # right braces if the line doesn't end in a brace we still have
    # more to read.
    if cmd == 'q':
        if not re.match(r"^{.*}$", data):
            log("Unfinished command detected")
            # read more lines as this command isn't finished yet
            while(1):
                line = sys.stdin.readline().rstrip()
                data = data + " " + line
                # Break out of this loop if the line ends in a right brace as this signals the end of this command
                if re.match(r".*}$", line):
                    break
    log ("cmd " + cmd + " data " + data)

    # hack needs fixing.  Skip commands which are just a right brace,
    # This happens as braces are used as delimiters for data in some
    # commands sent from emacs.  If the data contains a trailing
    # newline we read it as a new line and hence the right brace
    # becomes the cmd for the next line.
    if cmd == '':
        log("skipping empty cmd")
        continue

    # remove leading left brace if it exists
    data = re.sub(r"^{", "", data)
    # remove trailing right brace if it exists
    data = re.sub(r"}$", "", data)
    # remove dectalk control codes 
    data = re.sub(r"\[ ?:.*?\]", "", data)
    log( "data now '" + data + "'")

    # This long if elif else block should probably be replaced by
    # something nicer.  Right now I'm not sure what that is.
    if cmd == "q":
        client.speak(data)
    elif cmd == "tts_say":
        client.speak(data)
    elif cmd == "d":
        # not implimented yet, in tcl this function speaks the
        # currently queued text.  At the moment we are sending stuff
        # directly to speech dispatcher.  This may change.
        continue
    elif cmd == "s":
        log( "stopping")
        client.stop()
    elif cmd == "tts_set_speech_rate":
        set_rate(data)
    elif cmd == "tts_set_punctuations":
        set_punctuation(data)
    elif cmd == "l":
        log( "letter " + data)
        client.char(data)
        # x is for exit.  Not used by emacspeak, helpful for testing.
    elif cmd == "x":
        client.close()
        exit()
    # Log any unimplemented commands
    else:
        log("Unimplemented: " + line)
# close our connection to speech dispatcher although theoretically
client.close()
