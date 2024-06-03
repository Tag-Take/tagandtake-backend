from django.contrib.auth.hashers import make_password, check_password

def hash_password(plain_password):
    return make_password(plain_password)

def check_password_validity(plain_password, hashed_password):
    return check_password(plain_password, hashed_password)