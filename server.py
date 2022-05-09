#zdefiniowac Ip i port
host = "127.0.0.1" #127.0.0.1 domyślne ip pętli zwrotnej
port = 5002

#import usefull librarys
from time import strftime, sleep
import socket
from threading import Thread
from os import system

#funkcja do zapisywania logów
logs = "SERVER LOGS:"
mess = "MESSAGE LOGS"
def log(string, type):
    global logs
    types = ["+", "-", "*", "#", "/", "^"]
    if False == type in types: print(f"Bad type, {type}"); return "Err"
    logs = logs + f"\n{get_time()}| [{type}] {string}"
#funkcja do zwracania czasu
def get_time():
    time = strftime("[%H:%M:%S] ")
    return time
#funkcia do zapisywania waidomosci
def message_logs(ip,nick, message):
    global mess
    time = strftime("[%H %M] ")
    mess = mess + f"\n{time}{ip} | {nick}: {message}"
#definiujemy classe dla menu z argumentami ip oraz portu
class server():

    clients = set() #zmienna do przetrzymywania obiektów clientów
    

    def __init__(self, server_ip, server_port, version="1.2 Beta", server_name="Kucyx.inc"):
        system("cls")
        print("\n|[Witamy na serwerze: {} w wersji: {}]|\n".format(server_name, version))
        print("Aby wyświetlic liste komend wpisz \"help\"")
        log("Serwer zostal uruchomiony", "*")
        self.ip = server_ip
        self.port = server_port
        self.online = False
        self.ver = version
        self.name = server_name
        self.password = "null"

    def check_command(self, command, arg = "undefined", return_description = False):
        if command == "help": value = self.help
        elif command == "info": value = self.info
        elif command == "reboot": value = self.reboot
        elif command == "start": value = self.start
        elif command == "stop": value = self.stop
        elif command == "logs": value = self.show_logs
        elif command == "user": value = self.user
        elif command == "list": value = self.list
        elif command == "mess": value = self.show_message
        elif command == "send": value = self.send
        elif command == "password": value = self.password_change
        else: print(f"\nPolecenie {command} nie istnieje."); return
        if return_description == True:
            return f"{value.__doc__}"
        else: value(arg)


    def command(self, string="null"):
        if string == "null": return
        syntax = string.strip().split()
        if len(syntax) == 0: return
        command = syntax[0].lower()
        if len(syntax) > 1: 
            syntax.pop(0)
            argument = ' '.join(syntax) 
            self.check_command(command = command, arg = argument)
        else:
            self.check_command(command)


    #Commands tu
    def help(self, arg):
        """
        |help| - Pozwala na wyświetlenie pomocy do danego polecenia.

        Syntax:
        help <command>
        """
        if arg == "undefined":
            print("""Lista Poleceń - Kucyx.inc
            
    help <command> - Wyświetla informacje o poleceniu podanym w argumencie
    password - Umożliwia ustawienie hasła 
    info - Wyświetla podstawowe informacje o serwerze    
    logs - Wypisuje wszystkie działania serwera
    reboot - Wyłącza server

    start - Uruchamia gniazdo sieciowe.
    stop - Zamyka gniazdo sieciowe.

    user <user> - Zwraca informacje o użytkowniku
    list - Pokazuje liczbe użytkowników na serwerze            
    send - Wysyła alert do każdego użytkownika
    mess - Wypisuje całą historie wiadomosci
            """)
        else:
            description = self.check_command(command = arg, return_description=True)
            print(description)

    def reboot(self, args):
        """
        |reboot| - Em... poprostu wyłącza server bo co innego może robic.

        Radzę tego nie robic gdy server w trybie online, idk co sie stanie, nie testowałem.
        Just don't do this and propably everything can be fine.
        """
        if self.online == True: print("Nie możesz tego zrobić kiedy serwer jest w trybie Online\nSpróbuj najpier wyłączyc serwer poleceniem stop."); return
        log("Server shuting down...", "-")
        f=open("logs.txt", "w+")
        f.write(logs)
        f.close
        file = open("messages.txt", "w+")
        file.write(mess)
        file.close
        print("Server zostaje wyłączony. Logi zostały zapisane.")
        exit()

    def list(self, args):
        """
        |list| - Pokazuje liste wszystkich połączonych clientów z serwerem

        Syntax:
        list
        """
        if self.online == False: print("Ta komenda nie działa w trybie offline"); return
        self.search_client()

    def send(self, args):
        """
        |send| - Wysyła alert do wszystkich clientów z podaną wiadomoscią
        """
        if self.online == False: print("Ta komenda nie działa w trybie offline"); return
        if args == "undefined": print("Nie podano wiadomosci alertu"); return
        self.alert_for_all_clients(args)
        print("Pomyślnie przesłano wiadomosc: {}".format(args))

    def info(self, args):
        """
        |info| - Wyświetla informacje o podstawowych informacjach serwera
        
        Syntax:
        info
        """

        print(f"""
        Server Name : {self.name}
        Server Version : {self.ver}

        Server IP : {self.ip}
        Listening Port : {self.port}
        Online Status : {self.online} 
        Password : {self.password}
        """)

    def user(self, args):
        """
        |user| - Wyświetla infomacje o użytkwniku podanym w argumencie na podstawie podanego nicku

        Syntax:
        user <nick/id>
        """
        if self.online == False: print("Ta komenda nie działa w trybie offline"); return
        if args == "undefined": print("Nie zdefiniowano nicku użytkownika do przeszukania"); return  
        user = self.search_client(args=args, ret=True)
        if user == False: print("Nie znaleziono podanego użytkownika na serwerze")
        else:
            print(f"""
            User: 
                User IP: {user.addres_ip[0]}
                User ID: {user.id}
                User Nick: {user.nick}
            """)

        #Przeszukiwanie po all

    def show_logs(self, args):
        """
        |logs| - Wypisuje wszystkie akcje serwera na czacie

        Syntax:
        logs
        """

        print(logs)

    def show_message(self, args):
        """
        |mess| - Wypisuje wszystkie logi wiadomosci
        
        Syntax:
        mess
        """

        print(mess)

    def password_change(self, password = "off"):
        """
        |password| - Ustawia lub usuwa hasło

        Syntax:
        password <password> 
        to restart: password off
        """
        if self.online == True: print("\nNie możesz zmienic hasła kiedy serwer jest w trybie Online")
        elif password == "off" or password == "null" or password == "undefined":
            self.password = "null"
            log("Zresetowano hasło", "*")
            print("Hasło zostało zrestartowane, teraz podawanie hasła nie jest wymagane przy starcie")
        elif len(password) < 4: print("\nHasło musi zawierac przynajmniej 4 znaki")
        else: 
            self.password = password
            log(f"Ustawiono hasło na {password}", '*')
            print(f"Hasło zostało ustawione na {password}")


    #-------Funkcje Gniazda---------

    def start(self, args):
        """
        |start| - Polecenie te uruchamia tryb online servera.

        Uruchamia nasłuchiwanie połączeń z zdefiniowanego portu i ip.
        Umożliwa połączenie się clientą przy użyciu hasła o ile zdefiniowane

        Syntax:
        start
        """
        if self.online == True: print("Error: Serwer już chodzi w trybie online.\n"); return
        #command's in working
        log("Trwa uruchamianie gniazda...", "^")
        message_logs("SERVER", "+", "Running ONLINE... [SERVER PRIVATE MESSAGE]")
        self.net = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.net.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.net.bind((self.ip, self.port))
        self.net.listen(5)
        log(f"Nasłuchiwanie komunikacji {self.ip}:{self.port}", "*")
        self.online = True
        head_thread = Thread(target=self.listen_for_new_client)
        print("Tryb nasłuchiwania komnunikacji został pomyślnie uruchomiony")
        head_thread.start()


    def stop(self, args):
        """
        |stop| - Przełącza serwer na tryb offline.

        Rozłącza wszystkich clientów i wyłącza gniazdo.

        Syntax:
        stop
        """
        if self.online == False: print("Error: Serwer aktualnie chodzi w trybie Offline.\nJego socket jesy wyłączony więc nie mogę tego zrobić"); return
        print("Trwa próba rozłączenia clientów...")
        log("Rozłączanie clientów...", "^")
        #Tu zrobic disconnect, send
        self.disconnect_all()
        sleep(3)
        log("Zamykanie gniazda", "^")
        print("Zamykanie Gniazda...")
        self.online = False
        message_logs("SERVER", "-", "Get Offline [SERVER PRIVATE MESSAGE]")
        try:
            self.net.close()
        except:
            log("Something went wrong with closing socket", "#")
            print("Wystąpił jakis błąd z zamykaniem gniazda ale jebac")
        finally:
            log("Serwer Pomyślnie przeszedł w tryb Offline", "*")
            print("Tryb komunikacji został pomyślnie wyłączony.")


    #-------Server Function Online Mode----------
    def listen_for_new_client(self):
        i = 1
        while True:
            if self.online == False: break
            i += 1
            try:
                client_object, client_addres = self.net.accept() #connection accept
            except:
                log("Thread Closed", "-")
                break
            server_user = client(client_object, client_addres, i) #dodawanie klasy cienit
            self.clients.add(server_user) #dodawanie klasy do setu __clients

    def alert_for_all_clients(self, message):
        msg = f"HOST: {message}"
        message_logs("HOST", "HOST", message)
        for client in self.clients:
            try: client.client.send(msg.encode())
            except: continue

    def send_for_all_clients(self, msg, nick, id):
        time = strftime("[%H:%M] ")
        message = f"{time}| {nick}: {msg}"
        for client in self.clients:
            if client.id == id: continue
            if client.nick == " ":continue
            client.client.send(message.encode())

    def disconnect_all(self):
        for client in self.clients:
            client.client.close()
        self.clients.clear()

    def search_client(self, args=1, ret = False):
        if ret == True:
            for i in self.clients:
                if i.nick == args: return i
                else: continue
            return False
        else:
            msg_return = "\n"
            cout = 0
            for i in self.clients:
                if i.nick == "nul": nick = "..."
                else: nick = i.nick
                msg_return = msg_return + f"{nick} | {i.addres_ip} | {i.id} | {i.perm}\n"
                cout += 1
            msg_return = msg_return + "\nUsers count: {}".format(cout)
            print(msg_return)

    def disconnect(self,id,client):
       # client.send(b"<SERVER>DISCONNECT")
        sleep(0.5)
        client.close()
        for clientt in self.clients:
            if clientt.id == id: self.clients.discard(client); break

    def if_username_same(self, nick_to_check):
        for clients_nick in self.clients:
            if clients_nick.nick == nick_to_check: return False
            else: continue
        return True

    def connect_allert(self, message, typ):
        msg_to_send = f"[{typ}] {message}"
        message_logs("HOST", typ, message)
        for client in self.clients:
           try: client.client.send(msg_to_send.encode())
           except: continue


