import socket

#Initializes the socket and sets it to non-blocking in order to allow concurrent connections.
port = 4003
host = socket.gethostbyname(socket.gethostname())              
s = socket.socket()
s.setblocking(False)
s.bind((host, port))
s.listen(1)
print ('listening at %s %s' %(host,port))

#Processes the '/register <password>' command. Registers the nickname currently in use.
def register(nickname,conn,password):
    if nickname not in registered:
        registered[nickname] = password
        conn.send('Nickname successfully registered \n')
    else:
        conn.send('Nickname already registered \n')
#Processes the '/login <nickname> <password>' command. Logs in to a registered nickname. 
#Automatically transfer connection from previous user if nickname is used by another connection.
def login(name,nickname,password,conn):
    if registered.get(nickname,'***') == password:
        users[nickname] = users.pop(name)
        conn.send('Successful login \n')
        sendToAll(name,'Changed his nickname to %s \n'%nickname)
    elif nickname not in registered:
        conn.send('Account has not been registered \n')
    else:
        conn.send('Invalid password \n')

#Broadcasts the message sent by the user. Loops through all other users that is not the sender and sends the message to their connection.
def sendToAll(name,message):
    for recepient, conn in users.items():
        if recepient != name:
            try:
                conn.send(str(name)+":"+message)    
                conn.send("<LF> \n")
            except socket.error:
                pass
        else:
            try:
                conn.send("<LF> \n")
            except socket.error:
                pass
#Processes the different '/' commands made by the user.
def command(name,command,conn):
    try:
        comm = command.split(' ')[0]
        comm = comm.strip()
        name = name.strip()
        if comm == '/register':
            comm,password = command.split(' ')
            password = password.strip()
            register(name,conn,password)
        elif comm == '/nick':
            comm,nickname = command.split(' ')
            nickname = nickname.strip()          
            if users.get(nickname,0) == 0:
                users[nickname] = users.pop(name)
                conn.send('Successfully changed nickname')
                sendToAll(name,'Changed his nickname to %s'%nickname)

            elif nickname not in registered:
                conn.send('Nickname is available for registration but is currently in use. \n')
            else:
                conn.send('Nickname has already been registered. If you know the password to this nickname, use command "login <nickname> <password>" \n')
        elif comm =='/login':
            comm,nickname,password = command.split(' ')
            nickname = nickname.strip()
            password = password.strip()
            login(name,nickname,password,conn)
        elif(comm == '/exit'):
            del users[name]
            conn.close()
            sendToAll("Admin", "%s has been disconnected \n" % name)
            print("%s has been disconnected \n" % name)
        elif(comm == '/online'):
            conn.send("Here is a list of online users:"+str(users.keys())+" \n")
        
    except:
        conn.send('Invalid command format \n')
        
            
users = {}
registered = {}
counter = 0
#Main function loop    
while True:
    #Listen for connections
    try:
        while True:
            try:
                conn, addr = s.accept()
            except socket.error:
                break
            conn.setblocking(False)
            counter+=1
            name = 'GUEST%s'%counter
            users[name] = conn
            print ('Got connection from', name)
            sendToAll('Admin','%s has connected \n'%name)   
            conn.send("You have now connected as "+name+". Here is a list of online users:"+str(users.keys())+" \n")
        #Loop through the connections and listen for incoming messages
        for name, conn in users.items():
            try:
                message = conn.recv(1024)
                if not message:
                    del users[name]
                    conn.close()
                    print("%s has been disconnected \n" % name)
                    sendToAll("Admin", "%s has been disconnected \n" % name)
                elif message[0] == '/':
                    command(name,message,conn)
                else:
                    sendToAll(name,message)
            except socket.error:
                continue
    except (SystemExit, KeyboardInterrupt):
        break
