"""Show a self-repeating thrading.time that can be canceled externally."""


"""Notes:
   
       Return value from hello has no imact on running.
       
       Thread does not autorepeat. Here a new thread is created for each iteration of hello().
       
       Timer thread will run even while the main has the processor tied up. """

import threading, time

global timer_thread
global start
start = time.time()
# returnTF = True
def elapsed():
    return time.time() -  start

def tie_up_processor(secs):
    occupy_processor_time = time.time() + secs
    while time.time() < occupy_processor_time: ...

def hello():
    global timer_thread
    print(f"hello, world {elapsed():5.2f}")
    timer_thread = threading.Timer(1.0, hello)
    timer_thread.start()
    # return returnTF

# print(returnTF)

timer_thread = threading.Timer(1.0, hello)
timer_thread.start() # after 1 sec, "hello, world" will be printed

tie_up_processor(10)
for x in range(10):
    time.sleep(.44)
    print(f'I woke up    {elapsed():5.2f}')

timer_thread.cancel()

# returnTF = False
# print(returnTF)

timer_thread = threading.Timer(1.0, hello)
timer_thread.start() # after 1 sec, "hello, world" will be printed
for x in range(10):
    time.sleep(.44)
    print(f'I woke up    {elapsed():5.2f}')

timer_thread.cancel()