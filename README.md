# awaitchannel
Go-style concurrency and channels with Python 3.5 and asyncio

Extends the synchronisation objects of asyncio (e.g. Lock, Event, Condition, Semaphore, Queue) with Channels like in Go.
Channels can be used for asynchronous or synchronous message exchange.
select() can be used to react on finished await-calls and thus also on sending or receiving with channels.
The helper go() provides a simple way to schedule the concurrent functions in an event loop of a different thread.

    from awaitchannel import Chan, select, go, ChannelClosed, loop
    
    c = Chan()  # synchronous communication
    
    async def give(v):
      for i in range(0, 10):
        await c.send(v + str(i))
    
    async def consume(ID):
      async for v in c:
        print(ID, 'got', v)
    
    go(consume, 'A')
    go(consume, 'B')
    r1 = go(give, 'x')
    go(consume, 'C')
    r2 = go(give, 'y')
    # …
    r1.result()  # wait for sending to be complete
    r2.result()
    go(c.close)  # cleanup pending consume iters of 'async for' (i.e. await c.recv)

Chan(size=0): Go-style channel with await send/recv, can also be used as an iterator which is calling recv() until a ChannelClosed exception occurs,
size 0 indicates a synchronous channel (handshake), size -1 indicates an unlimited buffer size, otherwise send will block when buffer size is reached

@asyncio.coroutine
chan.close() closes the channel which leads to a failure at the recv side if empty and disallows further sending,

@asyncio.coroutine
chan.send(item) async-blocks if size=0 until there is a recv and this send operation was chosen, blocks if send was used <size> times without a recv, blocks never for size=-1,

chan.send_ready() and .recv_ready() are non-blocking testers,

@asyncio.coroutine
chan.recv() async-blocks until something is available and fails if channel is closed after all is processed



@asyncio.coroutine
select(futures_list): parameter: select on a list of identifier-await-tuples like ['r', c.recv()), (c, c.send(2))]

Returns a tuple consiting of an identifier-result-tuple like ('r', 7) or (c, None) and a special list object of pending tasks which can be directly used for the next select call or even expanded/appended on before.
Be aware that the results are internally buffered when more complete at the same time and thus the logical ordering can be different.


g(f, *args, **kwargs): schedule an async function on the asyncio event loop of the worker thread

Returns a concurrent.future which has a (non-await, but normal) blocking .result() method to wait until the result of f() is returned.


To run a blocking function in a background thread and get an awaitable future for it, use the run_in_executor method of the loop:

    f = loop.run_in_executor(None, normal_longrunning_function)
    res = await f

Note that you need to pass the .loop attribute of this module when you are using functions provided by asyncio yourself.


Run an example:

    PYTHONPATH=. examples/sieve.py
