# Pipeline de Dados – Ingestão - Tech Challenge Fase 1

## 1. Visão Geral do Projeto

Este projeto faz parte do desafio de Machine Learning Engineer – Fase 1, cujo objetivo é construir uma **API pública para consulta de livros**. O pipeline de dados foi desenvolvido para extrair, transformar e disponibilizar informações de livros, visando facilitar o acesso a dados estruturados para cientistas de dados e sistemas de recomendação. O foco está em **escalabilidade** e **reusabilidade** para futuras aplicações de machine learning.

---

## 2. Arquitetura da Solução

O pipeline é composto por duas grandes etapas:

- **Extração e Armazenamento (AWS Lambda + S3):** Uma função Lambda realiza o scraping de dados de livros e armazena os resultados em arquivos CSV em um bucket S3.
- **Ingestão e Processamento (Snowflake):** Scripts SQL criam o ambiente, integram o Snowflake ao S3 e automatizam a ingestão dos arquivos via Snowpipe.

**_Espaço para imagem da arquitetura geral:_**


---

## 3. Detalhamento da Extração (AWS Lambda)

O arquivo `scraper-lambda.py` implementa uma função Lambda que:

- Realiza scraping do site [books.toscrape.com](https://books.toscrape.com/) em 50 páginas.
- Coleta os seguintes dados de cada livro: título, preço, rating, disponibilidade, categoria e URL da imagem.
- Gera um arquivo CSV com os dados coletados.
- Faz upload do CSV para um bucket S3, utilizando as variáveis de ambiente:
  - `BUCKET_NAME`: nome do bucket de destino.
  - `OBJECT_KEY`: nome do arquivo (opcional, padrão: `books_<data>.csv`).


---

## 4. Recursos AWS Necessários (não inclusos nos códigos)

Além da Lambda e do bucket S3, são necessários outros recursos AWS para a integração completa com o Snowflake:

- **Role AWS:** Permite que o Snowflake acesse o bucket S3 e ative o Snowpipe.  
  _Obs.: O JSON da role não está incluso neste repositório. Consulte a documentação oficial da AWS e do Snowflake para criar a role com as permissões adequadas._
- **SQS:** Fila para notificação de novos arquivos e ativação do Snowpipe.  
  _Obs.: O recurso SQS não está incluso neste repositório. É necessário criar manualmente._
- **EventBridge:** Responsável por agendar a execução diária da Lambda.  
  _Obs.: O recurso EventBridge não está incluso neste repositório. É necessário criar manualmente._


---

## 5. Detalhamento da Ingestão e Processamento (Snowflake)

### Scripts SQL

- **`environment_ddl.sql`:**
  - Cria o banco de dados, schema e tabela principal (`TB_BOOKS_TO_SCRAPE`).
  - Cria usuários, roles e concede permissões de acesso.
- **`ingestion_ddl.sql`:**
  - Cria integração de armazenamento com o S3 (`STORAGE INTEGRATION`).
  - Cria um stage externo apontando para o bucket S3.
  - Define o formato de arquivo CSV.
  - Cria um pipe (`PIPE_BOOKS_TO_SCRAPE_AUTO`) com ingestão automática (Snowpipe) para carregar os dados do S3 para a tabela.
  - Concede permissões para a role do projeto.

### Fluxo de Ingestão

1. Arquivo CSV é gerado pela Lambda e enviado ao S3.
2. O Snowpipe detecta automaticamente novos arquivos no stage S3.
3. Os dados são carregados para a tabela `TB_BOOKS_TO_SCRAPE` no Snowflake.


## 6. Orientações de Uso e Próximos Passos

- Execute a função Lambda para gerar e enviar o arquivo CSV ao S3.
- Execute os scripts SQL no Snowflake para criar o ambiente e configurar a ingestão automática.
- Certifique-se de que a role AWS, SQS e EventBridge estejam devidamente configurados para integração completa.
- Verifique o carregamento dos dados na tabela `TB_BOOKS_TO_SCRAPE` no Snowflake.
- Para evoluir o pipeline, considere:
  - Adicionar monitoramento e alertas.
  - Implementar versionamento dos dados.
  - Expandir o pipeline para outros domínios de dados.

---

