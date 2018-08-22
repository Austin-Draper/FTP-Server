from socket import *
import os
import sys
import os.path

serverPort = int(sys.argv[1])
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)

print("The server is listening on port", serverPort, "...")

while 1:

        print("Waiting for client...")
        connectionSocket, addr = serverSocket.accept()
        print("Client found!")

        while 1:
                cmd = connectionSocket.recv(100)
                print("Command received was '", cmd, "'")
                
                if cmd.startswith("get"):
                        #get requested file name
                        return_file = cmd[4:]

                        if not return_file:
                                break

                        #Get the ephemeral port from the client
                        ephemeralPort = int(connectionSocket.recv(10))
                        print("Generated ephemeral port is: ", ephemeralPort)

                        #Create new connection for transfering the data
                        server_socket = socket(AF_INET, SOCK_STREAM)
                        server_socket.connect(("localhost", ephemeralPort))

                        strng = ""

                        #read file
                        fo = open(return_file, "rb")
                        strng = fo.read()
                        fo.close()

                        #Get the size of the string and 0 pad till 10 bytes
                        size = str(len(strng))
                        while len(size) < 10:
                                size = "0" + size
                        #put size header first
                        strng = size + strng

                        Bytes_Sent = 0
                        #Send all the data so client
                        while len(strng) > Bytes_Sent:
                                Bytes_Sent += server_socket.send(strng[Bytes_Sent:])

                        print("GET SUCCESS")
                        connectionSocket.send("1")

                elif cmd.startswith("put"):
                        recv_file = cmd[4:]

                        if not recv_file:
                                break

                        #Create an ephemeral port
                        data_socket = socket(AF_INET, SOCK_STREAM)
                        #Bind the socket to port 0
                        data_socket.bind(("",0))
                        #Retreive the ephemeral port number
                        print("Generated ephemeral port is: ", data_socket.getsockname()[1])

                        #Send the ephemeral port number to the client as a string
                        connectionSocket.send(str(data_socket.getsockname()[1]))
                        data_socket.listen(1)

                        print("Waiting for connection to client")

                        #Accept the connection from the cliient
                        connSocket, addr = data_socket.accept()
                        print("Received connection from client.")

                        #Get size of data coming from client side
                        #SizeBuffer = is it bytesSent? This needs to be size of data received from server.
                        #I can create a function to call every time this needs to be done.

                        Recv_Buffer = ""
                        Temp_Buffer = ""
                        while len(Recv_Buffer) < 10:
                            Temp_Buffer = connSocket.recv(10)
                            if not Temp_Buffer:
                                break
                            Recv_Buffer += Temp_Buffer

                        SizeBuffer = Recv_Buffer

                        Size = int(SizeBuffer)

                        #Get the data (list of files on server) from the server
                        Recv_Buffer = ""
                        Temp_Buffer = ""
                        while len(Recv_Buffer) < Size:
                            Temp_Buffer = connSocket.recv(Size)
                            if not Temp_Buffer:
                                break
                            Recv_Buffer += Temp_Buffer

                        Data = Recv_Buffer
                        #Print the data
                        print("Size of file is: ", Size)
                        
                        #write to file
                        fo = open(recv_file, "wb")
                        fo.write(Data)
                        fo.close()

                        print("PUT SUCCESS")

                        connFlag = connectionSocket.recv(4096)

                elif cmd == "quit":
                        #Send a 0 back to inform client ftp session is done
                        connectionSocket.send("0")
                        #Break out of while loop
                        break


                elif cmd == "ls":
                        #Get the ephemeral port from the client
                        ephemeralPort = int(connectionSocket.recv(10))
                        print("Generated ephemeral port is: ", ephemeralPort)

                        #Create new connection for transfering the data
                        server_socket = socket(AF_INET, SOCK_STREAM)
                        server_socket.connect(("localhost", ephemeralPort))

                        strng = ""

                        #Get file path of running file
                        path = os.path.dirname(os.path.realpath(__file__))

                        #list of all files in files directory
                        ls = os.listdir(path)

                        #Concatinate string for all items
                        for item in ls:
                                strng = strng + item + "\n"

                        #Get the size of the string and 0 pad till 10 bytes
                        size = str(len(strng))
                        while len(size) < 10:
                                size = "0" + size
                        #put size header first
                        strng = size + strng

                        Bytes_Sent = 0
                        #Send all the data so client
                        while len(strng) > Bytes_Sent:
                                Bytes_Sent += server_socket.send(strng[Bytes_Sent:])

                        print("LS: SUCCESS")

                        connectionSocket.send("1")

        #Close the connection
        server_socket.close()