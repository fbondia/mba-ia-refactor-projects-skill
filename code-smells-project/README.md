# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
export SECRET_KEY='replace-with-a-long-random-value'
export ADMIN_TOKEN='replace-with-a-long-random-value'
python app.py
```

A aplicação sobe em `http://127.0.0.1:5000`. O banco SQLite (`loja.db`) é criado automaticamente. Consulte `.env.example` para as configurações suportadas.

O endpoint legado `/admin/query` responde `410` porque executar SQL fornecido pelo cliente não possui alternativa segura compatível. `/admin/reset-db` exige `X-Admin-Token`.

## Testes

```bash
SECRET_KEY=test-secret-not-for-production .venv/bin/python -m unittest discover -s tests -v
```
