# Casa de Sucos — API com FastAPI

API desenvolvida em Python para consultar informações nutricionais de frutas na [Fruityvice](https://www.fruityvice.com/) e cadastrar sucos com o cálculo de calorias e açúcar.

Os cálculos consideram **100 g de cada fruta informada**. A aplicação utiliza armazenamento em memória, sem banco de dados; por isso, os sucos cadastrados são perdidos quando o servidor é reiniciado.

## Tecnologias

- Python
- FastAPI
- Requests
- Uvicorn
- Fruityvice API

## Como executar

### 1. Criar e ativar o ambiente virtual

No Windows (PowerShell), dentro da pasta `aula_14`:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear a ativação, execute nesta mesma janela:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

### 2. Instalar as dependências

```powershell
py -m pip install -r requirements.txt
```

### 3. Iniciar a API

```powershell
py -m uvicorn main:app --reload
```

A API ficará disponível em `http://127.0.0.1:8000`.

## Documentação e testes no Swagger

Com o servidor ligado, abra:

- Swagger: http://127.0.0.1:8000/docs
- Redoc: http://127.0.0.1:8000/redoc

No Swagger, expanda cada endpoint, clique em **Try it out** e depois em **Execute**.

## Endpoints

| Método | Rota | Função |
|---|---|---|
| GET | `/frutas/{nome}` | Consulta nome, calorias e açúcar de uma fruta. |
| POST | `/sucos` | Cadastra um suco e calcula seus valores nutricionais. |
| GET | `/sucos` | Lista os sucos cadastrados. |
| PUT | `/sucos/{id}` | Atualiza as frutas de um suco e recalcula os totais. |

### 1. Consultar uma fruta

Exemplo: `GET /frutas/banana`

Resposta ilustrativa (os valores reais vêm da Fruityvice):

```json
{
  "nome": "Banana",
  "calorias": 96.0,
  "acucar": 17.2
}
```

### 2. Cadastrar um suco

Exemplo: `POST /sucos`

Corpo da requisição:

```json
{
  "nome": "Vitamina Tropical",
  "frutas": ["banana", "strawberry"],
  "tem_gosto_de": "Tamarindo"
}
```

A API consulta cada fruta na Fruityvice, soma as calorias e o açúcar de 100 g de cada uma e retorna o registro com um ID.

### 3. Listar os sucos

Exemplo: `GET /sucos`

Retorna uma lista com todos os sucos cadastrados e seus valores nutricionais. Se ainda não houver cadastro, retorna uma lista vazia.

### 4. Atualizar as frutas de um suco (bônus)

Exemplo: `PUT /sucos/1`

Corpo da requisição:

```json
{
  "frutas": ["apple", "mango"]
}
```

O nome e a descrição do gosto são mantidos. As frutas, calorias e açúcar são atualizados.

## Tratamento de erros

- **404:** fruta não encontrada na Fruityvice ou ID de suco inexistente.
- **422:** dados enviados inválidos ou incompletos.
- **502:** falha de comunicação ou resposta inesperada da Fruityvice.
- **504:** tempo limite excedido durante a consulta externa.

A Fruityvice espera os nomes das frutas em inglês, por exemplo: `banana`, `apple`, `mango` e `strawberry`.

## Exemplos no Swagger

O arquivo `EXEMPLOS_SWAGGER.md` contém corpos de requisição e orientações para testar os endpoints em `/docs`. Os valores nutricionais de exemplo são ilustrativos; a aplicação consulta os valores reais na Fruityvice.

## Testes automatizados

Os testes automatizados usam respostas simuladas da Fruityvice, portanto não dependem de conexão com a API externa. Foram executados 5 testes automatizados, todos aprovados:

```powershell
py -m unittest -v
```

