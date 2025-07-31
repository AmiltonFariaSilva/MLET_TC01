# MLET_TC01

# 📚 BookScraper API

Projeto desenvolvido como parte do Tech Challenge para construir um pipeline completo de dados, com foco em escalabilidade, reusabilidade e integração futura com modelos de Machine Learning.

---

## 🧠 Objetivo

Criar um sistema de web scraping, armazenar os dados em formato estruturado, disponibilizar esses dados por meio de uma API RESTful e preparar o ambiente para possíveis integrações com modelos de IA.

---

## 🗂️ Estrutura do Projeto



# 🔖 Backlog do Projeto
Este projeto segue um cronograma de atividades para garantir o cumprimento dos entregáveis propostos no Tech Challenge. Abaixo estão as tarefas organizadas por status e prioridade.

## ✅ Concluídas
 Web scraping dos dados do site books.toscrape.com

 Criação da API com endpoints básicos:

/api/v1/books

/api/v1/books/{id}

/api/v1/books/search

/api/v1/categories

/api/v1/health

## 🚧 Em Progresso
   ### Organização do repositório (scripts/, api/, data/, etc.)

   ### Estruturação do README.md com:

   ### Descrição do projeto

   ### Documentação das rotas

   ### Exemplo de requests/responses

# 📋 A Fazer
## 🎯 Entregáveis obrigatórios - Telles
 Criar diagrama da arquitetura do pipeline (scraping → processamento → API → consumo)

 Deploy da API em ambiente público (Heroku, Render, etc.)

 Criar vídeo de apresentação (3 a 12 minutos)

## 🔍 Endpoints adicionais (Insights) - Zago
 /api/v1/stats/overview

 /api/v1/stats/categories

 /api/v1/books/top-rated

 /api/v1/books/price-range?min={min}&max={max}

## 🔐 Autenticação com JWT (Bônus) - Zago
 POST /api/v1/auth/login

 POST /api/v1/auth/refresh

 Proteger rotas sensíveis (/api/v1/scraping/trigger)

## 🧠 Integração com ML (Bônus)
 GET /api/v1/ml/features

 GET /api/v1/ml/training-data

 POST /api/v1/ml/predictions

## 📊 Monitoramento e Analytics (Bônus)
 Logs estruturados da API

 Métricas básicas de performance

 Dashboard com Streamlit

## 🧠 Observações
O prazo final para entrega está no plano da fase.

Adicionar comprovante de conclusão do curso GenAI (opcional, vale 10 pontos extras).

Cada membro do time pode assumir tarefas e marcar com seu nome no PR ou neste backlog.

####para execução:
   - .\venv\Scripts\activate 
   - pip install -r requirements.txt  
   - uvicorn app.main:app --reload    
