# seed.py
# Insere os dados iniciais: 30 cursos, 10 alunos e 30 matriculas.

from datetime import datetime
from random import choice, randint, sample, seed

from conexao import db, cliente
from validacao import configurar_banco

seed(10)

categorias = ["Programacao", "Dados", "Design", "Negocios", "Marketing"]

nomes_cursos = [
    "Python do Zero", "Logica de Programacao", "Java para Iniciantes",
    "Desenvolvimento Web", "Introducao ao C#", "Git e GitHub",
    "Excel para Analise", "SQL do Basico ao Avancado", "Power BI",
    "Introducao ao MongoDB", "Analise de Dados com Python", "Estatistica",
    "Design de Interfaces", "UI Design", "UX para Iniciantes",
    "Figma na Pratica", "Identidade Visual", "Design Grafico",
    "Gestao de Projetos", "Empreendedorismo", "Lideranca", "Financas Pessoais",
    "Organizacao e Produtividade", "Gestao de Pessoas", "Marketing Digital",
    "Redes Sociais", "Criacao de Conteudo", "SEO na Pratica",
    "Estrategia de Marca", "Publicidade Online"
]

instrutores = [
    {"nome": "Ana Lima", "email": "ana@aprendamais.com"},
    {"nome": "Carlos Souza", "email": "carlos@aprendamais.com"},
    {"nome": "Mariana Alves", "email": "mariana@aprendamais.com"},
    {"nome": "Joao Costa", "email": "joao@aprendamais.com"},
    {"nome": "Paula Santos", "email": "paula@aprendamais.com"}
]

nomes_alunos = [
    "Lucas Martins", "Beatriz Oliveira", "Pedro Souza", "Julia Costa",
    "Mariana Santos", "Rafael Lima", "Isabela Ferreira", "Gabriel Alves",
    "Laura Rodrigues", "Matheus Gomes"
]


def popular_banco():
    configurar_banco()

    # Apaga somente os dados criados por este arquivo, para nao duplicar.
    db.matriculas.delete_many({"origem": "seed"})
    db.cursos.delete_many({"origem": "seed"})
    db.alunos.delete_many({"origem": "seed"})

    # Cria os 30 cursos, sendo 6 em cada categoria.
    lista_cursos = []
    for i, titulo in enumerate(nomes_cursos):
        categoria = categorias[i // 6]
        lista_cursos.append({
            "titulo": titulo,
            "categoria": categoria,
            "carga_horaria": choice([10, 20, 30, 40, 60]),
            "preco": round(randint(80, 400) + 0.90, 2),
            "vagas": 20,
            "tags": [categoria.lower(), "iniciante", "online"],
            "instrutor": choice(instrutores),
            "modulos": [
                {"ordem": 1, "titulo": "Introducao", "aulas": ["Apresentacao", "Conceitos basicos"]},
                {"ordem": 2, "titulo": "Pratica", "aulas": ["Exemplos", "Exercicio final"]}
            ],
            "origem": "seed"
        })

    resultado_cursos = db.cursos.insert_many(lista_cursos)
    ids_cursos = resultado_cursos.inserted_ids

    # Cria os 10 alunos.
    lista_alunos = []
    for nome in nomes_alunos:
        email = nome.lower().replace(" ", ".") + "@email.com"
        lista_alunos.append({
            "nome": nome,
            "email": email,
            "data_cadastro": datetime.now(),
            "origem": "seed"
        })

    resultado_alunos = db.alunos.insert_many(lista_alunos)
    ids_alunos = resultado_alunos.inserted_ids

    # Cada aluno recebe tres cursos diferentes: total de 30 matriculas.
    lista_matriculas = []
    for id_aluno in ids_alunos:
        cursos_escolhidos = sample(ids_cursos, 3)
        for id_curso in cursos_escolhidos:
            progresso = choice([0, 25, 50, 75, 100])
            matricula = {
                "aluno_id": id_aluno,
                "curso_id": id_curso,
                "data_matricula": datetime.now(),
                "progresso": progresso,
                "concluida": progresso == 100,
                "origem": "seed"
            }
            if progresso == 100:
                matricula["nota_avaliacao"] = randint(3, 5)
            lista_matriculas.append(matricula)
            db.cursos.update_one({"_id": id_curso}, {"$inc": {"vagas": -1}})

    db.matriculas.insert_many(lista_matriculas)

    print("Carga inicial realizada com sucesso!")
    print("30 cursos, 10 alunos e 30 matriculas inseridos.")


if __name__ == "__main__":
    try:
        popular_banco()
    finally:
        cliente.close()
