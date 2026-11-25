from pymongo import MongoClient

cliente = MongoClient("localhost", 27017)

db = cliente["aprendamais"]

cursos = db["cursos"]
alunos = db["alunos"]
matriculas = db["matriculas"]

def obter_banco():
    return db