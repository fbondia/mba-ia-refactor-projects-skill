# Architecture Audit Report

- **Project:** `ecommerce-api-legacy`
- **Audit date:** `2026-09-21`
- **Stack:** Node.js + Express 4.18.2 + sqlite3 5.1.6
- **Scope:** `src/`, manifest e contrato HTTP
- **Analyzed:** 3 arquivos JavaScript, 180 linhas
- **Baseline:** não há testes configurados; boot e endpoints ainda não executados nesta implementação inicial

## Summary

| Severity | Count |
|---|---:|
| CRITICAL | 3 |
| HIGH | 3 |
| MEDIUM | 3 |
| LOW | 2 |
| **Total** | **11** |

## Findings

### [CRITICAL] AP-02 — Credenciais e chave de pagamento hardcoded

- **Location:** `src/utils.js:1-7`
- **Evidence:** usuário/senha de banco e chave `pk_live` estão em objeto versionado.
- **Impact:** comprometimento de banco e gateway; segredos exigem rotação.
- **Recommendation:** ambiente/secret manager com validação no boot.
- **Acceptance criteria:** nenhum segredo no código e ausência de configuração impede boot com erro seguro.
- **Status:** `OPEN`

### [CRITICAL] AP-02 — Número de cartão completo é registrado

- **Location:** `src/AppManager.js:43-46`
- **Evidence:** checkout imprime `cc` inteiro junto à chave do gateway.
- **Impact:** exposição de dados de pagamento e violação grave de práticas de segurança.
- **Recommendation:** não receber/logar PAN bruto; usar tokenização e redaction.
- **Acceptance criteria:** logs e payload persistido não contêm PAN/chave.
- **Status:** `OPEN`

### [CRITICAL] AP-03 — Função de hash caseira baseada em Base64

- **Location:** `src/utils.js:17-23`
- **Evidence:** repete Base64 e trunca para 10 caracteres.
- **Impact:** credenciais são trivialmente reversíveis/colidíveis.
- **Recommendation:** Argon2id/scrypt/bcrypt e migração progressiva.
- **Acceptance criteria:** verificação usa biblioteca segura e hashes antigos são migrados.
- **Status:** `OPEN`

### [HIGH] AP-04 — AppManager mistura banco, rotas e casos de uso

- **Location:** `src/AppManager.js:4-139`
- **Evidence:** a classe cria schema/seeds, registra HTTP, processa pagamento, matrícula, relatório e delete.
- **Impact:** classe não testável em isolamento e alto acoplamento.
- **Recommendation:** composition root, routers, controllers, services e repositories.
- **Acceptance criteria:** `AppManager` deixa de concentrar responsabilidades ou é removida.
- **Status:** `OPEN`

### [HIGH] AP-05 — Rotas administrativa e destrutiva sem autorização

- **Location:** `src/AppManager.js:80-137`
- **Evidence:** relatório financeiro e exclusão de usuário são públicos.
- **Impact:** vazamento financeiro e deleção não autorizada.
- **Recommendation:** autenticação e policy de admin/ownership.
- **Acceptance criteria:** chamadas não autorizadas retornam 401/403.
- **Status:** `OPEN`

### [HIGH] AP-06 — Checkout não é transacional

- **Location:** `src/AppManager.js:43-63`
- **Evidence:** matrícula, pagamento e audit log são escritos em callbacks independentes.
- **Impact:** falha intermediária deixa matrícula ou pagamento inconsistente.
- **Recommendation:** transação atômica, gateway idempotente e rollback/compensação.
- **Acceptance criteria:** falha injetada em cada etapa não deixa escrita parcial.
- **Status:** `OPEN`

### [MEDIUM] AP-08 — Relatório financeiro executa N+1 aninhado

- **Location:** `src/AppManager.js:83-127`
- **Evidence:** consulta enrollments por curso e user/payment por matrícula.
- **Impact:** latência e carga crescem multiplicativamente.
- **Recommendation:** join/agregação SQL e paginação.
- **Acceptance criteria:** relatório usa número constante/limitado de queries.
- **Status:** `OPEN`

### [MEDIUM] AP-06 — Exclusão deixa registros órfãos

- **Location:** `src/AppManager.js:131-136`
- **Evidence:** remove usuário sem tratar matrículas/pagamentos e a própria resposta admite sujeira.
- **Impact:** integridade referencial e relatórios incorretos.
- **Recommendation:** foreign keys e estratégia explícita de cascade/restrict/soft delete.
- **Acceptance criteria:** não há órfãos após delete e comportamento é testado.
- **Status:** `OPEN`

### [MEDIUM] AP-12 — Erros de callbacks são ignorados

- **Location:** `src/AppManager.js:57-61`, `src/AppManager.js:92-125`, `src/AppManager.js:131-136`
- **Evidence:** vários callbacks usam dados ou respondem sem testar `err`.
- **Impact:** crashes, respostas falsas e operações parcialmente concluídas.
- **Recommendation:** promises/async, middleware de erro e rollback.
- **Acceptance criteria:** falhas de DB produzem resposta consistente e log seguro.
- **Status:** `OPEN`

