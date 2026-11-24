"""Envoie la requête n° N de api.http à l'API locale et affiche le statut et le corps."""
import re, sys, urllib.request, urllib.error
from pathlib import Path
n = sys.argv[1]
texte = Path("api.http").read_text(encoding="utf-8")
bloc = re.search(rf"^### {n}\..*?\n(.*?)(?=^### |\Z)", texte, re.S | re.M).group(1).strip()
premiere, _, reste = bloc.partition("\n")
methode, url = premiere.split()
url = url.replace("{{base}}", "http://localhost:8000")
corps = reste.split("\n\n", 1)[1].encode() if "\n\n" in reste else None
req = urllib.request.Request(url, data=corps, method=methode, headers={"Content-Type": "application/json"})
try:
    r = urllib.request.urlopen(req)
except urllib.error.HTTPError as e:
    r = e
print(r.status, r.read().decode())
