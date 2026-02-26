import sys
import socket
import dico_protocol as protocol  # même module que le client normal

BUFSIZE = 1500


def usage(prog):
    print(f"Usage : {prog} <port> <password> <command> <dico> <args...>")
    print()
    print("Commandes admin :")
    print("  ADD <dico> <key> <value...>   ")  # ajouter l'entrée
    print("  SET <dico> <key> <value...>   ")  # créer ou modifier l'entrée
    print("  DEL <dico> <key...>           ")  # supprimer l'entrée
    print()
    print("Exemples :")
    print(f"  {prog} 7777 admin ADD mois_duree.json novembre 30")
    print(f"  {prog} 7777 admin SET mois_duree.json fevrier 28")
    print(f"  {prog} 7777 admin DEL mois_duree.json fevrier")


def main():
    
    if len(sys.argv) < 5:
        usage(sys.argv[0])
        sys.exit(1)

    HOST = "localhost"
    PORT = int(sys.argv[1])
    PASSWORD = sys.argv[2]
    COMMAND = sys.argv[3].upper()
    ARGS = sys.argv[4:]     

    
    REQ_ARGS = [PASSWORD] + ARGS

    
    REQUETE = protocol.make_request(COMMAND, *REQ_ARGS)

    
    SOCK = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    CONNECT = SOCK.connect_ex((HOST, PORT))
    if CONNECT != 0:
        print("Erreur de connexion :", CONNECT)
        SOCK.close()
        return

    
    SOCK.sendall(REQUETE)

    
    DATA = SOCK.recv(BUFSIZE)
    if not DATA:
        print("Aucune réponse du serveur")
        SOCK.close()
        return

    TXT = DATA.decode("utf-8", errors="ignore")
    STATUS, PAYLOAD = protocol.parse_response(TXT)

    if STATUS == "OK":
        if PAYLOAD.strip():
            print("[OK]", PAYLOAD)
        else:
            print("[OK]")
    elif STATUS == "ERR":
        print("[ERR]", PAYLOAD)
    else:
        print("Réponse invalide :", TXT)

    SOCK.close()


if __name__ == "__main__":
    main()
