# Instruções para Utilização de JWT na API

## Configuração de JWT

O JWT (JSON Web Token) já está configurado no arquivo `routers/auth.py` com as seguintes características:

- **Access Token**: Expira em 20 minutos
- **Refresh Token**: Expira em 7 dias
- **Algoritmo**: HS256


## Passo a Passo para Usar a API com JWT (via Swagger UI /docs)

### 1. Criar um Novo Usuário

1. Acesse `/docs`
2. Procure o endpoint `POST /auth/`
3. Clique em "Try it out"
4. Insira os dados do usuário no formato:
```json
{
  "username": "seu_usuario",
  "email": "seu@email.com",
  "first_name": "Seu",
  "last_name": "Nome",
  "password": "sua_senha",
  "role": "user"
}


{
  "username": "lzago",
  "email": "lzago@mail.com",
  "first_name": "Lucas",
  "last_name": "Zago",
  "password": "gft",
  "role": "admin"
}
```
5. Execute a requisição

### 2. Fazer Login e Obter Tokens

1. No Swagger UI, localize `POST /auth/login`
2. Clique em "Try it out"
3. Preencha:
   - Username: seu_usuario
   - Password: sua_senha
4. Execute
5. Você receberá:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJsemFnbyIsImlkIjoxLCJleHAiOjE3NTIyODY0Mzd9.gDg3uk4b0_eMtPu4VrbfpsYeYRM8TAQxIwI7f2HrJ10",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJsemFnbyIsImlkIjoxLCJleHAiOjE3NTI4OTAwMzd9.RY0GpaChzbsNW8LL0hPeEamjGxV9QD6VdixMOOBLUGI",
  "token_type": "bearer"
}
```

### 3. Autenticação via cURL (Recomendado)

Como o Swagger UI pode apresentar problemas de autenticação, o método mais confiável é usar cURL para acessar os endpoints protegidos:

```bash
# Substitua pelo seu token obtido no login
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJsemFnbyIsImlkIjoxLCJleHAiOjE3NTIyODY0Mzd9.gDg3uk4b0_eMtPu4VrbfpsYeYRM8TAQxIwI7f2HrJ10"

# Teste de autenticação
curl -X GET "http://localhost:8000/api/v1/test-auth" \
     -H "Authorization: Bearer $TOKEN"
```

Se a autenticação for bem-sucedida, você verá uma resposta como:
```json
{
  "message": "Autenticação bem-sucedida!",
  "user": {
    "username": "lzago",
    "id": 1
  }
}
```

### 4. Autenticação via Swagger UI

Para autenticar no Swagger UI:

1. Obtenha seu token usando o endpoint `/auth/login` (você pode usar esse próprio endpoint na UI do Swagger)
2. Copie o valor do `access_token` (sem as aspas)
3. Clique no botão "Authorize" (cadeado verde) no topo da página do Swagger
4. Na janela que se abre, você verá um campo de entrada único com texto "Value" ou "Valor"
5. Digite seu token neste campo, **incluindo o prefixo** `Bearer ` (com espaço após Bearer):
   ```
   Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJsemFnbyI...
   ```
6. Clique em "Authorize" e depois em "Close"
7. O cadeado deve ficar fechado (verde) indicando que você está autenticado
8. Agora você pode acessar todas as rotas protegidas!

### 4. Renovar Token (quando expirar)

Se o access token expirar (após 20 minutos):

1. Use `POST /auth/refresh`
2. O endpoint usa automaticamente seu token atual
3. Receberá um novo access token
4. Atualize a autorização no Swagger com o novo token

