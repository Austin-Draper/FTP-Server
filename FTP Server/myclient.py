from socket import *
import os
import sys
import os.path


serverName = sys.argv[1]
serverPort = int(sys.argv[2])

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

while True:
    cmd = raw_input("ftp> ")

    if cmd.startswith('get'):
        #get the file name to request
        get_file = cmd[4:]

        if not get_file:
            break

        print("requesting file: ", get_file)

        #Declare all variables here
        Data = ""
        Size = 0
        SizeBuffer = ""

        #Create a socket
        clientSocket.send(cmd)

        #Create an ephemeral port
        welcomeSocket = socket(AF_INET, SOCK_STREAM)
        #Bind the socket to port 0
        welcomeSocket.bind(("",0))
        #Retreive the ephemeral port number
        print("Generated ephemeral port is: ", welcomeSocket.getsockname()[1])

        #Send the ephemeral port number to the server as a string
        clientSocket.send(str(welcomeSocket.getsockname()[1]))
        welcomeSocket.listen(1)

        print("Waiting for connection to server")

        #Accept the connection from the server
        connSocket, addr = welcomeSocket.accept()
        print("Received connection from server.")

        #Get size of data coming from server side
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
        fo = open(get_file, "wb")
        fo.write(Data)
        fo.close()

        connFlag = clientSocket.recv(4096)
        print("Transfered: ", get_file, " bytes: ", Size)


    elif cmd.startswith("put"):
        put_file = cmd[4:]

        if not put_file:
            break

        print("pushing file: ", put_file)
        
        clientSocket.send(cmd)

        #Get the ephemeral port from the client
        ephemeralPort = int(clientSocket.recv(10))
        print("Generated ephemeral port is: ", ephemeralPort)

        #Create new connection for transfering the data
        data_socket = socket(AF_INET, SOCK_STREAM)
        data_socket.connect(("localhost", ephemeralPort))

        strng = ""

        #read file
        fo = open(put_file, "rb")
        strng = fo.read()
        fo.close()

        #Get the size of the string and 0 pad till 10 bytes
        size = str(len(strng))
        Size = size
        while len(size) < 10:
            size = "0" + size
        #put size header first
        strng = size + strng

        Bytes_Sent = 0
        #Send all the data so client
        while len(strng) > Bytes_Sent:
            Bytes_Sent += data_socket.send(strng[Bytes_Sent:])

        clientSocket.send("1")
        print("Transfered: ", put_file, " bytes: ", Size)



    #this is my idea for lls... only client side, no server necessary
    elif cmd == "lls":
        #Get the real path of file we are running.
        path = os.path.dirname(os.path.realpath(__file__))
        #Get the list of files in files directory
        lls = os.listdir(path)
        #Print the list of items
        for item in lls:
            print (item)



    elif cmd == 'ls':
        #Declare all variables here
        Data = ""
        Size = 0
        SizeBuffer = ""

        #Create a socket
        clientSocket.send(cmd)

        #Create an ephemeral port
        welcomeSocket = socket(AF_INET, SOCK_STREAM)
        #Bind the socket to port 0
        welcomeSocket.bind(("",0))
        #Retreive the ephemeral port number
        print("Generated ephemeral port is: ", welcomeSocket.getsockname()[1])

        #Send the ephemeral port number to the server as a string
        clientSocket.send(str(welcomeSocket.getsockname()[1]))
        welcomeSocket.listen(1)

        print("Waiting for connection to server")

        #Accept the connection from the server
        connSocket, addr = welcomeSocket.accept()
        print("Received connection from server.")

        #Get size of data coming from server side
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

        connFlag = clientSocket.recv(4096)
        #Print the data
        print("Size of data is: ", Size)
        print("Data from server:")
        print(Data)


    #if user input is quit
    elif cmd == 'quit':
        #send "quit" to the server
        clientSocket.send(cmd)
        #Receive the connection flag from the server indicating its shutting down
        connFlag = clientSocket.recv(4096) #I know 4096 is way too big. Just ensuring this works
        break
    elif cmd == "":
        #If blank, just do nothing
        pass
    else:
        #If user input is bad, print error message
        print("Invalid command.")

    #might need a break just outside of quit based on how we implement the rest

#breaking from the loops will allow the application to close
clientSocket.close()
print("Finished with client")
print("Closing connection")