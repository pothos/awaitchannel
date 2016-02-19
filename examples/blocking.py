#!/usr/bin/env python3.5

import time, random
from awaitchannel import Chan, select, go, ChannelClosed, loop

def blocking_sleep():
  i = random.randint(1, 3)
  print("sleeping for", i, "seconds")
  time.sleep(i)
  return i

async def count_sleeping():
  i = 0
  for _ in range(3):
    i += await loop.run_in_executor(None, blocking_sleep)
  print("slept", i, "seconds in total")

async def count_concurrent_sleeping():
  futures = []
  for _ in range(3):  # spawn in parallel
    futures.append(loop.run_in_executor(None, blocking_sleep))  # without await on the future
  s = 0
  for f in futures:
    s += await f
  print("slept concurrently", s, "seconds in total")

print("wait for each blocking function to finish before the next one starts")
go(count_sleeping).result()  # usage of result() forces to wait for count_sleeping to finish
print()
print("wait for each blocking function at the end")
go(count_concurrent_sleeping)
