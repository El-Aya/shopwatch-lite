import unittest

from src.contrat import Diagnostic, Signal
from src.notification import (approuver, choisir_canal, composer, consigner,
                              diffuser)


def exemple(critique=True, niveau="BLOQUANT"):
    s = Signal("SH-0125", "2026-11-27T17:02:11Z", "PAIEMENT", "paiement",
               "production", "JOURNAL", "MAJEUR", "timeout passerelle apres 30s")
    d = Diagnostic("SH-0125", niveau, "Passerelle lente",
                   "Isoler le service paiement", critique, ["PAIEMENT"])
    return s, d


class TestNotification(unittest.TestCase):
    def test_canaux(self):
        self.assertEqual(choisir_canal("BLOQUANT"), "SLACK")
        self.assertEqual(choisir_canal("MAJEUR"), "TEAMS")
        self.assertEqual(choisir_canal("MODERE"), "EMAIL")
        self.assertEqual(choisir_canal("MINEUR"), "TABLEAU")

    def test_canal_inconnu(self):
        with self.assertRaises(ValueError):
            choisir_canal("INCONNU")

    def test_composer(self):
        s, d = exemple()
        lignes = composer(s, d).split("\n")
        self.assertEqual(len(lignes), 5)
        self.assertEqual(lignes[0], "*** BLOQUANT *** Service : paiement")
        self.assertEqual(lignes[1], "Constat : timeout passerelle apres 30s")
        self.assertEqual(lignes[2], "Cause : Passerelle lente")
        self.assertEqual(lignes[3], "A faire : Isoler le service paiement")
        self.assertEqual(lignes[4], "Origines : PAIEMENT")

    def test_composer_plusieurs_origines(self):
        s, d = exemple()
        d.origines = ["PAIEMENT", "SCANNER"]
        self.assertTrue(composer(s, d).endswith("Origines : PAIEMENT + SCANNER"))

    def test_diffuser(self):
        s, d = exemple()
        registre = []
        msg = diffuser(s, d, registre)
        self.assertEqual(registre, [msg])
        self.assertEqual(msg.canal, "SLACK")
        self.assertEqual(msg.destinataire, "astreinte-shop")
        self.assertEqual(msg.signal_ref, "SH-0125")
        self.assertEqual(msg.contenu, composer(s, d))
        self.assertEqual(s.etat, "DIFFUSE")

    def test_approbation(self):
        _, d = exemple()
        self.assertTrue(approuver(d, " OUI "))
        self.assertTrue(approuver(d, "ok"))
        self.assertTrue(approuver(d, "Yes"))
        self.assertTrue(approuver(d, "o"))
        self.assertFalse(approuver(d, "n"))
        self.assertFalse(approuver(d, ""))

    def test_approbation_non_critique(self):
        _, d = exemple(critique=False, niveau="MINEUR")
        self.assertTrue(approuver(d, "n"))

    def test_consigner(self):
        _, d = exemple()
        carnet = []
        entree = consigner(d, True, "astreinte-shop", carnet,
                           "2026-11-27T17:10:00Z")
        self.assertEqual(carnet, [entree])
        self.assertEqual(entree, {
            "ref": "SH-0125",
            "action": "Isoler le service paiement",
            "accord": True,
            "responsable": "astreinte-shop",
            "instant": "2026-11-27T17:10:00Z",
        })


if __name__ == "__main__":
    unittest.main()