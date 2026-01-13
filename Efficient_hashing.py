import hashlib
import random
import string
import time

# Test authentication data provided by the problem
authdata = "ABC123"

# Difficulty = number of leading zeros required in SHA1 hash
difficulty = 4


def random_string(length=6):
    """
    Generates a random suffix of given length using
    alphanumeric characters and common symbols.
    """
    allowed_chars = (
        string.ascii_letters +
        string.digits +
        "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    )
    return "".join(random.choice(allowed_chars) for _ in range(length))


# Start timing to measure hashing performance
start_time = time.time()
attempts = 0

# Brute-force loop: keep generating hashes until difficulty is satisfied
while True:
    attempts += 1

    suffix = random_string()
    combined = authdata + suffix

    # Compute SHA1 hash of the combined string
    hash_hex = hashlib.sha1(combined.encode()).hexdigest()

    # Check if hash meets difficulty requirement
    if hash_hex.startswith('0' * difficulty):
        end_time = time.time()

        print(f"Success! Suffix: {suffix}")
        print(f"Suffix length: {len(suffix)}")
        print(f"First character of suffix: {suffix[0]}")
        print(f"Combined string: {combined}")
        print(f"SHA1 Hash: {hash_hex}")
        print(f"Attempts: {attempts}")

        # Performance metrics for single-core execution
        duration = end_time - start_time
        print(f"Time taken: {duration:.4f} seconds (single core)")
        print(f"Hashes per second: {attempts / duration:.4f}")

        break
