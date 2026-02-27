import socket
import select
import time
from typing import Optional
# import ahkHelper

# HOST = '198.128.209.117'
HOST = '10.0.0.1'
PORT = 24
TIMEOUT = 0.5

class SPCHelper:
    """Persistent TCP client for the stage controller."""

    def __init__(
        self,
        host: str = HOST,
        port: int = PORT,
        timeout: float = TIMEOUT,
        delimiter: Optional[bytes] = b'\n',
    ):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.delimiter = delimiter
        self.sock: Optional[socket.socket] = None

    # ------------------------------------------------------------------
    # Connection handling
    # ------------------------------------------------------------------
    def connect(self):
        """Open the TCP connection (only once)."""
        if self.sock:
            return

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # `settimeout` is used only for the *connect()* call.
        self.sock.settimeout(self.timeout)
        self.sock.connect((self.host, self.port))

        # After the connection is established we switch to non‑blocking mode.
        self.sock.setblocking(False)
        print(f"Connected to {self.host}:{self.port}")

        # Optional: read any initial banner the device may send.
        try:
            banner = self.read_message(timeout=self.timeout)
            print("Banner:", banner)
        except TimeoutError:
            print("No banner received (timeout).")

    def close(self):
        """Close the socket and forget it."""
        if self.sock:
            self.sock.close()
            self.sock = None
            print("Connection closed.")

    # ------------------------------------------------------------------
    # Send / receive helpers
    # ------------------------------------------------------------------
    def send(self, cmd: str):
        """Send a command string (UTF‑8 encoded)."""
        if not self.sock:
            self.connect()
        assert self.sock is not None
        print(f"Sending: {cmd}")
        self.sock.sendall(cmd.encode('utf-8'))

    # def send(self, cmd: str):
    #     if not self.sock:
    #         self.connect()
    #     assert self.sock is not None
    #     print("DEBUG – type of cmd:", type(cmd), "value:", cmd)  # <‑‑ add this
    #     self.sock.sendall(cmd.encode('utf-8'))

    def receive(self) -> str:
        """Read the reply for the most recent command."""
        if not self.sock:
            raise RuntimeError("Not connected")
        return self.read_message(timeout=self.timeout)

    def query(self, cmd: str) -> str:
        """Convenient one‑liner: send a command and return its reply."""
        self.send(cmd)
        try:
            reply = self.receive()
            print("Reply:", reply)
            return reply
        except TimeoutError:
            # print("No reply (timeout).")
            return ""

    # ------------------------------------------------------------------
    # Context‑manager support (optional)
    # ------------------------------------------------------------------
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    # ------------------------------------------------------------------
    # Read helper (instance method)
    # ------------------------------------------------------------------
    def read_message(
        self,
        *,
        timeout: float = 1,
        bufsize: int = 4096,
    ) -> str:
        """
        Read all data that arrives on *self.sock* within *timeout* seconds.

        Raises
        ------
        TimeoutError
            If no data is received at all before the timeout expires.
        ConnectionError
            If the remote side closes the connection before any data arrives.
        """
        if self.sock is None:
            raise RuntimeError("Socket not connected")

        # The socket is already non‑blocking (set in `connect()`), but calling
        # setblocking(False) again is harmless and makes the function safe if
        # it is ever used elsewhere.
        self.sock.setblocking(False)

        deadline = time.time() + timeout
        received = bytearray()

        while True:
            time_left = deadline - time.time()
            if time_left <= 0:
                break

            # Wait until the socket becomes readable (or we run out of time)
            rlist, _, _ = select.select([self.sock], [], [], time_left)
            if not rlist:
                break

            chunk = self.sock.recv(bufsize)
            if not chunk:          # remote closed the connection
                break
            received.extend(chunk)

        if not received:
            raise TimeoutError(f"No data received within {timeout:.1f}s")

        return received.decode('utf-8', errors='ignore')

    def wait_until_done(
        self,
        poll_interval: float = 5.0,
        overall_timeout: Optional[float] = None,
    ) -> None:
        """
        Repeatedly send *command* and read the reply until the reply contains
        *expected_substring*.

        Parameters
        ----------
        poll_interval : float, default 5.0
            Seconds to wait between polls when the expected text is not yet seen.
        overall_timeout : float or None, default None
            Maximum total time (seconds) to wait.  ``None`` means wait forever.
            If the timeout expires a ``TimeoutError`` is raised.

        Raises
        ------
        TimeoutError
            If *overall_timeout* is given and the expected text is not received
            within that period.
        """
        start_time = time.time()
        command= "status\n"
        expected_substring = "RUNNING DONE"

        while True:
            # Send the status request and read the reply.
            # ``query`` does both send() and receive() for us.
            reply = self.query(command)

            # The device may send extra whitespace or line‑breaks – strip them.
            if expected_substring in reply:
                # Success – the machine reports that it is done.
                print("Done detected.")
                return

            # Not done yet → pause before the next poll.
            if overall_timeout is not None:
                elapsed = time.time() - start_time
                if elapsed + poll_interval > overall_timeout:
                    raise TimeoutError(
                        f"Did not see '{expected_substring}' within "
                        f"{overall_timeout:.1f}s"
                    )
            # pint(f"Not done yet (reply: {reply!r})")
            time.sleep(poll_interval)

# static method that connects once and sends message
def command(text):
    with SPCHelper() as client:
        client.query(text)

#   static method that switches image from path
# must run as administrator and have the image with path clickable in SPC
def switchImage(path):
    print(path)
    ah = ahkHelper.AHKHelper()
    ah.getWindow('Smart Processing Commander')
    ah.clickButton('Browse','Smart Processing Commander')
    ah.ahk.type(path)
    time.sleep(0.5)
    ah.ahk.send("{enter}")

if __name__ == "__main__":
    # Using the class as a context manager is tidy:
    with SPCHelper() as client:
        client.query("compile\n")  # replace with a real command for your device
        client.query("status\n")
