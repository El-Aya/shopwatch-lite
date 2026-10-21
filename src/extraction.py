import re

from src.contrat import Signal

# Parametres sensibles : nom=valeur ou nom: valeur (casse ignoree).
# La valeur s'arrete a un espace, &, , ou ;
_MOTIF_SECRET = re.compile(
    r"\b(password|pwd|token|secret|card|iban)(\s*[=:]\s*)([^\s&,;]+)",
    re.IGNORECASE,
)


def masquer_donnees(texte: str) -> str:
    return _MOTIF_SECRET.sub(r"\1\2[MASQUE]", texte)


def lire_journal(ligne: str, numero: int, origine: str = "PAIEMENT",
                 env: str = "production") -> Signal:
    raise NotImplementedError


def lire_scan(rapport: dict, numero: int, env: str = "production") -> Signal:
    raise NotImplementedError


def lire_build(rapport: dict, numero: int, env: str = "production") -> Signal:
    raise NotImplementedError