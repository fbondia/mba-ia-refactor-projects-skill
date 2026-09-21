import hmac

from flask import Blueprint, current_app, jsonify, request

from src.controllers.admin_controller import AdminController
from src.controllers.order_controller import OrderController
from src.controllers.product_controller import ProductController
from src.controllers.user_controller import UserController
from src.exceptions import AuthorizationError
from src.infrastructure.database import get_db


api = Blueprint("api", __name__)
products = ProductController()
users = UserController()
orders = OrderController()


def respond(result):
    payload, status = result
    return jsonify(payload), status


def require_admin():
    expected = current_app.config.get("ADMIN_TOKEN")
    supplied = request.headers.get("X-Admin-Token", "")
    if not expected or not hmac.compare_digest(expected, supplied):
        raise AuthorizationError("Operação administrativa não autorizada")


@api.get("/")
def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": "1.0.0",
        "endpoints": {
            "produtos": "/produtos", "usuarios": "/usuarios", "pedidos": "/pedidos",
            "login": "/login", "relatorios": "/relatorios/vendas", "health": "/health",
        },
    })


@api.get("/produtos")
def list_products(): return respond(products.list_all())


@api.get("/produtos/busca")
def search_products(): return respond(products.search(request.args))


@api.get("/produtos/<int:product_id>")
def get_product(product_id): return respond(products.get(product_id))


@api.post("/produtos")
def create_product(): return respond(products.create(request.get_json(silent=True)))


@api.put("/produtos/<int:product_id>")
def update_product(product_id): return respond(products.update(product_id, request.get_json(silent=True)))


@api.delete("/produtos/<int:product_id>")
def delete_product(product_id): return respond(products.delete(product_id))


@api.get("/usuarios")
def list_users(): return respond(users.list_all())


@api.get("/usuarios/<int:user_id>")
def get_user(user_id): return respond(users.get(user_id))


@api.post("/usuarios")
def create_user(): return respond(users.create(request.get_json(silent=True)))


@api.post("/login")
def login(): return respond(users.login(request.get_json(silent=True)))


@api.post("/pedidos")
def create_order(): return respond(orders.create(request.get_json(silent=True)))


@api.get("/pedidos")
def list_orders(): return respond(orders.list_all())


@api.get("/pedidos/usuario/<int:user_id>")
def list_user_orders(user_id): return respond(orders.list_by_user(user_id))


@api.put("/pedidos/<int:order_id>/status")
def update_order(order_id): return respond(orders.update_status(order_id, request.get_json(silent=True)))


@api.get("/relatorios/vendas")
def sales_report(): return respond(orders.sales_report())


@api.get("/health")
def health():
    db = get_db()
    counts = {
        table: db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table in ("produtos", "usuarios", "pedidos")
    }
    return jsonify({
        "status": "ok", "database": "connected", "counts": counts, "versao": "1.0.0"
    })


@api.post("/admin/reset-db")
def reset_database():
    require_admin()
    return respond(AdminController.reset_database())


@api.post("/admin/query")
def disabled_query(): return respond(AdminController.deprecated_query_endpoint())
