class ImportedKey:
    user: str
    public_key: int

    def __init__(self, user: str, public_key: int):
        self.public_key = public_key
        self.user = user


    def __str__(self):
        return f"{self.user}\t{self.public_key % (1 << 64)}\t{self.public_key}"
