#!/usr/bin/env python3.5

from awaitchannel import Chan, select, go, run


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
  c = Chan()
  d = Chan(1)
  cases = [('r', c.recv()), ('r', c.recv()), ('s', c.send(3)), (d, d.send(1))]
  while cases:
    (id, r), cases = await select(cases)
    if id == 'r':
      print("received", r)
      if r == 3:
        cases.append(('s', c.send(5)))
    elif id == 's':
      print("send finished")
    elif id == d:
      print ("D", await d.recv())
      await id.send(5)

go(selectexample)

run()

