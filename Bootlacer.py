import threading

import Classes


scheduler = Classes.WaitingQueue(10)
schedulerThread = threading.Thread(target=scheduler.run, name='scheduler')
schedulerThread.start()
outputThread = threading.Thread(target=)

