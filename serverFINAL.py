# files
from os import listdir, remove
# threading
import threading
import re
# socket
import socket
# for testing
import time

IP = socket.gethostbyname(socket.gethostname())
PORT = 3000
FORMAT = "utf-8"
SIZE = 1024

TYPE_OF_DOWNLOAD = "1"
MRG_TITLE = "Merged.txt"


def invalid(Option):
    print("invalid command, try: ")

    if (Option == "MainCMD"):
        print(CommandList)
    elif (Option == "PrintCMD"):
        print(PrintOptions)


def PrintCommand(CMD):
    # Setup Data
    FilesInFolder = listdir()
    FilesInClients = listdir()
    regex = re.compile(".+\.FileList$")
    FilesInClients = [i for i in FilesInClients if regex.match(i)]

    # logic of what to print
    if (CMD == 'S_Files'):
        for i in FilesInClients:
            print(i)
    elif (CMD == 'C_Files'):
        # go through each file in "Fiels IN Clients" print files
        print('Note: there might be more connections, try again later if unsatisfied')
    elif (CMD == 'A_Files'):
        PrintCommand('S_Files')
        PrintCommand('C_Files')
    elif (CMD == 'Connections'):
        print("There are ", len(FilesInClients), " connections:")
        for i in range(len(FilesInClients)):
            # may need longer dunno how big the ip is going to be
            print((FilesInClients[i])[0:6], " Ip: ", (FilesInClients[i])[7:24])
    else:
        invalid("PrintCMD")


# return [ip, Port, fileidx] sorted by Filename Loacation (reversed)
def find(filenameARR):
    data = []
    # if not arr turn into arr
    if ((isinstance(filenameARR, list)) == False):
        filenameARR = [filenameARR]

    List = [(i + "\n") for i in filenameARR]
    regex = re.compile("Client.+\.FileList$")
    # Get the files and remove the reggex
    ClientLists = listdir()
    ClientLists = [i for i in ClientLists if regex.match(i)]

    # filenameARR.split(" ")
    # print(List)

    for i in ClientLists:
        file = open(i, "r")
        lines = file.readlines()
        for j in lines:
            if (j in List):
                data = data + [[i.split("-"), filenameARR[List.index(j)]]]

    # all filles in clients have been checked
    # print("BBBBBBBBBBBBB",data)

    FilesInFolder = listdir()
    for i in filenameARR:
        if (i in FilesInFolder):
            data = data + [[["Server", 0], filenameARR[filenameARR.index(i)]]]
    # all filles in server have been searched
    # print("AAAAAAAAAAAAA",data)

    Found = []

    if [data != []]:
        for i in range(0, len(data)):
            if (data[i][0][0] == "Server"):
                Found = Found + [[data[i][0][0], data[i][0][1], data[i][1]]]
            else:
                data.sort(key=lambda x: x[0][0], reverse=False)  # server will always be last
                Found = Found + [[str(data[0][0][0][7:len(data[i][0][0])]), int(data[i][0][1][0:4]), data[i][1]]]
    else:
        Found = []

    # print("Found ",Found, "EEEEE")

    return Found


# returns [client_ip-port.FileList , idx of File]
def GetFileNameList(fileINPT):
    # first check if its a list if not turn into list
    if ((isinstance(fileINPT, list)) == False):
        fileINPT = [fileINPT]

    data = find(fileINPT)

    FNL = [data[0] + data[1], data[2]]

    return FNL


def send(client, fileName):
    client.send(("SNF_" + fileName).encode(FORMAT))

    file = open(fileName, "r")
    data = file.read(1020)

    # print(data)
    time.sleep(0.3)

    while (data != ""):
        client.send(("SED_" + data).encode(FORMAT))
        data = file.read(1020)
        # print(data)
        time.sleep(1)  # FIX sleep

    time.sleep(1)
    client.send(("SOV_").encode(FORMAT))

    data = client.recv(SIZE).decode(FORMAT)


