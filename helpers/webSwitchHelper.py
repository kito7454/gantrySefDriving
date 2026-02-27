import socket
import time

# for this helper to work, you need to make sure the webswitch ip adress is the following
# webswtich serial num: 00-0C-C8-07-4D-79
# for help, see setups scheme option #2 on this
# website:
# https://controlbyweb.com/wp-content/uploads/2024/03/webswitch-plus-users-manual.pdf

# http://192.168.1.50/setup.html this in a browser can be used to control webswitch
# sometimes 192.168.1.2
# username: admin
# pass: webrelay or bulltd


host = "192.168.1.2"
port = 80

request0 = (
    "GET /customState.xml?outlet1=0 HTTP/1.1\r\n"
    "Host: {}\r\n\r\n".format(host)
)

request1= (
    "GET /customState.xml?outlet1=1 HTTP/1.1\r\n"
    "Host: {}\r\n\r\n".format(host)
)

def switch(arg):

    if arg ==1:
        request = request1
    else:
        request = request0

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(request.encode())
        response = s.recv(4096)
        print(response.decode())
        return response.decode()

if __name__ == "__main__":
    switch(1)
    time.sleep(0.5)
    switch (0)
