# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`. Diferente dos outros projetos, este já possui alguma separação de camadas (`models/`, `routes/`, `services/`, `utils/`), mas ainda contém problemas arquiteturais e de qualidade.

## Como rodar

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
export SECRET_KEY='replace-with-a-long-random-value'
export SEED_ADMIN_PASSWORD='replace-with-a-strong-development-password'
export SEED_USER_PASSWORD='replace-with-a-strong-development-password'
export SEED_MANAGER_PASSWORD='replace-with-a-strong-development-password'
python seed.py
python app.py
```

A aplicação sobe em `http://127.0.0.1:5000`. O `seed.py` recria o banco SQLite com usuários, categorias e tasks de exemplo.

Criação de usuário e login são públicos. Os demais endpoints exigem `Authorization: Bearer <token>`, e operações administrativas exigem role `admin`. Tokens são assinados e expiram conforme `TOKEN_MAX_AGE`.

## Testes

```bash
SECRET_KEY=test-secret-not-for-production .venv/bin/python -m unittest discover -s tests -v
```
