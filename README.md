# Aprenda+ - Catalogo de cursos com MongoDB

Projeto da atividade de MongoDB. O objetivo e guardar cursos, alunos e matriculas no MongoDB e executar consultas pelo terminal.

## 1. Estrutura

```text
nosql-lab/
|-- .env
|-- requirements.txt
|-- README.md
`-- mongo_cursos/
    |-- conexao.py
    |-- validacao.py
    |-- seed.py
    |-- repositorio.py
    `-- main.py
```

Os arquivos ficam separados por funcao, mas usam importacoes diretas, sem `__init__.py` ou estrutura de pacote. A conexao segue o exemplo utilizado em sala: cria um `MongoClient`, escolhe o banco e acessa as colecoes.

## 2. Instalar

Tenha Python instalado e um MongoDB local ou uma conta no MongoDB Atlas.

No terminal, dentro da pasta `nosql-lab`, crie e ative o ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate
```

No Windows:

```powershell
venv\Scripts\activate
```

Instale as bibliotecas:

```bash
pip install -r requirements.txt
```

## 3. Configurar a conexao

Crie um arquivo chamado `.env` na pasta `nosql-lab`:

```env
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=aprendamais
```

Esses valores usam um MongoDB local. Para usar o Atlas, substitua `MONGO_URI` pela string de conexao fornecida pelo Atlas.

No arquivo `mongo_cursos/conexao.py`, a conexao e feita desta forma:

```python
cliente = MongoClient(uri)
db = cliente[nome_banco]
cursos = db["cursos"]
```

A funcao `obter_banco()` retorna o banco selecionado.

## 4. Popular o banco

Execute na pasta `nosql-lab`:

```bash
python mongo_cursos/seed.py
```

O arquivo `seed.py` usa `insert_many` e cria:

- 30 cursos em 5 categorias;
- 10 alunos;
- 30 matriculas.

O script pode ser executado mais de uma vez. Antes de inserir os dados, ele remove os documentos marcados com `origem: "seed"`. Assim, nao acumula os mesmos dados a cada execucao.

## 5. Executar o programa

```bash
python mongo_cursos/main.py
```

O menu permite buscar cursos, matricular alunos, atualizar progresso, avaliar matriculas, exibir tres relatorios, adicionar modulo e remover aluno.

## 6. Modelagem do banco

O projeto utiliza tres colecoes: `cursos`, `alunos` e `matriculas`.

**Cursos:** os dados do instrutor e os modulos ficam dentro do documento do curso. Eles fazem parte das informacoes do curso e normalmente sao exibidos junto com ele. Assim, podemos consultar os dados principais e os modulos em um unico documento. O documento BSON tem limite de 16 MB; por isso, essa escolha funciona enquanto a quantidade de modulos e aulas permanecer controlada.

**Alunos:** ficam em uma colecao separada porque um aluno pode fazer varios cursos. Cada aluno tem nome, e-mail e data de cadastro. Um indice unico impede dois alunos com o mesmo e-mail.

**Matriculas:** ficam em uma colecao propria e guardam `aluno_id` e `curso_id`. Uma matricula pode ser criada, atualizada ou removida sem alterar a estrutura do curso. Tambem e possivel consultar as matriculas de um aluno ou de um curso. Um indice unico composto impede que o mesmo aluno se matricule duas vezes no mesmo curso.

O campo `vagas` guarda a quantidade de vagas ainda disponiveis. Ao matricular, o programa diminui esse numero somente quando ele e maior que zero. Ao remover um aluno, suas matriculas sao removidas e as vagas correspondentes sao devolvidas.

## 7. Pergunta: quando embutir matriculas dentro do curso seria um erro?

Seria um erro quando o curso pudesse acumular muitas matriculas, pois o documento cresceria continuamente e poderia atingir o limite de 16 MB do MongoDB. Tambem dificultaria consultar o historico de um aluno e atualizar uma matricula separadamente. Por isso, as matriculas ficam em uma colecao propria e usam referencias para aluno e curso.

## 8. Validacao

A colecao `cursos` exige os campos `titulo`, `categoria`, `preco`, `vagas` e `modulos`. O preco e as vagas nao podem ser negativos, e `modulos` deve ser um array.

No menu, escolha a opcao 8 para tentar inserir um curso com preco negativo. O MongoDB deve rejeitar esse documento.

## 9. Relatorios

O menu apresenta tres relatorios feitos com `aggregate()`:

1. Quantidade de cursos, preco medio e vagas disponiveis por categoria.
2. Quantidade de matriculas, conclusoes e progresso medio por curso.
3. Quantidade de matriculas, conclusoes, progresso medio e nota media por categoria.

## 10. Referencias

- MongoDB. PyMongo Documentation: https://www.mongodb.com/docs/languages/python/pymongo-driver/current/
- MongoDB. Schema Validation: https://www.mongodb.com/docs/manual/core/schema-validation/
- MongoDB. Limites BSON: https://www.mongodb.com/docs/manual/reference/limits/#mongodb-limit-BSON-Document-Size
- MongoDB. Embedding: https://www.mongodb.com/docs/manual/data-modeling/embedding/
- MongoDB. Referencing: https://www.mongodb.com/docs/manual/data-modeling/referencing/
- SADALAGE, Pramod J.; FOWLER, Martin. *NoSQL Essencial*. Sao Paulo: Novatec, 2013.
