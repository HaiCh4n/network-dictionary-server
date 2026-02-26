# 📚 DICO — Distributed Dictionary Server

> A lightweight TCP-based key-value dictionary system with a custom protocol, admin authentication, and master/slave architecture — built in **pure Python**.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 `GET` | Exact key lookup in a named dictionary |
| 🔎 `PREF` | Prefix-based search returning all matching entries |
| 🔐 `ADD / SET / DEL` | Admin commands protected by password |
| 🌐 Master / Slave | Slave servers forward unknown requests upstream |
| 📄 JSON Storage | Dictionaries are plain `.json` files — easy to edit |
| 🔵 IPv6 | All sockets use `AF_INET6` |
| 🧱 Zero dependencies | Only Python 3 stdlib (`socket`, `json`, `os`, `sys`) |

---

## 🗂️ Project Structure

```
.
├── dico_server.py      # Server (simple or slave mode)
├── dico_client.py      # Standard client (GET, PREF)
├── dico_admin.py       # Admin client (ADD, SET, DEL)
├── dico_protocol.py    # Protocol helpers (encode/decode)
├── protocol_dico.md    # Full protocol specification
└── *.json              # Your dictionary files
```

---

## ⚡ Quick Start

### 1. Prepare a dictionary file

```json
// mois_duree.json
{
  "janvier": "31",
  "février": "28",
  "mars": "31",
  "avril": "30",
  "juillet": "31"
}
```

### 2. Start the server

```bash
python3 dico_server.py 7777 mois_duree.json
```

### 3. Query from the client

```bash
# Exact lookup
python3 dico_client.py 7777 GET mois_duree.json février
# → 28

# Prefix search
python3 dico_client.py 7777 PREF mois_duree.json j
# → janvier=31 juillet=31
```

---

## 🔐 Admin Commands

Admin commands require a password (default: `admin`).

```bash
# Add a new entry (fails if key already exists)
python3 dico_admin.py 7777 admin ADD mois_duree.json novembre 30

# Create or overwrite an entry
python3 dico_admin.py 7777 admin SET mois_duree.json février 29

# Delete an entry
python3 dico_admin.py 7777 admin DEL mois_duree.json juillet
```

---

## 🏗️ Master / Slave Architecture

A slave server forwards any request it cannot answer locally to a master server.

```
[Client] ──► [Slave :8888] ──► (if not found) ──► [Master :7777]
```

```bash
# Start the master
python3 dico_server.py 7777 punchlines.json

# Start a slave pointing to the master
python3 dico_server.py 8888 mois_duree.json master localhost 7777
```

The slave transparently relays the original request and forwards the master's response back to the client. The client sees no difference.

---

## 🔌 Protocol Overview

All messages are **single UTF-8 lines** terminated by `\n`, sent over a TCP connection. One connection = one request + one response.

### Request format

```
COMMAND arg1 arg2 ... argN\n
```

### Response format

```
OK <payload>\n       # success
ERR <message>\n      # failure
```

### Full command table

| Command | Sender | Format |
|---|---|---|
| `GET` | Client | `GET <dico> <key...>` |
| `PREF` | Client | `PREF <dico> <prefix...>` |
| `ADD` | Admin | `ADD <pwd> <dico> <key> <value...>` |
| `SET` | Admin | `SET <pwd> <dico> <key> <value...>` |
| `DEL` | Admin | `DEL <pwd> <dico> <key...>` |

> See [`protocol_dico.md`](./protocol_dico.md) for the full specification.

---

## 🧪 Testing Scenarios

```bash
# Test 1 — key found
python3 dico_client.py 7777 GET mois_duree.json mars
# Expected: OK 31

# Test 2 — key not found
python3 dico_client.py 7777 GET mois_duree.json décembre
# Expected: ERR Key not found

# Test 3 — unknown dictionary
python3 dico_client.py 7777 GET unknown.json test
# Expected: ERR Dico not found

# Test 4 — prefix with no results
python3 dico_client.py 7777 PREF mois_duree.json z
# Expected: (empty)

# Test 5 — admin bad password
python3 dico_admin.py 7777 wrongpass DEL mois_duree.json mars
# Expected: ERR Unauthorized
```

---

## ⚙️ Configuration

| Parameter | Location | Default |
|---|---|---|
| Admin password | `dico_server.py` → `ADMIN_PASSWORD` | `"admin"` |
| Buffer size | `dico_client.py`, `dico_server.py` → `BUFSIZE` | `1500` bytes |
| Default host | `dico_client.py`, `dico_admin.py` → `HOST` | `"localhost"` |

> 💡 **Security note:** The admin password travels in plaintext. For production use, consider adding TLS or restricting admin access to loopback only.

---

## 🔧 Requirements

- Python **3.6+**
- No external libraries required

---

## 📜 License

This project is for educational purposes. See [LICENSE](./LICENSE) for details.

---

<div align="center">
  <sub>Built with 🐍 Python · Université de Bordeaux · Projet Réseaux</sub>
</div>
