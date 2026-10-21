import unittest

from src.extraction import (lire_build, lire_journal, lire_scan,
                            masquer_donnees)

LIGNE = ("2026-11-27 17:02:11 paiement ERROR timeout passerelle apres 30s "
         "card=4970123412341234")


class TestExtraction(unittest.TestCase):
    # ---- masquer_donnees
    def test_masquer_donnees(self):
        self.assertEqual(masquer_donnees("client=bob pwd=abc123"),
                         "client=bob pwd=[MASQUE]")

    def test_masquer_tous_les_parametres(self):
        for nom in ("password", "pwd", "token", "secret", "card", "iban"):
            self.assertEqual(masquer_donnees(f"{nom}=valeur"), f"{nom}=[MASQUE]")

    def test_masquer_casse_ignoree(self):
        self.assertEqual(masquer_donnees("PWD=abc Token=xyz"),
                         "PWD=[MASQUE] Token=[MASQUE]")

    def test_masquer_forme_deux_points(self):
        self.assertEqual(masquer_donnees("secret: abc123"), "secret: [MASQUE]")

    def test_masquer_la_valeur_s_arrete_au_separateur(self):
        self.assertEqual(masquer_donnees("a=1&token=abc&b=2"),
                         "a=1&token=[MASQUE]&b=2")
        self.assertEqual(masquer_donnees("pwd=abc,suite"), "pwd=[MASQUE],suite")
        self.assertEqual(masquer_donnees("pwd=abc;suite"), "pwd=[MASQUE];suite")

    def test_masquer_sans_secret(self):
        self.assertEqual(masquer_donnees("rien a cacher"), "rien a cacher")


if __name__ == "__main__":
    unittest.main()