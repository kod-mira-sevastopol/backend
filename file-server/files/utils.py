import hashlib

MB = 1024 * 1024

sizes = {
    "photos": MB * 15,
    "videos": MB * 100,
    "files": MB * 150
}


def generate_hash_name(filename: str):
    hash_object = hashlib.sha256(filename.encode())
    return hash_object.hexdigest()
