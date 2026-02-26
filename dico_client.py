import sys
import socket
import dico_protocol as protocol 

BUFSIZE = 1500 #host, port, commande, arguments... 

def main(): 
    if len(sys.argv) < 5:
        print(f"structure : {sys.argv[0]} <port> <command> <dico> <args...>")
        print(f"Exemple GET  : {sys.argv[0]} 7777 GET mois_duree.json février")
        print(f"Exemple PREF : {sys.argv[0]} 7777 PREF mois_duree.json j")
        sys.exit(1)

    HOST = "localhost"               # default host
    PORT = int(sys.argv[1])          # port fourni par l'utilisateur
    COMMAND = sys.argv[2].upper()    # GET, PREF
    ARGS = sys.argv[3:]              # dico + key/prefix

    REQUETE = protocol.make_request(COMMAND, *ARGS)

    SOCK = socket.socket(socket.AF_INET6, socket.SOCK_STREAM,0) 

    CONNECT = SOCK.connect_ex((HOST, PORT)) 

    if CONNECT != 0: 
        print("Erreur de connexion :", CONNECT) 
        SOCK.close() 
        return

    SOCK.sendall(REQUETE) #envoyer la requête
    DATA = SOCK.recv(BUFSIZE)  #recevoir la réponse

    if not DATA: 
        print("Aucun reponse du serveur") 
        SOCK.close() 
        return 

    COMMUNICATION = DATA.decode("utf-8", errors="ignore") 
    STATUS, PAYLOAD = protocol.parse_response(COMMUNICATION) 

    if STATUS == "OK": 
        if COMMAND == "PREF":
            if not PAYLOAD.strip():
                print("Aucun résultat pour ce prefixe")
            else:
                print(PAYLOAD) 
        else:   print(PAYLOAD)
    elif STATUS == "ERR": 
        print("error", PAYLOAD) 
    else: 
        print("Reponse invalide", COMMUNICATION) 
    
    SOCK.close() 

if __name__ == "__main__": 
    main()