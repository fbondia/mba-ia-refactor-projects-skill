# Architecture Audit Report

- **Project:** `task-manager-api`
- **Audit date:** `2026-09-21`
- **Source snapshot:** `6d1ce6248c3e956801010a89d8bdaab48029bf30`
- **Source inventory:** [inventário original](../validation/source-inventory.md)
- **Stack:** Python + Flask 3.0.0 + Flask-SQLAlchemy 3.1.1
- **Scope:** aplicação, models, routes, services e utils
- **Analyzed:** 15 arquivos Python, 1.158 linhas
- **Baseline:** snapshot anterior à refatoração; sem suíte de testes. Validações históricas declaradas abaixo; revalidação atual em `validation/`.

## Summary

| Severity | Count |
|---|---:|
| CRITICAL | 3 |
| HIGH | 2 |
| MEDIUM | 4 |
| LOW | 2 |
| **Total** | **11** |

## Findings

Snapshot da Fase 2: os status `OPEN` abaixo descrevem o código original. A tabela **Current finding status** registra o estado após correção e é a referência vigente.

### [CRITICAL] AP-02 — Segredos hardcoded na aplicação e SMTP

- **Location:** `app.py:11-15`, `services/notification_service.py:5-17`
- **Evidence:** secret key, usuário e senha SMTP estão no código.
- **Impact:** sessões e conta de e-mail podem ser comprometidas.
- **Recommendation:** configuração por ambiente/secret manager, validação no boot e rotação.
- **Acceptance criteria:** segredos não estão no repositório/log/resposta.
- **Status:** `OPEN`

### [CRITICAL] AP-03 — Hash MD5 e hash serializado

- **Location:** `models/user.py:16-32`
- **Evidence:** `to_dict` inclui `password`; set/check usam MD5 sem salt.
- **Impact:** quebra rápida de credenciais e exposição via endpoints.
- **Recommendation:** hasher adaptativo e DTO público sem password.
- **Acceptance criteria:** API nunca retorna hash e passwords usam helper seguro.
- **Status:** `OPEN`

### [CRITICAL] AP-05 — Token falso e autorização inexistente

- **Location:** `routes/user_routes.py:185-210`
- **Evidence:** login retorna string previsível `fake-jwt-token-<id>` e nenhuma rota a valida.
- **Impact:** qualquer cliente acessa/edita/deleta usuários, tarefas e relatórios.
- **Recommendation:** autenticação real, expiração, assinatura e policies por ação.
- **Acceptance criteria:** rotas protegidas rejeitam token ausente, inválido e papel inadequado.
- **Status:** `OPEN`

### [HIGH] AP-07 — Rotas concentram regras e persistência

- **Location:** `routes/task_routes.py:11-299`, `routes/user_routes.py:10-210`, `routes/report_routes.py:12-223`
- **Evidence:** handlers validam regras, consultam ORM, calculam métricas e controlam transações.
- **Impact:** baixa testabilidade e duplicação apesar das pastas existentes.
- **Recommendation:** controllers/use cases e repositories; rotas apenas adaptam HTTP.
- **Acceptance criteria:** handlers delegam casos de uso e não contêm regra/persistência detalhada.
- **Status:** `OPEN`

### [HIGH] AP-06 — Exclusões dependem de loops sem política relacional

- **Location:** `routes/user_routes.py:134-151`, `routes/report_routes.py:211-223`
- **Evidence:** delete de usuário apaga tasks manualmente; delete de categoria não define efeito nas tasks.
- **Impact:** integridade depende de código de rota e pode deixar referências inválidas.
- **Recommendation:** definir cascade/restrict/set-null no model e transação no caso de uso.
- **Acceptance criteria:** constraints e testes cobrem todas as relações.
- **Status:** `OPEN`

### [MEDIUM] AP-08 — N+1 ao listar tarefas e produtividade

- **Location:** `routes/task_routes.py:14-59`, `routes/report_routes.py:53-68`
- **Evidence:** busca user/category por tarefa e tasks por usuário em loops.
- **Impact:** volume de queries cresce com os registros.
- **Recommendation:** eager loading e agregação SQL.
- **Acceptance criteria:** contador de queries é constante/limitado por página.
- **Status:** `OPEN`

