from machine import Pin
import time

class TM1638:
    def __init__(self, stb, clk, dio):
        self.stb = Pin(stb, Pin.OUT, value=1)
        self.clk = Pin(clk, Pin.OUT, value=0)
        self.dio = Pin(dio, Pin.OUT, value=0)
        self.brightness = 7
        self.clear()

    def _write_byte(self, data):
        for _ in range(8):
            self.clk.value(0)
            self.dio.value(data & 1)
            data >>= 1
            self.clk.value(1)
            time.sleep_us(2)

    def _command(self, cmd):
        self.stb.value(0)
        self._write_byte(cmd)
        self.stb.value(1)

    def _write_data(self, addr, data):
        self._command(0x44)
        self.stb.value(0)
        self._write_byte(0xC0 | (addr & 0x0F))
        self._write_byte(data)
        self.stb.value(1)

    def clear(self):
        for i in range(16):
            self._write_data(i, 0x00)
        self._command(0x88 | self.brightness)

    def display_text(self, text):
        chars = {
            ' ':0x00,'0':0x3F,'1':0x06,'2':0x5B,'3':0x4F,'4':0x66,
            '5':0x6D,'6':0x7D,'7':0x07,'8':0x7F,'9':0x6F,
            'A':0x77,'B':0x7C,'C':0x39,'D':0x5E,'E':0x79,'F':0x71,
            'L':0x38,'O':0x3F,'P':0x73,'R':0x50,'S':0x6D,'T':0x78,
            'U':0x3E,'N':0x37,'G':0x3D,'K':0x76,'-':0x40
        }
        text = (text.upper() + "        ")[:8]
        for i, c in enumerate(text):
            self._write_data(i * 2, chars.get(c, 0x00))
        self._command(0x88 | self.brightness)

    def set_leds(self, mask):
        for i in range(8):
            val = 1 if (mask & (1 << i)) else 0
            self._write_data(i * 2 + 1, val)
        self._command(0x88 | self.brightness)

    def read_buttons(self):
        self.stb.value(0)
        self._write_byte(0x42)
        self.dio.init(Pin.IN, Pin.PULL_UP)
        keys = 0
        for i in range(4):
            for j in range(8):
                self.clk.value(0)
                time.sleep_us(2)
                if self.dio.value() == 1:
                    keys |= (1 << (i * 8 + j))
                self.clk.value(1)
                time.sleep_us(2)
        self.dio.init(Pin.OUT)
        self.stb.value(1)
        return keys