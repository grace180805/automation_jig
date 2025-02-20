import utime
import ntptime

class Utils:
    log_file_path = "./app.log"

    @staticmethod
    def sync_time():
        try:
            ntptime.settime()
            print("Time synchronized successfully.")
        except Exception as e:
            print("Failed to synchronize time:", e)

    @staticmethod
    def info(*args):
        timestamp = utime.localtime()
        formatted_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            timestamp[0], timestamp[1], timestamp[2],
            timestamp[3], timestamp[4], timestamp[5]
        )
        message = ' '.join(map(str, args))
        print("[{}] {}".format(formatted_time, message))

    @staticmethod
    def log(*args):
        # 获取当前时间
        timestamp = utime.localtime()
        formatted_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            timestamp[0], timestamp[1], timestamp[2],
            timestamp[3], timestamp[4], timestamp[5]
        )
        message = ' '.join(map(str, args))
        print("[{}] {}".format(formatted_time, message))
        # 打开日志文件并写入日志
        with open(Utils.log_file_path, "a") as f:
            f.write("[{}] {}\n".format(formatted_time, message))
