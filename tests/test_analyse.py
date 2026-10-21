import unittest
from src.analyse import (
    compter_incidents,
    diagnostiquer,
    est_repete,
    evaluer,
)
from src.contrat import FICHES, Signal


def sig(
    categorie="JOURNAL",
    gravite="MAJEUR",
    texte="timeout passerelle apres 30s",
    service="paiement",
):
    return Signal(
        "SH-0001",
        "2026-11-27T17:00:00Z",
        "PAIEMENT",
        service,
        "production",
        categorie,
        gravite,
        texte,
    )


class TestAnalyse(unittest.TestCase):

    def test_repete(self):
        vus = set()
        s = sig()
        self.assertFalse(est_repete(s, vus))
        self.assertTrue(est_repete(s, vus))

    def test_compter_incidents(self):
        compteur = {}
        s_majeur = sig(gravite="MAJEUR")
        s_mineur = sig(gravite="MINEUR")
        self.assertEqual(compter_incidents(s_majeur, compteur), 1)
        self.assertEqual(compter_incidents(s_majeur, compteur), 2)
        self.assertEqual(compter_incidents(s_mineur, compteur), 0)

    def test_evaluer_panne_en_boucle(self):
        s = sig()
        self.assertEqual(evaluer(s, 4), "BLOQUANT")
        self.assertEqual(evaluer(s, 3), "MAJEUR")

    def test_diagnostiquer_faille(self):
        s_faille = sig(categorie="FAILLE", service="lib-panier")
        diag = diagnostiquer(s_faille, FICHES)
        self.assertEqual(diag.action, "Corriger la dependance lib-panier")

    def test_diagnostiquer_bloquant(self):
        s = sig()
        diag = diagnostiquer(s, FICHES, nb_incidents=4)
        self.assertTrue(diag.critique)
        self.assertEqual(diag.action, "Isoler le service paiement")


if __name__ == "__main__":
    unittest.main()