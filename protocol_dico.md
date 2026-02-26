## 1. Objectif

Le protocole **DICO** permet la manipulation à distance de dictionnaires JSON via des sockets TCP, entre un client et un serveur écrits en Python.

Le système actuel prend en charge :

- Un client standard avec les commandes `GET` et `PREF`.
- Un client administrateur avec les commandes `ADD`, `SET` et `DEL` (le mot de passe est inclus dans chaque requête).
- Une architecture maître / esclave, où un serveur peut déléguer une requête à un serveur maître si la donnée n’est pas disponible localement.

Ce document spécifie uniquement le protocole **tel qu’il est réellement implémenté** dans les fichiers :

`dico_protocol.py`, `dico_server.py`, `dico_client.py`, `dico_admin.py`.

---

## 2. Transport et encodage

- **Transport** : TCP
- **Encodage** : UTF-8
- **Délimitation (framing)** : chaque message (requête ou réponse) est une **ligne unique** terminée par `\n`.
- Une connexion correspond à **une requête et une réponse**.

---

## 3. Acteurs et exécution

### 3.1 Serveur

Lancement en mode simple :

```
python3 dico_server.py <port> <json_file1> [json_file2 ...]

```

Lancement en mode esclave relié à un maître :

```
python3 dico_server.py <port> <json_file1> [json_file2 ...] master <host_master> <port_master>

```

Chaque fichier JSON représente un dictionnaire accessible via son nom.

### 3.2 Client standard

Le client standard envoie une requête simple et affiche la réponse.

Il se connecte par défaut à `localhost`.

Exécution :

```
python3 dico_client.py <port> <command> <dico> <args...>

```

Exemples :

```
python3 dico_client.py 7777 GET mois_duree.json février
python3 dico_client.py 7777 PREF mois_duree.json j

```

### 3.3 Client administrateur

Le client administrateur envoie des requêtes nécessitant un mot de passe.

Connexion par défaut à `localhost`.

Exécution :

```
python3 dico_admin.py <port> <password> <command> <dico> <args...>

```

Exemples :

```
python3 dico_admin.py 7777 admin ADD mois_duree.json novembre 30
python3 dico_admin.py 7777 admin SET mois_duree.json fevrier 28
python3 dico_admin.py 7777 admin DEL mois_duree.json juillet

```

---

## 4. Format général des messages

### 4.1. Requête (client → serveur)

```
COMMANDE arg1 arg2 ... argN\n

```

- Les arguments sont séparés par des espaces.
- Le serveur reconstitue certains champs avec des espaces dans les noms :
    - `GET <dico> <key...>` → clé = `" ".join(args[1:])`
    - `PREF <dico> <prefix...>` → préfixe = `" ".join(args[1:])`
    - `ADD/SET <pwd> <dico> <key> <value...>` → valeur = `" ".join(rest[1:])`
    - `DEL <pwd> <dico> <key...>` → clé = `" ".join(rest)`

### 4.2. Réponse (serveur → client)

```
OK <payload...>\n
ERR <message>\n

```

- `OK` sans contenu : `OK\n`
- `ERR` contient un message explicite.

---

## 5. Dictionnaires multiples

Le serveur peut charger plusieurs fichiers JSON simultanément.

Chaque dictionnaire est identifié par son **nom de fichier JSON**.

Exemples : `mois_duree.json`, `punchlines.json`.

Toutes les commandes prennent ce nom comme premier argument :

```
<dico>

```

---

## 6. Commandes client standard

### 6.1. GET

**Requête :**

```
GET <dico> <key...>\n

```

**Succès :**

```
OK <value>\n

```

**Erreurs possibles :**

- `ERR Usage: GET <dico> <key>`
- `ERR Dico not found`
- `ERR Key not found`
- `ERR No master configured`
- `ERR Master unreachable`
- `ERR Empty response from master`

**Comportement :**

- Si le dictionnaire n’existe pas et qu’un maître est défini → la requête est transférée.
- Si la clé est absente et qu’un maître est défini → transfert au maître.
- Sinon → erreur locale.

---

### 6.2. PREF

**Requête :**

```
PREF <dico> <prefix...>\n

```

**Succès :**

- Si résultat(s) :

```
OK key1=value1 key2=value2 ...\n

```

- Si aucun résultat :

```
OK\n

```

**Erreurs possibles :**

- `ERR Usage: PREF <dico> <prefix>`
- `ERR Dico not found`
- `ERR No master configured`
- `ERR Master unreachable`
- `ERR Empty response from master`

**Comportement :**

- Si le dictionnaire n’existe pas localement et qu’un maître est configuré → forward.
- Si aucun résultat local et qu’un maître est configuré → forward.
- Sinon → renvoyer `OK` vide.

---

## 7. Commandes administrateur

### 7.1. ADD

**Requête :**

```
ADD <pwd> <dico> <key> <value...>\n

```

**Succès :**

```
OK ADD <dico> <key>=<value>\n

```

**Erreurs possibles :**

- `ERR Unauthorized`
- `ERR Dico not found`
- `ERR Usage: ADD <pwd> <dico> <key> <value...>`
- `ERR Key already exists`

---

### 7.2. SET

**Requête :**

```
SET <pwd> <dico> <key> <value...>\n

```

**Succès :**

```
OK SET <dico> <key>=<value>\n

```

**Erreurs possibles :**

- `ERR Unauthorized`
- `ERR Dico not found`
- `ERR Usage: SET <pwd> <dico> <key> <value...>`

---

### 7.3. DEL

**Requête :**

```
DEL <pwd> <dico> <key...>\n

```

**Succès :**

```
OK DEL <dico> <key>\n

```

**Erreurs possibles :**

- `ERR Unauthorized`
- `ERR Dico not found`
- `ERR Usage: DEL <pwd> <dico> <key>`
- `ERR Key not found`

---

## 8. Hiérarchie maître / esclave

Lorsqu’un serveur esclave ne trouve pas une clé ou un dictionnaire, il peut transférer la requête au serveur maître.

**Principe :**

- L’esclave envoie au maître la **même ligne de requête** qu’il a reçue.
- Le maître renvoie une réponse conforme (`OK` ou `ERR`).
- L’esclave retransmet cette réponse au client.

**Erreurs spécifiques :**

- `ERR No master configured`
- `ERR Master unreachable`
- `ERR Empty response from master`

---

## 9. Commande inconnue

Si la commande n’est pas reconnue par le serveur :

```
ERR Unknown command\n

```

---

## 10. Résumé des commandes

### Client standard

- `GET <dico> <key...>`
- `PREF <dico> <prefix...>`

### Client administrateur

- `ADD <pwd> <dico> <key> <value...>`
- `SET <pwd> <dico> <key> <value...>`
- `DEL <pwd> <dico> <key...>`

### Communication maître / esclave

- Reprise du même format de requête et de réponse que le client standard.