#!/usr/bin/env python3.5
import time
from awaitchannel import Chan, select, go, ChannelClosed, loop

c = Chan()  # synchronous communication

async def give(v):
  for i in range(0, 10):
    await c.send(v + str(i))
  print('give', v, 'done')

async def consume(ID):
  async for v in c:
    print(ID, 'got', v)
    await loop.run_in_executor(None, time.sleep, 0.1)  # sleep because python does not guarantee fairness
  print('consume', ID, 'done')

go(consume, 'A')
go(consume, 'B')
r1 = go(give, 'x')
go(consume, 'C')
go(consume, 'D')
r2 = go(give, 'y')
r3 = go(give, 'z')
r1.result()  # wait for sending to be complete
r2.result()
r3.result()
go(c.close)  # cleanup pending consume iters of 'async for' (i.e. await c.recv)
print("closed")
