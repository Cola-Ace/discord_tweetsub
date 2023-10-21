import datetime

def getNowtime():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

class logger:
    def info(msg):
        print(getNowtime() + " [Info] " + msg)

    def error(msg):
        print(getNowtime() + " [Error] " + msg)

    def warning(msg):
        print(getNowtime() + " [Warning] " + msg)