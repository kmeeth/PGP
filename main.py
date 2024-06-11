import api
import models

if __name__ == "__main__":
    key_pair = models.KeyPair.generate("kmeeth", 1024)
    id = key_pair.public_key.public_numbers().n % (1 << 64)
    print(id)
    print(key_pair)
    key_pair.save("dobrojutro")
    key_pair = models.KeyPair.load("kmeeth", id, "dobrojutro")
    print(key_pair)