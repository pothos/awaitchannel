#!/usr/bin/env python3.5

from awaitchannel import Chan, select, go, ChannelClosed

async def generate(ch):
  # Send the sequence 2, 3, 4, ... to channel ch.
  for i in range(2, 300):
    await ch.send(i)  # Send i to channel ch.
  await ch.close()

async def filter(in_c, out_c, prime):
  # Copy the values from channel in to channel out,
  # removing those divisible by prime.
  async for i in in_c:  # (will stop on ChannelClosed)
    # Receive value of new variable i from in.
    if i % prime != 0:
      await out_c.send(i)  #  Send i to channel out.
  await out_c.close()

# The prime sieve: Daisy-chain filter processes together.
async def main():  # (defined as coroutine as it uses await)
  ch = Chan()  # Create a new channel.
  go(generate, ch)  # Start generate() as a coroutine.
  while True:
    try:  # (could also be written like above, with async for)
      prime = await ch.recv()
    except ChannelClosed:
      break
    print("{} ".format(prime), end='', flush=True)
    ch1 = Chan()
    go(filter, ch, ch1, prime)
    ch = ch1
go(main)