### [MEDIUM] AP-11 — `Query.get()` é API legacy na stack declarada

- **Location:** `routes/task_routes.py:42-52`, `routes/task_routes.py:65-68`, `routes/user_routes.py:27-30`
- **Evidence:** Flask-SQLAlchemy 3.1.1 usa SQLAlchemy 2.x e o padrão moderno é `db.session.get(Model, id)`.
- **Impact:** warnings e custo futuro de migração.
- **Recommendation:** substituir chamadas após validar comportamento.
- **Acceptance criteria:** não há `Model.query.get` e testes permanecem verdes.
- **Status:** `OPEN`

### [MEDIUM] AP-09 — Validação duplicada e inconsistente

- **Location:** `routes/task_routes.py:85-145`, `routes/task_routes.py:156-223`, `utils/helpers.py:57-108`
- **Evidence:** helper reutilizável existe, mas rotas repetem regras e diferem no parsing.
- **Impact:** mudanças não alcançam todos os fluxos.
- **Recommendation:** DTO/schema central usado por create/update.
- **Acceptance criteria:** uma fonte de regras cobre os dois fluxos.
- **Status:** `OPEN`

### [MEDIUM] AP-12 — `except:` amplo oculta falhas

- **Location:** `routes/task_routes.py:62-63`, `routes/task_routes.py:134-138`, `routes/user_routes.py:127-132`, `utils/helpers.py:43-50`
- **Evidence:** exceções são capturadas sem tipo e muitas sem log/contexto.
- **Impact:** bugs viram respostas genéricas e diagnóstico fica difícil.
- **Recommendation:** exceções específicas e handler central.
- **Acceptance criteria:** nenhuma captura ampla em fluxo HTTP; rollback/log consistentes.
- **Status:** `OPEN`

### [LOW] AP-15 — Imports e parâmetro não usados

- **Location:** `app.py:7`, `routes/task_routes.py:7`, `utils/helpers.py:3-7`, `utils/helpers.py:57`
- **Evidence:** múltiplos imports e `existing_task` não são referenciados.
- **Impact:** ruído e intenção enganosa.
- **Recommendation:** remover ou efetivamente usar no design final.
- **Acceptance criteria:** lint não reporta unused imports/arguments.
- **Status:** `OPEN`

### [LOW] AP-14 — Regras de status/prioridade duplicadas

- **Location:** `models/task.py:38-48`, `routes/task_routes.py:96-114`, `utils/helpers.py:74-115`
- **Evidence:** listas e limites aparecem em três lugares.
- **Impact:** divergência futura e manutenção repetida.
- **Recommendation:** enum/value object/policy compartilhada.
- **Acceptance criteria:** regras possuem fonte única e testes.
- **Status:** `OPEN`

## Deprecated API Review

| API | Location | Version evidence | Modern equivalent | Status |
|---|---|---|---|---|
| `Model.query.get(id)` | diversas rotas | Flask-SQLAlchemy 3.1.1 em `requirements.txt`; API legacy removida; testes executam com warnings de depreciação tratados como erro | `db.session.get(Model, id)` | OPEN |

## Refactoring Plan

1. Criar smoke tests Flask para todas as rotas existentes.
2. Externalizar segredos, corrigir senha/DTO e implementar auth/policies.
3. Extrair controllers/use cases e repositories sem reescrever models já separados.
4. Centralizar validação, transações e error handling.
5. Corrigir N+1 e APIs legacy; adicionar app factory/composition root.

## Validation Baseline

Registro histórico preservado: os comandos/observações desta tabela não possuem transcrição integral no repositório. Não confundir com os logs reproduzíveis da revalidação atual.

| Check | Command/request | Result before refactor |
|---|---|---|
| Syntax/import | import via Flask test client | PASS |
| Tests | — | NOT CONFIGURED |
| Boot | import de `app.py` em cópia isolada | PASS |
| Endpoints | `/`, health, tasks, users, reports e categories | PASS com HTTP 200 antes da proteção |

## Risks and Unverified Items

- O registro inicial não preservou a consulta à documentação de depreciação; a revalidação comprova execução com warnings tratados como erro, sem alegar reproduzir essa consulta.
- A migração de hashes exige compatibilidade com usuários já persistidos.

## Approval Gate

