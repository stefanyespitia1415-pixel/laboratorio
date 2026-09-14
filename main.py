from machine import Pin, PWM, ADC
import time
from tm1638 import TM1638
from sonidos import Sonidos

# ======================
# PINES
# ======================
SERVO_PIN   = 13
IN1, IN2, IN3, IN4 = 16, 17, 18, 19
POT_PIN     = 34
BUZZER_PIN  = 25
TM_STB, TM_CLK, TM_DIO = 23, 22, 21

# ======================
# SERVO
# ======================
servo = PWM(Pin(SERVO_PIN), freq=50)

def mover_servo(angulo):
    duty = int(26 + (angulo / 180) * 102)
    servo.duty(duty)
    time.sleep(0.35)

# ======================
# STEPPER
# ======================
pin_a = Pin(IN1, Pin.OUT)
pin_b = Pin(IN2, Pin.OUT)
pin_c = Pin(IN3, Pin.OUT)
pin_d = Pin(IN4, Pin.OUT)
stepper = [pin_a, pin_b, pin_c, pin_d]
secuencia = [
    [1,0,0,0], [1,1,0,0], [0,1,0,0], [0,1,1,0],
    [0,0,1,0], [0,0,1,1], [0,0,0,1], [1,0,0,1]
]

def girar_stepper(pasos, sentido=1, delay=0.006):
    for i in range(pasos):
        paso = secuencia[i % 8] if sentido == 1 else secuencia[7 - (i % 8)]
        for pin, val in zip(stepper, paso):
            pin.value(val)
        time.sleep(delay)
    for pin in stepper:
        pin.value(0)

# ======================
# POTENCIÓMETRO
# ======================
pot = ADC(Pin(POT_PIN))
pot.atten(ADC.ATTN_11DB)
pot.width(ADC.WIDTH_12BIT)

# ======================
# OBJETOS DE LAS LIBRERÍAS
# ======================
tm = TM1638(TM_STB, TM_CLK, TM_DIO)
sonidos = Sonidos(BUZZER_PIN)

# ======================
# PRUEBA DEL POTENCIÓMETRO (opcional)
# ======================
def test_potenciometro():
    print("=== MODO PRUEBA POTENCIÓMETRO ===")
    print("Gira el potenciómetro y observa el valor. Ctrl+C para salir.")
    while True:
        val = pot.read()
        freq = int(150 + (val / 4095) * 450)
        print("ADC:", val, " -> Frecuencia:", freq, "Hz")
        tm.display_text(str(freq))
        time.sleep_ms(200)

# ======================
# SELECCIÓN DE TONO AL INICIO
# ======================
def seleccionar_tono():
    print("=== SELECCIÓN DE TONO ===")
    print("Gira el potenciómetro para elegir el tono base de los sonidos.")
    print("Presiona el BOTÓN 5 del TM1638 para confirmar.")
    while True:
        val = pot.read()
        tono = int(150 + (val / 4095) * 450)
        sonidos.set_tono(tono)
        print("Tono actual:", tono, "Hz")
        tm.display_text(str(tono))
        botones = tm.read_buttons()
        if botones & (1 << 4):  # botón 5 = confirmar tono
            sonidos.beep_corto()
            print("Tono confirmado:", tono, "Hz")
            time.sleep(0.3)
            break
        time.sleep_ms(200)

# ======================
# LÓGICA
# ======================
CLAVE = "1234"
estado = "LOCKED"
clave = ""
intentos = 0
ultimo_boton = 0
tiempo_ultimo = 0
tiempo_bloqueo = 0

def mostrar_estado():
    if estado == "LOCKED":
        tm.display_text("LOCKED  ")
        tm.set_leds(0b00000001)
    elif estado == "OPEN":
        tm.display_text("OPEN    ")
        tm.set_leds(0b00000010)
    elif estado == "ERROR":
        tm.display_text("ERROR   ")
        tm.set_leds(0b11111111)
    elif estado == "BLOCKED":
        tm.display_text("BLOCKED ")
        tm.set_leds(0b10101010)

def verificar():
    global estado, clave, intentos, tiempo_bloqueo

    if clave == CLAVE:
        print("Clave CORRECTA")
        estado = "OPEN"
        mover_servo(90)
        girar_stepper(2048, 1)
        sonidos.melodia_victoria()
        mostrar_estado()
        intentos = 0
        clave = ""
    else:
        intentos += 1
        print("Clave INCORRECTA. Intentos:", intentos)
        estado = "ERROR"
        sonidos.alarma_error()
        mostrar_estado()
        time.sleep(1.2)

        if intentos >= 3:
            print(">>> BLOQUEADO por 3 intentos fallidos")
            estado = "BLOCKED"
            clave = ""
            mostrar_estado()
            sonidos.alarma_bloqueo()
            tiempo_bloqueo = time.ticks_ms()
        else:
            estado = "LOCKED"
            clave = ""
            mostrar_estado()

# ======================
# INICIO
# ======================
print("Caja Fuerte lista")
print("Clave correcta:", CLAVE)
mostrar_estado()
mover_servo(0)

seleccionar_tono()
mostrar_estado()  # vuelve a mostrar LOCKED después de la selección de tono

# Para probar el potenciómetro por separado, descomenta la siguiente línea:
# test_potenciometro()

while True:
    ahora = time.ticks_ms()

    # ------ Estado BLOCKED ------
    if estado == "BLOCKED":
        # Parpadeo de LEDs mientras está bloqueado
        if (time.ticks_ms() // 400) % 2 == 0:
            tm.set_leds(0b10101010)
        else:
            tm.set_leds(0b01010101)

        if time.ticks_diff(ahora, tiempo_bloqueo) > 10000:   # 10 segundos
            print("Fin del bloqueo")
            estado = "LOCKED"
            intentos = 0
            clave = ""
            mostrar_estado()
        time.sleep_ms(50)
        continue

    # ------ Lectura de botones ------
    botones = tm.read_buttons()

    if botones != 0 and botones != ultimo_boton and time.ticks_diff(ahora, tiempo_ultimo) > 200:
        tiempo_ultimo = ahora
        sonidos.beep_corto()

        digito = None
        if   botones & (1 << 0):  digito = "1"
        elif botones & (1 << 8):  digito = "2"
        elif botones & (1 << 16): digito = "3"
        elif botones & (1 << 24): digito = "4"
        elif botones & (1 << 4):  digito = "5"
        elif botones & (1 << 12): digito = "6"
        elif botones & (1 << 20): digito = "7"
        elif botones & (1 << 28): digito = "8"

        if estado == "LOCKED" and digito:
            clave += digito
            tm.display_text((clave + "        ")[:8])
            girar_stepper(40, 1)
            print("Clave actual:", clave)

            if len(clave) >= 4:
                time.sleep(0.15)
                verificar()

        elif estado == "OPEN":
            # Cerrar la caja
            print("Cerrando caja...")
            estado = "LOCKED"
            clave = ""
            mover_servo(0)
            girar_stepper(2048, -1)
            mostrar_estado()

    ultimo_boton = botones
    time.sleep_ms(40)