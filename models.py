import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class ImportedKey:
    user = None
    public_key = None

    def __init__(self, user, public_key):
        self.public_key = public_key
        self.user = user


    def get_string_representation(self):
        public = self.public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo)

        return public.hex()


    def __str__(self):
        return f"{self.user}\t{self.public_key.public_numbers().n % (1 << 64)}\t{self.get_string_representation()}"


class KeyPair:
    user = None
    public_key = None
    private_key = None

    def __init__(self, user, password, size):
        # Generate private key
        self.private_key = rsa.generate_private_key(key_size=size, public_exponent=65537)
        # Generate public key
        self.public_key = self.private_key.public_key()

        self.user = user


    def get_string_representations(self):
        private = self.private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption())

        public = self.public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo)

        return public.hex(), private.hex()

    def __str__(self):
        return f"{self.user}\t{self.public_key.public_numbers().n % (1 << 64)}\t{self.get_string_representations()[0]}\t{self.get_string_representations()[1]}"
