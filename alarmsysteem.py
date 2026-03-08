from gpiozero import LED, Button, Buzzer
from signal import pause
from time import time, sleep

groene_led = LED(18)
rode_led = LED(23)
buzzer = Buzzer(24)

knop1 = Button(4, bounce_time=0.05)
knop2 = Button(17, bounce_time=0.05)

PIN_CODE = [1,2,2,1]
PIN_TIMEOUT = 5
MAX_POGINGEN = 3

toestand = "uit"
invoer = []
laatste_druk = None
foute_pogingen = 0


def reset_invoer():
    global invoer, laatste_druk
    invoer = []
    laatste_druk = None


def piep_1():
    buzzer.on()
    sleep(0.1)
    buzzer.off()


def piep_2():
    for _ in range(2):
        buzzer.on()
        sleep(0.1)
        buzzer.off()
        sleep(0.1)


def piep_3():
    for _ in range(3):
        buzzer.on()
        sleep(0.1)
        buzzer.off()
        sleep(0.1)


def update_status():
    if toestand == "uit":
        buzzer.off()
        groene_led.on()
        rode_led.off()
        print("Alarm UIT")

    elif toestand == "aan":
        buzzer.off()
        groene_led.off()
        rode_led.on()
        print("Alarm AAN")

    elif toestand == "alarm":
        groene_led.off()
        rode_led.blink(on_time=0.2, off_time=0.2)
        buzzer.beep(on_time=0.1, off_time=0.1)
        print("ALARM!")

    elif toestand == "lockout":
        groene_led.off()
        rode_led.blink(on_time=0.1, off_time=0.1)
        buzzer.beep(on_time=0.05, off_time=0.05)
        print("LOCKOUT")


def schakel_alarm_in():
    global toestand
    toestand = "aan"
    update_status()
    piep_1()


def schakel_alarm_uit():
    global toestand, foute_pogingen
    toestand = "uit"
    foute_pogingen = 0
    reset_invoer()
    update_status()
    piep_2()


def controleer_pin():
    global toestand, foute_pogingen

    if invoer == PIN_CODE:
        print("Correcte PIN")
        schakel_alarm_uit()

    else:
        foute_pogingen += 1
        print("Foute PIN")

        piep_3()

        if foute_pogingen >= MAX_POGINGEN:
            toestand = "lockout"
        else:
            toestand = "alarm"

        reset_invoer()
        update_status()


def registreer_druk(knop_nr):
    global laatste_druk

    if toestand == "lockout":
        return

    if toestand == "uit":
        if knop_nr == 1:
            schakel_alarm_in()
        return

    nu = time()

    # timeout alleen op PIN invoer
    if invoer and laatste_druk and (nu - laatste_druk) > PIN_TIMEOUT:
        print("Timeout! Invoer gewist.")
        reset_invoer()

    laatste_druk = nu

    invoer.append(knop_nr)
    print("PIN:", "*" * len(invoer))

    if len(invoer) == len(PIN_CODE):
        controleer_pin()


print("Alarmsysteem gestart")

update_status()

knop1.when_pressed = lambda: registreer_druk(1)
knop2.when_pressed = lambda: registreer_druk(2)

pause()