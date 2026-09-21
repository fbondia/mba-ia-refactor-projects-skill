# Architecture Audit Report

- **Project:** `code-smells-project`
- **Audit date:** `2026-09-21`
- **Source snapshot:** `6d1ce6248c3e956801010a89d8bdaab48029bf30`
- **Source inventory:** [inventário original](../validation/source-inventory.md)
- **Stack:** Python 3 + Flask 3.1.1 + sqlite3
- **Scope:** código Python de primeira parte e `requirements.txt`
- **Analyzed:** 4 arquivos Python, 780 linhas
- **Baseline:** snapshot anterior à refatoração; sem suíte de testes. Validações históricas declaradas abaixo; revalidação atual em `validation/`.

## Summary

| Severity | Count |
|---|---:|
| CRITICAL | 4 |
| HIGH | 2 |
| MEDIUM | 3 |
| LOW | 2 |
| **Total** | **11** |

## Findings

Snapshot da Fase 2: os status `OPEN` abaixo descrevem o código original. A tabela **Current finding status** registra o estado após correção e é a referência vigente.

### [CRITICAL] AP-01 — Endpoint permite SQL arbitrário

- **Location:** `app.py:59-76`
- **Evidence:** o corpo HTTP fornece a string executada diretamente por `cursor.execute`.
- **Impact:** qualquer cliente pode ler, alterar ou apagar o banco.
- **Recommendation:** remover o endpoint; se houver caso administrativo legítimo, expor comandos allowlisted com autenticação forte.
- **Acceptance criteria:** nenhuma entrada HTTP é executada como SQL e a rota antiga retorna 404/410 ou exige operação segura equivalente.
- **Status:** `OPEN`

### [CRITICAL] AP-01 — SQL construído por concatenação

- **Location:** `models.py:24-29`, `models.py:43-50`, `models.py:105-111`, `models.py:285-299`
- **Evidence:** IDs, credenciais e filtros são concatenados em SQL.
- **Impact:** SQL injection permite bypass de login, exfiltração e alteração de dados.
- **Recommendation:** parametrizar todos os valores e aplicar allowlist a partes estruturais.
- **Acceptance criteria:** testes com payloads de injeção falham com segurança e nenhuma query concatena entrada.
- **Status:** `OPEN`

### [CRITICAL] AP-03 — Senhas armazenadas e comparadas em plaintext

- **Location:** `database.py:75-82`, `models.py:72-120`, `models.py:122-129`
- **Evidence:** seeds e inserts gravam `senha` diretamente; o login compara o valor recebido no SQL.
- **Impact:** vazamento do banco expõe imediatamente todas as credenciais.
- **Recommendation:** hash adaptativo com salt, migração de dados e exclusão do campo nas respostas.
- **Acceptance criteria:** senha não é recuperável nem serializada e autenticação usa verificador seguro.
- **Status:** `OPEN`

### [CRITICAL] AP-02 — Secret key hardcoded e exposta no health check

- **Location:** `app.py:6-9`, `controllers.py:264-290`
- **Evidence:** `SECRET_KEY` está no código e o mesmo valor é retornado por `/health`.
- **Impact:** compromete assinatura de sessão e divulga configuração sensível.
- **Recommendation:** variável de ambiente obrigatória, rotação e resposta de health mínima.
- **Acceptance criteria:** segredo não aparece no repositório, logs ou respostas.
- **Status:** `OPEN`

### [HIGH] AP-04 — Módulo de modelos concentra quatro domínios e regras

- **Location:** `models.py:4-314`
- **Evidence:** produtos, usuários, autenticação, pedidos e relatórios compartilham um módulo com SQL e regras.
- **Impact:** forte acoplamento e baixa testabilidade; mudanças têm amplo raio de impacto.
- **Recommendation:** separar repositories/models e casos de uso por domínio.
- **Acceptance criteria:** módulos têm responsabilidades coesas e controllers usam interfaces claras.
- **Status:** `OPEN`

