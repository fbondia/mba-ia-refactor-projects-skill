# Catálogo de anti-patterns

A severidade abaixo é o padrão. Ajuste-a conforme alcance, exposição e controles compensatórios, explicando o ajuste. Todo finding exige evidência com linhas exatas.

## CRITICAL

### AP-01 — Injeção em comandos ou queries

Sinais: concatenação/interpolação de input em SQL, shell, template ou path; endpoint que executa comando/query fornecido pelo cliente. Diferencie construção de cláusulas parametrizadas de concatenação insegura. Recomende parâmetros, allowlist e remoção de endpoints arbitrários.

### AP-02 — Segredos ou dados sensíveis expostos

Sinais: chaves, senhas ou tokens reais no código, logs ou respostas; PAN/cartão completo em logs; serialização de hash de senha. Não reporte valores de exemplo inequivocamente fictícios sem risco de reutilização. Recomende secret manager/ambiente, rotação e redaction.

### AP-03 — Credenciais armazenadas com algoritmo inseguro

Sinais: plaintext, MD5/SHA sem salt, Base64 ou algoritmo caseiro. Recomende função adaptativa apropriada à stack (Argon2id, scrypt, bcrypt ou helper seguro do framework) e migração progressiva.

## HIGH

### AP-04 — God Class / God Module

Sinais combinados: HTTP, acesso a dados, regras, integrações e configuração no mesmo módulo; muitos motivos de mudança; métodos extensos e acoplados. Tamanho isolado não basta. Separe por responsabilidade e caso de uso.

### AP-05 — Autorização ausente em operação privilegiada

Sinais: rotas admin, destrutivas, financeiras ou de dados pessoais sem autenticação e checagem de papel/ownership. Diferencie autenticação de autorização. Prefira deny-by-default e middleware/policy central.

### AP-06 — Transação ou integridade quebrada

Sinais: múltiplas escritas dependentes sem transação/rollback; delete deixando órfãos; estoque e pedido atualizados parcialmente; side effect irreversível antes do commit. Recomende transação, constraints e idempotência.

### AP-07 — Regra de negócio presa na rota/controller

Sinais: handlers decidem preço, status, elegibilidade, cálculo, notificações ou persistência detalhada. A rota deve adaptar HTTP; o controller/use case deve orquestrar; model/domain deve manter invariantes.

## MEDIUM

### AP-08 — N+1 queries

Sinais: consulta dentro de loop sobre resultados ou lazy loading repetido durante serialização. Confirme o número potencial de queries. Recomende join/eager load, agregação ou batch lookup.

### AP-09 — Validação inconsistente ou duplicada

Sinais: create/update com regras divergentes; validação copiada; input sem tipo/range/formato; `request.get_json()` presumido como objeto. Centralize schema/DTO e mantenha mensagens/contratos.

### AP-10 — Estado global mutável ou ciclo de vida inadequado

Sinais: conexão/cache/lista mutável compartilhada sem sincronização, teardown ou escopo de request. Avalie concorrência e testes. Injete recursos e use lifecycle do framework.

### AP-11 — API deprecated/legacy

Sinais: aviso oficial, documentação da versão ou runtime warning. Exemplos a confirmar pela versão: `Query.get()` no SQLAlchemy 2.x em vez de `Session.get()`, APIs de data UTC naïve quando a stack recomenda timestamps timezone-aware. Registre versão, fonte ou `needs verification`, impacto e equivalente moderno.

### AP-12 — Tratamento de erro inadequado

Sinais: `except:` vazio/amplo, erro ignorado em callback, detalhes internos retornados ao cliente, respostas inconsistentes, ausência de rollback. Recomende error middleware/handler central e logs estruturados.

## LOW

### AP-13 — Nomes opacos ou inconsistentes

Sinais: `u`, `e`, `p`, siglas não locais, mistura de convenções que dificulta entender o domínio. Não sinalize variáveis curtas convencionais de loops sem perda real de clareza.

### AP-14 — Magic numbers/strings e regras duplicadas

Sinais: status, limites, percentuais, portas ou mensagens repetidos e semanticamente relevantes. Extraia constantes/enums/config quando houver benefício de manutenção.

### AP-15 — Código morto, imports e exports não usados

Sinais: import/export sem referência, parâmetros ignorados, helpers duplicados, branches inalcançáveis. Confirme por busca antes de reportar.

### AP-16 — Logging ad hoc

Sinais: `print`/`console.log` em fluxo de produção, ausência de nível/contexto/correlation id, concatenação de dados pessoais. Dados sensíveis elevam para AP-02.

## Regras de classificação

- Um sintoma não deve gerar findings duplicados em categorias diferentes; escolha a causa principal e cite impactos relacionados.
- Agrupe ocorrências homogêneas, mas mantenha todas as localizações relevantes.
- Segurança explorável, perda de dados e quebra ampla de separação podem elevar severidade.
- Código de exemplo, seed ou teste pode reduzir severidade, salvo se executado no runtime ou incentivar segredo reutilizável.
