from typing import List
from models import *
import secrets

imported_ring: List[ImportedKey] = []
private_ring: List[KeyPair] = []


def update_imported_ring(user):
    return [ImportedKey(user, private_ring[0].public_key)]


def update_private_ring(user, password, size):
    return [KeyPair(user, password, size)]

