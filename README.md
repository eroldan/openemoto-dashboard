- threads
    - beeper
- metrics
    - Throttle / current graph (using half full filled characters to make two bars in 1 line)
    - total hours
    - total spinning hours
    - distance
    - energy count (done)
    - speed
        - motor rpm x chain reduction x wheel x time
    - Minimum and maximum cell voltages (not updated so often)
- configuration
- persistence
    - some metrics are persisted
- screens system
    - big numbers
        - https://www.youtube.com/watch?v=BrlVg5UsOHM
        - https://www.youtube.com/watch?v=9-lTWIIfhO8
        - https://imgur.com/a/zIYda
        - https://github.com/seanauff/BigNumbers
        - https://www.avrfreaks.net/forum/alphanumeric-lcd-hd44780-big-font-big-digits-generator-excel-sheet
        - http://lcdsmartie.sourceforge.net/BigNumPlugin.html
    - init
    - dash1
    - dash2
    - reset counters
    - system information
    - dashboard information
- input hardward & soft
    - rotary encoder:
        - https://github.com/miketeachman/micropython-rotary
        - https://github.com/BramRausch/encoderLib
    - button
        - debounce
- re-programming on the fly
    - power delivery curve
        - tansistors to cut hall sensors power and prevent "hanging"
    - transistor for reset
- Registry of external libraries used
    - lcd_api.py, i2c_lcd.py
        - https://github.com/dhylands/python_lcd/tree/a3e6c776059487bceabcb8a24b0d5e24574cf519
    - encoder.py
        - https://github.com/SpotlightKid/micropython-stm-lib



# Protocol
https://blog.ja-ke.tech/2020/02/07/ltt-power-bms-chinese-protocol.html
https://blog.ja-ke.tech/2019/12/18/ble-serial.html
https://github.com/kolins-cz/Smart-BMS-Bluetooth-ESP32
https://github.com/kolins-cz/Smart-BMS-Bluetooth-ESP32/blob/master/BMS_process_data.ino
https://github.com/simat/BatteryMonitor


# Bluetooth
https://github.com/micropython/micropython/tree/master/examples/bluetooth
https://github.com/Carglglz/upyble


# Other Resources
- BMS
    - https://github.com/fordtheriver/E-Bike-Speedometer-and-BMS-Interface
        - https://endless-sphere.com/forums/viewtopic.php?p=1461676&sid=f6490ac1dc0c22eb32506dedfbea108f#p1461676
    - https://github.com/bres55/Smart-BMS-arduino-Reader
    - BMS protocol description https://drive.google.com/file/d/0B3UXptx89r4NZ3VLTHlVS1ZGTTQ/view
    - Protocol on ES by simat: https://endless-sphere.com/forums/viewtopic.php?f=14&t=91672&p=1336585#p1336585
    - More protocol on ES https://endless-sphere.com/forums/viewtopic.php?p=1428772#p1428772
    - https://github.com/simat/BatteryMonitor/wiki
    - https://github.com/LibreSolar/bq769x0_ArduinoLibrary
    - https://mono.software/2018/11/15/multiple-bms-monitor/
    - How balancing works by izeman: https://endless-sphere.com/forums/viewtopic.php?f=14&t=88676&start=225#p1361461
    - Electric consumption by izeman: https://endless-sphere.com/forums/viewtopic.php?f=14&t=88676&start=225#p1361482
    - About BLE bluetooth modules probably using in this BMS: http://www.martyncurrey.com/hm-10-bluetooth-4ble-modules/

