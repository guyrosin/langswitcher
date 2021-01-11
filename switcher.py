from datetime import datetime
from time import sleep

import keyboard

TIMEOUT = 3

memory = []
reset_keys = ["alt", "tab"]
last_timestamp = datetime.now()


def on_triggered():
    global memory
    sleep(0.3)
    # switch language
    keyboard.send("alt+shift")
    num_to_delete = 0

    shift_pressed = False
    capslock_pressed = False
    codes = []
    for event in memory:
        name = event.name
        # shorten space and enter because later we filter by name length
        if event.name == 'space':
            name = ' '
        elif event.name == 'enter':
            name = '\n'
        if 'shift' in event.name:
            shift_pressed = event.event_type == 'down'
        elif event.name == 'caps lock' and event.event_type == 'down':
            capslock_pressed = not capslock_pressed
        elif event.name == 'backspace' and event.event_type == 'down':
            codes = codes[:-1]
            num_to_delete -= 1
        elif event.event_type == 'down':
            if len(name) == 1:  # skip modifier keys
                if shift_pressed ^ capslock_pressed:
                    codes.append('shift')
                codes.append(event.scan_code)
                num_to_delete += 1
    # delete the recently typed text
    keyboard.write('\b' * num_to_delete)
    shifted = False
    for code in codes:
        if code == 'shift':  # just press shift
            keyboard.send(code, do_release=False)
            shifted = True
        else:
            keyboard.send(code)
            if shifted:  # release shift
                keyboard.send('shift', do_press=False)
    memory = []


print('Started...')


def on_key_press(e):
    global memory
    global last_timestamp
    if not e.name or any(key in e.name for key in reset_keys):
        return
    time = e.time
    timestamp = datetime.fromtimestamp(time)
    delta = timestamp - last_timestamp
    if delta.total_seconds() > TIMEOUT:
        memory = []
    memory.append(e)
    last_timestamp = timestamp


def on_alt_release(e):
    global memory
    memory = []


keyboard.on_press(on_key_press)
keyboard.on_release_key('alt', on_alt_release)
keyboard.add_hotkey('ctrl+alt+shift', on_triggered)

print("Press TAB+ESC to stop.")
keyboard.wait('tab+esc')
