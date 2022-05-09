import socket
from threading import Thread

SERVER_PORT = 5002

net = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


SERVER_HOST = input("SERVER IP: ")
print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
try:
    net.connect((SERVER_HOST, SERVER_PORT))
except:
    print("\n[-] Nie udało się nawiązać połączenia z serwererem")
    net.close()
    exit()

print("[+] Connected.")

def keyboard():
    while True:
        try:
            string = input()
        except KeyboardInterrupt: exit()
        else:
            if string.lower() == "quit" or string.lower() == "q": net.send(b"<CLIENT>SELF_DISCONNECT"); continue
            net.send(string.encode())

t2 = Thread(target=keyboard, daemon=True)

def server_function(message):
    if message == "DISCONNECT":
        print("[-] Odebrano rządanie rozłączenia")
        net.close()
        return "Break"
    elif message == "GET_USERNAME":
        nick = input("Wpisz swój nick: ")
        net.send(nick.encode())
    elif message == "GET_PASSWORD":
        password = input("Password: ")
        net.send(password.encode())
    elif message == "OK":
        print("Aby zakończyć połączenie wpisz quit lub q")
        t2.start()
        return
    return True        



def listen_for_message():
    while True:
            try: 
                recovery = net.recv(1024).decode()
            except ConnectionResetError:
                print("[-] Połączenie zostało zamknięte przez hosta")
                break
            else:
                if recovery.startswith("<SERVER>") == True:
                    request = recovery.lstrip("<SERVER>")
                    x = server_function(request)
                    if x == "Break": break
                else: print(f"\n{recovery}\n")

t = Thread(target=listen_for_message)
t.start()