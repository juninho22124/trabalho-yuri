import sqlite3
import tkinter as tk
from tkinter import messagebox

def inicializar_db():
    banco = sqlite3.connect("academico.db")
    cur = banco.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS estudantes (id INTEGER PRIMARY KEY, nome TEXT NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS materias (codigo TEXT PRIMARY KEY, nome TEXT NOT NULL)")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS avaliacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estudante_id INTEGER,
            materia_codigo TEXT,
            nota REAL,
            FOREIGN KEY(estudante_id) REFERENCES estudantes(id),
            FOREIGN KEY(materia_codigo) REFERENCES materias(codigo)
        )
    """)
    banco.commit()
    banco.close()

def inserir_estudante(codigo, nome):
    try:
        with sqlite3.connect("academico.db") as banco:
            banco.execute("INSERT INTO estudantes (id, nome) VALUES (?, ?)", (codigo, nome))
        return True
    except sqlite3.IntegrityError:
        return False

def inserir_materia(codigo, nome):
    try:
        with sqlite3.connect("academico.db") as banco:
            banco.execute("INSERT INTO materias (codigo, nome) VALUES (?, ?)", (codigo, nome))
        return True
    except sqlite3.IntegrityError:
        return False

def registrar_nota(cod_aluno, cod_materia, valor):
    with sqlite3.connect("academico.db") as banco:
        cur = banco.cursor()
        cur.execute("SELECT 1 FROM estudantes WHERE id = ?", (cod_aluno,))
        if not cur.fetchone():
            return "Estudante não existe"
        cur.execute("SELECT 1 FROM materias WHERE codigo = ?", (cod_materia,))
        if not cur.fetchone():
            return "Matéria não existe"
        cur.execute("INSERT INTO avaliacao (estudante_id, materia_codigo, nota) VALUES (?, ?, ?)",
                    (cod_aluno, cod_materia, valor))
        banco.commit()
        return "Nota registrada"

def obter_notas(estudante_id):
    with sqlite3.connect("academico.db") as banco:
        cur = banco.cursor()
        cur.execute("""
            SELECT materias.nome, avaliacao.nota
            FROM avaliacao
            JOIN materias ON materias.codigo = avaliacao.materia_codigo
            WHERE estudante_id = ?
        """, (estudante_id,))
        return cur.fetchall()

class SistemaAcademico:
    def __init__(self, janela):
        self.janela = janela
        janela.title("Estacio")
        janela.geometry("420x520")

        self.ui = tk.Frame(janela, bg="#ececec", padx=15, pady=15)
        self.ui.pack(fill="both", expand=True)

        self.campos()

    def campos(self):
        linha = 0
        self.add_titulo("Cadastrar Estudante", linha)
        linha += 1
        self.id_entrada = self.add_campo("ID:", linha)
        linha += 1
        self.nome_entrada = self.add_campo("Nome:", linha)
        linha += 1
        self.add_botao("Salvar Estudante", self.salvar_estudante, linha)
        linha += 2

        self.add_titulo("Cadastrar Matéria", linha)
        linha += 1
        self.codigo_materia = self.add_campo("Código:", linha)
        linha += 1
        self.nome_materia = self.add_campo("Nome:", linha)
        linha += 1
        self.add_botao("Salvar Matéria", self.salvar_materia, linha)
        linha += 2

        self.add_titulo("Inserir Nota", linha)
        linha += 1
        self.id_nota = self.add_campo("ID Aluno:", linha)
        linha += 1
        self.cod_nota = self.add_campo("Código Matéria:", linha)
        linha += 1
        self.valor_nota = self.add_campo("Nota:", linha)
        linha += 1
        self.add_botao("Registrar Nota", self.salvar_nota, linha)
        linha += 2

        self.add_titulo("Ver Notas", linha)
        linha += 1
        self.id_busca = self.add_campo("ID do Aluno:", linha)
        linha += 1
        self.add_botao("Exibir Notas", self.ver_notas, linha)

    def add_titulo(self, texto, linha):
        tk.Label(self.ui, text=texto, font=("Arial", 12, "bold"), bg="#ececec").grid(row=linha, column=0, columnspan=2, pady=(10, 5))

    def add_campo(self, texto, linha):
        tk.Label(self.ui, text=texto, bg="#ececec").grid(row=linha, column=0, sticky="e")
        campo = tk.Entry(self.ui)
        campo.grid(row=linha, column=1)
        return campo

    def add_botao(self, texto, funcao, linha):
        tk.Button(self.ui, text=texto, command=funcao, bg="#4CAF50", fg="white").grid(row=linha, column=0, columnspan=2, pady=5)

    def salvar_estudante(self):
        try:
            id_aluno = int(self.id_entrada.get())
            nome = self.nome_entrada.get().strip()
            if not nome:
                raise ValueError
            if inserir_estudante(id_aluno, nome):
                messagebox.showinfo("OK", "Estudante salvo")
            else:
                messagebox.showerror("Erro", "ID já existe")
        except ValueError:
            messagebox.showerror("Erro", "Dados inválidos")

    def salvar_materia(self):
        codigo = self.codigo_materia.get().strip()
        nome = self.nome_materia.get().strip()
        if codigo and nome:
            if inserir_materia(codigo, nome):
                messagebox.showinfo("OK", "Matéria salva")
            else:
                messagebox.showerror("Erro", "Código já existe")
        else:
            messagebox.showerror("Erro", "Preencha tudo")

    def salvar_nota(self):
        try:
            aluno = int(self.id_nota.get())
            codigo = self.cod_nota.get().strip()
            nota = float(self.valor_nota.get())
            if nota < 0 or nota > 10:
                raise ValueError
            resultado = registrar_nota(aluno, codigo, nota)
            if resultado == "Nota registrada":
                messagebox.showinfo("OK", resultado)
            else:
                messagebox.showerror("Erro", resultado)
        except ValueError:
            messagebox.showerror("Erro", "Dados inválidos")

    def ver_notas(self):
        try:
            aluno = int(self.id_busca.get())
            dados = obter_notas(aluno)
            if dados:
                texto = "\n".join(f"{disc}: {nota}" for disc, nota in dados)
                messagebox.showinfo("Notas", texto)
            else:
                messagebox.showinfo("Notas", "Nenhuma nota encontrada")
        except ValueError:
            messagebox.showerror("Erro", "ID inválido")

if __name__ == "__main__":
    inicializar_db()
    tela = tk.Tk()
    app = SistemaAcademico(tela)
    tela.mainloop()
