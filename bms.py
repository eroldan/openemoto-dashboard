import bluetooth, time, machine, struct
from micropython import const

_IRQ_PERIPHERAL_CONNECT = const(7)
_IRQ_PERIPHERAL_DISCONNECT = const(8)
_IRQ_GATTC_SERVICE_RESULT = const(9)
_IRQ_GATTC_SERVICE_DONE = const(10)
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
_IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
_IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
_IRQ_GATTC_DESCRIPTOR_DONE = const(14)
_IRQ_GATTC_READ_RESULT = const(15)
_IRQ_GATTC_READ_DONE = const(16)
_IRQ_GATTC_WRITE_DONE = const(17)
_IRQ_GATTC_NOTIFY = const(18)
_IRQ_GATTC_INDICATE = const(19)


class JBD_BMS_PROTOCOL:
    _ms_in_hour = 3600000

    def __init__(self, comm):
        #self._decodeA(b'\xdd\x03\x00\x1b\x1bb\x00\x00\x03f\x06@\x00\x00&\x8a\x00\x00\x00\x00')
        self._comm = comm
        self._buffer = bytearray()
        self._last_getA = None

        self.energy_count = 0

        self.comm_ok = 0
        self.comm_err = 0

        self.voltage = 0
        self.current = 0
        self.capacity_remain = 0
        #self.capacity_typical = int.from_bytes(packet[10:12], 'big') * 0.01 # Amp/hour
        #self.cycles = int.from_bytes(packet[12:14], 'big')
        #######self.prod_date = int.from_bytes(packet[14:16], 'big')
        #######self.balance_status = packet[16:20]
        #######self.protection_status = packet[20:22]
        #######self.software_version = int.from_bytes(packet[22:23], 'big')
        self.capacity_remain_percent = 0
        #######self.fet_status = packet[24:25]
        #self.cell_count = int.from_bytes(packet[25:26], 'big')
        #self.ntc_count = int.from_bytes(packet[26:27], 'big')
        self.temp1 = None
        self.temp2 = None
        self.temp3 = None
        self.temp4 = None

    def alive(self, window=3000):
        if self._last_getA and time.ticks_diff(time.ticks_ms(), self._last_getA) < window:
            return True
        else: return False

    def refresh(self):
        if self._getA():
            if self._last_getA:
                _elapsed_ms = time.ticks_diff(time.ticks_ms(), self._last_getA)

                # Calculatled fields
                self.power = self.voltage * self.current
                self.energy_count = self.energy_count + (self.power * _elapsed_ms / self._ms_in_hour) # Watt/hour

            self._last_getA = time.ticks_ms()
        return self

    def _getA(self):
        self._comm.write(b'\xdd\xa5\x03\x00\xff\xfd\x77', response=False)
        self._buffer = self._comm.read()
        return self._decodeA()

    def _decodeA(self):
        packet = self._buffer

        if len(packet) != 34:
            print('- BMS - Invalid packet lenght:', packet, len(packet))
            if self.comm_ok != 0 or self.comm_err !=0: self.comm_err += 1
            return

        head = packet[:2]
        if head != b'\xdd\x03':
            print('- BMS - Invalid header:', head)
            self.comm_err += 1
            return

        packet_ok = packet[2]
        if packet_ok != 0x00:
            print('- BMS - Packet flag is NOT OK, weird:', packet_ok)
            self.comm_err += 1
            return

        checksum = packet[-3:-1]
        payload = packet[2:-3]
        magic_end = packet[-1]
        checksum_calc = 0x10000
        for i in payload: checksum_calc = checksum_calc - int(i)
        checksum_valid = checksum_calc == int.from_bytes(checksum, 'big')

        if not checksum_valid:
            print('- BMS - Checksum invalid')
            self.comm_err += 1
            return

        if magic_end != 0x77:
            print('- BMS - Packet magic end not OK:', magic_end)
            self.comm_err += 1
            return

        packet_len = packet[3]
        self.voltage = int.from_bytes(packet[4:6], 'big') * 0.01             # Volts
        self.current = struct.unpack('>h', packet[6:8])[0] * 0.01            # Amps
        self.capacity_remain = int.from_bytes(packet[8:10], 'big') * 0.01    # Amp/hour
        self.capacity_typical = int.from_bytes(packet[10:12], 'big') * 0.01  # Amp/hour
        self.cycles = int.from_bytes(packet[12:14], 'big')
        self.prod_date = int.from_bytes(packet[14:16], 'big')
        self._balance_status_bits = packet[16:20]
        self.balance_status = bin(int.from_bytes(self._balance_status_bits, 'big'))
        self._protection_status_bits = packet[20:22]
        self.software_version = int.from_bytes(packet[22:23], 'big')
        self.capacity_remain_percent = int.from_bytes(packet[23:24], 'big')  # %Total
        self._fet_status_bits = int.from_bytes(packet[24:25], 'big')
        self.discharge_gate= bool(0x1 & self._fet_status_bits)
        self.charge_gate = bool(0x2 & self._fet_status_bits)
        self.cell_count = int.from_bytes(packet[25:26], 'big')
        self.ntc_count = int.from_bytes(packet[26:27], 'big')
        if self.ntc_count > 0: self.temp1 = int.from_bytes(packet[27:29], 'big') * 0.1 - 273.1      # Celsius
        if self.ntc_count > 1: self.temp2 = int.from_bytes(packet[29:31], 'big') * 0.1 - 273.1      # Celsius
        if self.ntc_count > 2: self.temp3 = int.from_bytes(packet[31:33], 'big') * 0.1 - 273.1      # Celsius
        if self.ntc_count > 3: self.temp4 = int.from_bytes(packet[33:35], 'big') * 0.1 - 273.1      # Celsius

        # calculate balance_status, protection_status, fet_status

        self.comm_ok += 1
        return True

    def values(self):
        keys = [a for a in dir(self) if (not a.startswith('_')) and (a != 'refresh') and (a != 'values')]
        return dict([(k, getattr(self, k)) for k in keys])


