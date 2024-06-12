import api
import models

if __name__ == "__main__":
    my_key_pair = models.KeyPair.generate("kmeeth", 1024)
    my_key_pair.save("dobrojutro")
    other_key_pair = models.KeyPair.generate("rahel", 1024)
    other_key_pair.save("dobrojutro")
    imported_key = models.ImportedKey("rahel", other_key_pair.public_key)
    imported_key.save("kmeeth")
    api.imported_rings["kmeeth"] = api.update_imported_ring("kmeeth")
    print(api.imported_rings["kmeeth"][0])
