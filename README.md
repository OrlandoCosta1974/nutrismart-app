<div align="center">

# 🥗 NutriSmart App

Planejamento alimentar e acompanhamento de hábitos nutricionais, com foco em simplicidade, organização e evolução contínua.

<a href="#pt-br"><b>🇧🇷 Português</b></a> • <a href="#en-us"><b>🇺🇸 English</b></a>

<br/>

<img src="https://img.shields.io/badge/Status-Em%20Desenvolvimento-orange?style=for-the-badge" />
<img src="https://img.shields.io/badge/Projeto-Pessoal-blue?style=for-the-badge" />
<br/>
<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" />
<img src="https://img.shields.io/badge/SQL-003B57?style=for-the-badge&logo=postgresql&logoColor=white" />
<img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" />
<br/>
<img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" />
<img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" />
<img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=000" />

<br/><br/>

<a href="https://github.com/OrlandoCosta1974/nutrismart-app">
  <img src="https://img.shields.io/badge/GitHub-Reposit%C3%B3rio-181717?style=for-the-badge&logo=github&logoColor=white" />
</a>

</div>

---

## 🇧🇷 Visão Geral

O **NutriSmart App** é um projeto em desenvolvimento para ajudar no **planejamento alimentar** e no **acompanhamento de hábitos nutricionais**, com uma experiência simples e organizada.

**Objetivo (1 frase):** Aplicativo em desenvolvimento para ajudar no planejamento alimentar e no acompanhamento de hábitos nutricionais de forma simples e organizada.

---

## ✅ Funcionalidades (atual e planejado)

### Atual
- [ ] Cadastro de refeições
- [ ] Registro de hábitos diários
- [ ] Histórico por data

### Planejado
- [ ] Metas e lembretes
- [ ] Painel com gráficos (evolução semanal)
- [ ] Exportação (CSV/PDF)
- [ ] Autenticação e perfil de usuário

---

## 🧰 Tecnologias

> Ajuste conforme o projeto evoluir.

- Back-end: Python (Flask)
- Banco de dados: SQLite/MySQL
- Front-end: HTML/CSS/JS
- Dados/relatórios: Pandas (opcional)

---

## 🗂️ Estrutura do projeto (sugestão)

```text
nutrismart-app/
├─ app/
│  ├─ __init__.py
│  ├─ routes.py
│  ├─ models.py
│  ├─ services/
│  └─ templates/
├─ static/
├─ tests/
├─ requirements.txt
├─ .env.example
└─ README.md

git clone https://github.com/OrlandoCosta1974/nutrismart-app.git
cd nutrismart-app

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt

FLASK_ENV=development
SECRET_KEY=troque-esta-chave
DATABASE_URL=sqlite:///nutrismart.db

flask run
Acesse: http://127.0.0.1:5000

📫 Contato



Orlando Costa — orlando.trafegopago@gmail.com


pytest -q
