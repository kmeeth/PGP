import zlib
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import padding
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


def send_message(message, sender_key_pair, recipient_public_key, need_signature, need_confidentiality, encryption_algorithm):
    X = bytes(f"{str(datetime.now())}\nFrom: {sender_key_pair.id()}\n{message}", 'utf-8')
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

    if need_confidentiality:
        session_key = os.urandom(16)
        
    print(X)

