import hashlib
import random
import string
import time
import multiprocessing as mp
import os


# Worker function executed by each process
def worker(found_event, result_queue):

    # Local constants kept inside worker to avoid repeated sharing overhead
    authdata = "ABC123"
    difficulty = 6
    batch_size = 100000 
    
    length = 6

    # Pre-encode authdata to avoid encoding cost in every iteration
    authdata_bytes = authdata.encode()

    # Precompute allowed characters once per process
    allowed_chars = string.ascii_letters + string.digits + "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"

    attempts_total = 0

    # Continue until any process finds a valid hash
    while not found_event.is_set():
        for _ in range(batch_size):

            # Generate random suffix locally
            suffix = "".join(random.choice(allowed_chars) for _ in range(length))

            # Combine bytes directly to reduce overhead
            combined = authdata_bytes + suffix.encode()
            hash_hex = hashlib.sha1(combined).hexdigest()
            attempts_total += 1

            # Check difficulty condition
            if hash_hex.startswith('0' * difficulty):
                found_event.set()
                result_queue.put((suffix, combined, hash_hex, attempts_total, os.getpid()))
                return  # Exit immediately on success


if __name__ == "__main__":
    start_time = time.time()

    # Detect available CPU cores
    cpu_count = mp.cpu_count()
    print(f"Using {cpu_count} cores")

    # Shared synchronization primitives
    found_event = mp.Event()
    result_queue = mp.Queue()

    processes = []

    # Spawn one process per CPU core
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
    print(f"Time taken: {end_time - start_time:.4f} seconds for MULTI CORE with 6 difficult level")
    print(f"Hash Attempts Per Second Per Core {attempts/(end_time-start_time):.4f}")

    # Terminate remaining processes
    for p in processes:
        p.terminate()
