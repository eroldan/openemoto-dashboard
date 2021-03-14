import machine, time
from machine import I2C, Pin
from esp8266_i2c_lcd import I2cLcd

def some_math(f):
    machine.freq(f)
    t = time.ticks_ms()
    for x in range(100000):
        a = x * x - x
    print("{} {}".format(f, time.ticks_diff(time.ticks_ms(), t)))

def cpu():
    some_math(160000000)
    some_math(240000000)

def lcd_paint():
    I2C_FREQ = 400000
    lcd = I2cLcd(I2C(0, scl=Pin(18), sda=Pin(19), freq=I2C_FREQ), 0x27, 4, 20)
    lcd.clear()
    lcd.backlight_on()
    start = time.ticks_ms()
    for n in range(200):
        lcd.move_to(0,0)
        lcd.putstr("x" * 20)
        lcd.move_to(0,1)
        lcd.putstr("x" * 20)
        lcd.move_to(0,2)
        lcd.putstr("x" * 20)
        lcd.move_to(0,3)
        lcd.putstr("{}".format(n))
    elapsed = time.ticks_diff(time.ticks_ms(), start) / 1000
    print("{}".format(elapsed))
