from typing import List

import models
from models import *
import secrets

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
        user = file.split('_')[1]
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

