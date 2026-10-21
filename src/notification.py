from src.contrat import Diagnostic, Message, Signal

CANAUX = {"BLOQUANT": "SLACK", "MAJEUR": "TEAMS",
          "MODERE": "EMAIL", "MINEUR": "TABLEAU"}


def choisir_canal(niveau: str) -> str:
    if niveau not in CANAUX:
        raise ValueError(f"Niveau inconnu : {niveau}")
    return CANAUX[niveau]


def composer(sig: Signal, diag: Diagnostic) -> str:
    return "\n".join([
        f"*** {diag.niveau} *** Service : {sig.service}",
        f"Constat : {sig.texte}",
        f"Cause : {diag.cause}",
        f"A faire : {diag.action}",
        f"Origines : {' + '.join(diag.origines)}",
    ])


def diffuser(sig: Signal, diag: Diagnostic, registre: list) -> Message:
    raise NotImplementedError


def approuver(diag: Diagnostic, reponse: str) -> bool:
    raise NotImplementedError


def consigner(diag: Diagnostic, accord: bool, responsable: str,
              carnet: list, instant: str) -> dict:
    raise NotImplementedError
def diffuser(sig: Signal, diag: Diagnostic, registre: list) -> Message:
    msg = Message(sig.ref, choisir_canal(diag.niveau),
                  "astreinte-shop", composer(sig, diag))
    registre.append(msg)
    sig.etat = "DIFFUSE"
    return msg
def approuver(diag: Diagnostic, reponse: str) -> bool:
    if not diag.critique:
        return True
    return reponse.strip().lower() in {"o", "oui", "ok", "yes"}


def consigner(diag: Diagnostic, accord: bool, responsable: str,
              carnet: list, instant: str) -> dict:
    entree = {"ref": diag.signal_ref, "action": diag.action,
              "accord": accord, "responsable": responsable,
              "instant": instant}
    carnet.append(entree)
    return entree  