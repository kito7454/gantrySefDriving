import socket
import time


def send_to_localhost(port, message):
    """Send a UTF-8 encoded message to localhost on the given TCP port."""
    if not isinstance(port, int) or not (1 <= port <= 65535):
        raise ValueError("Port must be an integer between 1 and 65535.")
    if not isinstance(message, str):
        raise ValueError("Message must be a string.")

    try:
        # Create a TCP socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)  # 5-second timeout for connection
            sock.connect(("127.0.0.1", port))
            sock.sendall(message.encode("utf-8"))
            print(f"Sent to localhost:{port} -> {message}")
    except ConnectionRefusedError:
        print(f"Error: No server is listening on port {port}.")
    except socket.timeout:
        print("Error: Connection timed out.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    # Example usage
    try:
        send_to_localhost(9004, "CAMERA ON\n")
        time.sleep(15)
        send_to_localhost(9004, "START 10\n")
        time.sleep(5)
        send_to_localhost(9004, "STOP\n")
    except ValueError as ve:
        print(f"Input error: {ve}")
