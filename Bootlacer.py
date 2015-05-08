import threading
import time

import OutputDrivers


OutputDriverThread = threading.Thread(target=OutputDrivers.run, name=OutputDrivers.name + '#root')
OutputDriverThread.start()

time.sleep(10)

# scheduler = Classes.WaitingQueue(10)
# schedulerThread = threading.Thread(target=scheduler.run, name='scheduler')
#schedulerThread.start()

