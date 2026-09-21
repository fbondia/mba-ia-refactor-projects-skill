# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
npm install
export ADMIN_TOKEN='replace-with-a-long-random-value'
npm start
```

A aplicação sobe em `http://127.0.0.1:3000`. O banco SQLite é em memória por padrão e carrega seeds automaticamente. Consulte `.env.example` para persistência e porta.

As rotas administrativas exigem `Authorization: Bearer <ADMIN_TOKEN>`. O checkout mantém o payload legado, mas cartão e configuração sensível não são registrados nem persistidos.

## Testes

```bash
npm test
```

Exemplos de requisições estão em `api.http`.
