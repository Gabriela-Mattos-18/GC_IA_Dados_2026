# Exemplos para testar no Swagger

Inicie a API e acesse `http://127.0.0.1:8000/docs`.

Os valores nutricionais retornados pela API são obtidos da Fruityvice. Os exemplos de valores abaixo são apenas ilustrativos; a resposta real pode variar conforme os dados fornecidos pela API externa.

## 1. Consultar uma fruta — GET `/frutas/{nome}`

Use `banana` como parâmetro de caminho.

Exemplo de resposta:

```json
{
  "nome": "Banana",
  "calorias": 96.0,
  "acucar": 17.2
}
```

## 2. Cadastrar um suco — POST `/sucos`

Corpo para testar:

```json
{
  "nome": "Vitamina Tropical",
  "frutas": ["banana", "strawberry"],
  "tem_gosto_de": "Tamarindo"
}
```

A resposta deverá conter `id`, `nome`, `frutas`, `tem_gosto_de`, `total_calorias` e `total_acucar`. Os totais são calculados considerando 100 g de cada fruta.

## 3. Listar sucos — GET `/sucos`

Execute depois de cadastrar um suco. A resposta será uma lista com os sucos cadastrados. Antes de qualquer cadastro, a resposta será `[]`.

## 4. Atualizar frutas — PUT `/sucos/{id}` (bônus)

Se o suco cadastrado recebeu o ID `1`, use `1` como parâmetro de caminho.

Corpo para testar:

```json
{
  "frutas": ["apple", "mango"]
}
```

A API consultará as novas frutas e recalculará os totais nutricionais.

## 5. Testar fruta não encontrada — GET `/frutas/{nome}`

Use um nome que não exista na Fruityvice, por exemplo `fruta-inexistente`.

A resposta esperada é HTTP `404`, com uma mensagem amigável.
