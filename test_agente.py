import unittest

from agente import CaixaDeSaidaFicticia, executar, propor_registro


class TestAprovacao(unittest.TestCase):
    def setUp(self):
        self.ferramenta = CaixaDeSaidaFicticia()
        self.proposta = propor_registro("contrato_exemplo.txt")

    def test_recusa_e_ausencia_nao_executam(self):
        for decisao in ("", "recusar", "sim"):
            self.assertIn("não executada", executar(self.proposta, decisao, self.ferramenta))
        self.assertEqual(self.ferramenta.registros, {})

    def test_aprovacao_executa_uma_vez(self):
        primeira = executar(self.proposta, "aprovar", self.ferramenta)
        segunda = executar(self.proposta, "aprovar", self.ferramenta)
        self.assertEqual(primeira, segunda)
        self.assertEqual(len(self.ferramenta.registros), 1)

    def test_entrada_invalida(self):
        with self.assertRaises(ValueError):
            propor_registro(" ")


if __name__ == "__main__":
    unittest.main()
