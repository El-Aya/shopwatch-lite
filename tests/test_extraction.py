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

    # ---- lire_journal
    def test_lire_journal(self):
        sig = lire_journal(LIGNE, 42)
        self.assertEqual(sig.ref, "SH-0042")
        self.assertEqual(sig.date, "2026-11-27T17:02:11Z")
        self.assertEqual(sig.gravite, "MAJEUR")
        self.assertNotIn("4970123412341234", sig.texte)

    def test_lire_journal_champs_fixes(self):
        sig = lire_journal(LIGNE, 1)
        self.assertEqual(sig.service, "paiement")
        self.assertEqual(sig.categorie, "JOURNAL")
        self.assertEqual(sig.origine, "PAIEMENT")
        self.assertEqual(sig.env, "production")
        self.assertEqual(sig.texte, "timeout passerelle apres 30s card=[MASQUE]")

    def test_lire_journal_gravites(self):
        attendu = {"FATAL": "BLOQUANT", "CRITICAL": "BLOQUANT",
                   "ERROR": "MAJEUR", "WARN": "MODERE", "WARNING": "MODERE",
                   "INFO": "MINEUR", "debug": "MINEUR", "error": "MAJEUR"}
        for niveau, gravite in attendu.items():
            ligne = f"2026-11-27 17:00:00 paiement {niveau} message"
            self.assertEqual(lire_journal(ligne, 1).gravite, gravite, niveau)

    def test_lire_journal_ligne_trop_courte(self):
        with self.assertRaises(ValueError):
            lire_journal("2026-11-27 17:00:00 paiement ERROR", 1)


if __name__ == "__main__":
    unittest.main()