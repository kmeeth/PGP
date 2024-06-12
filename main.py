import api
import models

if __name__ == "__main__":
    my_key_pair = models.KeyPair.generate("kmeeth", 1024)
    my_key_pair.save("dobrojutro")
    other_key_pair = models.KeyPair.generate("rahel", 1024)
    other_key_pair.save("dobrojutro")
    imported_key = models.ImportedKey("rahel", other_key_pair.public_key)
    imported_key.save("kmeeth")
    api.import_rings["kmeeth"] = api.update_import_ring("kmeeth")
    api.private_rings["kmeeth"] = api.update_private_ring("kmeeth")
    api.import_rings["rahel"] = api.update_import_ring("rahel")
    api.private_rings["rahel"] = api.update_private_ring("rahel")
    print(api.private_rings["kmeeth"][0])
    print(api.import_rings["kmeeth"][0])
    print(api.private_rings["rahel"][0])
    print(api.import_rings["rahel"][0])