def recive(Client, filename):
    msg = "masfoihjf[osihrg[iuiwehrg[iofd"

    file = open(filename, 'w')

    while (msg[0:4] != "SOV_"):
        msg = Client.recv(SIZE).decode(FORMAT)
        if (msg[0:4] == "SED_"):
            file.write(msg[4:SIZE])
            Client.send("ACK".encode(FORMAT))

    file.close()


def KillSR(ADDR_OF_SR):
    ADDR_OF_SR = ADDR_OF_SR.split('-')
    addr = ADDR_OF_SR[0][7:len(ADDR_OF_SR[0])]
    port = ADDR_OF_SR[1][0:4]

    print("Ending CLient ", addr, "'s SR with Port:", port)

    SOKADDR = (addr, int(port))

    SRRQ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SRRQ.connect(SOKADDR)
    # "CONFIRM"
    data = ""
    while (data == ""):
        data = SRRQ.recv(SIZE).decode(FORMAT)

    INFO_SENT = "TER_YOU ARE NOW DIE"
    SRRQ.send(INFO_SENT.encode(FORMAT))

    data = ""
    while (data == ""):
        data = SRRQ.recv(SIZE).decode(FORMAT)

    data = SRRQ.recv(SIZE).decode(FORMAT)

    SRRQ.send("CONFIRM".encode(FORMAT))
    SRRQ.close()


def SRGET(fileArr):
    AddrP = ("", int(0))
    AddrN = (str(fileArr[0][0]), fileArr[0][1])

    # print(fileArr)
    # print(fileArr)
    idx = 0
    for i in range(0, len(fileArr)):
        if (fileArr[i][0] == "Server"):
            AddrP = AddrN
            AddrN = (str(fileArr[i][0]), int(fileArr[i][1]))
            break;

        if (AddrN != AddrP):
            SRRQ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            SRRQ.connect(AddrN)
            # "CONFIRM"
            data = SRRQ.recv(SIZE).decode(FORMAT)

        CurrFile = fileArr[i][2]

        # print("For ", i, " with ", CurrFile, " at ", AddrN[0], " ", AddrN[1])
        # send intent + FileName
        INFO_SENT = "SRD_" + CurrFile
        SRRQ.send(INFO_SENT.encode(FORMAT))

        # Upload vvvv

        # their Upload shinanigans
        data = SRRQ.recv(SIZE).decode(FORMAT)
        SRRQ.send("ACK".encode(FORMAT))

        # Recive the file
        recive(SRRQ, CurrFile)

        AddrP = AddrN
        AddrN = (str(fileArr[i][0]), int(fileArr[i][1]))

        print("P ", AddrP, "N", AddrN)

        # data = SRRQ.recv(SIZE).decode(FORMAT)

        if (data == "Done"):
            print("Done with ", CurrFile)

        if ((AddrN != AddrP) or (i == (len(fileArr) - 1))):
            # temp Connection termination
            SRRQ.send(("SRT_").encode(FORMAT))
            data = SRRQ.recv(SIZE).decode(FORMAT)
            if (data != "TERMINATING"):
                print("Termination failed")
            SRRQ.send("CONFIRM".encode(FORMAT))
            SRRQ.close()
            print("disconected from ", AddrP, "Last file downloaded", fileArr[i][2])

    print("P ", AddrP, "N", AddrN)
    if ((AddrN != AddrP)):
        # temp Connection termination
        SRRQ.send(("SRT_").encode(FORMAT))
        data = SRRQ.recv(SIZE).decode(FORMAT)
        if (data != "TERMINATING"):
            print("Termination failed")
        SRRQ.send("CONFIRM".encode(FORMAT))
        SRRQ.close()
        print("disconected from ", AddrP)


