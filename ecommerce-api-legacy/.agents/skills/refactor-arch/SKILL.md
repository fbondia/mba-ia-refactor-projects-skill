---
name: refactor-arch
description: Analisa e audita um ou mais projetos backend do workspace e, após confirmação explícita, os refatora para uma arquitetura MVC adequada à stack. Use para auditoria arquitetural, code smells, segurança, SOLID ou migração MVC; não use para uma correção pontual sem revisão arquitetural.
---

# Refactor Arch

Execute as três fases em ordem. A skill pode estar instalada na raiz do repositório ou em um dos projetos-alvo. Descubra a raiz com Git e não dependa do diretório em que a sessão foi iniciada.

## Seleção do alvo

- Se o usuário nomear um ou mais caminhos, limite o trabalho a eles.
- Sem alvo explícito, encontre a aplicação que contém o diretório atual usando manifests, entry points e código de primeira parte. Não dependa do nome da pasta nem da presença de Git.
- Na raiz de um workspace com várias aplicações independentes, descubra-as pelos manifests/entry points, excluindo dependências, exemplos vendorizados e builds. Apresente os alvos identificados antes da auditoria; peça esclarecimento somente se houver ambiguidade real de escopo.
- Detecte stack e comandos separadamente para cada aplicação. Para vários alvos, conclua análise e auditoria de todos antes de apresentar um único gate.
- Use a raiz Git como raiz dos relatórios, quando disponível; sem Git, use a raiz do workspace selecionado ou da aplicação isolada. Grave em `reports/audit-<identificador-do-alvo>.md`, derivando o identificador do caminho relativo e evitando colisões.
- Os nomes de relatório específicos do desafio abaixo são aliases de compatibilidade; não limitam as aplicações suportadas.
- Exclua `.agents/`, `.claude/`, `reports/` e outras aplicações do source set de cada alvo.

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

Registre o commit ou snapshot auditado, o inventário de arquivos contados (incluindo o critério para arquivos vazios) e salve a saída da análise como evidência. Imprima um bloco por projeto:

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

Para os projetos deste desafio, preserve estes destinos na raiz dos relatórios. Para qualquer outro alvo, use o nome genérico definido acima:

| Projeto | Relatório |
|---|---|
| `code-smells-project/` | `reports/audit-project-1.md` |
| `ecommerce-api-legacy/` | `reports/audit-project-2.md` |
| `task-manager-api/` | `reports/audit-project-3.md` |

Depois de exibir o resumo de todos os alvos, encerre a resposta com exatamente uma pergunta de aprovação inequívoca:

```text
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Não continue no mesmo turno sem resposta afirmativa, exceto quando o usuário já tiver aprovado explicitamente esse mesmo escopo e plano na conversa. A aprovação vale apenas para os projetos e o plano apresentados. Registre a resposta real e o escopo aprovado; nunca invente uma transcrição ausente.

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
- exercitar cada endpoint original ao menos uma vez, comparando também campos, tipos e valores relevantes das respostas com a baseline;
- testar autorização com dois usuários distintos: leitura, edição, exclusão, reatribuição e filtragem de coleções, além de acesso administrativo;
- verificar que segredos não estão no código nem nas respostas;
- confirmar rollback e integridade em fluxos transacionais modificados.

Se não houver testes, crie smoke tests mínimos antes da mudança ou registre claramente a lacuna. Não use "zero anti-patterns" como conclusão absoluta; relate o que foi rechecado e o que permanece fora de escopo.

Finalize com resultados separados por projeto: nova estrutura, arquivos alterados, comandos e saídas, endpoints verificados e findings remanescentes.
