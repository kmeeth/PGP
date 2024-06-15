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
    # Section for importing a foreign key from shared into your import ring
    import_section = [
        [sg.Text("User"), sg.InputText(key="-IMPORT_KEY_USER-")],
        [sg.Text("ID"), sg.InputText(key="-IMPORT_KEY_ID-")],
        [sg.Button("Import", key="-IMPORT_KEY-"), sg.Text("", key="-IMPORT_KEY_ERROR-")]
    ]
    # Section for exporting a public part of a key pair into shared
    export_section = [
        [sg.Text("ID"), sg.InputText(key="-EXPORT_KEY_ID-"), sg.Button("Export", key="-EXPORT_KEY-")],
        [sg.Text("", key="-EXPORT_KEY_ERROR-")]
    ]

    # Layout definition
    layout = [
        [sg.Frame("New Key Pair", new_section), sg.Frame("Delete Key Pair", delete_section), sg.Frame("Import Public Key", import_section), sg.Frame("Export Public Key", export_section)]
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
        elif event == "-IMPORT_KEY-":
            try:
                imported_key = models.ImportedKey.import_from_shared(values["-IMPORT_KEY_USER-"], int(values["-IMPORT_KEY_ID-"]))
                imported_key.save(api.current_user)
                window["-IMPORT_KEY_ERROR-"].update(f"Imported {imported_key.id()}")
            except:
                window["-IMPORT_KEY_ERROR-"].update("ID not a number or file was not found.")
        elif event == "-EXPORT_KEY-":
            try:
                id = int(values["-EXPORT_KEY_ID-"])
                correct_key = None
                for key in api.private_rings[api.current_user]:
                    if key.id() == id:
                        correct_key = key
                        break
                if correct_key == None:
                    raise
                correct_key.export_to_shared()
                window["-EXPORT_KEY_ERROR-"].update(f"Exported {id}.")
            except:
                window["-EXPORT_KEY_ERROR-"].update("ID not a number or no key with that ID.")

        api.refresh_state()

    # Close window
    window.close()