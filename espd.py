#!/usr/bin/python
import os
import sys
import speechd
from collections import deque
import re
import select 
#import fcntl

# functions

# Write a line to a fixed log file and close the file after writing
# not very efficient but helpful for my debugging
def log(data):
    log_file = open("/tmp/espd.log", "a")
    log_file.write(data + "\n")
    log_file.close()

# Takes the speech rate as a string and converts to int and sets the rate 
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

def tts_capitalize(val):
    log("Setting capitalization to " + val)
    v = int(val)
    if v == 0:
        client.set_cap_let_recogn("none")
    else:
        client.set_cap_let_recogn("icon")
    
def         tts_sync_state(punct, capitalize, allcaps, splitcaps, rate):
    log("punctuation: " + punct)
    log("capitalize: " + capitalize)
    log("allcaps: " + allcaps)
    log("splitcaps: " + splitcaps)
    log("rate: " + rate)
    set_punctuation(punct)
    tts_capitalize(capitalize)
    set_rate(rate)


def clean(data):
    # remove leading left brace if it exists
    data = re.sub(r"^{", "", data)
    # remove trailing right brace if it exists
    data = re.sub(r"}$", "", data)
    # remove dectalk control codes 
    data = re.sub(r"\[ ?:.*?\]", "", data)
    return data

# take action on a command sent from emacspeak
# This is basically a big if/elif/else statement block
def process_cmd(cmd, data):
    log("process_cmd")
    # This long if elif else block should probably be replaced by
    # something nicer.  Right now I'm not sure what that is.
    if cmd == "q":
        log("queueing " +  data)
        queue.appendleft(data)
    elif cmd == "tts_say":
        client.speak(clean(data))
    elif cmd == "d":
        # this command speaks the currently queued text.
        while(len(queue) > 0):
            log("q length: " + str(len(queue)))
            i = queue.pop()
            log("i: " +  i)
            i = clean(i)
            log("ic: " +  i)
            client.set_priority(speechd.Priority.MESSAGE)
            client.speak(i)
    elif cmd == "s":
        log( "stopping")
        client.stop()
    elif cmd == "tts_set_speech_rate":
        set_rate(data)
    elif cmd == "tts_set_punctuations":
        set_punctuation(data)
    elif cmd == "l":
        log( "letter " + data)
        client.char(clean(data))
    elif cmd == "tts_sync_state":
        log("tts_sync disabled")
        #punct, capitalize, allcaps, splitcaps, rate = re.split("\s+", data)
        #tts_sync_state(punct, capitalize, allcaps, splitcaps, rate)
        # x is for exit.  Not used by emacspeak, helpful for testing.
    elif cmd == "x":
        client.close()
        exit()
    # Log any unimplemented commands
    else:
        log("Unimplemented: " + line)

# Main
client = speechd.SSIPClient('espd')
#     client.set_output_module('festival')
client.set_language('en')
client.set_punctuation(speechd.PunctuationMode.SOME)
client.set_priority(speechd.Priority.MESSAGE)
client.speak("Emacspeak Speech Dispatcher!")


queue = deque([])               # queue of things to speak

# Main loop
read_partial_cmd = 0            # flag to indicate if we have only read a partial command so far

#flags = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
#fcntl.fcntl(sys.stdin, fcntl.F_SETFL, flags | os.O_NONBLOCK)

input = [sys.stdin] 
while 1:

    log("select")
    [inputready,outputready,exceptready] = select.select(input,[],[]) 
    #print "inputready: ", inputready
    if sys.stdin in inputready:
        #line = sys.stdin.readline().rstrip()
        line = sys.stdin.readline()
        #line = sys.stdin .read(2048)
        log("original: " + line)
        log("partial " + str(read_partial_cmd))
        # if we already have a partial command then append the data
        if read_partial_cmd == 1:
            log("appending '" + line + "' to data")
            data = data + " " + line
            if re.match(r".*}$", line):
                # if the line ends in a right brace we have got the entire cmd
                log("found end of cmd marker")
                read_partial_cmd = 0
                process_cmd(cmd, data)
        else:
            # split out the command from the data 
            if re.search("\s+", line):
                cmd, data = re.split("\s+", line, 1)
            else:
                cmd = line
                data = ""

            # This tests if we have a q command if we received the
            # entire data.  As the data to the q command is delimited
            # with left and right braces if the line doesn't end in a
            # brace we still have more to read.
            if cmd == 'q':
                if not re.match(r"^{.*}$", data):
                    log("partial data detected")
                    read_partial_cmd = 1
                    continue

            log( "cmd: " + cmd + " data now '" + data + "'")
            process_cmd(cmd, data)
    # If we fell through because of a timeout
    else:
        log("timeout")
        #print "timeout"


# close our connection to speech dispatcher although theoretically
client.close()

