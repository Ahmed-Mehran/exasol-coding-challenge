import socket
import ssl
import hashlib
import multiprocessing as mp
import string

# ---------------- POW CODE ----------------
def worker(found_event, result_queue, worker_id, total_workers, authdata, difficulty):
    batch_size = 200000
    length = 7

    authdata_bytes = authdata.encode()
    allowed_chars = (
        string.ascii_letters +
        string.digits +
        "!\"#$%&'()*+,-./:;<=>?@[\\]^_{|}~"
    ).encode()

    base = len(allowed_chars)
    prefix_len = len(authdata_bytes)
    target_prefix = '0' * difficulty

    # --- Odometer Initialization ---
    # We start each worker at a different starting point to cover different ground
    indices = [0] * length
    indices[0] = (worker_id * (base // total_workers)) % base


    # Pre-build the buffer
    current_suffix = bytes([allowed_chars[i] for i in indices])
    buffer = bytearray(authdata_bytes + current_suffix)
    
    sha1 = hashlib.sha1

    while not found_event.is_set():

        for _ in range(batch_size):

            for i in range(length - 1, -1, -1):

                indices[i] += 1

                if indices[i] < base:
                    buffer[prefix_len + i] = allowed_chars[indices[i]]
                    break
                
                else:
                    indices[i] = 0
                    buffer[prefix_len + i] = allowed_chars[0]

            if sha1(buffer).hexdigest().startswith(target_prefix):
                found_event.set()
                result_queue.put(buffer[prefix_len:].decode())
                return


def solve_pow(authdata, difficulty):
    found_event = mp.Event()
    result_queue = mp.Queue()
    cpu_count = mp.cpu_count()

    processes = []
    for i in range(cpu_count):
        p = mp.Process(
            target=worker,
            args=(found_event, result_queue, i, cpu_count, authdata, difficulty)
        )
        p.start()
        processes.append(p)

    suffix = result_queue.get()

    for p in processes:
        p.terminate()

    return suffix


# ---------------- MAIN ENTRY POINT ----------------
if __name__ == "__main__":

    # -------- TLS SETUP --------
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False        
    context.verify_mode = ssl.CERT_NONE  
    context.load_cert_chain(certfile="client.crt", keyfile="client.key")

    sock = socket.create_connection(("18.202.148.130", 3336))
    conn = context.wrap_socket(sock)

    authdata = ""

    print("Connected to server, waiting for commands...")

    # -------- PROTOCOL LOOP --------
    while True:
        line = conn.recv(4096).decode().strip()
        if not line:
            print("Server closed connection or no data received.")
            break

        print("Received:", line)
        args = line.split(" ")

        if args[0] == "HELO":
            conn.sendall(b"TOAKUEI\n")

        elif args[0] == "POW":
            authdata = args[1]
            difficulty = int(args[2])
            print(f"Starting POW: authdata={authdata}, difficulty={difficulty}")

            suffix = solve_pow(authdata, difficulty)
            print(f"POW solved: suffix={suffix}")
            conn.sendall((suffix + "\n").encode())

        elif args[0] == "NAME":
            token = args[1]
            h = hashlib.sha1((authdata + token).encode()).hexdigest()
            conn.sendall(f"{h} Mehran Ahmed Dar\n".encode())

        elif args[0] == "MAILNUM":
            token = args[1]
            h = hashlib.sha1((authdata + token).encode()).hexdigest()
            conn.sendall(f"{h} 1\n".encode())

        elif args[0] == "MAIL1":
            token = args[1]
            h = hashlib.sha1((authdata + token).encode()).hexdigest()
            conn.sendall(f"{h} mehranahmed22@gmail.com\n".encode())

        elif args[0] == "SKYPE":
            token = args[1]
            h = hashlib.sha1((authdata + token).encode()).hexdigest()
            conn.sendall(f"{h} N/A\n".encode())

        elif args[0] == "BIRTHDATE":
            token = args[1]
            h = hashlib.sha1((authdata + token).encode()).hexdigest()
            conn.sendall(f"{h} 10.06.1997\n".encode())

        elif args[0] == "COUNTRY":
            token = args[1]
            h = hashlib.sha1((authdata + token).encode()).hexdigest()
            conn.sendall(f"{h} India\n".encode())

        elif args[0] == "ADDRNUM":
            token = args[1]
            h = hashlib.sha1((authdata + token).encode()).hexdigest()
            conn.sendall(f"{h} 1\n".encode())

        elif args[0] == "ADDRLINE1":
            token = args[1]
            h = hashlib.sha1((authdata + token).encode()).hexdigest()
            conn.sendall(f"{h} Jammu Kashmir Srinagar Baghat Barzulla\n".encode())

        elif args[0] == "END":
            conn.sendall(b"OK\n")
            print("Received END. Closing connection.")
            break

        elif args[0] == "ERROR":
            print("Server error:", " ".join(args[1:]))
            break

    conn.close()
    print("Connection closed.")