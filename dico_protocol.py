COMMENDE_GET = "GET"

def make_request(cmd, *args):
    
    cmd_str = str(cmd)
    if args:
        arg_list = []
        for a in args:
            arg_list.append(str(a))
        line = cmd_str + " " + " ".join(arg_list) + "\n"
    else:
        line = cmd_str + "\n"
    return line.encode("utf-8")



def parse_request(line):
    
    txt = line.strip()
    if txt == "":
        return None, []

    parts = txt.split()
    cmd = parts[0].upper()
    args = parts[1:]
    return cmd, args



def make_response_ok(*CPT):

    if len(CPT) == 0:
        ligne = "OK\n"
    else:

        TAB = []
        for i in CPT:
            TAB.append(str(i))
        load = " ".join(TAB)
        ligne = "OK " + load + "\n"
        
    return ligne.encode("utf-8")

def make_response_err(message):
    
    RES = str(message)
    LIGNE = "ERR " + RES + "\n"
    return LIGNE.encode("utf-8")



def parse_response(ligne):
    
    TXT = ligne.strip()
    if TXT == "":
        return None, ""

    parties = TXT.split(" ", 1)
    status = parties[0]
    if len(parties) == 2:
        payload = parties[1]
    else:
        payload = ""

    return status, payload