def S1(client, fileArr):
    Serveridx = len(fileArr)

    client.send(("WIT_").encode(FORMAT))
    print(fileArr)
    time.sleep(0.5)
    client.send(("RED_").encode(FORMAT))
    time.sleep(0.5)
    # find server index start
    for i in range(0, len(fileArr)):
        if (fileArr[i][0] == "Server"):
            Serveridx = i
            break;
    print(Serveridx)
    # Keep going in loop but send instead
    for i in range(Serveridx, len(fileArr)):
        if (fileArr[i][0] == "Server"):
            send(client, fileArr[i][2])
            print("Sent \"", fileArr[i][2], "\" to ", fileArr[i][0], fileArr[i][1])

    client.send(("WIT_").encode(FORMAT))
    # data = client.recv(SIZE).decode(FORMAT) #Confirmation

    SRGET(fileArr)

    # send ready to download
    client.send(("RED_").encode(FORMAT))

    time.sleep(0.5)
    # data = client.recv(SIZE).decode(FORMAT) #Confirmation

    if (Serveridx != 0):
        for i in range(0, Serveridx):
            if (fileArr[i][0] != "Server"):
                send(client, fileArr[i][2])
                print("Sent \"", fileArr[i][2], "\" from ", fileArr[i][0], fileArr[i][1])
                remove(fileArr[i][2])

    time.sleep(0.5)
    # send done sending
    client.send(("DON_").encode(FORMAT))


def S2(client, fileArr):
    # make client wait
    client.send(("WIT_").encode(FORMAT))

    SRGET(fileArr)

    MRG = open(MRG_TITLE, "w")

    DirList = listdir()
    for i in range(0, len(fileArr)):

        if (fileArr[i][2] in DirList):
            currFile = open(fileArr[i][2], 'r')
            lines = currFile.readlines()
            MRG.write("\n<T>_" + fileArr[i][2] + "\n")
            for j in lines:
                MRG.write("<D>_" + j)

            currFile.close()
        else:
            pass

    MRG.write("\n<E>_This is aTEST\n")
    MRG.close()

    client.send(("RED_").encode(FORMAT))
    time.sleep(.5)

    send(client, MRG_TITLE)

    remove(MRG_TITLE)

    time.sleep(.3)
    # send done sending
    client.send(("DON_").encode(FORMAT))


def S3(client, fileArr):
    client.send(("WIT_").encode(FORMAT))
    # data = client.recv(SIZE).decode(FORMAT) #Confirmation

    SRGET(fileArr)

    time.sleep(1)
    client.send(("RED_").encode(FORMAT))

    for i in range(0, len(fileArr)):
        send(client, fileArr[i][2])
        print("Sent \"", fileArr[i][2], "\" to ", fileArr[i][0], fileArr[i][1])
        if (fileArr[i][0] != "Server"):
            remove(fileArr[i][2])

    # send done sending
    client.send(("DON_").encode(FORMAT))


def S4(client, fileArr):
    client.send(("WIT_").encode(FORMAT))
    # get file if it is on diff client
    SRGET(fileArr)
    # continue
    client.send(("RED_").encode(FORMAT))

    time.sleep(.2)

    send(client, fileArr[0][2])
    # recive info

    if (fileArr[0][0] != "Server"):
        remove(fileArr[0][2])

    time.sleep(.2)

    client.send(("DON_").encode(FORMAT))

    data = client.recv(SIZE).decode(FORMAT)
    while (data[0:4] != "END_"):
        client.send(("WIT_").encode(FORMAT))
        # get file if it is on diff client
        fileArr = find(data[4:SIZE])

        SRGET(fileArr)
        # continue
        client.send(("RED_").encode(FORMAT))

        time.sleep(0.2)

        send(client, fileArr[0][2])
        # recive info

        if (fileArr[0][0] != "Server"):
            remove(fileArr[0][2])

        time.sleep(.2)

        client.send(("DON_").encode(FORMAT))

        data = client.recv(SIZE).decode(FORMAT)


def sendWithSenarios(client, fileArr):
    Split = fileArr.split(" ")
    print(Split)
    if (Split[-1] == ""):
        Split.pop(-1)
        print(Split)
    FileList = find(Split)
    ##

    if (TYPE_OF_DOWNLOAD == "1"):
        # Communication
        S1(client, FileList)
    elif (TYPE_OF_DOWNLOAD == "2"):
        # Merge
        S2(client, FileList)
    elif (TYPE_OF_DOWNLOAD == "3"):
        # def (back to back after all are aquired)
        S3(client, FileList)
    elif (TYPE_OF_DOWNLOAD == "4"):
        # def (back to back after all are aquired)
        S4(client, FileList)
    elif (TYPE_OF_DOWNLOAD == "0"):
        # Default
        S3(client, FileList)

    print("Done")


