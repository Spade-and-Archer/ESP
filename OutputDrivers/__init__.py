import glob
import time
import threading


__file__ = __file__.replace('/', '\\')
print __file__
pos = len(__file__) - __file__[::-1].index('\\')
parent_folder = __file__[:pos] + '*.py'
name = 'OutDrivers'
list_of_modules = glob.glob(parent_folder)  # gets a list of all python files in this folder
print list_of_modules  # DO NOT REMOVE
print __file__  # bug where all variables are none because this is still initiating or something.
# print statement makes this pause for a sec and collect these variables/wait for them to get into ram/do magic
# honestly, this is the weirdest bug ever, just don't get rid of these
try:
    list_of_modules.remove(__file__)
except:
    list_of_modules.remove(__file__[:-1])  # removes this module from the list of files in this folder

for i in range(len(list_of_modules)):
    list_of_modules[i] = list_of_modules[i][len(parent_folder) - 4:-3]  # removes the parent folder and '.py'
    __import__(list_of_modules[i], globals(), locals(), [], -1)  # imports the modules


class DummyThread():
    def __init__(self):
        self.live = False

    def is_alive(self):
        return self.live

    def isAlive(self):
        return self.live


def run():
    """
    WARNING: this is the call that never eeeennnds
    it just goes on an on forever
    This function should always be run in a thread. It will, every 1 'tick', update each output driver
    Modules will be ignored until their update_period has passed. All modules must have an update_period
    the update period should be an integer between 0 and ten thousand inclusively
    under no load, 1 'tick' is one millisecond
    under high load, it is expected to grow to possibly 5 or 6
    in will NEVER dip below one millisecond, even with no load at all, this is to save CPU for other things
    ^ To justify the above, recall that this is to run on a raspberry pi
    :return:
    """
    cur_tick = 0
    running_inputs = []
    for i in range(len(list_of_modules)):
        running_inputs.append(DummyThread())

    while True:
        start = time.time()
        cur_tick += 1
        if cur_tick > 10000:
            cur_tick = 0
        i = -1
        for module in list_of_modules:
            i += 1
            exec "module = " + module + ".main"  # my solution to not putting this whole thing in an exec  string
            if not cur_tick % module.update_period and not running_inputs[i].is_alive():
                running_inputs.append(threading.Thread(target=module.post, name=name + str(i)))
                module.post()
            else:
                pass
        time.sleep(min(0, .01 - (time.time() - start)))