class JBD_BMS_BLE:
    _UART_SERVICE_UUID = bluetooth.UUID(0xff00)
    _UART_TX_CHAR_UUID = bluetooth.UUID(0xff01)
    _UART_RX_CHAR_UUID = bluetooth.UUID(0xff02)

    _deadline = 10

    def __init__(self, addr):

        self._buffer = bytearray()
        self._buff_updated_t = None

        self._reset()
        self._addr = addr
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self._irq)
        self._ble.gap_connect(0, self._addr)

        print('- BMS - Waiting to establish connection to BMS ...')
        count = 0
        while not self._is_connected():
            time.sleep_ms(100)
            count += 1
            if count > 100:
                print('- BMS - BLE failed to connect')
                break
        else:
            print("- BMS - BLE Connected")

    def disconnect(self):
        r = self._ble.gap_disconnect(self._conn_handle)
        self._reset()
        return r

    def write(self, data, response=False):
        assert self._is_connected()
        self._ble.gattc_write(self._conn_handle, self._rx_handle, data, 1 if response else 0)

    def read(self):
        time.sleep_ms(self._deadline)
        self._buff_updated_t = None
        return self._buffer

    def _on_notify(self, data):
        #print('RX', data)
        if self._buff_updated_t is None:
            self._buffer = bytearray()
        self._buffer.extend(data)
        self._buff_updated_t = time.ticks_ms()

    def _is_connected(self):
        return self._conn_handle is not None and self._tx_handle is not None and self._rx_handle is not None

    def _reset(self):
        self._conn_handle = None
        self._start_handle = None
        self._end_handle = None
        self._tx_handle = None
        self._rx_handle = None

    def _irq(self, event, data):

        if event == _IRQ_PERIPHERAL_CONNECT:
            #print('IRQ_PERIPHERAL_CONNECT')
            conn_handle, addr_type, addr = data
            #print(data)
            self._conn_handle = conn_handle
            self._ble.gattc_discover_services(self._conn_handle)

        elif event == _IRQ_PERIPHERAL_DISCONNECT:
            #print('IRQ_PERIPHERAL_DISCONNECT')
            # conn_handle, _, _ = data
            self._reset()

        elif event == _IRQ_GATTC_SERVICE_RESULT:
            #print('IRQ_GATTC_SERVICE_RESULT')
            # Connected device returned a service.
            conn_handle, start_handle, end_handle, uuid = data
            #print(data)
            if conn_handle == self._conn_handle and uuid == self._UART_SERVICE_UUID:
                self._start_handle, self._end_handle = start_handle, end_handle

        elif event == _IRQ_GATTC_SERVICE_DONE:
            #print('IRQ_GATTC_SERVICE_DONE')
            # Service query complete.
            if self._start_handle and self._end_handle:
                self._ble.gattc_discover_characteristics(self._conn_handle, self._start_handle, self._end_handle)
            else:
                print("- BMS - Failed to find uart service.")

        elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
            #print('IRQ_GATTC_CHARACTERISTIC_RESULT')
            # Connected device returned a characteristic.
            conn_handle, def_handle, value_handle, properties, uuid = data
            #print(data)
            if uuid == self._UART_RX_CHAR_UUID:
                self._rx_handle = value_handle
            if uuid == self._UART_TX_CHAR_UUID:
                self._tx_handle = value_handle

        elif event == _IRQ_GATTC_CHARACTERISTIC_DONE:
            #print('_IRQ_GATTC_CHARACTERISTIC_DONE')
            if not (self._tx_handle is not None and self._rx_handle is not None):
                print("- BMS - Failed to find UART characteristics.")

        elif event == _IRQ_GATTC_WRITE_DONE:
            #print('IRQ_GATTC_WRITE_DONE')
            conn_handle, value_handle, status = data

        elif event == _IRQ_GATTC_NOTIFY:
            #print('IRQ_GATTC_NOTIFY')
            conn_handle, value_handle, notify_data = data
            assert conn_handle == self._conn_handle and value_handle == self._tx_handle
            self._on_notify(notify_data)
