# Playbook de refatoração

Os exemplos mostram a forma da transformação, não código para copiar literalmente. Adapte à stack e preserve contratos.

## 1. SQL concatenado → query parametrizada

Antes:

```python
cursor.execute("SELECT * FROM users WHERE email='" + email + "'")
```

Depois:

```python
cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
```

No ORM, componha expressões do próprio ORM. Use allowlist para nomes de coluna, direção de ordenação e outros trechos que não aceitam bind parameter.

## 2. Segredo hardcoded → configuração validada

Antes:

```javascript
const paymentKey = "pk_live_...";
```

Depois:

```javascript
const paymentKey = process.env.PAYMENT_GATEWAY_KEY;
if (!paymentKey) throw new Error('PAYMENT_GATEWAY_KEY is required');
```

Forneça `.env.example` sem valor real. Rotacione qualquer segredo exposto.

## 3. Hash inseguro → password hasher adaptativo

Antes:

```python
self.password = hashlib.md5(password.encode()).hexdigest()
```

Depois:

```python
from werkzeug.security import generate_password_hash
self.password = generate_password_hash(password)
```

Implemente `check_password_hash` e uma estratégia de migração; nunca serialize o hash.

## 4. Handler gordo → route + controller + repository

Antes:

```javascript
app.post('/checkout', (req, res) => { /* valida, consulta, cobra e grava */ });
```

Depois:

```javascript
router.post('/checkout', validateCheckout, checkoutController.create);
// controller chama checkoutService.execute(command)
// service usa repositories e paymentGateway injetados
```

Extraia por caso de uso, mantendo o router como adapter HTTP.

## 5. Múltiplas escritas → transação atômica

Antes:

```javascript
await enrollments.insert(enrollment);
await payments.insert(payment);
```

Depois:

```javascript
await db.transaction(async (tx) => {
  const enrollment = await enrollments.with(tx).insert(input);
  await payments.with(tx).insert({ enrollmentId: enrollment.id, ...payment });
});
```

Faça integração externa idempotente e defina compensação/outbox quando ela não puder participar da transação.

## 6. N+1 → join/eager loading/agregação

Antes:

```python
for task in Task.query.all():
    owner = User.query.get(task.user_id)
```

Depois:

```python
tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
```

Confirme com contador/log de queries e preserve ordenação/paginação.

## 7. Validação duplicada → schema/DTO único

Antes:

```python
if len(title) < 3: ...
# regra repetida em create e update
```

Depois:

```python
command = TaskInput.from_payload(request.get_json(), partial=is_update)
```

O schema valida tipo, presença, range e formato; regras de domínio continuam no domínio.

## 8. Erros locais → handler central

Antes:

```python
try:
    ...
except:
    return {'error': 'Erro interno'}, 500
```

Depois:

```python
@app.errorhandler(DomainError)
def handle_domain_error(error):
    return {'error': error.message}, error.status_code
```

Capture exceções específicas; faça rollback e log estruturado com stack trace no handler apropriado.

## 9. Estado global → dependência com lifecycle

Antes:

```python
db_connection = sqlite3.connect(path, check_same_thread=False)
```

Depois:

```python
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
    return g.db
```

Registre teardown ou pool idiomático e injete repository/session em testes.

## 10. Operação privilegiada aberta → middleware/policy

Antes:

```javascript
app.delete('/api/users/:id', deleteUser);
```

Depois:

```javascript
router.delete('/users/:id', authenticate, requireRole('admin'), deleteUser);
```

Teste ausência de token, papel incorreto, ownership e caminho autorizado.

## 11. API legacy → equivalente moderno

Antes (SQLAlchemy 2.x):

```python
user = User.query.get(user_id)
```

Depois:

```python
user = db.session.get(User, user_id)
```

Confirme versão e release notes antes de alterar; deprecation sem prova fica no relatório como `needs verification`.

## Ordem segura sugerida

1. Capture baseline e smoke tests.
2. Remova exposição e introduza configuração externa.
3. Parametrize queries e proteja rotas.
4. Garanta transações/integridade.
5. Extraia repositories e casos de uso mantendo adapters compatíveis.
6. Centralize validação e erros.
7. Elimine N+1 e APIs deprecated.
8. Execute testes, boot, endpoint matrix e nova auditoria.
