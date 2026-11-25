# validacao.py
# Cria as colecoes, a validacao de cursos e os indices.

from conexao import db
from pymongo.errors import WriteError

validador_cursos = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["titulo", "categoria", "preco", "vagas", "modulos"],
        "properties": {
            "titulo": {"bsonType": "string"},
            "categoria": {"bsonType": "string"},
            "preco": {
                "bsonType": ["double", "int", "long", "decimal"],
                "minimum": 0
            },
            "vagas": {
                "bsonType": ["int", "long"],
                "minimum": 0
            },
            "modulos": {"bsonType": "array"}
        }
    }
}


def configurar_banco():
    colecoes = db.list_collection_names()

    if "cursos" not in colecoes:
        db.create_collection("cursos", validator=validador_cursos)
    else:
        db.command("collMod", "cursos", validator=validador_cursos)

    if "alunos" not in colecoes:
        db.create_collection("alunos")

    if "matriculas" not in colecoes:
        db.create_collection("matriculas")

    # Um e-mail por aluno e uma matricula por aluno em cada curso.
    db.alunos.create_index("email", unique=True)
    db.matriculas.create_index(
        [("aluno_id", 1), ("curso_id", 1)], unique=True
    )


def testar_preco_negativo():
    curso_teste = {
        "titulo": "Curso de teste invalido",
        "categoria": "Teste",
        "preco": -10.0,
        "vagas": 5,
        "modulos": []
    }

    try:
        db.cursos.insert_one(curso_teste)
        print("ERRO: o MongoDB aceitou um preco negativo.")
        db.cursos.delete_one({"titulo": "Curso de teste invalido"})
    except WriteError:
        print("Certo! O MongoDB rejeitou o curso com preco negativo.")
