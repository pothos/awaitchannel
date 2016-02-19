"""
Extends the synchronisation objects of asyncio (e.g. Lock, Event, Condition, Semaphore, Queue) with Channels like in Go.
Channels can be used for asynchronous or synchronous message exchange.
select() can be used to react on finished await-calls and thus also on sending or receiving with channels.
The helper go() provides a simple way to schedule the concurrent functions in an event loop of a different thread.

Note that you need to pass the .loop attribute of this module when you are using functions provided by asyncio yourself.
"""
import asyncio


class Chan:
  """
  Go-style channel with await send/recv
  can also be used as an iterator which is calling recv() until a ChannelClosed exception occurs
  """
  q = None  # data channel
  x = None  # sync channel for size=0
  size = None
  is_closed = False
  close = "{}{}".format(hash("Chan.closed"), "Chan.closed")  # magic string as last element
  def __init__(self, size=0):
    """size 0 or None indicates a blocking channel (handshake)
    size -1 indicates an unlimited buffer size
    otherwise send will block when buffer size is reached"""
    if size == 0:
      self.q = asyncio.Queue(1, loop=loop)
      self.x = asyncio.Queue(1, loop=loop)
    elif size == -1:
      self.q = asyncio.Queue(0, loop=loop)
    else:
      self.q = asyncio.Queue(size, loop=loop)
    self.size = size

  @asyncio.coroutine
  def close(self):
    """closes the channel which leads to a failure at the recv side and disallows further sending"""
    self.is_closed = True
    yield from self.q.put(self.close)

  @asyncio.coroutine
  def send(self, item):
    """blocks if size=0 until recv is called
    blocks if send was used <size> times without a recv
    blocks never for size=-1"""
    if self.is_closed:
      raise ChannelClosed
    yield from self.q.put(item)
    if self.size == 0:
      yield from self.x.get()

  def send_ready(self):
    return not self.q.full()

  def recv_ready(self):
    return not self.q.empty()

  @asyncio.coroutine
  def recv(self):
    """blocks until something is available
    fails if channel is closed"""
    if self.is_closed and self.q.empty():
      self.put_nowait(self.close)
      raise ChannelClosed
    g = yield from self.q.get()
    if self.is_closed and self.q.empty() and g == self.close:
      self.q.put_nowait(self.close)  # push back
      raise ChannelClosed
    if self.size == 0:
      yield from self.x.put(True)
    return g

  async def __aiter__(self):
    return self

  async def __anext__(self):
    try:
      return await self.recv()
    except ChannelClosed:
      raise StopAsyncIteration

class ChannelClosed(Exception):
  pass


### select on await events

async def wrap_future(e, f):
  return e, await f

class SelectTasks:
  """helper class used for (pending) await-tasks monitored by select()"""
  tasks = []
  completed = []
  def __init__(self, futures_list=None, already_running=False, completed=[]):
    if futures_list and not already_running:
      self.extend(futures_list)
    elif futures_list and already_running:
      self.tasks = list(futures_list)
    else:
      self.tasks = []
    self.completed = completed

  def append(self, a):
    e, f = a
    self.tasks.append(wrap_future(e, f))

  def extend(self, futures_list):
    self.tasks.extend([wrap_future(e, f) for e, f in futures_list])

  def __bool__(self):
    return bool(self.tasks) or bool(self.completed)

  def __len__(self):
    return len(self.tasks) + len(self.completed)


@asyncio.coroutine
def select(futures_list):
  """
  parameter: select on a list of identifier-await-tuples like ['r', c.recv()), (c, c.send(2))]
  returns: a tuple consiting of an identifier-result-tuple like ('r', 7) or (c, None) and
  a special list object of pending tasks which can be directly used for the next select call or even expanded/appended on before

  Be aware that the results are internally buffered when more complete at the same time and thus the logical ordering can be different.
  """
  if type(futures_list) is not SelectTasks:
    futures_list = SelectTasks(futures_list)
  if futures_list.completed:
    result = futures_list.completed.pop()
    return result, futures_list
  done, running = yield from asyncio.wait(futures_list.tasks, return_when=asyncio.FIRST_COMPLETED, loop=loop)
  result = done.pop().result()
  results = [r.result() for r in done]
  return result, SelectTasks(running, already_running=True, completed=results)


# short helper functions

import threading
import atexit

count_tasks = 0
def counter(i=0):
  global count_tasks
  count_tasks += i
  return count_tasks

loop = asyncio.get_event_loop()  # This thread's loop will be used - unfortunately needs to be passed
                                 # everywhere as the execution takes place in a background thread.
                                 # If you do only use Chan() and select() and not go(), you can
                                 # omit this by forcing it to None if it causes trouble.
atexit.register(loop.close)

def go(f, *args, **kwargs):
  """schedule an async function on the asyncio event loop of the worker thread"""
  async def cleanup():
    x = await f(*args, **kwargs)
    counter(-1)
    if counter() == 0:
      loop.call_soon(loop.stop)
    return x
  r = asyncio.run_coroutine_threadsafe(cleanup(), loop)
  counter(+1)
  if not loop.is_running():
    threading.Thread(name='eventloop-worker', target=loop.run_forever).start()
  return r
