import os


def remove_dir(target):
    target = target.replace('\\', '/')
    if os.path.isdir(target):
        for p in os.listdir(target):
            remove_dir(os.path.join(target, p))
        if os.path.exists(target):
            os.rmdir(target)
    else:
        if os.path.exists(target):
            os.remove(target)
