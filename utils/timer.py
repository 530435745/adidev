import time
import datetime
import threading
import signal


def get_work_interval(interval=None, minute=None, hour=None, day=None):
    if interval:
        return interval
    now = datetime.datetime.now()
    if day is not None:
        work_time = datetime.datetime(
            year=now.year, month=now.month, day=day,
            hour=hour, minute=minute
        )
        if now.month == 12:
            next_work_time = datetime.datetime(
                year=now.year + 1, month=1, day=day,
                hour=hour, minute=minute
            )
        else:
            next_work_time = datetime.datetime(
                year=now.year, month=now.month + 1, day=day,
                hour=hour, minute=minute
            )
    else:
        work_time = datetime.datetime(
            year=now.year, month=now.month, day=now.day,
            hour=hour or now.hour, minute=minute
        )
        if hour is not None:
            td = datetime.timedelta(days=1)
        else:
            td = datetime.timedelta(hours=1)
        next_work_time = work_time + td
    if work_time > now:
        print("下次执行时间: ", work_time)
        print("还需等待：", (work_time - now).total_seconds())
        return (work_time - now).total_seconds()
    else:
        print("下次执行时间: ", next_work_time)
        print("还需等待：", (next_work_time - now).total_seconds())
        return (next_work_time - now).total_seconds()


def do_at(interval=None, minute=None, hour=None, day=None):
    class Wrapper:
        def __init__(self, func):
            self.func = func

        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)

        def delay(self, *args, **kwargs):
            time_event = threading.Event()
            exit_event = threading.Event()

            def signal_handler(signum, frame):
                print("等待最后一次任务完成中，请勿强制退出...")
                exit_event.set()
                time_event.set()
                time.sleep(1)

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            def time_event_worker():
                # 延迟一秒开始，以便任务不会开始就被阻塞
                time.sleep(1)
                while True:
                    exit_event.wait(get_work_interval(interval, minute, hour, day))
                    if exit_event.is_set():
                        return
                    time_event.set()
                    time_event.clear()

            def main_worker():
                while True:
                    time_event.wait()
                    if exit_event.is_set():
                        break
                    self.func(*args, **kwargs)

            threading.Thread(target=time_event_worker).start()
            t = threading.Thread(target=main_worker)
            t.start()
            t.join()
    return Wrapper


if __name__ == '__main__':
    @do_at(interval=5)
    def print_time():
        print(time.time())

    print_time.delay()
