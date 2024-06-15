import PySimpleGUI as sg

import api
import models


def gui_loop():
    # Section for creating new pairs
    new_section = [
        [sg.Text("Password"), sg.InputText(key="-NEW_KEY_PASSWORD-")],
        [sg.Button("1024", key="-CREATE1024-"), sg.Button("2048", key="-CREATE2048-")]
    ]

    # Layout definition
    layout = [
        [sg.Frame("New key pair", new_section)]
    ]

    # Window
    window = sg.Window(f"PGP: {api.current_user}", layout)

    # Loop
    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break
        elif event == "-CREATE1024-":
            new_key_pair = models.KeyPair.generate(api.current_user, 1024)
            new_key_pair.save(values["-NEW_KEY_PASSWORD-"])
            print(values["-NEW_KEY_PASSWORD-"])

        api.refresh_state()

    # Close window
    window.close()