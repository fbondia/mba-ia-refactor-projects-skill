# Heurísticas de análise de projeto

## 1. Delimitar o escopo

Considere código de primeira parte. Exclua `.git`, `node_modules`, `.venv`, `venv`, `dist`, `build`, cobertura, caches, bancos gerados e arquivos minificados. Conte arquivos por extensão e linhas físicas apenas como contexto; arquitetura não é inferida por volume.

## 2. Detectar stack por evidência

Use múltiplos sinais e registre a fonte:

| Aspecto | Sinais comuns |
|---|---|
| Python | `pyproject.toml`, `requirements*.txt`, `Pipfile`, arquivos `.py` |
| Node.js | `package.json`, lockfile, arquivos `.js/.ts`, campo `type` |
| Flask | dependência `flask`, `Flask(__name__)`, Blueprints, `flask run` |
| Express | dependência `express`, `express()`, `Router`, `app.listen` |
| Banco | SQLite/SQLAlchemy/Sequelize/Prisma imports, migrations, DDL, URI de conexão |
| Versão | manifest/lockfile primeiro; runtime local apenas como confirmação |

Não confunda biblioteca instalada com framework efetivamente usado. Quando versões do manifest e lockfile divergirem, informe ambas.

## 3. Encontrar entry points e comandos

- Leia scripts do gerenciador (`package.json`, `Makefile`, `pyproject.toml`) e blocos `if __name__ == "__main__"`.
- Procure factory functions, `app.listen`, `app.run`, WSGI/ASGI e arquivos de container.
- Descubra testes em `tests/`, scripts, CI e documentação. Não invente um comando ausente.

## 4. Mapear o domínio

Infira o domínio a partir de rotas, entidades, tabelas e casos de uso. Marque explicitamente como inferência. Liste entidades e fluxos principais, por exemplo checkout, matrícula, autenticação e relatórios.

## 5. Mapear arquitetura atual

Construa uma matriz simples por arquivo/módulo:

| Componente | HTTP/UI | Orquestração | Regra de negócio | Persistência | Infra/config |
|---|---:|---:|---:|---:|---:|

Um arquivo que ocupa três ou mais colunas é candidato a responsabilidade excessiva. Verifique dependências e ciclos, não apenas nomes de pastas: um diretório `models/` não prova separação adequada.

Classifique a estrutura como uma descrição factual, por exemplo monólito em scripts, MVC parcial, arquitetura em camadas ou modular por domínio. Inclua as evidências.

## 6. Inventariar a superfície observável

- Rotas, métodos, parâmetros, autenticação, respostas e status.
- Tabelas/coleções, relações, constraints e transações.
- Configurações, variáveis de ambiente e integrações externas.
- Side effects: e-mail, pagamento, arquivos, filas e logs.

Esse inventário vira a baseline da fase 3.

## 7. APIs deprecated

Extraia versões antes de classificar uma API como deprecated. Confirme na documentação/changelog da versão quando houver acesso; caso contrário marque `needs verification`. Diferencie deprecated de apenas antigo ou estilisticamente indesejado.
