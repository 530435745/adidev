from filter.main import after_main, unlock_errs


if __name__ == '__main__':
    unlock_errs()
    after_main.delay()
