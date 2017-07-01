#!/usr/bin/env python3.5

from awaitchannel import Chan, select, go, ChannelClosed


c = Chan()
go(c.send, 4)  # start the send itself as coroutine

f = go(c.recv)  # start the receive as coroutine
x = f.result()
print("got", x)

