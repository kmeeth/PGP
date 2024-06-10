from api import *

if __name__ == "__main__":
    for i in range(4):
        imported_ring = update_imported_ring("kmeeth")
        for key in imported_ring:
            print(key)