from threading import Thread
import Queue
import random
import time
import signal

SHUTDOWN = False
queue_length = 10
q = Queue.Queue(queue_length)


def pi(digits):
    """ variable calculation time example """
    from decimal import Decimal, getcontext
    getcontext().prec = digits
    return sum(1 / Decimal(16) ** k *
                (Decimal(4) / (8 * k + 1) -
                Decimal(2) / (8 * k + 4) -
                Decimal(1) / (8 * k + 5) -
                Decimal(1) / (8 * k + 6)) for k in range(digits))


class Work(object):
    def __init__(self, name_thread):
        self.digits = name_thread

    def run(self):
        return pi(self.digits)


class ProducerThread(Thread):
    def __init__(self):
        super(ProducerThread, self).__init__()

    def run(self):
        global q
        while True:
            if not q.full():
                num = random.randint(1, 10)
                q.put(num)
                print "Produced:", num
                if SHUTDOWN:
                    break

                time.sleep(1)


class ConsumerThread(Thread):
    def __init__(self):
        super(ConsumerThread, self).__init__()

    def run(self):
        global q
        while True:
            try:
                num = q.get(timeout=1)
            except Queue.Empty:
                # queue empty, must've completed work
                break

            this_work = Work(num * 100 + 200)
            response = this_work.run()
            print "Consumed:", num, ' result:', len(str(response))
            q.task_done()
            time.sleep(1)


class StopMeClass(object):
    def __init__(self):
        signal.signal(signal.SIGINT, self.stop_me)

    def stop_me(self, *unused): # signal, frame
        global SHUTDOWN
        SHUTDOWN = True


a = StopMeClass()
p = ProducerThread()
p.start()
c = ConsumerThread()
c.start()

while q:
    if SHUTDOWN:
        break

while not q.empty():
    print 'queue not empty..'
    time.sleep(1)

while q.unfinished_tasks:
    print 'unfinished tasks..'
    time.sleep(1)

p.join()
c.join()