### [HIGH] AP-05 — Rotas destrutivas sem autorização

- **Location:** `app.py:47-76`
- **Evidence:** reset de banco e execução de query não têm autenticação nem policy.
- **Impact:** exclusão ou manipulação remota de dados.
- **Recommendation:** remover SQL arbitrário e proteger qualquer função administrativa restante.
- **Acceptance criteria:** requisições não autenticadas/sem papel recebem 401/403.
- **Status:** `OPEN`

### [MEDIUM] AP-08 — N+1 no carregamento de pedidos

- **Location:** `models.py:171-233`
- **Evidence:** para cada pedido consulta itens e, para cada item, consulta o produto.
- **Impact:** número de queries cresce com pedidos e itens.
- **Recommendation:** carregar pedido, itens e nomes por joins/batch.
- **Acceptance criteria:** quantidade de queries é constante ou limitada por página.
- **Status:** `OPEN`

### [MEDIUM] AP-10 — Conexão global compartilhada e thread checks desativados

- **Location:** `database.py:4-11`
- **Evidence:** conexão SQLite global usa `check_same_thread=False` sem lifecycle/lock.
- **Impact:** concorrência, vazamento de recurso e testes interferentes.
- **Recommendation:** conexão por request com teardown ou extensão/pool da stack.
- **Acceptance criteria:** cada request tem lifecycle seguro e conexão é fechada.
- **Status:** `OPEN`

### [MEDIUM] AP-09 — Validação duplicada e divergente

- **Location:** `controllers.py:24-96`
- **Evidence:** create/update repetem validações, mas update não valida categoria nem tamanho do nome.
- **Impact:** regras inconsistentes e manutenção propensa a regressão.
- **Recommendation:** schema/DTO compartilhado com modo parcial.
- **Acceptance criteria:** create/update exercitam a mesma fonte de regras.
- **Status:** `OPEN`

### [LOW] AP-14 — Regras e percentuais mágicos

- **Location:** `models.py:256-262`, `controllers.py:242-243`
- **Evidence:** faixas de desconto e status válidos estão embutidos no fluxo.
- **Impact:** mudança exige edição dispersa e pode gerar divergência.
- **Recommendation:** constantes/policies de domínio nomeadas.
- **Acceptance criteria:** regras têm nomes e testes próprios.
- **Status:** `OPEN`

### [LOW] AP-16 — Logging ad hoc com `print`

- **Location:** `controllers.py:5-12`, `controllers.py:208-220`
- **Evidence:** eventos e erros são impressos sem nível ou contexto estruturado.
- **Impact:** baixa observabilidade e risco de dados sensíveis em logs.
- **Recommendation:** logger estruturado com redaction.
- **Acceptance criteria:** não há `print` em fluxo de request.
- **Status:** `OPEN`

## Deprecated API Review

| API | Location | Version evidence | Modern equivalent | Status |
|---|---|---|---|---|
| Nenhuma API deprecated comprovada | — | Flask 3.1.1 em `requirements.txt` | — | N/A |

## Refactoring Plan

1. Criar baseline de contratos com Flask test client.
2. Extrair configuração, retirar endpoints inseguros e proteger funções administrativas.
3. Parametrizar queries, migrar senhas e introduzir lifecycle de conexão.
4. Separar routes, controllers/use cases e repositories por domínio.
5. Agregar queries de pedidos, centralizar erros e validação.

## Validation Baseline

Registro histórico preservado: os comandos/observações desta tabela não possuem transcrição integral no repositório. Não confundir com os logs reproduzíveis da revalidação atual.

| Check | Command/request | Result before refactor |
|---|---|---|
| Syntax/import | import via Flask test client | PASS |
| Tests | — | NOT CONFIGURED |
| Boot | import de `app.py` em cópia isolada | PASS |
| Endpoints | `/`, produtos, usuários, pedidos, relatório, health e admin query | PASS; admin query confirmou vulnerabilidade com HTTP 200 |

