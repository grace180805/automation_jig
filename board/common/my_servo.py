from machine import PWM, Pin
import math
import time

# originally by Radomir Dopieralski http://sheep.art.pl
# from https://bitbucket.org/thesheep/micropython-servo

class MyServo:
    """
    A simple class for controlling hobby servos.
    Args:
        pin (machine.Pin): The pin where servo is connected. Must support PWM.
        freq (int): The frequency of the signal, in hertz.
        min_us (int): The minimum signal length supported by the servo.
        max_us (int): The maximum signal length supported by the servo.
        angle (int): The angle between the minimum and maximum positions.
    """
    def __init__(self, pin=Pin(13), freq=50, min_us=1000, max_us=2000, angle=180):
        self.min_us = min_us
        self.max_us = max_us
        self.us = 0
        self.freq = freq
        self.angle = angle
        self.pwm = PWM(pin, freq=freq, duty=0)

    def release(self):
        """释放舵机扭矩"""
        #self.pwm.deinit()  # 关闭PWM输出
        #可选：将引脚设置为高阻态
        #Pin(13, Pin.IN)
        #self.pwm.duty_ns(0)
    
    def write_us(self, us):
        """Set the signal to be ``us`` microseconds long. Zero disables it."""
        if us == 0:
            self.pwm.duty(0)
            return
        us = min(self.max_us, max(self.min_us, us))
        duty = us * 1024 * self.freq // 1000000
        self.pwm.duty(duty)

    def write_angle(self, degrees=None, radians=None, release=False):
        """Move to the specified angle in ``degrees`` or ``radians``."""
        if degrees is None:
            degrees = math.degrees(radians)
        degrees = degrees % 360
        total_range = self.max_us - self.min_us
        us = self.min_us + total_range * degrees // self.angle
        self.write_us(us)
        time.sleep(1)
        if release:
            self.release()
