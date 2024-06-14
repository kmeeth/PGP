import api
import models

if __name__ == "__main__":
    my_key_pair = models.KeyPair.generate("kmeeth", 1024)
    my_key_pair.save("dobrojutro")
    other_key_pair = models.KeyPair.generate("rahel", 1024)
    other_key_pair.save("dobrojutro")
    models.ImportedKey("rahel", other_key_pair.public_key).save("kmeeth")
    models.ImportedKey("kmeeth", my_key_pair.public_key).save("rahel")
    api.import_rings["kmeeth"] = api.update_import_ring("kmeeth")
    api.private_rings["kmeeth"] = api.update_private_ring("kmeeth")
    api.import_rings["rahel"] = api.update_import_ring("rahel")
    api.private_rings["rahel"] = api.update_private_ring("rahel")

    loaded_key = models.KeyPair.load("kmeeth",api.private_rings["kmeeth"][0].id(), "dobrojutro", True)
    print(api.private_rings["kmeeth"][0])
    print(api.import_rings["kmeeth"][0])

    enc = api.send_message("Hello world", loaded_key, api.import_rings["kmeeth"][0], True, 'CAST5', "msg.txt")
    msg = api.receive_message("msg.txt", "rahel", api.private_rings["rahel"][0].id(), "dobrojutro")
