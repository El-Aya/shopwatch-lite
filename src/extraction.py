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


_GRAVITE_JOURNAL = {
    "FATAL": "BLOQUANT",
    "CRITICAL": "BLOQUANT",
    "ERROR": "MAJEUR",
    "WARN": "MODERE",
    "WARNING": "MODERE",
}


def lire_journal(ligne: str, numero: int, origine: str = "PAIEMENT",
                 env: str = "production") -> Signal:
    champs = ligne.split(None, 4)
    if len(champs) < 5:
        raise ValueError("ligne de journal invalide : moins de 5 champs")
    jour, heure, service, niveau, message = champs
    return Signal(
        ref=f"SH-{numero:04d}",
        date=f"{jour}T{heure}Z",
        origine=origine,
        service=service,
        env=env,
        categorie="JOURNAL",
        gravite=_GRAVITE_JOURNAL.get(niveau.upper(), "MINEUR"),
        texte=masquer_donnees(message),
    )


def lire_scan(rapport: dict, numero: int, env: str = "production") -> Signal:
    raise NotImplementedError


def lire_build(rapport: dict, numero: int, env: str = "production") -> Signal:
    raise NotImplementedError