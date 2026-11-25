

## Instalar

Professor, tendo em base que você já tem o python,
basta iniciar a venv e baixar os requirements

```bash
python -m venv venv
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```

## Popular o banco

Execute na pasta `nosql-lab`:

```bash
python mongo_cursos/seed.py
```

O arquivo `seed.py` usa `insert_many` e cria:

- 30 cursos em 5 categorias;
- 10 alunos;
- 30 matriculas.

## Executar de verdade esse trem:

```bash
python mongo_cursos/main.py
```

## Quando embutir matriculas dentro do curso seria um erro?

Seria um erro quando o curso pudesse acumular muitas matriculas, pq o documento cresceria continuamente e poderia atingir o limite de 16 MB do MongoDB. Tambem dificultaria consultar o historico de um aluno e atualizar uma matricula separadamente. Por isso, as matriculas ficam em uma colecao propria e usam referencias para aluno e curso.
