# Template do relatório de auditoria

Use este formato sem omitir seções. Substitua placeholders por dados comprovados.

```markdown
# Architecture Audit Report

- **Project:** `<nome>`
- **Audit date:** `<YYYY-MM-DD>`
- **Stack:** `<linguagem + framework + persistência>`
- **Scope:** `<arquivos/diretórios>`
- **Analyzed:** `<N arquivos | N linhas>`
- **Baseline:** `<test/boot/smoke commands ou not configured>`

## Summary

| Severity | Count |
|---|---:|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 0 |
| LOW | 0 |
| **Total** | **0** |

## Findings

### [CRITICAL] AP-00 — Título objetivo

- **Location:** `path/file.ext:10-24`
- **Evidence:** descrição factual e curta do trecho observado
- **Impact:** consequência técnica ou de negócio
- **Recommendation:** ação verificável, adequada à stack
- **Acceptance criteria:** condição observável para considerar resolvido
- **Status:** `OPEN`

<!-- repetir em ordem CRITICAL → HIGH → MEDIUM → LOW -->

## Deprecated API Review

| API | Location | Version evidence | Modern equivalent | Status |
|---|---|---|---|---|
| `<api ou none found>` | `<path:line>` | `<manifest/docs/needs verification>` | `<equivalente>` | `<OPEN/N/A>` |

## Refactoring Plan

1. `<mudança pequena, findings cobertos, risco e validação>`

## Validation Baseline

| Check | Command/request | Result before refactor |
|---|---|---|
| Syntax/import | `<command>` | `<PASS/FAIL/NOT RUN + detalhe>` |
| Tests | `<command>` | `<PASS/FAIL/NOT CONFIGURED>` |
| Boot | `<command>` | `<PASS/FAIL/NOT RUN>` |
| Endpoints | `<requests>` | `<resultado>` |

## Risks and Unverified Items

- `<limitação, possível falso positivo ou dependência externa>`

## Approval Gate

No source files were modified during phases 1–2.

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Após a fase 3, acrescente `## Refactoring Result`, a nova estrutura, os comandos/resultados completos e atualize o status dos findings sem apagar a evidência original.
