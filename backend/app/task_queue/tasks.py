import time


def example(seconds: int, **kwargs):
    print('Starting task')
    time.sleep(int(seconds))
    print('Task completed')
    return seconds
