#!/usr/bin/env python3
"""Generate a SHA512 password hash for data/users.json."""
from passlib.hash import sha512_crypt
import getpass
import sys


def main():
    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Confirm: ")
    if password != confirm:
        print("Passwords do not match.", file=sys.stderr)
        sys.exit(1)
    print(sha512_crypt.hash(password))


if __name__ == "__main__":
    main()
