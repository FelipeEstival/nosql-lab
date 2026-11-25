from conexao import cliente
from validacao import configurar_banco, testar_preco_negativo
from repositorio import (
    buscar_cursos,
    matricular_aluno,
    adicionar_modulo,
    atualizar_progresso,
    avaliar_matricula,
    remover_aluno,
    listar_alunos,
    listar_matriculas,
    relatorio_cursos_categoria,
    relatorio_matriculas_curso,
    relatorio_desempenho_categoria
)


def mostrar_cursos(cursos):
    for curso in cursos:
        print(
            curso["_id"], "|", curso["titulo"], "|",
            curso["categoria"], "| R$", curso["preco"],
            "| vagas:", curso["vagas"]
        )


def mostrar_alunos():
    for aluno in listar_alunos():
        print(aluno["_id"], "|", aluno["nome"], "|", aluno["email"])


def mostrar_matriculas():
    for matricula in listar_matriculas():
        print(
            matricula["_id"], "|", matricula["aluno"], "|",
            matricula["curso"], "|", matricula["progresso"], "% |",
            "Concluida" if matricula["concluida"] else "Em andamento",
            "| Nota:", matricula["nota"]
        )


def mostrar_relatorio(titulo, dados):
    print("\n" + titulo)
    for linha in dados:
        print(linha)


def menu():
    configurar_banco()

    while True:
        print("1 - Buscar cursos")
        print("2 - Matricular aluno")
        print("3 - Atualizar progresso")
        print("4 - Avaliar matricula")
        print("5 - Exibir os tres relatorios")
        print("6 - Adicionar modulo a um curso")
        print("7 - Remover aluno")
        print("8 - Testar validacao de preco negativo")
        print("0 - Sair")

        opcao = input("Escolha: ")

        try:
            if opcao == "1":
                categoria = input("Categoria (Enter para ignorar): ") or None
                preco = input("Preco maximo (Enter para ignorar): ")
                tag = input("Tag (Enter para ignorar): ") or None
                preco = float(preco) if preco else None
                mostrar_cursos(buscar_cursos(categoria, preco, tag))

            elif opcao == "2":
                print("\nAlunos:")
                mostrar_alunos()
                aluno_id = input("ID do aluno: ")
                print("\nCursos:")
                mostrar_cursos(buscar_cursos())
                curso_id = input("ID do curso: ")
                id_matricula = matricular_aluno(aluno_id, curso_id)
                print("Matricula criada:", id_matricula)

            elif opcao == "3":
                mostrar_matriculas()
                matricula_id = input("ID da matricula: ")
                progresso = float(input("Novo progresso (0 a 100): "))
                atualizar_progresso(matricula_id, progresso)
                print("Progresso atualizado.")

            elif opcao == "4":
                mostrar_matriculas()
                matricula_id = input("ID da matricula: ")
                nota = int(input("Nota de 1 a 5: "))
                avaliar_matricula(matricula_id, nota)
                print("Avaliacao registrada.")

            elif opcao == "5":
                mostrar_relatorio("Cursos por categoria:", relatorio_cursos_categoria())
                mostrar_relatorio("Matriculas por curso:", relatorio_matriculas_curso())
                mostrar_relatorio("Desempenho por categoria:", relatorio_desempenho_categoria())

            elif opcao == "6":
                mostrar_cursos(buscar_cursos())
                curso_id = input("ID do curso: ")
                titulo = input("Titulo do modulo: ")
                texto_aulas = input("Aulas separadas por virgula: ")
                aulas = [aula.strip() for aula in texto_aulas.split(",")]
                adicionar_modulo(curso_id, {"titulo": titulo, "aulas": aulas})
                print("Modulo adicionado.")

            elif opcao == "7":
                mostrar_alunos()
                aluno_id = input("ID do aluno que deseja remover: ")
                quantidade = remover_aluno(aluno_id)
                print("Aluno removido. Matriculas removidas:", quantidade)

            elif opcao == "8":
                testar_preco_negativo()

            elif opcao == "0":
                print("Encerrando o programa.")
                break

            else:
                print("Opcao invalida.")

        except Exception as erro:
            print("Erro:", erro)


if __name__ == "__main__":
    try:
        menu()
    finally:
        cliente.close()
