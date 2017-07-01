#!/usr/bin/env python3.5

from awaitchannel import Chan, select, go, ChannelClosed


async def give(start, end, c):
  for i in range(start, end):
    await c.send(i)
  await c.close()
  print("give DONE")

async def consume_iter(t, c):
  async for i in c:
    print(t, i)
  print("consume_iter DONE")

async def consume(t, c):
  while True:
    try:
      x = await c.recv()
    except:
      break
    print(t, x)
  print("consume DONE")

c = Chan()
go(give, 1, 21, c)
go(consume, "A", c)
go(consume_iter, "B", c)
go(consume, "C", c)

async def selectexample():
  s = Chan()
  d = Chan(1)
  cases = [('rec', s.recv()), ('rec', s.recv()), ('snd', s.send(3)), (d, d.send(1))]
  while cases:
    (id_, r), cases = await select(cases)
    if id_ == 'rec':
      print("received", r)
      if r == 3:
        cases.append(('snd', s.send(5)))  # fill for other s.recv
    elif id_ == 'snd':
      print("send finished")
    elif id_ == d:
      print ("D", await d.recv())
      await d.send(5)
      print("filled D again")
  print("select DONE")

go(selectexample)
