import os
import zlib
from datetime import datetime

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.padding import PKCS7

import models
from models import *

# These are user : ring dicts
# Ring is a list of keys for public, and pairs for private
import_rings = {}
private_rings = {}

current_user = "kmeeth"


def update_import_ring(owner):
    ring = []
    dir = f"{owner}/import"
    os.makedirs(dir, exist_ok=True)
    for file in os.listdir(dir):
        id = (int)(file.split('_')[0])
        user = file.split('_')[1].split('.')[0]
        ring.append(models.ImportedKey.load(owner, user, id))
    return ring


def update_private_ring(user):
    ring = []
    dir = f"{user}/private"
    os.makedirs(dir, exist_ok=True)
    for file in os.listdir(dir):
        id = (int)(file.split('_')[0])
        # Avoid duplication
        if file.split('_')[1] != "public.pem":
            continue
        ring.append(models.KeyPair.load(user, id, "x", False))
    return ring


def send_message(message, sender_key_pair, recipient_public_key, need_signature, encryption_algorithm, filename):
    X = bytes(f"{str(datetime.now())}\nFrom: {sender_key_pair.id()}\nTo: {recipient_public_key.id()}\n{message}", 'utf-8')
    separator = b"||||||||"
    hasher = hashes.Hash(hashes.SHA1())
    hasher.update(X)
    hashed_message = hasher.finalize()
    if need_signature:
        signature = sender_key_pair.private_key.sign(
            hashed_message,
            padding.PKCS1v15(),
            hashes.SHA1()
        )
        X = X + separator + signature

    X = zlib.compress(X)

    if encryption_algorithm != None:
        session_key = os.urandom(16)
        cipher = Cipher(algorithms.CAST5(session_key) if encryption_algorithm == 'CAST5' else algorithms.AES128(session_key), modes.CFB(os.urandom(8 if encryption_algorithm == 'CAST5' else 16)))
        encryptor = cipher.encryptor()
        padder = PKCS7(16).padder()
        padded_data = padder.update(message.encode()) + padder.finalize()
        encrypted_message = encryptor.update(padded_data) + encryptor.finalize()

        encrypted_key = recipient_public_key.public_key.encrypt(
            session_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None
            )
        )
        X = encrypted_message + separator + encrypted_key + separator + bytes(encryption_algorithm, 'utf-8') + separator + bytes(str(sender_key_pair.id()), 'utf-8')

    # R64 here

    os.makedirs("messages", exist_ok=True)
    with open(f"messages/{filename}", 'wb') as file:
        file.write(X)
    return X

