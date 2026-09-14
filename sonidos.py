from machine import Pin, PWM
import time

REFERENCIA_TONO = 375  # punto medio del rango 150-600 Hz, usado para escalar los sonidos

class Sonidos:
    def __init__(self, pin_buzzer):
        self.buzzer = PWM(Pin(pin_buzzer), freq=440, duty=0)
        self.tono_base = REFERENCIA_TONO  # valor por defecto antes de seleccionar tono

    def set_tono(self, tono):
        self.tono_base = tono

    def beep_corto(self):
        self.buzzer.freq(900)
        self.buzzer.duty(400)
        time.sleep(0.06)
        self.buzzer.duty(0)

    def alarma_error(self):
        factor = self.tono_base / REFERENCIA_TONO
        frecuencia = int(280 * factor)
        for _ in range(3):
            self.buzzer.freq(frecuencia)
            self.buzzer.duty(500)
            time.sleep(0.14)
            self.buzzer.duty(0)
            time.sleep(0.07)

    def alarma_bloqueo(self):
        # Sonido bien diferente y más largo
        factor = self.tono_base / REFERENCIA_TONO
        frecuencia = int(160 * factor)
        for _ in range(8):
            self.buzzer.freq(frecuencia)
            self.buzzer.duty(700)
            time.sleep(0.22)
            self.buzzer.duty(0)
            time.sleep(0.10)

    def melodia_victoria(self):
        factor = self.tono_base / REFERENCIA_TONO
        notas = [523, 659, 784, 1047]
        for n in notas:
            self.buzzer.freq(int(n * factor))
            self.buzzer.duty(450)
            time.sleep(0.16)
            self.buzzer.duty(0)
            time.sleep(0.04)