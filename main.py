import api

if __name__ == "__main__":
    api.private_ring = api.update_private_ring("kmeeth", "dobrojutro", 1024)
    api.imported_ring = api.update_imported_ring("kmeeth")
    for key in api.imported_ring:
        print(key)