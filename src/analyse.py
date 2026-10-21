from src.contrat import Diagnostic, Signal

def est_repete(sig: Signal, vus: set) -> bool:
    """Clé (date, origine, service, categorie, texte).
    Renvoie True si la clé est déjà dans vus ; sinon l'ajoute et renvoie False."""
    cle = (sig.date, sig.origine, sig.service, sig.categorie, sig.texte)
    if cle in vus:
        return True
    vus.add(cle)
    return False


def compter_incidents(sig: Signal, compteur: dict) -> int:
    """Si categorie vaut JOURNAL et gravite vaut MAJEUR ou BLOQUANT:
    ajoute 1 au compteur de son service et renvoie le nouveau total. Sinon renvoie 0."""
    if sig.categorie == "JOURNAL" and sig.gravite in ["MAJEUR", "BLOQUANT"]:
        compteur[sig.service] = compteur.get(sig.service, 0) + 1
        return compteur[sig.service]
    return 0


def chercher_fiches(sig: Signal, base: dict) -> list:
    """Recherche les conseils dont le mot-clé figure dans le texte (casse ignorée)."""
    texte_lower = sig.texte.lower()
    conseils = []
    for mot_cle, conseil in base.items():
        if mot_cle.lower() in texte_lower:
            conseils.append(conseil)
    return conseils


def evaluer(sig: Signal, nb_incidents: int = 0) -> str:
    """(1) si nb_incidents >= 4: BLOQUANT; (2) sinon la gravite du signal."""
    if nb_incidents >= 4:
        return "BLOQUANT"
    return sig.gravite


def diagnostiquer(sig: Signal, base: dict, nb_incidents: int = 0) -> Diagnostic:
    """Rassemble l'évaluation, la recherche de fiches et prépare le Diagnostic."""
    niveau = evaluer(sig, nb_incidents)
    conseils = chercher_fiches(sig, base)

    if conseils:
        cause = "; ".join(conseils)
    else:
        cause = "Cause inconnue verification manuelle"

    if sig.categorie == "FAILLE":
        action = f"Corriger la dependance {sig.service}"
    elif sig.categorie == "BUILD_ECHEC":
        action = f"Rejouer le build {sig.service}"
    elif niveau == "BLOQUANT":
        action = f"Isoler le service {sig.service}"
    else:
        action = "Observer"

    critique = action.startswith("Isoler")
    sig.etat = "EVALUE"

    return Diagnostic(
        signal_ref=sig.ref,
        niveau=niveau,
        cause=cause,
        action=action,
        critique=critique,
        origines=[sig.origine],
    )