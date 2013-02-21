import hashlib
import uuid


def get_random_hash():
    return hash_string(str(uuid.uuid4()))


def hash_string(string):
    return hashlib.sha256(string).hexdigest()
