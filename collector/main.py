from collector.collect_workers import *
from collector.config import COLLECTOR_INTERVAL
from filter.utils.timer import do_at


@do_at(interval=COLLECTOR_INTERVAL)
def worker():
    ReturnCollector.process()
    TotalCollector.process()


if __name__ == '__main__':
    worker.delay()
