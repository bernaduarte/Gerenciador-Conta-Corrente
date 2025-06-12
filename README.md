# Gerenciador de Conta Corrente 

### Tecnologias utilizadas

- 🐍 Python
- ⚡ FastAPI (Framework Web)
- 🧪 Pytest (Testes unitários)
- 🐘 SQLAlchemy (ORM)

### 📋 Prerequisites

- 🐍 Python  3.8+
- 🐬 PIP  (Gerenciador de pacotes)
- (Opcional, mas recomendado) Ambiente virtual: `venv`

### 👥 Tipos de Contas Disponíveis

O sistema possui dois tipos de contas disponíveis para testes:

| Tipo de Conta | Nome do Usuário   | Número da Conta | Senha | Nível de Acesso |
|---------------|-------------------|------------------|-------|-----------------|
| 🧍 Conta Normal | Bernardo Normal    | `12345`          | `1111`| Normal          |
| 👑 Conta VIP    | Amanda VIP         | `54321`          | `2222`| VIP             |

- As contas normal possue saldo inicial de **R$ 1000,00**.
- As contas vip possue saldo inicial de **R$ 5000,00**.

---

### 🪟 Windows

1. 🔧 Criar ambiente virtual:  

`` python -m venv env_name ``

2. ▶️ Ativar ambiente:

`` env_name/Scripts/activate ``

3. 📦 Instalar dependências: 

`` pip install -r requirements.txt ``

4. 📄 Criar o `.env` dentro  da pasta do **projeto**.

5. ✍️ Adicionar a variavel no `.env` como exemplificado no `.env_example`:

`` SECRET_KEY='nome da chave' ``  

6. 🚀 Rodar o servidor:
  
`` uvicorn main:app --reload  ``
ou
`` uvicorn app.main:app --reload ``

---

### 💻 Linux

1. 🔧 Criar ambiente virtual:  

`` python3 -m venv env_name ``

2. ▶️ Ativar ambiente:

`` source env_name/Scripts/activate ``

3. 📦 Instalar dependências: 

`` pip install -r requirements.txt ``

4. 📄 Criar o `.env` dentro  da pasta do **projeto**.

5. ✍️ Adicionar a variavel no `.env` como exemplificado no `.env_example`:

`` SECRET_KEY='nome da chave' ``  

6. 🚀 Rodar o servidor:
  
`` uvicorn main:app --reload  ``
ou
`` uvicorn app.main:app --reload ``

---

### 🧪 Rodando os testes unitários

`` pytest .\tests\ ``