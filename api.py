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

# Used for concatenation
separator = b"||||||||"
flag_separator = b"########"

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
    # Load message with added info
    X = bytes(f"{str(datetime.now())}\nFrom: {sender_key_pair.id()}\nTo: {recipient_public_key.id()}\n{message}", 'utf-8')

    # Sign message if needed
    if need_signature:
        hasher = hashes.Hash(hashes.SHA1())
        hasher.update(X)
        hashed_message = hasher.finalize()
        signature = sender_key_pair.private_key.sign(
            hashed_message,
            padding.PKCS1v15(),
            hashes.SHA1()
        )
        X = X + separator + signature

    # Compress message
    X = zlib.compress(X)

    # Encrypt message if needed
    if encryption_algorithm != None:
        # Encrypt message with session key
        session_key = os.urandom(16)
        print(session_key)
        cipher = Cipher(algorithms.CAST5(session_key) if encryption_algorithm == 'CAST5' else algorithms.AES128(session_key), modes.CFB(os.urandom(8 if encryption_algorithm == 'CAST5' else 16)))
        encryptor = cipher.encryptor()
        padder = PKCS7(16).padder()
        padded_data = padder.update(message.encode()) + padder.finalize()
        encrypted_message = encryptor.update(padded_data) + encryptor.finalize()

        # Encrypt session key with recipient's public key
        encrypted_key = recipient_public_key.public_key.encrypt(
            session_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None
            )
        )
        # Concatenate
        X = encrypted_message + separator + encrypted_key

    # Added tags
    X = X + flag_separator + bytes(str(sender_key_pair.id()), 'utf-8')
    X = X + separator + (b"SIGN" if need_signature else b"NOSIGN")
    X = X + separator + (b"NOENC" if encryption_algorithm == None else bytes(encryption_algorithm, 'utf-8'))

    # Base64
    X = base64.b64encode(X)

    os.makedirs("messages", exist_ok=True)
    with open(f"messages/{filename}", 'wb') as file:
        file.write(X)
    return X


def receive_message(filename, recipient_user, recipient_id, recipient_password):
    # Read message
    with open(f"messages/{filename}", 'rb') as file:
        X = file.read()

    # Base64 decode
    X = base64.b64decode(X)
    print(X)

    # Get parts
    flags = X.split(flag_separator)[1]
    sender_id = int(flags.split(separator)[0].decode('utf-8'))
    is_signed = (flags.split(separator)[1].decode('utf-8') == b"SIGN")
    encryption_algorithm = flags.split(separator)[2].decode('utf-8')
    if encryption_algorithm == "NOENC":
        encryption_algorithm = None
    X = X.split(flag_separator)[0]
    print(X)

    # Decrypt if needed
    if encryption_algorithm != None:
        encrypted_message = X.split(separator)[0]
        encrypted_key = X.split(separator)[1]
        recipient_key_pair = None
        for key_pair in private_rings[recipient_user]:
            if recipient_id == key_pair.id():
                recipient_key_pair = key_pair
                break
        if recipient_key_pair == None:
            return "Failed: This message does not seem to be for you."
        recipient_key_pair = KeyPair.load(recipient_user, recipient_id, recipient_password, True)
        session_key = recipient_key_pair.private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None
            )
        )
        print(session_key)

