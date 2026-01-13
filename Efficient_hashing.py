import hashlib
import random
import string
import time
import multiprocessing as mp
import os

# Static auth data provided as part of the challenge
authdata = "ABC123"

# Difficulty = number of leading zeros required in the hash
difficulty = 4


# Generates a random suffix to append to authdata
# Each process independently generates random strings
def random_string(length=6):
    allowed_chars = (
        string.ascii_letters
        + string.digits
        + "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    )
    result = []
    for i in range(length):
        result.append(random.choice(allowed_chars))
    return "".join(result)


# Worker function executed by each process
# All processes run the SAME code but explore DIFFERENT parts of the search space
def worker(found_event, result_queue):
    attempts = 0

    # Loop continues until some process finds a valid hash
    while not found_event.is_set():
        attempts += 1

        suffix = random_string()
        combined = authdata + suffix

        # Hash computation (CPU-bound work)
        hash_hex = hashlib.sha1(combined.encode()).hexdigest()

        # Check if hash satisfies difficulty condition
        if hash_hex.startswith('0' * difficulty):
            # Signal other processes to stop
            found_event.set()

            # Send result back to main process
            result_queue.put(
                (suffix, combined, hash_hex, attempts, os.getpid())
            )
            break


if __name__ == "__main__":
    start_time = time.time()

    # Number of CPU cores available
    cpu_count = mp.cpu_count()
    print(f"Using {cpu_count} cores")

    # Event used for inter-process coordination
    # Once set, all processes should stop work
    found_event = mp.Event()

    # Queue used to collect result from the winning process
    result_queue = mp.Queue()

    processes = []

    # Spawn one worker per CPU core
    for _ in range(cpu_count):
        p = mp.Process(target=worker, args=(found_event, result_queue))
        p.start()
        processes.append(p)

    # Wait for the first successful result
    suffix, combined, hash_hex, attempts, pid = result_queue.get()
    end_time = time.time()

    print("\nSuccess!")
    print(f"Found by process PID: {pid}")
    print(f"Suffix: {suffix}")
    print(f"Combined: {combined}")
    print(f"MD5 Hash: {hash_hex}")
    print(f"Attempts (by winning process): {attempts}")
    print(
        f"Time taken: {end_time - start_time:.4f} seconds "
        f"for MULTI CORE with difficulty {difficulty}"
    )
    print(
        f"Hash Attempts Per Second Per Core "
        f"{attempts / (end_time - start_time):.4f}"
    )

    # Terminate all remaining processes
    # Many processes are killed after partial work → wasted computation
    for p in processes:
        p.terminate()
