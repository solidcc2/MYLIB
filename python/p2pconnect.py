# code with Python 3.7.11
# Function Summary:
#      Peer to Peer String Socket Lib

import socket as socket
import argparse
class P2PServer:
    def __init__(self, server = ("127.0.0.1", 3344), block = True):
        self._server = server # (ip, port)
        self._init = False
        self._buf = b""
        self._pos = -1
        self._block = block

    def connectInit(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(self._server)
        sock.listen(1)
        self._conn, self._clientAddr = sock.accept()
        self._conn.setblocking(self._block)
        self._init = True
    
    def recv(self):
        if self._init == False:
            print("connect not init")
            return
        if self._block == True:
            while self._pos == -1:
                self._pos = self._buf.find(ord('\n'))
                if self._pos == -1:
                    self._buf += self._conn.recv(1024)
        else:
            try:
                while self._pos == -1:
                    self._pos = self._buf.find(ord('\n'))
                    if self._pos == -1:
                        self._buf += self._conn.recv(1024)
            except BlockingIOError as e:
                return ""
        msg = self._buf[:self._pos]
        self._buf = self._buf[self._pos+1:]
        self._pos = -1
        return str(msg, encoding='utf8')  # default utf8
    
    def send(self, msg):   
        if self._init == False:
            print("connect not init")
            return 
        if '\n' not in msg:
            msg += "\n"
        self._conn.sendall(str.encode((msg + "\n"), encoding='utf8'))
    
    def close(self):
        self._conn.close()

class P2PClient:
    def __init__(self, server=("127.0.0.1", 3344), block = True):
        self._server = server
        self._init = False
        self._buf = b""
        self._pos = -1
        self._block = block

    def connectInit(self):
        self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._conn.connect(self._server)
        self._conn.setblocking(self._block)
        self._init = True

    def recv(self):
        if self._init == False:
            print("connect not init")
            return
        if self._block == True:
            while self._pos == -1:
                self._pos = self._buf.find(ord('\n'))
                if self._pos == -1:
                    self._buf += self._conn.recv(1024)
        else:
            try:
                while self._pos == -1:
                    self._pos = self._buf.find(ord('\n'))
                    if self._pos == -1:
                        self._buf += self._conn.recv(1024)
            except BlockingIOError as e:
                return ""
        msg = self._buf[:self._pos]
        self._buf = self._buf[self._pos+1:]
        self._pos = -1
        return str(msg, encoding='utf8')  # default utf8
    
    def send(self, msg):   
        if self._init == False:
            print("connect not init")
            return 
        if '\n' not in msg:
            msg += "\n"
        self._conn.sendall(str.encode((msg + "\n"), encoding='utf8'))
    
    def close(self):
        self._conn.close()

def server(addr, block):
    """
        wait connect...
        > CONNECT
        wait client msg...
        > RECV
        msg is ({msg})
        send msg({msg})...
        > SEND
        close
        > CLOSE
    """
    p2pServer = P2PServer(addr, block)
    print(f"\n\rblock server init...")
    print(f"\n\rwait connect...")
    p2pServer.connectInit()
    print(f"\n\rwait client msg...")
    msg = ""
    while msg == "":
        msg = p2pServer.recv()
    print(f"\n\rmsg is ({msg})")
    toSend = "I am server"
    print(f"\n\rsend msg ({toSend})...")
    p2pServer.send(toSend)
    print(f"\n\rclose")
    p2pServer.close()

def client(addr, block):
    """
        connect to {addr[0]}:{addr[1]} ...
        > CONNECT
        send msg ({msg})
        > SEND
        msg is ({msg})
        wait server msg...
        > RECV
        msg is ({msg})
        close
        > CLOSE
    """
    p2pClient = P2PClient(addr, block)
    print(f"\n\rconnect to {addr[0]}:{addr[1]} ...")
    p2pClient.connectInit()
    msg = "I am client"
    print(f"\n\rsend msg ({msg})")
    p2pClient.send(msg)
    print(f"\n\rwait server msg...")
    msg = ""
    while msg == "":
        msg = p2pClient.recv()
    print(f"\n\rmsg is ({msg})")
    print(f"\n\rclose")
    p2pClient.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="P2PConnect Default Test")
    parser.add_argument("role", help="role of process, one of client and server")
    parser.add_argument("-s", "--server", type=str, default="127.0.0.1")
    parser.add_argument("-p", "--port", type=int, default=3344)
    parser.add_argument("-b", "--block", type=bool, default=True)
    args = parser.parse_args()
    if args.role == "server":
        server((args.server, args.port), args.block)
    elif args.role == "client":
        client((args.server, args.port), args.block)
    else:
        parser.print_help()