Registro histórico declarado: nenhuma alteração de código nas fases 1–2. A transcrição da invocação original e da resposta ao gate não foi preservada; este texto não comprova aquela execução.

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]

## Refactoring Result

Refatoração inicial registrada em 2026-09-21. Sua autorização histórica foi declarada, mas a transcrição não foi preservada. As correções posteriores foram autorizadas nesta conversa por “Aplique as correções e ajustes necessários”.

### Current finding status

| Finding | Status | Evidence after refactor |
|---|---|---|
| Segredos hardcoded | RESOLVED | `config/settings.py:6-9` exige `SECRET_KEY`; serviço SMTP inseguro e não usado foi removido. |
| MD5/hash serializado | RESOLVED | `models/user.py:29-36` usa Werkzeug e `to_dict` exclui senha. |
| Token falso/sem auth | RESOLVED | `services/auth_service.py` assina/expira tokens; services recebem o ator e restringem tarefas/perfis/relatórios por propriedade ou papel, cobertos pelos testes de autorização. |
| Regras nas routes | RESOLVED | Blueprints delegam a controllers e services. |
| Integridade de delete | RESOLVED | relações declaram `CASCADE`/`SET NULL` e service controla commit. |
| N+1 | RESOLVED | `joinedload`/`selectinload` e agregações substituem queries em loops. |
| `Query.get()` legacy | RESOLVED | todo lookup usa `db.session.get` ou `db.select`. |
| Validação duplicada | RESOLVED | normalização fica em `TaskService._normalize` e `UserService._validate`. |
| `except:` amplo | RESOLVED | error handler central e exceções de domínio substituem capturas locais. |
| Imports/parâmetro mortos | RESOLVED | helpers e imports legados foram removidos. |
| Constantes duplicadas | RESOLVED | `models/task.py:6-8` é a fonte dos status e limites. |

### New structure

`application.py` fornece app factory; routes são adapters; `controllers/` delega; `services/` contém casos de uso; models preservam invariantes; `middlewares/` centraliza autenticação e erros; `config/` lê o ambiente.

### Validation after refactor

Resultados da primeira entrega, preservados como histórico. Consulte a revalidação atual ao final para os testes/logs vigentes.

| Check | Result |
|---|---|
| Tests | PASS — 4 testes (`unittest`) cobrindo auth, matriz de endpoints e CRUD |
| Syntax | PASS — `python -m compileall` em aplicação e testes |
| Boot | PASS — Flask em `127.0.0.1:5103` |
| Smoke | `/` 200, health 200, tasks sem token 401, login 200, tasks/report/categories com token 200 |
| Secret response scan | PASS |
| Deprecated APIs | PASS — seed executado com `DeprecationWarning` tratado como erro |

### Remaining risks

- Bancos antigos com hashes MD5 precisam de migração de dados; a implementação nova não aceita MD5 silenciosamente.
- Alterações de autenticação são incompatíveis por segurança: consumidores devem efetuar login e enviar Bearer token.

### Correções da revisão

- Usuários comuns e managers acessam apenas suas próprias tarefas, perfis e relatórios individuais. Listagem, busca e estatísticas de tarefas são filtradas pelo ator. Somente administradores acessam o relatório global e atribuem tarefas a terceiros; a reatribuição por usuário comum é rejeitada.
- O contrato original de `overdue.tasks` foi restaurado: `id`, `title`, `due_date` e `days_overdue`. Teste verifica os valores e as chaves.
- Incompatibilidade de segurança explícita: acessos a recursos alheios retornam 403; cadastro e login continuam públicos.

### Revalidação atual

- Testes: **7 passaram**, incluindo ownership, acesso administrativo e contrato de tarefas atrasadas.
- Comando reproduzível na raiz: `python3 validation/revalidate.py --node /caminho/para/node` (Node >=18 <23; esta execução usa 18.20.8).
- Saída atual: [testes](../validation/project-3-tests.log), [boot real](../validation/boot-smoke.log).
- Boot usa banco temporário e encerra o servidor após a requisição HTTP. Os testes cobrem métodos/rotas, não uma equivalência exaustiva de todos os payloads legados.
- A execução inicial da skill nas três fases não foi reconstituída; as evidências atuais demonstram o estado corrigido da entrega.
