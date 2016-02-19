#!/usr/bin/env python3.5

from awaitchannel import Chan, select, go, ChannelClosed


c = Chan()
go(c.send, 4)

x = go(c.recv).result()
print(x)

