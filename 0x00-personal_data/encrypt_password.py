#!/usr/bin/env python3
""" The Encrypted Password Module. """

import bcrypt


def hash_password(password: str) -> bytes:
    """
    Hashes the given password using bcrypt.

    Args:
        password (str): The plaintext password.

    Returns:
        bytes: The salted, hashed password as a byte string.
    """
    gen_salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(password.encode(), gen_salt)
    return hashed_pw


def is_valid(hashed_pw: bytes, plain_pw: str) -> bool:
    """
    Validates the provided password against the hashed password using bcrypt.

    Args:
        hashed_password (bytes): The salted, hashed password as a byte string.
        password (str): The plaintext password to validate.

    Returns:
        bool: True if the password matches the hashed password, False otherwise.
    """
    return bcrypt.checkpw(plain_pw.encode(), hashed_pw)

