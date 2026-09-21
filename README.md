# Desafio 03 — Skill de auditoria e refatoração MVC

Implementação da skill `refactor-arch` e resultado de sua execução nos três projetos backend: análise, auditoria, refatoração MVC e validação dos contratos.

- **Fork público:** [fbondia/mba-ia-refactor-projects-skill](https://github.com/fbondia/mba-ia-refactor-projects-skill)
- **Repositório-base:** [devfullcycle/mba-ia-refactor-projects-skill](https://github.com/devfullcycle/mba-ia-refactor-projects-skill)

## Estado da implementação

- [x] Três projetos-base importados
- [x] Análise manual dos três projetos
- [x] `SKILL.md` com fases sequenciais e approval gate
- [x] Cinco referências Markdown obrigatórias
- [x] Catálogo com 16 anti-patterns e detecção de APIs deprecated
- [x] Playbook com 11 transformações antes/depois
- [x] Skill Codex na raiz e copiada para `.agents/skills/refactor-arch/` dentro dos três projetos
- [x] Relatórios de auditoria com resultado da Fase 3
- [x] Baseline executável de boot e endpoints
- [x] Fase 3 executada após confirmação
- [x] Código dos três projetos refatorado e validado

A Fase 3 foi executada após aprovação explícita. Cada relatório preserva a evidência original e acrescenta status atual, nova estrutura, comandos de validação e riscos remanescentes.

## Estrutura

```text
desafio-03/
├── .agents/skills/refactor-arch/
│   ├── SKILL.md
│   └── references/
│       ├── anti-patterns.md
│       ├── mvc-guidelines.md
│       ├── project-analysis.md
│       ├── refactoring-playbook.md
│       └── report-template.md
├── code-smells-project/
│   └── .agents/skills/refactor-arch/
├── ecommerce-api-legacy/
│   └── .agents/skills/refactor-arch/
├── task-manager-api/
│   └── .agents/skills/refactor-arch/
└── reports/
    ├── audit-project-1.md
    ├── audit-project-2.md
    └── audit-project-3.md
```

## Análise Manual

### Projeto 1 — `code-smells-project` (Python/Flask)

| Severidade | Problema | Evidência | Por que importa |
|---|---|---|---|
| CRITICAL | Execução remota de SQL arbitrário | `app.py:59-76` | Um cliente pode ler, alterar ou apagar o banco. |
| CRITICAL | SQL injection por concatenação | `models.py:24-29`, `43-50`, `105-111`, `285-299` | Input entra diretamente em queries, inclusive no login. |
| CRITICAL | Senhas em plaintext | `database.py:75-82`, `models.py:105-129` | Vazamento do banco revela imediatamente as credenciais. |
| CRITICAL | Secret key hardcoded e exposta | `app.py:6-9`, `controllers.py:285-290` | Compromete sessões e divulga configuração sensível no health check. |
| HIGH | God Module com vários domínios | `models.py:4-314` | Produtos, usuários, pedidos e relatórios não podem evoluir/testar isoladamente. |
| HIGH | Operações administrativas públicas | `app.py:47-76` | Reset e SQL não possuem autenticação/autorização. |
| MEDIUM | N+1 em pedidos | `models.py:171-233` | Queries crescem com pedidos e itens. |
| MEDIUM | Conexão global insegura | `database.py:4-11` | Lifecycle e concorrência da conexão não são controlados. |
| MEDIUM | Validação duplicada/divergente | `controllers.py:24-96` | Create e update aplicam regras diferentes. |
| LOW | Magic numbers e strings | `models.py:256-262`, `controllers.py:242-243` | Regras de domínio ficam dispersas e anônimas. |
| LOW | Logging com `print` | `controllers.py:5-12`, `208-220` | Falta estrutura, nível, contexto e redaction. |

### Projeto 2 — `ecommerce-api-legacy` (Node.js/Express)

| Severidade | Problema | Evidência | Por que importa |
|---|---|---|---|
| CRITICAL | Segredos versionados | `src/utils.js:1-7` | Expõe credenciais e chave de pagamento. |
| CRITICAL | Cartão completo no log | `src/AppManager.js:43-46` | Vaza dado de pagamento altamente sensível. |
| CRITICAL | Hash caseiro baseado em Base64 | `src/utils.js:17-23` | Senhas são trivialmente comprometidas. |
| HIGH | God Class | `src/AppManager.js:4-139` | Banco, rotas, pagamento, matrícula e relatórios estão acoplados. |
| HIGH | Rotas privilegiadas públicas | `src/AppManager.js:80-137` | Relatórios financeiros e deletes não exigem permissão. |
| HIGH | Checkout sem transação | `src/AppManager.js:43-63` | Falhas intermediárias deixam matrícula/pagamento inconsistentes. |
| MEDIUM | N+1 aninhado | `src/AppManager.js:83-127` | Relatório faz queries por curso e por matrícula. |
| MEDIUM | Delete gera órfãos | `src/AppManager.js:131-136` | Matrículas e pagamentos ficam sem integridade. |
| MEDIUM | Erros de callback ignorados | `src/AppManager.js:57-61`, `92-125`, `131-136` | A API pode responder sucesso após falha interna. |
| LOW | Nomes opacos | `src/AppManager.js:28-34` | Campos e variáveis escondem a intenção do checkout. |
| LOW | Estado/export morto | `src/utils.js:9-10`, `25` | Aumenta ruído e sugere comportamento inexistente. |

### Projeto 3 — `task-manager-api` (Python/Flask)

| Severidade | Problema | Evidência | Por que importa |
|---|---|---|---|
| CRITICAL | Segredos da aplicação e SMTP no código | `app.py:11-15`, `services/notification_service.py:5-17` | Sessões e conta de e-mail podem ser comprometidas. |
| CRITICAL | MD5 e hash exposto nas respostas | `models/user.py:16-32` | Hash fraco e serialização ampliam o impacto de vazamento. |
| CRITICAL | Token previsível sem autenticação real | `routes/user_routes.py:185-210` | O token não protege nenhuma rota e pode ser forjado. |
| HIGH | Regras/persistência dentro de routes | `routes/task_routes.py:11-299`, `routes/report_routes.py:12-223` | A separação por pastas não produz separação de responsabilidades. |
| HIGH | Integridade de delete na rota | `routes/user_routes.py:134-151`, `routes/report_routes.py:211-223` | Relações dependem de loops e comportamento implícito. |
| MEDIUM | N+1 em tarefas/relatórios | `routes/task_routes.py:14-59`, `routes/report_routes.py:53-68` | Número de queries cresce com os dados. |
| MEDIUM | Uso legacy de `Query.get()` | `routes/task_routes.py:42-52`, `routes/user_routes.py:27-30` | A stack 3.1.1 deve migrar para `db.session.get`. |
| MEDIUM | Validação duplicada | `routes/task_routes.py:85-223`, `utils/helpers.py:57-108` | O helper existe, mas as rotas repetem regras. |
| MEDIUM | Capturas amplas de exceção | `routes/task_routes.py:62-63`, `utils/helpers.py:43-50` | Bugs ficam ocultos e difíceis de diagnosticar. |
| LOW | Imports/parâmetro sem uso | `app.py:7`, `utils/helpers.py:3-7`, `57` | Adiciona ruído e intenção falsa. |
| LOW | Constantes de domínio duplicadas | `models/task.py:38-48`, `utils/helpers.py:74-115` | Status e limites podem divergir. |

## Construção da Skill

O `SKILL.md` mantém apenas o workflow, invariantes de segurança e roteamento para referências. O conhecimento detalhado foi separado por uso:

- `project-analysis.md`: detecção orientada a evidência de stack, domínio, entry points, banco e arquitetura;
- `anti-patterns.md`: 16 padrões distribuídos entre CRITICAL/HIGH/MEDIUM/LOW, com sinais e controle de falsos positivos;
- `report-template.md`: schema único para findings, baseline, riscos e approval gate;
- `mvc-guidelines.md`: responsabilidades e direção de dependências sem impor a mesma árvore a todas as stacks;
- `refactoring-playbook.md`: 11 transformações concretas, com exemplos antes/depois.

A abordagem é agnóstica de tecnologia porque procura papéis e dependências — transporte, caso de uso, domínio, persistência e infraestrutura — em vez de depender de nomes como `controllers.py`. Exemplos Python e JavaScript demonstram a transformação, mas as regras exigem adaptar a implementação às convenções da stack detectada.

O principal cuidado foi evitar uma falsa promessa de automação segura. A Fase 2 pode criar apenas o relatório e termina com uma pergunta explícita. A Fase 3 exige baseline, mudanças incrementais e evidência de testes/boot/endpoints antes de declarar sucesso.

Para atender tanto à convenção do Codex quanto à execução isolada exigida pelo desafio, a mesma skill está instalada em cada projeto em `.agents/skills/refactor-arch/`. Uma cópia também permanece na raiz para permitir a auditoria conjunta. A seleção do alvo usa o diretório atual: dentro de um projeto, a execução sem alvo processa apenas aquele projeto; na raiz, processa os três.

### Desafios encontrados

- **Segurança versus compatibilidade:** `/admin/query` não possui alternativa segura equivalente. O path foi preservado, mas agora responde `410`, e a incompatibilidade está documentada.
- **Stacks diferentes:** Flask usa app factory, Blueprints e lifecycle por request; Express usa composition root, routers, Promises e adapters. A skill define responsabilidades MVC, não uma árvore rígida.
- **Projeto parcialmente organizado:** no Task Manager, a refatoração preservou models e Blueprints úteis e moveu apenas regras, autenticação e persistência indevidamente acopladas.
- **Evidência reproduzível:** foram adicionados testes de contrato e logs versionados de testes, compilação, boot e smoke HTTP.

## Resultados

| Projeto | Findings iniciais | Resolvidos | Mitigados | Testes | Boot/smoke |
|---|---:|---:|---:|---:|---|
| code-smells-project | 11 | 10 | 1 | 4/4 | PASS |
| ecommerce-api-legacy | 11 | 11 | 0 | 3/3 | PASS |
| task-manager-api | 11 | 11 | 0 | 4/4 | PASS |

O E-commerce Flask passou de quatro scripts acoplados para app factory, views/routes, controllers, repositories, infraestrutura e middleware. O LMS Express substituiu a God Class por composition root, controllers, services, repositories e adapters. O Task Manager preservou seus models/Blueprints, mas moveu regras para services/controllers e adicionou autenticação assinada e error handling central.

| Projeto | Antes | Depois |
|---|---|---|
| `code-smells-project` | Quatro scripts com HTTP, SQL e regras misturados | App factory, routes, controllers, repositories, infraestrutura, config e error handler |
| `ecommerce-api-legacy` | `AppManager` concentrando rotas, banco, checkout e relatórios | Composition root, routers, controllers, service de checkout, repositories e adapters |
| `task-manager-api` | Pastas existentes, mas regras e persistência concentradas nas routes | Routes finas, controllers, services, autenticação assinada, eager loading e erros centrais |

Relatórios completos: [`reports/audit-project-1.md`](reports/audit-project-1.md), [`reports/audit-project-2.md`](reports/audit-project-2.md) e [`reports/audit-project-3.md`](reports/audit-project-3.md).

Logs reais da validação: [`validation/project-1-tests.log`](validation/project-1-tests.log), [`validation/project-2-tests.log`](validation/project-2-tests.log), [`validation/project-3-tests.log`](validation/project-3-tests.log), [`validation/boot-smoke.log`](validation/boot-smoke.log) e [`validation/skill-validation.log`](validation/skill-validation.log).

## Checklist de validação

| Item | Projeto 1 | Projeto 2 | Projeto 3 |
|---|:---:|:---:|:---:|
| Linguagem detectada corretamente | ✓ | ✓ | ✓ |
| Framework detectado corretamente | ✓ | ✓ | ✓ |
| Domínio descrito corretamente | ✓ | ✓ | ✓ |
| Número de arquivos condizente com o source set original | ✓ | ✓ | ✓ |
| Relatório segue o template | ✓ | ✓ | ✓ |
| Findings possuem arquivos e linhas do código auditado | ✓ | ✓ | ✓ |
| Findings ordenados por severidade | ✓ | ✓ | ✓ |
| Pelo menos 5 findings | ✓ (11) | ✓ (11) | ✓ (11) |
| APIs deprecated avaliadas | ✓ | ✓ | ✓ (`Query.get`) |
| Approval gate antes da Fase 3 | ✓ | ✓ | ✓ |
| Estrutura MVC adequada à stack | ✓ | ✓ | ✓ |
| Configuração sem segredos hardcoded | ✓ | ✓ | ✓ |
| Models/repositories abstraem dados | ✓ | ✓ | ✓ |
| Views/routes separadas | ✓ | ✓ | ✓ |
| Controllers concentram o fluxo | ✓ | ✓ | ✓ |
| Error handling centralizado | ✓ | ✓ | ✓ |
| Entry point/composition root claro | ✓ | ✓ | ✓ |
| Aplicação inicia sem erros | ✓ | ✓ | ✓ |
| Endpoints originais cobertos por testes/smoke | ✓ | ✓ | ✓ |

## Como executar no Codex

### Pré-requisitos

- Git e OpenAI Codex instalados e autenticados;
- Python 3 com suporte a ambientes virtuais;
- Node.js 18 para o projeto Express;
- dependências instaladas com `pip install -r requirements.txt` nos projetos Flask e `npm install` no projeto Express.

O Codex descobre skills de repositório em `.agents/skills`, conforme a [documentação oficial de skills](https://learn.chatgpt.com/docs/build-skills). Cada projeto contém sua própria cópia, portanto pode ser aberto e executado isoladamente.

```bash
cd desafio-03/code-smells-project
codex
```

No prompt interativo do Codex, invoque a skill:

```text
$refactor-arch
```

Repita nos outros projetos:

```text
cd ../ecommerce-api-legacy
codex
# prompt: $refactor-arch

cd ../task-manager-api
codex
# prompt: $refactor-arch
```

Dentro de cada projeto, a invocação sem alvo processa somente o projeto atual e grava o relatório na pasta comum `reports/`. Também é possível abrir a raiz de `desafio-03` e pedir `$refactor-arch Analise e audite os três projetos deste workspace.`

Revise o resultado da Fase 2 e responda `y` apenas quando quiser autorizar a Fase 3 para os alvos e o plano apresentados. Depois, confira no relatório atualizado os comandos de teste, boot e a matriz de endpoints executada; resultados não executados devem permanecer explicitamente como `NOT RUN`.

### Como validar a refatoração

```bash
# Projeto 1
cd code-smells-project
SECRET_KEY=test-secret-not-for-production .venv/bin/python -m unittest discover -s tests -v

# Projeto 2 (Node.js 18)
cd ../ecommerce-api-legacy
npm test

# Projeto 3
cd ../task-manager-api
SECRET_KEY=test-secret-not-for-production .venv/bin/python -W error::DeprecationWarning -m unittest discover -s tests -v
```

Os outputs capturados desses comandos e do boot real estão em [`validation/`](validation/README.md).
