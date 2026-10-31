"""Testes básicos dos endpoints com respostas simuladas da Fruityvice."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import main


class RespostaFalsa:
    def __init__(self, status_code, dados=None):
        self.status_code = status_code
        self._dados = dados or {}

    def json(self):
        return self._dados


class TesteApiCasaDeSucos(unittest.TestCase):
    def setUp(self):
        main.sucos.clear()
        main.proximo_id = 1
        self.cliente = TestClient(main.app)

    @patch("main.requests.get")
    def test_consultar_fruta(self, requisicao):
        requisicao.return_value = RespostaFalsa(
            200,
            {"name": "Banana", "nutritions": {"calories": 96, "sugar": 17.2}},
        )
        resposta = self.cliente.get("/frutas/banana")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["nome"], "Banana")
        self.assertEqual(resposta.json()["calorias"], 96.0)
        self.assertEqual(resposta.json()["acucar"], 17.2)

    @patch("main.requests.get")
    def test_fruta_nao_encontrada(self, requisicao):
        requisicao.return_value = RespostaFalsa(404)
        resposta = self.cliente.get("/frutas/fruta-inexistente")
        self.assertEqual(resposta.status_code, 404)
        self.assertIn("não foi encontrada", resposta.json()["detail"])

    @patch("main.requests.get")
    def test_cadastrar_e_listar_suco(self, requisicao):
        requisicao.side_effect = [
            RespostaFalsa(200, {"name": "Banana", "nutritions": {"calories": 96, "sugar": 17.2}}),
            RespostaFalsa(200, {"name": "Strawberry", "nutritions": {"calories": 32, "sugar": 4.9}}),
        ]
        corpo = {
            "nome": "Vitamina Tropical",
            "frutas": ["banana", "strawberry"],
            "tem_gosto_de": "Tamarindo",
        }
        criada = self.cliente.post("/sucos", json=corpo)
        self.assertEqual(criada.status_code, 201)
        self.assertEqual(criada.json()["total_calorias"], 128.0)
        self.assertEqual(criada.json()["total_acucar"], 22.1)

        listagem = self.cliente.get("/sucos")
        self.assertEqual(listagem.status_code, 200)
        self.assertEqual(len(listagem.json()), 1)

    @patch("main.requests.get")
    def test_atualizar_frutas_do_suco(self, requisicao):
        requisicao.side_effect = [
            RespostaFalsa(200, {"name": "Banana", "nutritions": {"calories": 96, "sugar": 17.2}}),
            RespostaFalsa(200, {"name": "Apple", "nutritions": {"calories": 52, "sugar": 10.4}}),
        ]
        criado = self.cliente.post(
            "/sucos",
            json={"nome": "Suco simples", "frutas": ["banana"], "tem_gosto_de": "Doce"},
        )
        self.assertEqual(criado.status_code, 201)

        atualizado = self.cliente.put("/sucos/1", json={"frutas": ["apple"]})
        self.assertEqual(atualizado.status_code, 200)
        self.assertEqual(atualizado.json()["frutas"], ["apple"])
        self.assertEqual(atualizado.json()["total_calorias"], 52.0)
        self.assertEqual(atualizado.json()["total_acucar"], 10.4)

    def test_atualizar_id_inexistente(self):
        resposta = self.cliente.put("/sucos/999", json={"frutas": ["banana"]})
        self.assertEqual(resposta.status_code, 404)


if __name__ == "__main__":
    unittest.main()
