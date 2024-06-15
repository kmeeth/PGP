import PySimpleGUI as sg

import api
import models


def gui_loop():
    # Section for creating new pairs
    new_section = [
        [sg.Text("Password"), sg.InputText(key="-NEW_KEY_PASSWORD-")],
        [sg.Button("1024", key="-CREATE1024-"), sg.Button("2048", key="-CREATE2048-")]
    ]
    # Section for deleting an existing pair
    delete_section = [
        [sg.Text("ID"), sg.InputText(key="-DELETE_KEY_ID-")],
        [sg.Button("Delete", key="-DELETE_KEY-")],
        [sg.Text("", key="-DELETE_KEY_ERROR-")]
    ]

    # Layout definition
    layout = [
        [sg.Frame("New Key Pair", new_section), sg.Frame("Delete Key Pair", delete_section)]
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
        elif event == "-CREATE2048-":
            new_key_pair = models.KeyPair.generate(api.current_user, 2048)
            new_key_pair.save(values["-NEW_KEY_PASSWORD-"])
            print(values["-NEW_KEY_PASSWORD-"])
        elif event == "-DELETE_KEY-":
            try:
                id = int(values["-DELETE_KEY_ID-"])
                api.delete_from_private_ring(api.private_rings[api.current_user], api.current_user, id)
                window["-DELETE_KEY_ERROR-"].update(f"Deleted {id}.")
            except:
                window["-DELETE_KEY_ERROR-"].update("ID must be a number.")

        api.refresh_state()

    # Close window
    window.close()