#Klasa do przechowywania clientów
class client():
    nick = "nul"
    def __init__(self, client, client_addres, id):
        self.id = id
        self.client = client
        self.perm = "User"
        self.addres_ip = client_addres
        self.nick = "nul"
        log(f"Nawiązywanie Połączenia z adresu {client_addres[0]}", "^")
        Thread_connection = Thread(target=self.connection_process)
        Thread_connection.start()
        Thread_connection.join()
        if self.nick == "nul":
            server.disconnect(self.id, self.client)
        else:
            log(f"Połączono {self.addres_ip[0]} jako {self.nick}", "+")
            to_send = f"Zostałeś pomyślnie połączony z serwerem jako {self.nick}.\nWpisz coś aby się przywitac"
            self.client.send(to_send.encode())
            server.connect_allert(f"User {self.nick} Connected", "+")
            Thread_message_get = Thread(target=self.listen_for_message)
            Thread_message_get.start()
        

    def connection_process(self):

        if server.password != "null" :
            def check_password():
                i = 0
                while True:
                    i += 1
                    if i > 3: 
                        log(f"{self.addres_ip[0]} disconnected: To many password try", "-")
                        self.client.send(b"<SERVER>DISCONNECT")
                        server.disconnect(self.id, self.client)
                        return False; break 
                    sleep(0.5)
                    self.client.send("<SERVER>GET_PASSWORD".encode())
                    try:
                        message_output = self.client.recv(1024).decode()
                    except:
                        log(f"{self.addres_ip[0]} disconnected: Password_Get_Failed", "-")
                        server.disconnect(self.id, self.client)
                        return False; break
                    else:
                        if message_output == server.password:
                            self.client.send("|SERVER|: Przyznano Dostęp".encode())
                            return True; break
                        else:
                            self.client.send("|SERVER|: Niepoprawne Hasło".encode())
                            continue
        
            password_get_from_client = check_password()
            if password_get_from_client == False:
                return False, " "

        def get_ussername():
            while True:
                sleep(0.5)
                self.client.send("<SERVER>GET_USERNAME".encode())
                try:
                    message_output = self.client.recv(1024).decode()
                except:
                    log(f"{self.addres_ip[0]} disconnected: Nickname_Get_Failed", "-")
                    server.disconnect(self.id, self.client)
                    return False
                else:
                    nickname = message_output.strip().replace(" ", "_")
                    banned_worlds = ["server", "host", "serwer", "127.0.0.1", "admin"]
                    if nickname.lower in banned_worlds: self.client.send("|SERWER|: Ta nazwa jest zbanowana nie można jej użyć"); continue
                    if len(nickname) < 4 or len(nickname) > 20:
                        self.client.send("|SERWER|: Nazwa użytkownika jest niepoprawna\n(min 4 max 20 znaków, oraz najlepiej bez spacji)".encode())
                        continue
                    check_if_same = server.if_username_same(nickname)
                    if check_if_same == False:
                        self.client.send("|SERWER|: Nazwa użytkownika jest już zajęta".encode())
                        continue
                    else:
                        return nickname

        get_nick = get_ussername()
        if get_nick == False: self.nick = "nul"; return
        else: 
            self.client.send("<SERVER>OK".encode())
            self.nick = get_nick
            return
            
    def listen_for_message(self):
        while True:
            try:
                msg = self.client.recv(1024).decode().strip()
            except:
                log(f"{self.addres_ip[0]} disconnected", "-")
                server.disconnect(self.id,self.client)
                server.connect_allert(f"{self.nick} Disconnected", "-")
                break
            else: 
                if len(msg.strip()) < 1: continue
                if msg.startswith("<CLIENT>"):
                    request = msg.lstrip("<CLIENT>")
                    if request == "SELF_DISCONNECT":
                        self.client.send(b"<SERVER>DISCONNECT")
                        server.disconnect(self.id,self.client)
                else: 
                    message_logs(self.addres_ip[0], self.nick, msg)
                    server.send_for_all_clients(msg, self.nick, self.id)

server = server(host, port, "1.3", "Kucyx.inc")

while True:
    try:
        print()
        command = input("$ ")
    except KeyboardInterrupt:
        server.stop("menu")
        exit()
    else:
        server.command(command)