# Guidelines da arquitetura MVC alvo

MVC aqui descreve responsabilidades e direção de dependências, não nomes rígidos de pastas. Preserve convenções idiomáticas do framework.

## Responsabilidades

### View / Route / Transport

- Declara rota, método, middleware e serialização HTTP.
- Converte request em DTO/comando e resultado em response.
- Não executa SQL nem decide regra de negócio.

### Controller / Use case

- Orquestra um caso de uso e suas dependências.
- Define limites de transação e coordena side effects depois do commit.
- Não depende diretamente de globais ou detalhes do framework quando isso impedir teste isolado.

### Model / Domain / Repository

- Model/domain preserva entidades, estados e invariantes.
- Repository encapsula persistência e queries específicas.
- Serialização pública deve excluir campos sensíveis por padrão.

### Infrastructure / Config

- Cria conexão, cliente de e-mail/pagamento, logger e configuração externa.
- Configuration vem de ambiente/secret store, é validada no boot e não retorna em endpoints.

### Error handling

- Exceções de domínio são traduzidas uma vez para códigos HTTP.
- Erros internos são logados com contexto e retornam mensagem segura.
- Rollback ocorre no limite transacional.

## Direção de dependências

```text
HTTP route/view -> controller/use case -> model/domain + repository interface
composition root -----------------------> concrete infrastructure
```

Evite import inverso de model para rota e acesso direto da rota ao banco. Dependências concretas são montadas no entry point/factory.

## Estruturas aceitáveis

Flask pode usar `app/`, factory, Blueprints, controllers/services, repositories e extensions. Express pode usar routers, controllers, services/use-cases, repositories, middleware e config. Um projeto pequeno pode ter menos arquivos; separação deve acompanhar motivos reais de mudança.

## Compatibilidade

- Preserve paths, métodos, payloads e status existentes, exceto vulnerabilidades explicitamente aprovadas.
- Introduza adapters temporários quando a migração for incremental.
- Não misture refatoração arquitetural com mudanças de produto.
- Use transações nos fluxos multi-write e constraints para integridade.
- Extraia interfaces nas fronteiras variáveis (DB, pagamento, e-mail), não para toda classe.

## Critérios de conclusão

- Rotas são finas e testáveis via client HTTP.
- Casos de uso podem ser testados com dependências falsas.
- SQL/ORM fica fora do transporte e queries repetidas foram agregadas.
- Segredos e configuração não estão hardcoded nem expostos.
- Há entry point/composition root claro e error handling central.
- Baseline de endpoints permanece verde ou mudanças incompatíveis estão documentadas e aprovadas.
