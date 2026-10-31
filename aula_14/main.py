"""API de uma Casa de Sucos integrada à Fruityvice."""

from typing import Any

import requests
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

URL_FRUITYVICE = "https://www.fruityvice.com/api/fruit"
TEMPO_LIMITE = 10

app = FastAPI(
    title="API da Casa de Sucos",
    description=(
        "API para consultar informações nutricionais de frutas e cadastrar sucos. "
        "Os valores são calculados considerando 100 g de cada fruta."
    ),
    version="1.0.0",
)


class SucoEntrada(BaseModel):
    nome: str = Field(min_length=1, description="Nome do suco")
    frutas: list[str] = Field(min_length=1, description="Frutas em inglês, conforme a Fruityvice")
    tem_gosto_de: str = Field(min_length=1, description="Descrição do gosto do suco")


class AtualizacaoFrutas(BaseModel):
    frutas: list[str] = Field(min_length=1, description="Nova lista de frutas")


sucos: dict[int, dict[str, Any]] = {}
proximo_id = 1


def consultar_dados_fruta(nome: str) -> dict[str, Any]:
    """Consulta uma fruta na Fruityvice e devolve os dados necessários."""
    nome_consulta = nome.strip().lower()
    if not nome_consulta:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Informe o nome de uma fruta.",
        )

    try:
        resposta = requests.get(
            f"{URL_FRUITYVICE}/{nome_consulta}",
            timeout=TEMPO_LIMITE,
        )
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="A consulta à base de frutas demorou demais. Tente novamente.",
        )
    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Não foi possível acessar a base de informações das frutas.",
        )

    if resposta.status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"A fruta '{nome_consulta}' não foi encontrada. Confira o nome em inglês e tente novamente.",
        )

    if resposta.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="A base de frutas retornou um erro. Tente novamente mais tarde.",
        )

    try:
        dados = resposta.json()
        nutricao = dados["nutritions"]
        return {
            "nome": dados["name"],
            "calorias": float(nutricao["calories"]),
            "acucar": float(nutricao["sugar"]),
        }
    except (ValueError, TypeError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="A resposta recebida da base de frutas está em um formato inesperado.",
        )


def calcular_nutricao(frutas: list[str]) -> tuple[float, float]:
    """Soma calorias e açúcar de 100 g de cada fruta informada."""
    total_calorias = 0.0
    total_acucar = 0.0


    for fruta in frutas:
        dados = consultar_dados_fruta(fruta)
        total_calorias += dados["calorias"]
        total_acucar += dados["acucar"]

    return round(total_calorias, 2), round(total_acucar, 2)


@app.get("/")
def inicio():
    return {"mensagem": "API da Casa de Sucos. Acesse /docs para testar os endpoints."}


@app.get("/frutas/{nome}")
def consultar_fruta(nome: str):
    """Retorna nome, calorias e açúcar de uma fruta (por 100 g)."""
    return consultar_dados_fruta(nome)


@app.post("/sucos", status_code=status.HTTP_201_CREATED)
def cadastrar_suco(suco: SucoEntrada):
    """Cadastra um suco e calcula os totais nutricionais das frutas."""
    global proximo_id

    nome = suco.nome.strip()
    gosto = suco.tem_gosto_de.strip()
    if not nome or not gosto:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O nome do suco e a descrição do gosto não podem ficar vazios.",
        )

    frutas = [fruta.strip().lower() for fruta in suco.frutas]
    if any(not fruta for fruta in frutas):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A lista contém uma fruta vazia. Informe o nome de todas as frutas.",
        )

    calorias, acucar = calcular_nutricao(frutas)
    novo_suco = {
        "id": proximo_id,
        "nome": nome,
        "frutas": frutas,
        "tem_gosto_de": gosto,
        "total_calorias": calorias,
        "total_acucar": acucar,
    }
    sucos[proximo_id] = novo_suco
    proximo_id += 1
    return novo_suco


@app.get("/sucos")
def listar_sucos():
    """Lista todos os sucos cadastrados."""
    return list(sucos.values())


@app.put("/sucos/{id}")
def atualizar_frutas_suco(id: int, atualizacao: AtualizacaoFrutas):
    """Atualiza as frutas de um suco e recalcula seus valores nutricionais."""
    if id not in sucos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Não existe suco cadastrado com o ID {id}.",
        )

    frutas = [fruta.strip().lower() for fruta in atualizacao.frutas]
    if any(not fruta for fruta in frutas):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A lista contém uma fruta vazia. Informe o nome de todas as frutas.",
        )

    calorias, acucar = calcular_nutricao(frutas)
    sucos[id]["frutas"] = frutas
    sucos[id]["total_calorias"] = calorias
    sucos[id]["total_acucar"] = acucar
    return sucos[id]