## Risks and Unverified Items

- A execução com SQLite foi revalidada em banco temporário; a matriz HTTP é exercitada pelos testes, sem comprovar todo payload possível.
- Não foi verificado se as credenciais hardcoded foram usadas fora deste exercício; devem ser tratadas como comprometidas.

## Approval Gate

Registro histórico declarado: nenhuma alteração de código nas fases 1–2. A transcrição da invocação original e da resposta ao gate não foi preservada; este texto não comprova aquela execução.

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]

## Refactoring Result

Refatoração inicial registrada em 2026-09-21. Sua autorização histórica foi declarada, mas a transcrição não foi preservada. As correções posteriores foram autorizadas nesta conversa por “Aplique as correções e ajustes necessários”.

### Current finding status

| Finding | Status | Evidence after refactor |
|---|---|---|
| SQL arbitrário | MITIGATED | `src/views/routes.py:121-122` mantém o path legado, mas retorna HTTP 410 sem executar input. |
| SQL por concatenação | RESOLVED | repositories usam bind parameters, por exemplo `src/models/product_model.py:13`. |
| Senhas plaintext | RESOLVED | `src/models/user_model.py:1-36` usa helpers adaptativos do Werkzeug e não serializa o hash. |
| Secret exposto | RESOLVED | `src/config/settings.py:6-9` exige ambiente; health não retorna configuração. |
| God Module | RESOLVED | responsabilidades separadas em `views/`, `controllers/`, `models/` e `infrastructure/`. |
| Admin público | RESOLVED | `src/views/routes.py:24-29` valida token em tempo constante. |
| N+1 em pedidos | RESOLVED | `src/models/order_model.py:67-75` carrega pedidos/itens/produtos em um join. |
| Conexão global | RESOLVED | `src/infrastructure/database.py:48-65` usa conexão em `flask.g` com teardown. |
| Validação duplicada | RESOLVED | validação create/update está em `ProductController._validate`. |
| Magic values | RESOLVED | status/categorias/descontos possuem constantes nomeadas. |
| Logging ad hoc | RESOLVED | error handler central usa `logging`; não há `print` no request flow. |

### New structure

`app.py` é o entry point; `src/app.py` é a factory; `views/` adapta HTTP; `controllers/` orquestra casos de uso; `models/` contém repositories; `infrastructure/` gerencia SQLite; `middlewares/` centraliza erros.

### Validation after refactor

Resultados da primeira entrega, preservados como histórico. Consulte a revalidação atual ao final para os testes/logs vigentes.

| Check | Result |
|---|---|
| Tests | PASS — 4 testes (`unittest`) |
| Syntax | PASS — `python -m compileall -q app.py src tests` |
| Boot | PASS — Flask em `127.0.0.1:5101` |
| Smoke | `/` 200, `/produtos` 200, `/health` 200, `/admin/query` 410 |
| Secret response scan | PASS |
| Transaction/integrity | PASS — criação de pedido coberta por teste e rollback no repository |

### Remaining risks

- O endpoint incompatível `/admin/query` foi deliberadamente desativado; clientes devem removê-lo.
- Valores de credenciais anteriormente versionados devem ser considerados comprometidos e rotacionados fora do repositório.

### Revalidação atual

- Testes: **4 passaram**, incluindo matriz de endpoints original e CRUD.
- Comando reproduzível na raiz: `python3 validation/revalidate.py --node /caminho/para/node` (Node >=18 <23; esta execução usa 18.20.8).
- Saída atual: [testes](../validation/project-1-tests.log), [boot real](../validation/boot-smoke.log).
- Boot usa banco temporário e encerra o servidor após a requisição HTTP. Os testes cobrem métodos/rotas, não uma equivalência exaustiva de todos os payloads legados.
- A execução inicial da skill nas três fases não foi reconstituída; as evidências atuais demonstram o estado corrigido da entrega.
