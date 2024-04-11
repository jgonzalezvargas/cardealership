import hashlib

def hash_password(password):
    hashed_pss = hashlib.sha256(password.encode()).hexdigest()
    return hashed_pss