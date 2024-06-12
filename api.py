from typing import List

import models
from models import *
import secrets

# These are user : ring dicts
# Ring is a list of keys for public, and pairs for private
imported_rings = {}
private_rings = {}

current_user = "kmeeth"


def update_imported_ring(owner):
    ring = []
    dir = f"{owner}/import"
    for file in os.listdir(dir):
        print(file)
        id = (int)(file.split('_')[0])
        user = file.split('_')[1]
        ring.append(models.ImportedKey.load(owner, user, id))
    return ring


def update_private_ring(user):
    return None

