import PySimpleGUI as sg

import api
import models


def make_import_ring():
    headings = ["User", "ID", "Public Key"]
    values = [[x.user, x.id(), x.get_string_representation()] for x in api.import_rings[api.current_user]]
    import_ring_section = [
        [sg.Table(values=values, headings=headings, key="-IMPORT_RING-", auto_size_columns=True, expand_x=True, vertical_scroll_only=False)]
    ]
    return import_ring_section


def make_private_ring():
    headings = ["ID", "Public Key", "Private Key"]
    values = [[x.id(), x.get_string_representations()[0], "SECRET"] for x in api.private_rings[api.current_user]]
    private_ring_section = [
        [sg.Table(values=values, headings=headings, key="-PRIVATE_RING-", auto_size_columns=True, expand_x=True, vertical_scroll_only=False)]
    ]
    return private_ring_section


def gui_loop():
    api.refresh_state()
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

    # Import and private rings view
    import_ring_section = make_import_ring()
    private_ring_section = make_private_ring()

    # Send message section
    send_section = [
        [sg.Text("Message"), sg.Multiline(key="-SEND_MESSAGE-", size=(None, 5))],
        [sg.Checkbox("Signature", default=True, key="-SEND_MESSAGE_SIGNATURE-"), sg.Text("Encryption algorithm"), sg.InputCombo([None, "AES128", "CAST5"], default_value="AES128", key="-SEND_MESSAGE_ALGORITHM-")],
        [sg.Text("Sender ID"), sg.InputText(key="-SEND_MESSAGE_SENDER-"),sg.Text("Recipient ID"), sg.InputText(key="-SEND_MESSAGE_RECIPIENT-")],
        [sg.Text("Password"), sg.InputText(key="-SEND_MESSAGE_PASSWORD-"), sg.Text("Output Filename"), sg.InputText(key="-SEND_MESSAGE_FILENAME-")],
        [sg.Button("Send", key="-SEND_MESSAGE_BUTTON-"), sg.Text("", key="-SEND_MESSAGE_ERROR-")]
    ]

    # Receive message section
    receive_section = [
        [sg.Text("Input"), sg.InputText(key="-RECEIVE_MESSAGE_INPUT-")],
        [sg.Text("Output"), sg.InputText(key="-RECEIVE_MESSAGE_OUTPUT-")],
        [sg.Text("Key ID"), sg.InputText(key="-RECEIVE_MESSAGE_ID-")],
        [sg.Text("Password"), sg.InputText(key="-RECEIVE_MESSAGE_PASSWORD-")],
        [sg.Button("Receive", key="-RECEIVE_MESSAGE_BUTTON-"), sg.Text("", key="-RECEIVE_MESSAGE_ERROR-")]
    ]

    # Layout definition
    layout = [
        [sg.Frame("New Key Pair", new_section), sg.Frame("Delete Key Pair", delete_section), sg.Frame("Import Public Key", import_section), sg.Frame("Export Public Key", export_section)],
        [sg.Frame("Import Ring", import_ring_section, expand_x=True)],
        [sg.Frame("Private Ring", private_ring_section, expand_x=True)],
        [sg.Frame("Send Message", send_section), sg.Frame("Receive Message", receive_section)]
    ]

    # Window
    window = sg.Window(f"PGP: {api.current_user}", layout, resizable=True)

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
        elif event == "-SEND_MESSAGE_BUTTON-":
            try:
                message = values["-SEND_MESSAGE-"]
                need_signature = values["-SEND_MESSAGE_SIGNATURE-"]
                algorithm = values["-SEND_MESSAGE_ALGORITHM-"]
                sender_id = int(values["-SEND_MESSAGE_SENDER-"])
                recipient_id = int(values["-SEND_MESSAGE_RECIPIENT-"])
                password = values["-SEND_MESSAGE_PASSWORD-"]
                sender_key_pair = models.KeyPair.load(api.current_user, sender_id, password, True)
                if sender_key_pair == None:
                    raise
                recipient_public_key = [x for x in api.import_rings[api.current_user] if x.id() == recipient_id][0]
                filename = values["-SEND_MESSAGE_FILENAME-"]
                api.send_message(message, sender_key_pair, recipient_public_key, need_signature, algorithm, filename)
                window["-SEND_MESSAGE_ERROR-"].update("")
            except:
                window["-SEND_MESSAGE_ERROR-"].update("IDs must be numbers and must exist. Password must be correct. Sender must be known.")
        elif event == "-RECEIVE_MESSAGE_BUTTON-":
            try:
                input_file = values["-RECEIVE_MESSAGE_INPUT-"]
                output_file = values["-RECEIVE_MESSAGE_OUTPUT-"]
                id = values["-RECEIVE_MESSAGE_ID-"]
                password = values["-RECEIVE_MESSAGE_PASSWORD-"]
                msg = api.receive_message(input_file, api.current_user, id, password, output_file)
                window["-RECEIVE_MESSAGE_ERROR-"].update(msg)
            except:
                window["-RECEIVE_MESSAGE_ERROR-"].update("ID must exist. Password must be correct. File must exist.")

        api.refresh_state()
        private_ring_values = [[x.id(), x.get_string_representations()[0], "SECRET"] for x in api.private_rings[api.current_user]]
        window["-PRIVATE_RING-"].update(values=private_ring_values)
        import_ring_values = [[x.user, x.id(), x.get_string_representation()] for x in api.import_rings[api.current_user]]
        window["-IMPORT_RING-"].update(values=import_ring_values)

    # Close window
    window.close()