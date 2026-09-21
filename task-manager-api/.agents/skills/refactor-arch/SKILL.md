---
name: refactor-arch
description: Analisa e audita um ou mais projetos backend do workspace e, após confirmação explícita, os refatora para uma arquitetura MVC adequada à stack. Use para auditoria arquitetural, code smells, segurança, SOLID ou migração MVC; não use para uma correção pontual sem revisão arquitetural.
---

# Refactor Arch

Execute as três fases em ordem. A skill pode estar instalada na raiz do repositório ou em um dos projetos-alvo. Descubra a raiz com Git e não dependa do diretório em que a sessão foi iniciada.

## Seleção do alvo

- Se o usuário nomear um ou mais projetos, limite análise, auditoria e refatoração a eles.
- Se a sessão estiver dentro de `code-smells-project/`, `ecommerce-api-legacy/` ou `task-manager-api/` e não houver alvo explícito, processe somente esse projeto.
- Se a sessão estiver na raiz do repositório e não houver alvo explícito, processe os três projetos na ordem `code-smells-project/`, `ecommerce-api-legacy/`, `task-manager-api/`.
- Trate cada diretório como uma aplicação independente: detecte stack e comandos separadamente.
- Para múltiplos alvos, conclua as fases 1 e 2 de todos, apresente um resumo agregado e faça um único gate antes de modificar qualquer código-fonte.
- Grave relatórios em `<raiz-do-repositório>/reports/`, mesmo quando a skill for invocada dentro de um projeto.
- Não trate `.agents/`, `.claude/`, `reports/` ou os outros projetos como parte do source set do projeto que está sendo auditado.

## Regras invariantes

- Preserve rotas, formatos de resposta, códigos HTTP e comportamento observável, salvo quando uma vulnerabilidade exigir mudança incompatível; nesse caso, explique-a no plano.
- Cite todo finding como `projeto/caminho:linha-inicial-linha-final`, com evidência observada no código. Não invente linhas nem trate ausência de evidência como finding.
- Ignore dependências vendorizadas, ambientes virtuais, artefatos gerados, caches e diretórios de build.
- Nunca altere código-fonte ou configuração das aplicações durante as fases 1 e 2. A única escrita permitida é criar/atualizar os relatórios de auditoria.
- Ao final da fase 2, pare e peça confirmação explícita. Só inicie a fase 3 se a resposta for afirmativa.
- Faça mudanças incrementais. Não reescreva uma aplicação já organizada apenas para impor uma árvore de diretórios uniforme.
- Não afirme que um problema foi eliminado sem repetir a inspeção e as validações relevantes.
- Preserve alterações preexistentes do usuário e não faça commits sem solicitação explícita.

## Fase 1 — Análise

Leia [references/project-analysis.md](references/project-analysis.md) e siga as heurísticas. Para cada alvo, inspecione manifests, entry points, configuração, rotas, persistência, testes e documentação.

Imprima um bloco por projeto:

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Project:       <diretório relativo à raiz>
Language:      <linguagem e versão quando comprovada>
Framework:     <framework e versão quando comprovada>
Dependencies:  <principais dependências>
Domain:        <domínio inferido, marcado como inferência>
Architecture:  <arquitetura atual e evidências>
Source files:  <quantidade analisada>
DB tables:     <tabelas/coleções ou "not detected">
Test command:  <comando descoberto ou "not configured">
================================
```

## Fase 2 — Auditoria

Leia [references/anti-patterns.md](references/anti-patterns.md), incluindo APIs deprecated, e compare o catálogo com evidências reais. Leia [references/report-template.md](references/report-template.md) e gere um relatório por projeto.

Ordene findings por `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` e, dentro da severidade, por caminho e linha. Consolide ocorrências repetidas quando tiverem a mesma causa, registrando todas as localizações relevantes. Inclua riscos de falso positivo e itens não verificados.

Use estes destinos na raiz do workspace:

| Projeto | Relatório |
|---|---|
| `code-smells-project/` | `reports/audit-project-1.md` |
| `ecommerce-api-legacy/` | `reports/audit-project-2.md` |
| `task-manager-api/` | `reports/audit-project-3.md` |

Depois de exibir o resumo de todos os alvos, encerre a resposta com exatamente uma pergunta de aprovação inequívoca:

```text
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Não continue no mesmo turno sem resposta afirmativa. A aprovação vale apenas para os projetos e o plano apresentados.

## Fase 3 — Refatoração e validação

Após confirmação, leia [references/mvc-guidelines.md](references/mvc-guidelines.md) e [references/refactoring-playbook.md](references/refactoring-playbook.md). Para cada alvo aprovado:

1. Registre o estado inicial: comandos de teste, boot e smoke test; rotas públicas; arquivos que serão tocados.
2. Planeje a menor sequência de transformações que resolve os findings aceitos.
3. Mantenha um composition root claro e dependências orientadas para dentro: rota/view → controller → model/repository; infraestrutura é injetada nas camadas que a usam.
4. Corrija primeiro segurança e integridade, depois separação MVC, performance e legibilidade.
5. Após cada grupo pequeno de mudanças, execute a validação mais barata aplicável dentro do diretório do projeto.
6. Faça nova auditoria do escopo alterado e atualize o relatório correspondente com status `RESOLVED`, `MITIGATED`, `ACCEPTED` ou `OPEN` e evidências novas.

Validação mínima obrigatória por projeto:

- instalar dependências somente quando necessário, respeitando permissões e o gerenciador detectado;
- executar testes existentes;
- validar importação/compilação/sintaxe;
- iniciar a aplicação de forma limitada e encerrá-la ao concluir;
- exercitar cada endpoint original ao menos uma vez, cobrindo sucesso e erros críticos quando houver fixture segura;
- verificar que segredos não estão no código nem nas respostas;
- confirmar rollback e integridade em fluxos transacionais modificados.

Se não houver testes, crie smoke tests mínimos antes da mudança ou registre claramente a lacuna. Não use "zero anti-patterns" como conclusão absoluta; relate o que foi rechecado e o que permanece fora de escopo.

Finalize com resultados separados por projeto: nova estrutura, arquivos alterados, comandos e saídas, endpoints verificados e findings remanescentes.
