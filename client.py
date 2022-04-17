import socket 
import threading 
from tkinter import *
from tkinter import font 
from tkinter import ttk 
import pickle
import tkinter

  
from chat import *
  
PORT = 5000
SERVER = "192.168.0.10"
ADDRESS = (SERVER, PORT) 
FORMAT = "utf-8"
  
client = socket.socket(socket.AF_INET,  
                      socket.SOCK_STREAM) 
client.connect(ADDRESS) 
  
  
class GUI: 
    user = ('', '', '', '')
    
    def __init__(self): 
        
        
        self.Window = Tk() 
        self.Window.withdraw() 
          
        
        self.login = Toplevel() 
        
        self.login.title("Login") 
        self.login.resizable(width = False,  
                             height = False) 
        self.login.configure(width = 400, 
                             height = 300) 
        
        self.pls = Label(self.login,  
                       text = "Please login to continue", 
                       justify = CENTER,  
                       font = "Helvetica 14 bold") 
          
        self.pls.place(relheight = 0.15, 
                       relx = 0.2,  
                       rely = 0.07) 
        
        self.labelName = Label(self.login, 
                               text = "Name: ", 
                               font = "Helvetica 12") 
          
        self.labelName.place(relheight = 0.2, 
                             relx = 0.1,  
                             rely = 0.2) 
          
        
        
        self.entryName = Entry(self.login,  
                             font = "Helvetica 14") 
          
        self.entryName.place(relwidth = 0.4,  
                             relheight = 0.12, 
                             relx = 0.35, 
                             rely = 0.2) 
          
        
        self.entryName.focus() 
          
        
        
        self.go = Button(self.login, 
                         text = "CONTINUE",  
                         font = "Helvetica 14 bold",  
                         command = lambda: self.goAhead(self.entryName.get())) 
          
        self.go.place(relx = 0.4, 
                      rely = 0.55) 
        self.Window.mainloop()
  
    def goAhead(self, name): 
        self.login.destroy() 
        
        res = client.recv(1024).decode(FORMAT)

        if res == 'AUTH':
            client.send(name.encode(FORMAT))
            self.user = pickle.loads(client.recv(1024))
            self.layout()
            rcv = threading.Thread(target=self.receive) 
            rcv.start()
        else: 
            tkinter.messagebox.showerror(title="Auth", message="L'authentification à echouer")
          
        
    def layout(self): 
        
        self.name = self.user[1] 
        
        self.Window.deiconify() 
        self.Window.title("CHATROOM: "+self.name) 
        self.Window.resizable(width = False, 
                              height = False) 
        self.Window.configure(width = 470, 
                              height = 550, 
                              bg = "#17202A") 
        self.labelHead = Label(self.Window, 
                             bg = "#17202A",  
                              fg = "#EAECEE", 
                              text = self.name , 
                               font = "Helvetica 13 bold", 
                               pady = 5) 
          
        self.labelHead.place(relwidth = 1) 
        self.line = Label(self.Window, 
                          width = 450, 
                          bg = "#ABB2B9") 
          
        self.line.place(relwidth = 1, 
                        rely = 0.07, 
                        relheight = 0.012) 
          
        self.textCons = Text(self.Window, 
                             width = 20,  
                             height = 2, 
                             bg = "#17202A", 
                             fg = "#EAECEE", 
                             font = "Helvetica 14",  
                             padx = 5, 
                             pady = 5) 
          
        self.textCons.place(relheight = 0.745, 
                            relwidth = 1,  
                            rely = 0.08) 
          
        self.labelBottom = Label(self.Window, 
                                 bg = "#ABB2B9", 
                                 height = 80) 
          
        self.labelBottom.place(relwidth = 1, 
                               rely = 0.825) 
          
        self.entryMsg = Entry(self.labelBottom, 
                              bg = "#2C3E50", 
                              fg = "#EAECEE", 
                              font = "Helvetica 13") 
          
        
        
        self.entryMsg.place(relwidth = 0.74, 
                            relheight = 0.06, 
                            rely = 0.008, 
                            relx = 0.011) 
          
        self.entryMsg.focus() 
          
        
        self.buttonMsg = Button(self.labelBottom, 
                                text = "Send", 
                                font = "Helvetica 10 bold",  
                                width = 20, 
                                bg = "#ABB2B9", 
                                command = lambda : self.sendButton(self.entryMsg.get())) 
          
        self.buttonMsg.place(relx = 0.77, 
                             rely = 0.008, 
                             relheight = 0.06,  
                             relwidth = 0.22) 
          
        self.textCons.config(cursor = "arrow") 
          
        
        scrollbar = Scrollbar(self.textCons) 
          
        
        
        scrollbar.place(relheight = 1, 
                        relx = 0.974) 
          
        scrollbar.config(command = self.textCons.yview) 
          
        self.textCons.config(state = DISABLED) 
  
    
    def sendButton(self, msg): 
        self.textCons.config(state = DISABLED) 
        self.msg=msg 
        self.entryMsg.delete(0, END) 
        snd= threading.Thread(target = self.sendMessage) 
        snd.start()
    
    def refreshMsg(self):
        client.send("MSG_RELOAD_REQUEST".encode(FORMAT))

    
    def receive(self): 
        while True: 
            try: 
                res = client.recv(1024).decode(FORMAT)
                if res == 'AUTH':
                    client.send(self.name.encode(FORMAT))
                elif res == 'NEW_MESSAGE':
                    # server sends msg length
                    msg_length = int(client.recv(1024).decode(FORMAT))
                    msg_b = b''
                    while True:
                        # receiving msg content from the server
                        msg_b += client.recv(1024)
                        # break when msg fully received
                        if len(msg_b) >= msg_length:
                            break
                    msg = pickle.loads(msg_b)
                    print(msg)
                    
                    self.textCons.config(state = NORMAL) 
                    self.textCons.insert(END, 
                                            msg+"\n\n") 
                        
                    self.textCons.config(state = DISABLED) 
                    self.textCons.see(END) 
                elif res == 'RELOAD':
                    self.refreshMsg()
                else: 
                    self.refreshMsg()
            except Exception as e: 
                
                print(str(e)) 
                # client.close() 
                break

            # wait server response if user exist
          
    
    def sendMessage(self): 
        self.textCons.config(state=DISABLED) 
        client.send("NEW_MESSAGE_INSERT".encode(FORMAT))

        message = pickle.dumps({ 'user_id': self.user[0], 'msg': self.msg })

        message_length = str(len(message))

        # Send msg length first
        client.send(message_length.encode(FORMAT))
        # Send msg content
        client.send(message)
        self.refreshMsg()
  
g = GUI() 