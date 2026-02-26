import sys
import socket
import json
import os
import dico_protocol as protocol

BUFSIZE = 1500
ADMIN_PASSWORD = "admin"

def printProbleme(probleme):
    print("probleme is \n", probleme)
    sys.exit(1)


def load_dict(path):

    if not os.path.exists(path):
        printProbleme("path doesnt exists")

    FILE = open(path, "r", encoding="utf-8")
    TXT = FILE.read()
    FILE.close()

    if not TXT.strip():
        printProbleme("txt is probleme")

    DATA = json.loads(TXT)
    if isinstance(DATA, dict):
        CPT = {}
        for i, j in DATA.items():
            CPT[str(i)] = str(j)
        return CPT

    printProbleme("load dict got a trouble")

def save_dict(path, dico):
    FILE = open(path, "w", encoding="utf-8")
    TXT = json.dumps(dico, ensure_ascii=False, indent=2)
    FILE.write(TXT)
    FILE.close()



def load_all_dicts(dicts):
    tab = {}
    for d in dicts:
        tab[d] = load_dict(d)
    return tab


def handle_get(dicos, args,host,port,line):

    if len(args) < 2:
        return protocol.make_response_err("Usage: GET <dico> <key>")

    element = args[0];

    if element not in dicos:
        if host is not None:
            return master(host,port,line)
        return protocol.make_response_err("Dico not found")

    dico = dicos[element]

    CLE = " ".join(args[1:])
    VALUE = dico.get(CLE)


    if VALUE is None:
        if host is not None:
            return master(host,port,line)
        return protocol.make_response_err("Key not found")

    return protocol.make_response_ok(VALUE)

def handle_pref(dicos, args,host,port,line):

    if len(args) < 2:
        return protocol.make_response_err("Usage: PREF <dico> <prefix>")

    element = args[0]
    if element not in dicos:
        if host is not None:
            return master(host,port,line)
        return protocol.make_response_err("Dico not found")

    dico = dicos[element]


    prefix = " ".join(args[1:])

    pairs = []
    for k, v in dico.items():
        if k.startswith(prefix):
            pairs.append(f"{k}={v}")



    if not pairs:
        if host is not None:
            return master(host,port,line)
        return protocol.make_response_ok()

    return protocol.make_response_ok(*pairs)

def check_admin(args):
    
    if len(args) < 2:
        return False, None, None

    password = args[0]
    if password != ADMIN_PASSWORD:
        return False, None, None

    dico_name = args[1]
    rest = args[2:]
    return True, dico_name, rest

def handle_add(dicos, args):
    FINE, dico_name, rest = check_admin(args)
    if not FINE:
        return protocol.make_response_err("Unauthorized")

    if dico_name not in dicos:
        return protocol.make_response_err("Dico not found")

    if len(rest) < 2:
        return protocol.make_response_err("Usage: ADD <pwd> <dico> <key> <value...>")

    KEY = rest[0]
    VAL = " ".join(rest[1:])

    DICO = dicos[dico_name]

    if KEY in DICO:
        return protocol.make_response_err("Key already exists")

    DICO[KEY] = VAL
    
    return protocol.make_response_ok(f"ADD {dico_name} {KEY}={VAL}")

def handle_set(dicos, args):
    FINE, dico_name, rest = check_admin(args)
    if not FINE:
        return protocol.make_response_err("Unauthorized")

    if dico_name not in dicos:
        return protocol.make_response_err("Dico not found")

    if len(rest) < 2:
        return protocol.make_response_err("Usage: SET <pwd> <dico> <key> <value...>")

    KEY = rest[0]
    VAL = " ".join(rest[1:])

    DICO = dicos[dico_name]
    DICO[KEY] = VAL
    save_dict(dico_name, DICO)
    return protocol.make_response_ok(f"SET {dico_name} {KEY}={VAL}")



def handle_del(dicos, args):
    FINE, dico_name, rest = check_admin(args)
    if not FINE:
        return protocol.make_response_err("Unauthorized")

    if dico_name not in dicos:
        return protocol.make_response_err("Dico not found")

    if len(rest) < 1:
        return protocol.make_response_err("Usage: DEL <pwd> <dico> <key>")

    KEY = " ".join(rest)

    DICO = dicos[dico_name]

    if KEY not in DICO:
        return protocol.make_response_err("Key not found")

    del DICO[KEY]
    save_dict(dico_name, DICO)
    return protocol.make_response_ok(f"DEL {dico_name} {KEY}")

def master(host, port, line):

    if host is None:
        return protocol.make_response_err("No master configured")

    SOCK = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)

    CONNECT = SOCK.connect_ex((host, port))
    if CONNECT != 0:
        SOCK.close()
        return protocol.make_response_err("Master unreachable")


    SOCK.sendall(line.encode("utf-8"))
    DATA = SOCK.recv(BUFSIZE)
    SOCK.close()

    if not DATA:
        return protocol.make_response_err("Empty response from master")

    return DATA



def process_request(line, dicos,host,port):
    COMMANDE, ARGV = protocol.parse_request(line)

    if COMMANDE == "GET":
        return handle_get(dicos, ARGV,host,port,line)
    elif COMMANDE == "PREF":
        return handle_pref(dicos, ARGV,host,port,line)
    elif COMMANDE == "ADD":
        return handle_add(dicos, ARGV)
    elif COMMANDE == "SET":
        return handle_set(dicos, ARGV)
    elif COMMANDE == "DEL":
        return handle_del(dicos, ARGV)

    return protocol.make_response_err("Unknown command")


def main():

    if len(sys.argv) < 3:
        print("Erreur: Argument invalide.")
        printProbleme(f"Usage: {sys.argv[0]} <port> <json_file>")

    PORT_STR = sys.argv[1]
    if not PORT_STR.isdigit():
        print("Erreur: le port doit être un entier.")
        printProbleme(f"Usage: {sys.argv[0]} <port> <json_file1> [json_file2]")

   
    HOST = None
    PORT = None

    if "master" in sys.argv[2:]:
        pos = sys.argv.index("master")
        JSON = sys.argv[2:pos]
        if len(sys.argv) < pos+3:
            printProbleme("Usage Master: <port> <js1> <js2> master <host> <port>")
        HOST = sys.argv[pos+1]
        PORT = int(sys.argv[pos+2])
    else:
        JSON = sys.argv[2:]
    if not JSON:
        printProbleme("No Json file")
    
    DICO = load_all_dicts(JSON)

    srv = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    srv.bind(("", int(PORT_STR)))
    srv.listen(5)

    if HOST is None:
        print(f"[server] écoute sur le port {int(PORT_STR)} (dict = {', '.join(JSON)})")
    else:
        print(f"[escalve] écoute sur le port {int(PORT_STR)}"
            f"(dicts = {', '.join(JSON)} ; master = {HOST}:{PORT}")


    while True:
        CONNECT, ADDR = srv.accept()

        DATA = CONNECT.recv(BUFSIZE)
        if not DATA:
            CONNECT.close()
            continue

        LIGNE = DATA.decode("utf-8", errors="ignore")
        RESULT = process_request(LIGNE, DICO,HOST, PORT)

        CONNECT.sendall(RESULT)
        CONNECT.close()


if __name__ == "__main__":
    main()
