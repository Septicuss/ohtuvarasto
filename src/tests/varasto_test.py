import unittest
from varasto import Varasto


class TestVarasto(unittest.TestCase):
    def setUp(self):
        self.tilavuus = 10
        self.alku_saldo_puolitaynna = 5
        self.alku_saldo_ylitaynna = 20

        self.varasto = Varasto(10)
        self.virheellinen_varasto = Varasto(-1, -1)
        self.puolitaynna_varasto = Varasto(self.tilavuus, self.alku_saldo_puolitaynna)
        self.taynna_varasto = Varasto(self.tilavuus, self.tilavuus)
        self.ylitaynna_varasto = Varasto(self.tilavuus, self.alku_saldo_ylitaynna)

    def test_konstruktori_luo_tyhjan_varaston(self):
        # https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertAlmostEqual
        self.assertAlmostEqual(self.varasto.saldo, 0)

    def test_uudella_varastolla_oikea_tilavuus(self):
        self.assertAlmostEqual(self.varasto.tilavuus, 10)

    def test_lisays_lisaa_saldoa(self):
        self.varasto.lisaa_varastoon(8)

        self.assertAlmostEqual(self.varasto.saldo, 8)

    def test_lisays_lisaa_pienentaa_vapaata_tilaa(self):
        self.varasto.lisaa_varastoon(8)

        # vapaata tilaa pitäisi vielä olla tilavuus-lisättävä määrä eli 2
        self.assertAlmostEqual(self.varasto.paljonko_mahtuu(), 2)

    def test_ottaminen_palauttaa_oikean_maaran(self):
        self.varasto.lisaa_varastoon(8)

        saatu_maara = self.varasto.ota_varastosta(2)

        self.assertAlmostEqual(saatu_maara, 2)

    def test_ottaminen_lisaa_tilaa(self):
        self.varasto.lisaa_varastoon(8)

        self.varasto.ota_varastosta(2)

        # varastossa pitäisi olla tilaa 10 - 8 + 2 eli 4
        self.assertAlmostEqual(self.varasto.paljonko_mahtuu(), 4)

    def test_virheellinen_tilavuus(self):
        self.assertEqual(self.virheellinen_varasto.tilavuus, 0)

    def test_virheellinen_alku_saldo(self):
        self.assertEqual(self.virheellinen_varasto.saldo, 0)

    def test_virheellinen_maara_ei_muuta_saldoa(self):
        alku_maara = self.varasto.saldo

        self.varasto.lisaa_varastoon(-1)

        self.assertEqual(self.varasto.saldo, alku_maara)

    def test_lisays_ei_ylita_tilavuutta(self):
        self.varasto.lisaa_varastoon(self.alku_saldo_ylitaynna)

        self.assertEqual(self.varasto.saldo, self.varasto.tilavuus)

    def test_virheellinen_ottaminen(self):
        saatu_maara = self.varasto.ota_varastosta(-1)

        self.assertEqual(saatu_maara, 0.0)

    def test_kaikki_mita_voidaan_ottaa(self):
        alku_maara = self.varasto.saldo
        saatu_maara = self.varasto.ota_varastosta(self.alku_saldo_ylitaynna)

        self.assertEqual(saatu_maara, alku_maara)

    def test_merkkijono(self):
        odotettu = f"saldo = {self.alku_saldo_puolitaynna}, vielä tilaa {self.tilavuus - self.alku_saldo_puolitaynna}"

        self.assertEqual(self.puolitaynna_varasto.__str__(), odotettu)
