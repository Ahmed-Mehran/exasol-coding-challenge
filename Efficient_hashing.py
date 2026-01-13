import hashlib
import random
import string
import time
import multiprocessing as mp
import os

# Static auth data
authdata = "ABC123"

# Difficulty = number of leading zeros required in hash
difficulty = 5   # number of leading zeros required in hash

# Batch size to reduce inter-process synchronization overhead
# Each process performs many attempts locally before checking shared state
batch_size = 100000  # number of attempts per batch


# Generates a random suffix to append to authdata
def random_string(length=6):
    allowed_chars = string.ascii_letters + string.digits + "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    result = []
    for i in range(length):
        result.append(random.choice(allowed_chars))
    return "".join(result)


# Worker process
# Uses batching to amortize process coordination and event-check overhead
def worker(found_event, result_queue):
    attempts_total = 0

    # Continue work until another process signals success
    while not found_event.is_set():
        # Perform a large batch of hash attempts locally
        for _ in range(batch_size):

            suffix = random_string()
            combined = authdata + suffix

            hash_hex = hashlib.sha1(combined.encode()).hexdigest()
            attempts_total += 1

            # Check difficulty condition
            if hash_hex.startswith('0' * difficulty):
                # Signal all processes to stop
                found_event.set()

                # Send result to main process
                result_queue.put((suffix, combined, hash_hex, attempts_total, os.getpid()))
                return  # Exit immediately on success


if __name__ == "__main__":
    start_time = time.time()

    # Number of CPU cores available
    cpu_count = mp.cpu_count()
    print(f"Using {cpu_count} cores")

    # Shared synchronization primitives
    found_event = mp.Event()
    result_queue = mp.Queue()

    processes = []

    # Spawn one worker per CPU core
    for _ in range(cpu_count):
        p = mp.Process(target=worker, args=(found_event, result_queue))
        p.start()
        processes.append(p)

    # Wait for first successful result
    suffix, combined, hash_hex, attempts, pid = result_queue.get()
    end_time = time.time()

    print("\nSuccess!")
    print(f"Found by process PID: {pid}")
    print(f"Suffix: {suffix}")
    print(f"Combined: {combined}")
    print(f"SHA1 Hash: {hash_hex}")
    print(f"Attempts (by winning process): {attempts}")
    print(f"Time taken: {end_time - start_time:.4f} seconds for MULTI CORE with {difficulty} difficult level")
    print(f"Hash Attempts Per Second Per Core {attempts/(end_time-start_time):.4f}")

    # Terminate remaining processes after solution is found
    for p in processes:
        p.terminate()