def Transmit(Id, Ip, Port):
    # print Server info
    print("S1, Thread", Id, "| IP", Ip, "| Port", Port)
    # Setup for connection
    ADDR = (Ip, Port)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()

    Connected = True

    filename = "3R  Q2WEDa3 S"  # random trash that is unlikely to be an acctual file
    # get client list, store in file

    # connect and get file list
    conn, addr = server.accept()
    print("connection accepted {addr}")
    filename = (conn.recv(SIZE).decode(FORMAT))[4:1024]
    while (filename == "3R  Q2WEDa3 S"):
        filename = conn.recv(SIZE).decode(FORMAT)[4:1024]

    conn.send(("ACK").encode(FORMAT))
    SRaddr = filename
    recive(conn, filename)

    # Get files from folder set them to array
    FilesInFolder = listdir()
    regex = re.compile("Client.+\.FileList$")
    # Get the files and remove the reggex
    ClientLists = listdir()
    ClientLists = [i for i in ClientLists if regex.match(i)]
    FilesInClients = list()
    for i in ClientLists:
        file = open(i, "r")
        lines = file.readlines()
        for i in lines:
            FilesInClients.append(i)
        file.close()
    # ^ not correct fucked up forgot i was reading file not that
    print('Server: \n', FilesInFolder)
    print("Client :\n", FilesInClients)
    # set up loop vars
    Connected = True
    temp = "[1024]"

    FileDownloads = ("FileName", "Number")

    # SEND TYPE OF DOWNLOAD TO SERVER

    conn.send((TYPE_OF_DOWNLOAD).encode(FORMAT))

    # send (Handover controll)
    while (Connected):

        temp = conn.recv(SIZE).decode(FORMAT)
        # lissen
        if (temp[0:4] == 'END_'):
            KillSR(SRaddr)
            conn.send("CONFIRM".encode(FORMAT))
            conn.close()
            Connected = False
            print("Connection ended with", SRaddr)
            remove("./" + SRaddr)

        elif (temp[0:4] == 'GET_'):
            # print(temp)
            sendWithSenarios(conn, temp[4:SIZE])
        elif (temp[0:4] == 'PSH_'):
            # forcefull push to server (No Delete):
            conn.send("Pushing to server".encode(FORMAT))
            # Fn download
            recive(conn, temp[4:SIZE])

        elif (temp[0:4] == 'DTA_'):
            # send data
            datafile = open("ServerSesion.Data", "w")

        else:
            print("Dunno CMD mesage was not found")
            print("Line \"", temp, "\"")
            print("CMD : \"", temp[0:4], "\"From :", conn.getsockname())
            time.sleep(4)


def TestFN(x):
    # print x
    print(x)


def main():
    # clear commands
    Command = ""
    # create thread list
    threadList = list()

    while (Command != "Disconect"):

        Command = input("Server Command: ")

        if (Command == "Start"):
            # Todo: fix args
            PORT = 3000 + 1 + (len(threadList) * 10)  # new thread per Thread (10 ports apart)
            x = threading.Thread(target=Transmit, args=(len(threadList), IP, PORT))
            threadList.append(x)
            x.start()

        elif (Command == "Close"):
            Command = "Disconect"
            print("Server shutting down, waiting for current processes to finish...")

        elif (Command == "Print"):
            Command = input("what do you want to print? ")
            PrintCommand(Command)
            Command = ""

        elif (Command == "Test"):
            x = threading.Thread(target=TestFN, args=(len(threadList),))
            threadList.append(x)
            x.start()

        else:
            invalid("MainCMD")
        print("\n")

    # join all threads
    for index, CurrThread in enumerate(threadList):
        CurrThread.join()
        print("Main: thread", index, "has been killed successfully")

    print("The server is now a Graveyard!")


CommandList = ["Start", "Close", "Print", "Test"]
PrintOptions = ["S_Files", "C_files", "A_files", "Connections"]
main()