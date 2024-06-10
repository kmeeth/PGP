from typing import List
from models import *
import secrets

imported_ring: List[ImportedKey] = []


def update_imported_ring(user: str):
    return [generate_key()]


def generate_key():
    return ImportedKey("kmeeth", secrets.randbits(1024))
