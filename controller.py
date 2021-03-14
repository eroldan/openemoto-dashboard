import sys, time

# Protocol decode
class ProtocolDecode:
    """
### Bytes sent by the manufacturer's application to get data sets
'3A 00 3A'
'3B 00 3B'
'3C 00 3C'

### Example bytes received by the manufacturer's application, with field descriptions.

'3A 10 2C    06     00     00     00     00    00     01    00     81    00      0C     00     00     00     00     D2'
       Throt BrkPdl BrkSw1 FootSw FrwdSw RevSw HallA  HallB HallC  Volt  MtrTmp  CtrTmp SetDir ActDir BrkSw2 LowSpd ChkSum

'3B 10 00    00    00     A2     00     00     00     00 00 00 00 00 00 00 00 00 ED'
       Stat1 Stat2 MtrSp1 MtrSp2 PhCur1 PhCur2                                   ChkSum

"""

### Bit mask to decode status (Stat1, Stat2) field
status_table = """
# Stat1  Stat2     LedCode  Message                         Source
00000000 00000000  0,0      All OK                          Tested
00000000 00000001  1,1      Automatic error identification  Deduced
00000000 00000010  1,2      Over Voltage                    Tested
00000000 00000100  1,3      Low Voltage                     Tested
00000000 00001000  1,4      Reserved                        Deduced
00000000 00010000  2,1      Motor did not start             Deduced
00000000 00100000  2,2      Internal volts fault            Deduced
00000000 01000000  2,3      Controller over temperature     Deduced
00000000 10000000  2,4      Throttle error at power up      Tested
00000001 00000000  3,1      Reserved                        Deduced
00000010 00000000  3,2      Internal reset                  Tested
00000100 00000000  3,3      Throttle fault                  Tested
00001000 00000000  3,4      Motor halls fault               Tested
00010000 00000000  4,1      Reserved                        Deduced
00100000 00000000  4,2      Reserved                        Deduced
01000000 00000000  4,3      Motor over temperature          Deduced
10000000 00000000  4,4      Hall galvanometer error         Deduced
"""
status_dict = dict()
for l in  status_table.splitlines()[2:]:
    fields = l.split()
    stat1, stat2 = fields[:2]
    ledcode = fields[2]
    message = ' '.join(fields[3:-1])
    status_dict[int(''.join((stat1, stat2)), 2)] = ' - '.join((message, ledcode))

class KLS:
    """ Generic KLS controller class """

    def __init__(self):
        self.comm_err = 0
        if sys.implementation.name != 'micropython':
            import serial
            self.ser = serial.Serial('COM6', 19200, timeout=0.1)
        else:
            from machine import UART
            self._ser = UART(2, baudrate=19200, bits=8, parity=None, stop=1, timeout=100)
            self._ser.read() # flush

        self._last_getA = None
        self._last_getB = None

        self.brake_switch = 0
        self.throttle = 50
        self.hall_a = True
        self.hall_b = False
        self.hall_c = False
        self.motor_temp = 0
        self.controller_temp = 0
        self.battery_voltage = 0
        self.motor_speed = 0
        self.phase_amps = 0
        self.status_code = 0
        self.status_msg = 'Unknown'
        self.comm_err = 0
        self.comm_ok = 0
        print(status_dict)
        # self.stat_dict = dict()
        # for l in status_table:
        #     print(repr(l))
        #     if l.startswith('#'): continue
        #     bitA, bitB, ledcode, message, other = l.split()
        #     self.status_dict[ledcode] = message
        # print(self.status_dict)


    def alive(self, window=3000):
        if self._last_getA and self._last_getB and \
           time.ticks_diff(time.ticks_ms(), self._last_getA) < window and \
           time.ticks_diff(time.ticks_ms(), self._last_getB) < window:
           return True
        else: return False

    def refresh(self, a=True, b=True):
        if a:
            self._getA()
        if b:
            self._getB()
        return self

    def values(self):
        keys = [a for a in dir(self) if (not a.startswith('_')) and (a != 'refresh') and (a != 'values')]
        return dict([(k, getattr(self, k)) for k in keys])

    def _checksum(self, d):
        return sum(d[:-1]) % 256 == d[-1]

    def _get(self, msg):
        err_msg = None
        self._ser.write(bytes(msg))
        d = self._ser.read(19)
        if not d:
            err_msg = '- CTRLR - Empty packet'
        elif len(d) != 19:
            err_msg = '- CTRLR - Wrong packet size != 19'
        elif not self._checksum(d):
            err_msg = '- CTRLR - Packet failed checksum'

        if err_msg:
            print(err_msg)
            self.comm_err += 1
            e = self._ser.read() # Clean remaining buffer
            if e: print("- CTRLR - Discarding rx buffer: {} bytes".format(len(e)))
            return None
        else:
            self.comm_ok += 1
            return d

    def _getB(self):
        d = self._get((0x3b, 0x00, 0x3b))
        if not d: return

        self.motor_speed = int.from_bytes(bytes((d[4], d[5])), 'big')
        self.phase_amps = int.from_bytes(bytes((d[6], d[7])), 'big')
        self.status_code = int.from_bytes(bytes((d[2], d[3])), 'big')
        self.status_msg = status_dict.get(self.status_code, 'Unknown (program error)')
        self._last_getB = time.ticks_ms()

    def _getA(self):
        d = self._get((0x3a, 0x00, 0x3a))
        if not d: return

        self.throttle = d[2]
        self.brake_switch = bool(d[4])
        self.hall_a, self.hall_b, self.hall_c = bool(d[8]), bool(d[9]), bool(d[10])
        self.battery_voltage = d[11]
        self.motor_temp = d[12]
        self.controller_temp = d[13]
        self._last_getA = time.ticks_ms()

    def _calc_speed(self, unit="km/h"):
        pass

KLS_S     = KLS # Tested
KLS_N     = KLS # Deduced
KLS_8080H = KLS # Deduced
KLS_D     = KLS # Deduced
KLS_8080I = KLS # Deduced
KLS_H     = KLS # Deduced


if __name__ == '__main__':
    k = KLS()