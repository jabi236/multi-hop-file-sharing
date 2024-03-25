import socket
from os import listdir
import threading
import os
import re
from time import sleep
import time

IP = socket.gethostbyname(socket.gethostname())
PORT = 3011
SREQUESTPORT = 3040
FORMAT = "utf-8"
SIZE = 1024
MRG_TITLE = "Merged.txt"

def UPtimes(files, start, end):
    send = end - start
    sz = 0
    for i in files:
        fsize = os.path.getsize(i)
        upload_times[i] = send
        upload_speed[i] = (fsize / send)
        sz = sz + fsize


    print("Rate of transfer for files:", files, "is", sz, "bytes per second over", send, "seconds.")

def DNTimes(files, start, end):
    send = end - start
    sz = 0
    for i in files:
        fsize = os.path.getsize(i)
        download_times[i] = send
        download_speed[i] = (fsize / send)
        sz = sz + fsize

    print("Rate of transfer for files:", files, "is", sz, "bytes per second over", send, "seconds.")


def mergesplit(filename):
    file = open(filename, "r")
    file_split = False
    while file_split == False:
        for i in file.readlines():
            i = i.split("\n")
            i = i.pop(0)
            if i[0:4] == "<T>_":
                new_file = open(i[4:SIZE], "w")
            elif i[0:4] == "<D>_":
                line = i[4:SIZE] + "\n"
                new_file.write(line)
            elif i[0:SIZE] == "\n":
                new_file.write("\n")
                new_file.close()
            elif i[0:4] == "<E>_":
                break

        file_split = True

def upload(client, cmd, filename):
    client.send(cmd.encode(FORMAT))
    print("Waiting for ACK")
    msg = client.recv(SIZE).decode(FORMAT)
    print(f"[SERVER]: {msg}")


    if filename in recDict:
        recDict[filename] += 1
    else:
        recDict[filename] = 1

    if (msg != ''):
        file = open(filename, "r")
        data = file.read(SIZE-4)
        print(data)

        while data != "":
            cmd = "SED_" + data
            client.send(cmd.encode(FORMAT))
            data = file.read(SIZE-4)
            #print(data)

        print("Waiting for ACK")
        msg = client.recv(SIZE).decode(FORMAT)
        print(f"[SERVER]: {msg}")
        if (msg != ''):
            file.close()
            end = time.time()
            client.send(("SOV_connect").encode(FORMAT))


def download(client, filename):
    cmd = filename
    client.send(cmd.encode(FORMAT))
    data = client.recv(SIZE).decode(FORMAT)
    print("File name Recieved", data)
    filename= filename[4:len(filename)]
    print(filename)
    filename.split()
    print(filename)

    if data in receivedDict:
        receivedDict[filename] += 1
    else:
        receivedDict[filename] = 1

    while (data[0:4] != "DON_"):
        #print("1")
        data = client.recv(SIZE).decode(FORMAT)
        #print(data)
        #print("2")
        if (data[0:4] == "SNF_"):
            print("AAAAAAAAAAAAAAAA", data)

            print("Open File")
            data[4:SIZE]
            f = open(data[4:SIZE], "w")
            start = time.time()
            print("file opened", data[4:SIZE])
            data = ''

            while data[0:4] != "SOV_":
                print("dowloading...")
                data = client.recv(SIZE).decode(FORMAT)
                data2 = data[4:SIZE]

                if data[0:4] == "SOV_":
                   data2 = ''
                print('datalin=', (data[0:4]))
                print('data=', (data2))
                f.write(data2)

            f.close()
            print("File downloaded!")
            #end = time.time()
            #download_times[filename] = (end - start)
            #download_speed[filename] = (os.path.getsize(filename) / (end - start))

            client.send(("Done").encode(FORMAT))

        if (data[0:4] == "WIT_"):
            while (data[0:4] != "RED_"):
                data = client.recv(SIZE).decode(FORMAT)
                #print(data)

        print(data)

def direct():
    #FilesInFolder = listdir()
    print("\nPrinting all files in directory and details")
    for i in recDict.keys():
        print("Filename:", i, "| Size:", os.path.getsize(i), "bytes | Creation date:", time.ctime(os.path.getctime(i)),
              "| Number of downloads by server:", recDict[i])

    print("\nPrinting all files downloaded from network")
    for i in receivedDict.keys():
        print("Filename:", i, "| Size:", os.path.getsize(i), "bytes | Creation date:", time.ctime(os.path.getctime(i)),
              "| Number of downloads by client:", receivedDict[i])

    print(recDict,
        receivedDict,
        upload_times,
        download_times,
        upload_speed,
        download_speed)


# End connection
def terminate(client):
    cmd = "END_"
    client.send(cmd.encode(FORMAT))
    conf = client.recv(SIZE).decode(FORMAT)
    if conf == "CONFIRM":
        client.close()
        print("Disconnecting from Server...")

# Server request file from client 2
def SRequest(bl, CURRENT_PORT):
    sleep(1)
    # print Server info
    print(" \nS1, Thread", "| IP", IP, "| Port", CURRENT_PORT)
    # Setup for connection
    ADDR = (IP, CURRENT_PORT)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    Connected = True
    filename = "3R  Q2WEDa3 S"  # random trash that is unlikely to be an acctual file
    while (Connected):
        server.listen(1)
        conn, addr = server.accept()
        print("connection accepted")
        conn.send("CONFIRM".encode(FORMAT))
        socket_connect = True
        print("We're connected")

        while (socket_connect):
            intent = conn.recv(SIZE).decode(FORMAT)
            if (intent[0:4] == "SRD_"):
                filename = intent[4:SIZE]
                print("The File to send was recived: ", filename)
                cmd = "PSH_" + filename
                upload(conn, cmd, filename)

            # added "[0:4]" to intent
            if (intent[0:4] == "SRT_"):
                socket_connect = False# terminate connection process

            # added "[0:4]" to intent
            if (intent[0:4] == "TER_"):
                socket_connect = False
                Connected = False

        # Added indentation from Fn to While
        conn.send("TERMINATING".encode(FORMAT))
        terminate(conn)

