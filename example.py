#!/usr/bin/env python3.5

from awaitchannel import Chan, select, go


async def give(start, end, c):
  for i in range(start, end):
    await c.send(i)
  await c.close()

async def consume_iter(t, c):
  async for i in c:
    print(t, i)
  return

async def consume(t, c):
  while True:
    try:
      x = await c.recv()
    except:
      break
    print(t, x)

c = Chan()
go(give, 1, 21, c)
go(consume, "A", c)
go(consume_iter, "B", c)
go(consume, "C", c)

async def selectexample():
  s = Chan()
  d = Chan(1)
  cases = [('r', s.recv()), ('r', s.recv()), ('s', s.send(3)), (d, d.send(1))]
  while cases:
    (id_, r), cases = await select(cases)
    if id_ == 'r':
      print("received", r)
      if r == 3:
        cases.append(('s', s.send(5)))
    elif id_ == 's':
      print("send finished")
    elif id_ == d:
      print ("D", await d.recv())
      await id_.send(5)

go(selectexample)