### [LOW] AP-13 — Nomes opacos no contrato e implementação

- **Location:** `src/AppManager.js:28-34`
- **Evidence:** `u`, `e`, `p`, `cid`, `cc` e campos `usr`, `eml`, `pwd`, `c_id` obscurecem o domínio.
- **Impact:** leitura e manutenção mais difíceis.
- **Recommendation:** DTO compatível que traduza o contrato legado para nomes expressivos.
- **Acceptance criteria:** lógica interna usa nomes de domínio claros.
- **Status:** `OPEN`

### [LOW] AP-15 — Estado/export sem uso

- **Location:** `src/utils.js:9-10`, `src/utils.js:25`
- **Evidence:** `totalRevenue` é exportado/importado, mas nunca atualizado ou lido; cache global não tem lifecycle.
- **Impact:** ruído, comportamento enganoso e risco de crescimento indefinido.
- **Recommendation:** remover código morto e encapsular cache se necessário.
- **Acceptance criteria:** exports têm consumidores e lifecycle definido.
- **Status:** `OPEN`

## Deprecated API Review

| API | Location | Version evidence | Modern equivalent | Status |
|---|---|---|---|---|
| Nenhuma API deprecated comprovada | — | versões em `package.json`/lockfile | — | N/A |

## Refactoring Plan

1. Capturar contratos de `api.http` em smoke tests.
2. Externalizar/rotacionar segredos e substituir cartão por token.
3. Extrair repositories e um `CheckoutService` transacional.
4. Criar routers/controllers finos, auth middleware e error middleware.
5. Agregar relatório e definir integridade de exclusão.

## Validation Baseline

| Check | Command/request | Result before refactor |
|---|---|---|
| Syntax/import | processo Node 18 | PASS |
| Tests | — | NOT CONFIGURED |
| Boot | `node src/app.js` | PASS em porta 3000 |
| Endpoints | checkout, relatório e delete | PASS; 200 sem autenticação nas rotas administrativas confirmou o risco |

## Risks and Unverified Items

- Integração de pagamento é simulada; a refatoração deve preservar o contrato sem perpetuar tratamento de PAN inseguro.
- O comportamento assíncrono de criação do schema precisa de smoke test de boot.

## Approval Gate

No source files were modified during phases 1–2.

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]

## Refactoring Result

Refatoração autorizada e concluída em 2026-09-21.

### Current finding status

| Finding | Status | Evidence after refactor |
|---|---|---|
| Segredos hardcoded | RESOLVED | `src/config/index.js:1-10` exige `ADMIN_TOKEN` por ambiente; não há chave de gateway no código. |
| Cartão no log | RESOLVED | `PaymentGateway` valida em memória e nenhuma camada registra ou persiste o PAN. |
| Hash caseiro | RESOLVED | `src/services/passwordService.js:1-16` usa `crypto.scrypt` com salt. |
| God Class | RESOLVED | composition root monta routes, controllers, service, repositories e adapters. |
| Admin público | RESOLVED | `src/routes/index.js:4-10` aplica middleware de admin. |
| Checkout não transacional | RESOLVED | `src/services/checkoutService.js:19-34` executa as escritas em uma transação. |
| N+1 no relatório | RESOLVED | `src/models/repositories.js:57-68` usa um único join. |
| Delete órfão | RESOLVED | schema usa cascades e delete é transacional. |
| Callbacks ignorando erro | RESOLVED | adapters Promise rejeitam erros e middleware central os traduz. |
| Nomes opacos | RESOLVED | DTO legado é traduzido para `name`, `email`, `courseId` e `password`. |
| Estado/export morto | RESOLVED | `utils.js` e cache global foram removidos. |

### New structure

`app.js` inicia o processo; `compositionRoot.js` monta dependências; `routes/`, `controllers/`, `services/`, `models/`, `infrastructure/` e `middlewares/` separam as responsabilidades.

### Validation after refactor

| Check | Result |
|---|---|
| Tests | PASS — 3 testes Node, incluindo rollback e cascade |
| Syntax | PASS — `node --check` em `src/` e `tests/` |
| Boot | PASS — Express em `127.0.0.1:3103` com Node 18.20.8 |
| Smoke | checkout 200; admin sem token 401; relatório com token 200; delete com token 200 |
| Secret response/log scan | PASS — PAN e token não apareceram |
| Dependency audit | 8 vulnerabilidades transitivas permanecem na toolchain de build de `sqlite3`; `npm audit fix` não-breaking aplicado |

### Remaining risks

- O payload legado ainda recebe um número de cartão para compatibilidade; produção deve substituí-lo por tokenização do provedor.
- `sqlite3@5.1.7` traz advisories transitivos majoritariamente pela toolchain `node-gyp/tar`; remover exige trocar o driver ou aceitar uma mudança breaking. O risco permanece `OPEN` e documentado.