def connect(conn, CONNECT_IP, PORT):
    # connect to server
    ADDR = (CONNECT_IP, PORT)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    # Print conformation of connection
    print(f"[CONNECTED] Client connected to server at {CONNECT_IP}:{PORT}")

    # Create File with list of files
    FilesInFolder = listdir()

    # Set file name with IP and PORT
    filename = "Client_" + IP + "-" + str(SREQUESTPORT) + ".FileList"
    file = open(filename, "w")

    for i in FilesInFolder:
        file.write(i)
        file.write("\n")
    file.close()
    # Set Command to SND(Send file)
    cmd = "SND_" + filename
    # Upload File List
    upload(client, cmd, filename)

    cmd = ""
    while (cmd == ""):
        cmd = client.recv(SIZE).decode(FORMAT)

    act = cmd
    # loop as long connection is true
    Connection = True

    while Connection:
        msg = input("Enter Instruction: ")
        # Set input to array
        files = msg.split()
        # First Part of Message for if statements (Desired Instruction)
        instruction = files[0]

        # Upload [filename]
        if (instruction == "Upload"):
            # Set command to push(force download on server)
            for i in range(1, len(files)):
                filename = files[i]
                cmd = "PSH_" + filename
                start = time.time()
                upload(client, cmd, filename)
                end = time.time()
                UPtimes(files, start, end)

        # Download [filename]
        elif (instruction == "Download"):
            # Scen 2-1
            if (act == "1"):
                files.pop(0)
                CMD = "GET_"
                for i in files:
                    CMD = CMD + i + " "
                start = time.time()
                download(client, CMD)
                end = time.time()
                DNTimes(files, start, end)
            # Scen 2-2
            elif (act == "2"):
                files.pop(0)
                CMD = "GET_"
                for i in files:
                    CMD = CMD + i + " "
                start = time.time()
                download(client, CMD)
                mergesplit(MRG_TITLE)
                end = time.time()
                DNTimes(files, start, end)
            # Scen 2-3
            elif (act == "3"):
                files.pop(0)
                CMD = "GET_"
                for i in files:
                    CMD = CMD + i + " "
                start = time.time()
                download(client, CMD)
                end = time.time()
                DNTimes(files, start, end)
            # Scen 2-4
            elif (act == "4"):
                files.pop(0)
                start = time.time()
                for i in files:
                    CMD = "GET_"
                    CMD = CMD + i
                    download(client, CMD)
                client.send(("END_").encode(FORMAT))
                end = time.time()
                DNTimes(files, start, end)
        # Dir
        elif (msg == "Dir"):
            direct()

        # Terminate
        elif (msg == "Terminate"):
            terminate(client)
            Connection = False

            for i in recDict.keys():
                print("File Name:", i, "Times Uploaded to Server:", recDict[i])

            for i in receivedDict.keys():
                print("File Name:", i, "Times Downloaded from Server:", receivedDict[i])

            print("Disconnected")
        else:
            print("Invalid Instruction! Try ", connectList)

# Main function (Instruction Loop)
def main():
    # Set threadList and initialize message to empty space
    for i in listdir():
        recDict[i] = 0

    threadList = list()
    message = ""

    while (message != "Exit"):
        message = input("Client Message: ")
        # Connect [IP] [PORT]
        if (message.split()[0] == "Connect"):
            # Get IP and PORT form input
            CONNECT_IP = message.split()[1]
            PORT = int(message.split()[2])

            # open thread to connect and SRequests
            connecting_thread = threading.Thread(target=connect, args=(len(threadList), CONNECT_IP, PORT))
            SRequest_thread = threading.Thread(target=SRequest, args=(len(threadList), SREQUESTPORT))

            # add threads to list
            threadList.append(connecting_thread)
            threadList.append(SRequest_thread)

            # Start Threads
            SRequest_thread.start()
            connecting_thread.start()

        # Print valid commands
        elif (message == "Help"):
            print(mainList)

        # Delete file
        elif (message == "Delete"):
            for file in receivedDict.keys():
                path = os.path.join(os.getcwd(), file)
                os.remove(path)

        # Exit loop
        elif (message == "Terminate"):
            message = "Exit"
            print("Exiting...")
        # File Directory
        elif (message == "Dir"):
            direct()

        else:
            # No valid command, print valid commands
            print("Invalid Command! Valid commands:", mainList)

        # join threads
        for index, CurrThread in enumerate(threadList):
            CurrThread.join()

# Intialize Upload Dictionary, Download Dictionary, List of Main Instructions, List of Connect Instructions
recDict = {}
receivedDict = {}
upload_times = {}
download_times = {}
#in bytes
upload_speed = {}
download_speed = {}
mainList = ["Connect [IP] [PORT]", "Help", "Delete", "Terminate", "Dir"]
connectList = ["Upload [FileName(s)]", "Download [FileName(s)]", "Delete [Filename]", "Dir", "Terminate"]

main()
#Connect 10.47.144.248 3001