import socket
import sys
import ssl

def StartServerProcess():

    IsTLSEnabledAtServer = 0

    s = socket.socket()
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    port = 9009
    s.bind((host, port))
    
    s.listen(5)
    print("Waiting for incoming connections.")
    conn, addr = s.accept()
    print("Received connection from ", addr[0], "(", addr[1], ")")

    print("\n******************************************")
    print("You are chatting in insecure manner")
    print("******************************************\n")

    while True:

        while(IsTLSEnabledAtServer != 1):
            Received = conn.recv(1024)
            Received = Received.decode()
            print("Client: " + str(Received))

            if (Received ==  'chat_close'):
                print("Closing connection")
                exit(0)

            elif (Received ==  'chat_STARTTLS'):
                print("Sending Acknowledgement");
                message = "chat_STARTTLS_ACK"
                conn.send(message.encode())
                IsTLSEnabledAtServer = 1
                print("\n******************************************")
                print("TLS is enabled at server side. Now chat will be encrypted")
                print("******************************************\n")

                # TLS is enabled here
                server_cert = 'bob.crt'
                server_key = 'bob.key'
                client_certs = 'root.crt'
                context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                #context.verify_mode = ssl.CERT_REQUIRED
                context.load_cert_chain(certfile=server_cert, keyfile=server_key)
                context.keylog_filename="keylog.txt"
                #context.load_verify_locations(cafile=client_certs)
                conn = context.wrap_socket(conn, server_side=True)

                break
            
            else:
                message = input(str("Server : "))
                conn.send(message.encode())
                if(message.find('chat_close') != -1):
                    exit(0)

        Received = conn.recv(1024)
        Received = Received.decode()
        print("Client: " + str(Received))

        if (Received ==  'chat_close'):
            print("Closing connection")
            exit(0)

        else:
            message = input(str("Server : "))
            conn.send(message.encode())
            if(message.find('chat_close') != -1):
                exit(0)

    
def StartClientProcess(serverToConnnect):
    
    IsTLSEnabledAtClient = 0

    s = socket.socket()
    shost = socket.gethostname()
    ip = socket.gethostbyname(shost)
    #print(shost, "(", ip, ")\n")

    Server_IP = socket.gethostbyname(str(serverToConnnect))
    Server_Port = str('9009')

    s.connect((str(Server_IP), int(Server_Port)))
    print("Connected to server")

    print("\n******************************************")
    print("You are chatting in insecure  manner")
    print("******************************************\n")

    while True:
        while(IsTLSEnabledAtClient != 1):
            message = input(str("Client : "))
            s.send(message.encode())
            if(message.find('chat_close') != -1):
                exit(0)

            Received = s.recv(1024)
            Received = Received.decode()
            print("Server: " + str(Received))

            if (Received ==  'chat_close'):
                print("Closing connection")
                exit(0)

            if (Received ==  'chat_STARTTLS_ACK'):
                IsTLSEnabledAtClient = 1

                print("\n******************************************")
                print("TLS is enabled at server side. Now chat will be encrypted")
                print("******************************************\n")

                # TLS is enabled here
                server_cert = 'root.crt'
                client_cert = 'alice.crt'
                client_key = 'alice.key'
                context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
                #context.load_cert_chain(certfile=client_cert, keyfile=client_key)
                context.check_hostname = False
                s = context.wrap_socket(s, server_side=False, server_hostname=shost, do_handshake_on_connect=False)
                s.do_handshake()

                break

            if (Received ==  'chat_STARTTLS_NOT_SUPPORTED'):
                break

        message = input(str("Client : "))
        s.send(message.encode())
        if(message.find('chat_close') != -1):
            exit(0)

        Received = s.recv(1024)
        Received = Received.decode()
        print("Server: " + str(Received))

        if (Received ==  'chat_close'):
            print("Closing connection")
            exit(0)


    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Invalid no  of arguments")
        exit(-1)

    if(sys.argv[1] == "-c"):
        print("I am client")
        serverToConnnect = sys.argv[2]
        StartClientProcess(serverToConnnect)

    elif(sys.argv[1] == "-s"):
        print("I am server")
        StartServerProcess()

    else:
        print("Command line arguments are incorrect")
        