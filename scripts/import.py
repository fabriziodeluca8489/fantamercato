#!/usr/bin/env python3
"""Converte l'xlsx delle rose (Divisione A) in seed.sql. Uso: import.py file.xlsx > seed.sql"""
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
# Blocchi di righe per ruolo, dopo la riga di intestazione: 3 P, 8 D, 8 C, 6 A
RUOLI = ["P"] * 3 + ["D"] * 8 + ["C"] * 8 + ["A"] * 6


def col(ref):
    """Indice colonna (0-based) da riferimento tipo 'C5'."""
    n = 0
    for ch in re.match(r"[A-Z]+", ref).group():
        n = n * 26 + ord(ch) - 64
    return n - 1


def righe(path):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    out = []
    for r in root.iterfind(".//m:row", NS):
        d = {}
        for c in r.iterfind("m:c", NS):
            d[col(c.get("r"))] = "".join(t.text or "" for t in c.iter("{%s}t" % NS["m"])) or (
                c.findtext("m:v", "", NS)
            )
        out.append(d)
    return out


def q(s):
    return "'" + s.replace("'", "''") + "'"


def main(path):
    rows = righe(path)
    head, body = rows[0], rows[1 : 1 + len(RUOLI)]
    assert len(body) == len(RUOLI) and rows[1 + len(RUOLI)].get(0) == "totale", "layout inatteso"
    print("-- generato da scripts/import.py")
    print("truncate players, teams restart identity cascade;")
    # Ogni squadra occupa 2 colonne (nome, costo) + 1 colonna vuota di separazione
    for tid, i in enumerate(sorted(k for k in head if head[k] != "costo"), 1):
        print(f"insert into teams(id,nome) values ({tid},{q(head[i])});")
        for ruolo, r in zip(RUOLI, body):
            print(
                f"insert into players(team_id,nome,ruolo,costo) values "
                f"({tid},{q(r[i])},'{ruolo}',{int(r[i + 1])});"
            )


if __name__ == "__main__":
    main(sys.argv[1])
