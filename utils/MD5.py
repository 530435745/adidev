import hashlib


def get_md5(filename):
    with open(filename, "rb") as f:
        m = hashlib.md5()
        m.update(f.read())
        return m.hexdigest()


if __name__ == '__main__':
    print(get_md5("multiprocess.py"))
