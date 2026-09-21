# Evidências de validação

Execute da raiz, com as dependências já instaladas nas `.venv` e em `node_modules`:

```bash
python3 validation/revalidate.py --node /caminho/para/node
```

O Node informado deve atender `>=18 <23`; os logs atuais usam 18.20.8. O script falha se um teste/check falhar, usa bancos temporários ou em memória e encerra todos os processos de boot. É necessário permitir conexões localhost para os testes HTTP.

- `project-1-tests.log`: 4 testes Flask, runtime e compilação.
- `project-2-tests.log`: 4 testes Node, incluindo HTTP real, runtime e sintaxe.
- `project-3-tests.log`: 7 testes Flask, incluindo ownership e contrato de relatório; warnings de depreciação tratados como erro.
- `boot-smoke.log`: boot real das três aplicações e uma requisição HTTP de sucesso por aplicação. A matriz de endpoints está nos testes.
- `skill-validation.log`: validação estrutural e comparação das quatro cópias; não comprova execução comportamental da skill.
- `source-inventory.md`: inventário reconstruído do commit original, incluindo arquivos vazios. Não é log da execução inicial da Fase 1.

A transcrição da invocação inicial da skill e da confirmação humana não foi preservada. Essa limitação permanece explícita no README e nos relatórios. A autorização desta rodada foi a mensagem “Aplique as correções e ajustes necessários”; não é substituta retroativa da aprovação histórica.

Os comandos usam somente segredos fictícios de teste. As saídas identificam runtime, data e commit-base; as correções podem estar na working tree quando a validação é executada.
