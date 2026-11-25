# repositorio.py
# Funcoes para consultar e alterar os dados do MongoDB.

from datetime import datetime

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from conexao import db


def buscar_cursos(categoria=None, preco_max=None, tag=None):
    filtros = {}

    if categoria:
        filtros["categoria"] = categoria
    if preco_max is not None:
        filtros["preco"] = {"$lte": float(preco_max)}
    if tag:
        filtros["tags"] = tag.lower()

    # O segundo parametro esconde os modulos no resultado.
    return list(db.cursos.find(filtros, {"modulos": 0}))


def matricular_aluno(aluno_id, curso_id):
    aluno_id = ObjectId(aluno_id)
    curso_id = ObjectId(curso_id)

    if db.alunos.find_one({"_id": aluno_id}) is None:
        raise ValueError("Aluno nao encontrado.")

    if db.matriculas.find_one({"aluno_id": aluno_id, "curso_id": curso_id}):
        raise ValueError("Este aluno ja esta matriculado neste curso.")

    # O curso so e atualizado quando ainda existe pelo menos uma vaga.
    curso = db.cursos.find_one_and_update(
        {"_id": curso_id, "vagas": {"$gt": 0}},
        {"$inc": {"vagas": -1}},
        return_document=ReturnDocument.AFTER
    )

    if curso is None:
        raise ValueError("Curso nao encontrado ou sem vagas.")

    nova_matricula = {
        "aluno_id": aluno_id,
        "curso_id": curso_id,
        "data_matricula": datetime.now(),
        "progresso": 0,
        "concluida": False
    }

    try:
        resultado = db.matriculas.insert_one(nova_matricula)
        return resultado.inserted_id
    except DuplicateKeyError:
        # Devolve a vaga caso o indice identifique uma matricula duplicada.
        db.cursos.update_one({"_id": curso_id}, {"$inc": {"vagas": 1}})
        raise ValueError("Este aluno ja esta matriculado neste curso.")


def adicionar_modulo(curso_id, modulo):
    curso_id = ObjectId(curso_id)
    curso = db.cursos.find_one({"_id": curso_id})

    if curso is None:
        raise ValueError("Curso nao encontrado.")

    modulo["ordem"] = len(curso.get("modulos", [])) + 1
    db.cursos.update_one(
        {"_id": curso_id},
        {"$push": {"modulos": modulo}}
    )


def atualizar_progresso(matricula_id, progresso):
    progresso = float(progresso)
    if progresso < 0 or progresso > 100:
        raise ValueError("O progresso deve estar entre 0 e 100.")

    matricula_id = ObjectId(matricula_id)
    dados = {
        "progresso": progresso,
        "concluida": progresso == 100
    }

    if progresso < 100:
        db.matriculas.update_one(
            {"_id": matricula_id},
            {"$set": dados, "$unset": {"nota_avaliacao": ""}}
        )
    else:
        db.matriculas.update_one({"_id": matricula_id}, {"$set": dados})

    if db.matriculas.find_one({"_id": matricula_id}) is None:
        raise ValueError("Matricula nao encontrada.")


def avaliar_matricula(matricula_id, nota):
    nota = int(nota)
    if nota < 1 or nota > 5:
        raise ValueError("A nota deve ser de 1 a 5.")

    matricula_id = ObjectId(matricula_id)
    matricula = db.matriculas.find_one({"_id": matricula_id})

    if matricula is None:
        raise ValueError("Matricula nao encontrada.")
    if not matricula.get("concluida"):
        raise ValueError("So e possivel avaliar uma matricula concluida.")

    db.matriculas.update_one(
        {"_id": matricula_id},
        {"$set": {"nota_avaliacao": nota}}
    )


def remover_aluno(aluno_id):
    aluno_id = ObjectId(aluno_id)
    matriculas_do_aluno = list(db.matriculas.find({"aluno_id": aluno_id}))

    # Devolve as vagas dos cursos antes de apagar as matriculas.
    for matricula in matriculas_do_aluno:
        db.cursos.update_one(
            {"_id": matricula["curso_id"]},
            {"$inc": {"vagas": 1}}
        )

    db.matriculas.delete_many({"aluno_id": aluno_id})
    resultado = db.alunos.delete_one({"_id": aluno_id})

    if resultado.deleted_count == 0:
        raise ValueError("Aluno nao encontrado.")

    return len(matriculas_do_aluno)


def listar_alunos():
    return list(db.alunos.find().sort("nome", 1))


def listar_matriculas():
    consulta = [
        {"$lookup": {
            "from": "alunos", "localField": "aluno_id",
            "foreignField": "_id", "as": "aluno"
        }},
        {"$lookup": {
            "from": "cursos", "localField": "curso_id",
            "foreignField": "_id", "as": "curso"
        }},
        {"$unwind": "$aluno"},
        {"$unwind": "$curso"},
        {"$sort": {"aluno.nome": 1}}
    ]

    resultado = []
    for item in db.matriculas.aggregate(consulta):
        resultado.append({
            "_id": item["_id"],
            "aluno": item["aluno"]["nome"],
            "curso": item["curso"]["titulo"],
            "progresso": item["progresso"],
            "concluida": item["concluida"],
            "nota": item.get("nota_avaliacao", "Sem nota")
        })
    return resultado


def relatorio_cursos_categoria():
    consulta = [
        {"$group": {
            "_id": "$categoria",
            "quantidade": {"$sum": 1},
            "preco_medio": {"$avg": "$preco"},
            "vagas_disponiveis": {"$sum": "$vagas"}
        }},
        {"$sort": {"_id": 1}}
    ]
    return list(db.cursos.aggregate(consulta))


def relatorio_matriculas_curso():
    consulta = [
        {"$lookup": {
            "from": "cursos", "localField": "curso_id",
            "foreignField": "_id", "as": "curso"
        }},
        {"$unwind": "$curso"},
        {"$group": {
            "_id": "$curso.titulo",
            "matriculas": {"$sum": 1},
            "concluidas": {"$sum": {"$cond": ["$concluida", 1, 0]}},
            "progresso_medio": {"$avg": "$progresso"}
        }},
        {"$sort": {"matriculas": -1}}
    ]
    return list(db.matriculas.aggregate(consulta))


def relatorio_desempenho_categoria():
    consulta = [
        {"$lookup": {
            "from": "cursos", "localField": "curso_id",
            "foreignField": "_id", "as": "curso"
        }},
        {"$unwind": "$curso"},
        {"$group": {
            "_id": "$curso.categoria",
            "matriculas": {"$sum": 1},
            "concluidas": {"$sum": {"$cond": ["$concluida", 1, 0]}},
            "progresso_medio": {"$avg": "$progresso"},
            "nota_media": {"$avg": "$nota_avaliacao"}
        }},
        {"$sort": {"_id": 1}}
    ]
    return list(db.matriculas.aggregate(consulta))
