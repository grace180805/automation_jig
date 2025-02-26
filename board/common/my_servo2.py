from machine import PWM, Pin
import math
import time

# originally by Radomir Dopieralski http://sheep.art.pl
# from https://bitbucket.org/thesheep/micropython-servo

class MyServo:
    
    def __init__(self, pin=Pin(13), min_us=500, max_us=2400):
        self.pwm = PWM(pin, freq=50)
        self.min_us = min_us
        self.max_us = max_us
    
    def set_angle(self, angle, hold_time = 800, release=False):
        """控制舵机转动并可选释放"""
        pulse = self.min_us + (self.max_us - self.min_us) * angle / 180
        self.pwm.duty_ns(int(pulse * 1000))
        
        if release:
            self.release()
            
    def release(self):
        """释放舵机扭矩"""
        #self.pwm.deinit()  # 关闭PWM输出
        #可选：将引脚设置为高阻态
        #Pin(SERVO_PIN, Pin.IN)
        self.pwm.duty_ns(0)
    
    
    
# 使用示例
servo = MyServo()
while True:
    servo.set_angle(80, release=False)  # 转动90度后释放
    time.sleep(2)
    servo.set_angle(45, release=False)  # 转动90度后释放
    time.sleep(2)

