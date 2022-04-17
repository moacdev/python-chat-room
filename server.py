import datetime
import socket 
import sqlite3
import threading 
import pickle


def initDB(cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(150) UNIQUE,
    password VARCHAR(255) NULL,
    photo_path VARCHAR(255) NULL
        )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS chats(
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        message TEXT NULL,
        date DATE timestamp,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
            )""")

with open(".db", "a+") as dbFile:
    pass

db = sqlite3.connect('.db')
initDB(db.cursor())

csr = db.cursor()

  
PORT = 5000
  
SERVER = socket.gethostbyname(socket.gethostname()) 
  
ADDRESS = (SERVER, PORT) 
  
FORMAT = "utf-8"
  
clients, users = [], [] 
  
server = socket.socket(socket.AF_INET, 
                       socket.SOCK_STREAM) 
  
server.bind(ADDRESS) 
  
def startChat(): 
    
    print("server is working on " + SERVER)
      
    
    server.listen()
      
    while True: 
        
        
        
        
        conn, addr =  server.accept()
        print('new conn')
        conn.send("AUTH".encode(FORMAT)) 
        
        name = conn.recv(1024).decode(FORMAT) 
          
        # check username in db
        try:
            isUserQuery = csr.execute("SELECT * FROM users where username = ? limit 1", (name,)).fetchall()
            if len(isUserQuery) > 0:
                user = isUserQuery[0]
            else: 
                csr1 = db.cursor()
                csr1.execute("INSERT INTO users values(null,?, '', '') ", (name,))
                db.commit()
                user = csr1.execute("SELECT * FROM users where username = ? limit 1", (name,)).fetchall()[0]
        except Exception:
            print(Exception)
    
        conn.send(pickle.dumps(user))

        users.append(user)
        clients.append(conn)




          
        print(f"Name is :{name}") 
          
        
        # broadcastMessage(f"{name} has joined the chat!")
          
        # conn.send('Connection successful!'.encode(FORMAT)) 
          
        
        thread = threading.Thread(target = handle, 
                                  args = (conn, addr)) 
        thread.start() 
          
        
        
        print(f"active connections {threading.active_count()-1}") 
  
def handle(conn, addr): 
    dbH = sqlite3.connect('.db')
    
    print(f"new connection {addr}") 
    connected = True
      
    try:
        while connected: 
            cres = conn.recv(1024).decode(FORMAT)

            if cres == 'MSG_RELOAD_REQUEST':
                conn.send('NEW_MESSAGE'.encode(FORMAT))

                csrN = dbH.cursor()
                allchatsarray = csrN.execute('SELECT * FROM chats').fetchall()

                messages = ''

                for chat in allchatsarray:
                    messages += chat[1] + '\n'
                messages = messages.encode(FORMAT)

                
                messages_length = str(len(messages))

                # Send msg length first
                conn.send(messages_length.encode(FORMAT))
                # Send msg content
                conn.send(messages)
            elif cres == 'NEW_MESSAGE_INSERT':
                # client sends msg length
                data_length = int(conn.recv(1024).decode(FORMAT))
                data_b = b''
                while True:
                    # receiving msg content from the client
                    data_b += conn.recv(1024)
                    # break when msg fully received
                    if len(data_b) >= data_length:
                        break
                data = pickle.loads(data_b)
                print(data)
                csrI = dbH.cursor()
                csrI.execute("INSERT INTO chats values(null,?, ?, ?) ", (data['msg'],datetime.datetime.now(),data['user_id']))
                dbH.commit()
                broadcastMessage('RELOAD')
            else:
                broadcastMessage('RELOAD')
    except Exception as e:
        print(str(e))
        # conn.close()
  
def broadcastMessage(message: str): 
    for client in clients: 
        print("->>>>>toAll")
        client.send(message.encode(FORMAT)) 
  
startChat() 