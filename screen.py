from machine import I2C, Pin
import time
from esp8266_i2c_lcd import I2cLcd # https://github.com/dhylands/python_lcd

I2C_FREQ = 800000

class Screen:
    def __init__(self, size_x=20, size_y=4):
        self.size_x = size_x
        self.size_y = size_y
        lcd = I2cLcd(I2C(0, scl=Pin(18), sda=Pin(19), freq=I2C_FREQ), 0x27, 4, 20)
        lcd.clear()
        lcd.backlight_on()
        self.lcd = lcd

        self.throttle_max = 1
        self.throttle_min = 255
        self.phase_amps_max = 10
        self.phase_amps_max = 10
        self._spinner = self._spinner_iter()
        self._draw_count = 0
        self._braking = 0


    def _spinner_iter(self):
        while True:
            for c in ['_', '-', '^', '-']:
                yield c


    def draw_connecting(self, ctrl, bms, ds, count):
        self.lcd.clear()
        self.lcd.move_to(0, 0)
        self.lcd.putstr('Controller: {}'.format('OK!' if ctrl else 'Wait ...'))
        self.lcd.move_to(0, 1)
        self.lcd.putstr('BMS: {}'.format('OK!' if bms else 'Wait ...'))
        self.lcd.move_to(0, 2)
        self.lcd.putstr('DataStore: {}'.format('OK!' if ds else 'Wait ...'))
        self.lcd.move_to(0, 3)
        self.lcd.putstr('{:>20}'.format(count))


    def draw_main(self, ctrlr, bms, calc):

        self.throttle_max = max(self.throttle_max, ctrlr.throttle)
        self.throttle_min = min(self.throttle_min, ctrlr.throttle)
        #self.phase_amps_max = max(self.phase_amps_max, ctrlr.phase_amps)

        self.lcd.move_to(0, 2)
        throttle_bar = (ctrlr.throttle - self.throttle_min) * 19 // ((self.throttle_max - self.throttle_min) or 1)
        throttle_space = 19 - throttle_bar
        self.lcd.putstr('{}{}{}'.format(next(self._spinner), '\xFF' * throttle_bar, ' ' * throttle_space))
        if ctrlr.brake_switch and not self._braking:
            self.lcd.move_to(8, 1)
            self.lcd.putstr('BRAKE')
        elif self._braking:
            self.lcd.move_to(8, 1)
            self.lcd.putstr('     ')
            self._braking = False


        if self._draw_count < 1:
            self._draw_count = 10
            self.lcd.move_to(0, 0)
            self.lcd.putstr('m {:3d}C c {:3d}C b {:3d}V'.format(ctrlr.motor_temp, ctrlr.controller_temp, ctrlr.battery_voltage))

            self.lcd.move_to(0, 1)
            self.lcd.putstr('{:4d}W {:4d}Wh'.format(int(calc.get('power')), int(calc.get('energy_count'))))
            #self.lcd.putstr('{:4.1f}A {:4.1f}V'.format(ctrlr.phase_amps, ctrlr.battery_voltage))

            self.lcd.move_to(0, 3)
            self.lcd.putstr('{:3d}h {:5d}Wh {:4}KM'.format(int(calc.get('uptime') / 3600),
                                                               int(calc.get('energy_count')),
                                                               89882
                                                             ))
        else:
            self._draw_count -= 1


    def browse_chars(self):
        for s in list(range(1, 256, 20)):
          e = min(s+20, 256)
          self.lcd.clearmmm()
          for n in range(s, e):
              print(n)
              self.lcd.putstr(chr(n))
          if e == 256:
              print('End')
              break
          else: input('Press Enter')


    def save_ranges(self):
        pass


Screen20x4 = Screen
