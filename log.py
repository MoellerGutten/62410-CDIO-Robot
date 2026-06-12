from time import time, localtime

# a bit unreadable but Mr AI tells me this is the most performant way to do it in Python 3.5 and the robot is slow as balls so performance is key

def log(message):
    t = time()
    sec = int(t)
    ms = int((t - sec) * 1000)

    lt = localtime(sec)

    print(
        "[%04d-%02d-%02d %02d:%02d:%02d.%03d] %s" % (
            lt.tm_year,
            lt.tm_mon,
            lt.tm_mday,
            lt.tm_hour,
            lt.tm_min,
            lt.tm_sec,
            ms,
            message
        )
    )