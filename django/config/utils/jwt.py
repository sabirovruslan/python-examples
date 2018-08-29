import os
import jwt


JWT_KEY = os.environ.get('JWT_KEY')
ALGORITHM = 'HS256'


def encode(id):
    return jwt.encode({'id': id}, JWT_KEY, algorithm=ALGORITHM)


def decode(hash_string):
    return jwt.decode(hash_string, JWT_KEY, algorithms=[ALGORITHM])


def encode_user(user):
    return encode(user.id)
