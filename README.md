# DICO — Distributed Dictionary Server over TCP

A lightweight client-server dictionary system built in Python,
using a custom text-based TCP protocol.

## Features
- Query JSON-based key-value dictionaries remotely
- `GET` — exact key lookup
- `PREF` — prefix-based search
- Admin commands (`ADD`, `SET`, `DEL`) with password authentication
- Master/slave architecture for request forwarding
- IPv6 socket support

## Tech Stack
- Python 3 (stdlib only — `socket`, `json`, `os`, `sys`)
- Custom application-layer protocol over TCP
- JSON file storage

## Use Case
Educational project — demonstrates socket programming,
custom protocol design, and distributed server architecture.
