import sys
import socket
from html.parser import HTMLParser

#username = sys.argv[0]
#password = sys.argv[1]
HOST = 'webcrawler-site.ccs.neu.edu'
PORT = 80
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)



def login():
    login_get_request = ('GET /accounts/login/ HTTP/1.1\n'
        'Host: webcrawler-site.ccs.neu.edu\n\n')

    sock.connect((HOST, PORT))
    sock.sendall(bytes(login_get_request, "utf-8"))
    login_page_response = str(sock.recv(8192), "utf-8")
    print(login_page_response)

login()