import hashlib
import multiprocessing as mp
import time
import string
import os


# Worker function executed by each process
def worker(found_event, result_queue, start_counter, step):
    authdata = "ABC123"
    difficulty = 7
    batch_size = 100000
    length = 6

    # Pre-encode static data to reduce per-iteration overhead
    authdata_bytes = authdata.encode()

    # Allowed characters encoded once
    allowed_chars = (
        string.ascii_letters +
        string.digits +
        "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    ).encode()

    base = len(allowed_chars)

    # Reusable buffer to avoid repeated allocations
    buffer = bytearray(authdata_bytes + b' ' * length)
    prefix_len = len(authdata_bytes)

    sha1 = hashlib.sha1
    target_prefix = '0' * difficulty

    # Each process starts at a different counter
    counter = start_counter
    attempts_total = 0

    while not found_event.is_set():
        for _ in range(batch_size):

            # Convert counter to base-N representation (deterministic suffix generation)
            temp = counter

            for i in range(length):

                buffer[prefix_len + i] = allowed_chars[temp % base]
                temp //= base

            hash_hex = sha1(buffer).hexdigest()
            attempts_total += 1

            # Check difficulty condition
            if hash_hex.startswith(target_prefix):
                
                found_event.set()
                result_queue.put(
                    (
                        buffer[prefix_len:].decode(),
                        buffer.decode(),
                        hash_hex,
                        attempts_total,
                        os.getpid()
                    )
                )
                return

            # Skip ahead so processes do not overlap search space
            counter += step


if __name__ == "__main__":
    start_time = time.time()
    cpu_count = mp.cpu_count()
    print(f"Using {cpu_count} cores")

    found_event = mp.Event()
    result_queue = mp.Queue()

    processes = []

    # Assign each process a unique starting point
    for i in range(cpu_count):
        p = mp.Process(
            target=worker,
            args=(found_event, result_queue, i, cpu_count)
        )
        p.start()
        processes.append(p)

    # Wait for first successful result
    suffix, combined, hash_hex, attempts, pid = result_queue.get()
    end_time = time.time()

    total_time = end_time - start_time

    print("\nSuccess!")
    print(f"Found by process PID: {pid}")
    print(f"Suffix: {suffix}")
    print(f"Combined: {combined}")
    print(f"Hash: {hash_hex}")
    print(f"Attempts (by winning process): {attempts}")
    print(f"Total Time: {total_time:.4f} seconds")
    print(f"Approximate Hash/Sec Per Core: {attempts / total_time:.2f}")

    # Terminate remaining processes
    for p in processes:
        p.terminate()
