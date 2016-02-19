#!/usr/bin/env python3.5

from awaitchannel import Chan, select, go


c = Chan()
go(c.send, 4)

x = go(c.recv).result()
print(x)

