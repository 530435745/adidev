import signal
import time
import sys
import multiprocessing


def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)


def multiprocess():
    """
    多线程封装，返回进程池对象
    :return:
    """
    pool = multiprocessing.Pool()

    def signal_handler(signum, frame):
        print("Please wait until all processes done...")
        pool.terminate()
        pool.join()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    return pool


if __name__ == '__main__':
    def custom():
        while True:
            time.sleep(5)
            print("AAAAAA")
    pool = multiprocess()
    pool.apply_async(func=custom)
    pool.close()
    pool.join()
