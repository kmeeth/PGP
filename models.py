import base64
import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
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
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return public.hex()


    # Save public key of self.user into owner's storage
    def save(self, owner):
        os.makedirs(f"{owner}/import", exist_ok=True)
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open(f"{owner}/import/{self.public_key.public_numbers().n % (1 << 64)}_{self.user}_public.pem", 'wb') as public_key_file:
            public_key_file.write(public_pem)


    # Load user's public key with a given id from owner's storage
    @staticmethod
    def load(owner, user, id):
        with open(f"{owner}/import/{id}_{user}_public.pem", 'rb') as public_key_file:
            public_pem = public_key_file.read()
        public_key = serialization.load_pem_public_key(public_pem)
        return ImportedKey(user, public_key)


    def __str__(self):
        return f"{self.user}\t{self.public_key.public_numbers().n % (1 << 64)}\t{self.get_string_representation()}"


class KeyPair:
    user = None
    public_key = None
    private_key = None


    @staticmethod
    def generate(user, size):
        # Generate private key
        private_key = rsa.generate_private_key(key_size=size, public_exponent=65537)
        # Generate public key
        public_key = private_key.public_key()
        return KeyPair(user, private_key, public_key)


    def __init__(self, user, private_key, public_key):
        self.private_key = private_key
        self.public_key = public_key
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


    def save(self, password):
        id = self.public_key.public_numbers().n % (1 << 64)
        os.makedirs(f"{self.user}/private", exist_ok=True)
        # Save private key
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(password.encode())
        )
        with open(f"{self.user}/private/{id}_private.pem", 'wb') as private_pem_file:
            private_pem_file.write(private_pem)
        # Save public key
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open(f"{self.user}/private/{id}_public.pem", 'wb') as public_pem_file:
            public_pem_file.write(public_pem)
        # Save hashed password, for checking
        password = password.encode()
        digest = hashes.Hash(hashes.SHA1())
        digest.update(password)
        password_hash = digest.finalize()
        with open(f"{self.user}/private/{id}_password.hash", 'wb') as password_file:
            password_file.write(password_hash)


    @staticmethod
    def load(user, id, password):
        digest = hashes.Hash(hashes.SHA1())
        digest.update(password.encode())
        password_hash = digest.finalize()
        # Check password hash
        with open(f"{user}/private/{id}_password.hash", 'rb') as password_file:
            password_hash_file = password_file.read()
            # Hash mismatch, return None
            if(password_hash_file != password_hash):
                return None
        # Load private key
        with open(f"{user}/private/{id}_private.pem", 'rb') as private_pem_file:
            private_pem = private_pem_file.read()
        private_key = serialization.load_pem_private_key(
            private_pem,
            password=password.encode()
        )
        # Load public key
        with open(f"{user}/private/{id}_public.pem", 'rb') as public_pem_file:
            public_pem = public_pem_file.read()
        public_key = serialization.load_pem_public_key(public_pem)
        return KeyPair(user, private_key, public_key)


    def __str__(self):
        return f"{self.user}\t{self.public_key.public_numbers().n % (1 << 64)}\t{self.get_string_representations()[0]}\t{self.get_string_representations()[1]}"
