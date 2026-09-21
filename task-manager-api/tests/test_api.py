import os
import tempfile
import unittest

os.environ.setdefault("SECRET_KEY", "test-secret-not-for-production")

from application import create_app
from database import db
from models.category import Category
from models.user import User


class TaskManagerApiTest(unittest.TestCase):
    def setUp(self):
        handle, self.database = tempfile.mkstemp(suffix=".db")
        os.close(handle)
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-secret-not-for-production",
                "SQLALCHEMY_DATABASE_URI": f"sqlite:///{self.database}",
            }
        )
        self.client = self.app.test_client()
        with self.app.app_context():
            admin = User(name="Admin", email="admin@example.com", role="admin")
            admin.set_password("strong-admin-pass")
            db.session.add(admin)
            db.session.add(Category(name="Backend", color="#112233"))
            db.session.commit()
        login = self.client.post(
            "/login", json={"email": "admin@example.com", "password": "strong-admin-pass"}
        )
        self.headers = {"Authorization": f"Bearer {login.get_json()['token']}"}

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
        os.unlink(self.database)

    def test_public_endpoints_and_authentication(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/health").status_code, 200)
        self.assertEqual(self.client.get("/tasks").status_code, 401)
        response = self.client.post(
            "/users", json={"name": "User", "email": "user@example.com", "password": "strong-user-pass"}
        )
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("password", response.get_json())

    def test_user_can_update_and_delete_self(self):
        created = self.client.post(
            "/users", json={"name": "Self", "email": "self@example.com", "password": "strong-self-pass"}
        )
        user_id = created.get_json()["id"]
        login = self.client.post(
            "/login", json={"email": "self@example.com", "password": "strong-self-pass"}
        )
        headers = {"Authorization": f"Bearer {login.get_json()['token']}"}
        self.assertEqual(self.client.put(
            f"/users/{user_id}", headers=headers, json={"name": "Self Updated"}
        ).status_code, 200)
        self.assertEqual(self.client.delete(
            f"/users/{user_id}", headers=headers
        ).status_code, 200)

    def test_original_endpoint_matrix_and_task_crud(self):
        created = self.client.post(
            "/tasks",
            headers=self.headers,
            json={"title": "Refatorar API", "priority": 1, "user_id": 1, "category_id": 1},
        )
        self.assertEqual(created.status_code, 201)
        task_id = created.get_json()["id"]
        paths = [
            "/tasks", f"/tasks/{task_id}", "/tasks/search?q=Refatorar", "/tasks/stats",
            "/users", "/users/1", "/users/1/tasks", "/reports/summary",
            "/reports/user/1", "/categories",
        ]
        for path in paths:
            self.assertEqual(self.client.get(path, headers=self.headers).status_code, 200, path)
        self.assertEqual(self.client.put(
            f"/tasks/{task_id}", headers=self.headers, json={"status": "done"}
        ).status_code, 200)
        self.assertEqual(self.client.delete(f"/tasks/{task_id}", headers=self.headers).status_code, 200)

    def test_category_admin_crud_and_signed_token(self):
        created = self.client.post(
            "/categories", headers=self.headers,
            json={"name": "Security", "description": "Security work", "color": "#abcdef"},
        )
        self.assertEqual(created.status_code, 201)
        category_id = created.get_json()["id"]
        self.assertEqual(self.client.put(
            f"/categories/{category_id}", headers=self.headers, json={"color": "#fedcba"}
        ).status_code, 200)
        self.assertEqual(self.client.delete(
            f"/categories/{category_id}", headers=self.headers
        ).status_code, 200)
        self.assertEqual(self.client.get(
            "/tasks", headers={"Authorization": "Bearer forged-token"}
        ).status_code, 401)

    def test_task_ownership_and_admin_access(self):
        created_user = self.client.post('/users', json={
            'name': 'Other', 'email': 'other@example.com', 'password': 'strong-other-pass',
        }).get_json()
        token = self.client.post('/login', json={
            'email': 'other@example.com', 'password': 'strong-other-pass',
        }).get_json()['token']
        headers = {'Authorization': f'Bearer {token}'}
        admin_task = self.client.post('/tasks', headers=self.headers, json={
            'title': 'Admin private task', 'user_id': 1,
        }).get_json()['id']
        own = self.client.post('/tasks', headers=headers, json={'title': 'Own task'})
        self.assertEqual(own.status_code, 201)
        own_id = own.get_json()['id']
        self.assertEqual(own.get_json()['user_id'], created_user['id'])
        for response in (
            self.client.get(f'/tasks/{admin_task}', headers=headers),
            self.client.put(f'/tasks/{admin_task}', headers=headers, json={'status': 'done'}),
            self.client.delete(f'/tasks/{admin_task}', headers=headers),
            self.client.post('/tasks', headers=headers, json={'title': 'Invalid owner', 'user_id': 1}),
            self.client.put(f'/tasks/{own_id}', headers=headers, json={'user_id': 1}),
            self.client.put(f'/tasks/{own_id}', headers=headers, json={'user_id': None}),
        ):
            self.assertEqual(response.status_code, 403)
        for path in ('/tasks', '/tasks/search?q=task'):
            response = self.client.get(path, headers=headers)
            self.assertEqual([task['id'] for task in response.get_json()], [own_id])
        self.assertEqual(self.client.get('/tasks/stats', headers=headers).get_json()['total'], 1)
        self.assertEqual(self.client.get(f'/tasks/{own_id}', headers=headers).status_code, 200)
        self.assertEqual(self.client.put(f'/tasks/{own_id}', headers=headers,
                                         json={'status': 'done'}).status_code, 200)
        self.assertEqual(self.client.get(f'/tasks/{admin_task}', headers=self.headers).status_code, 200)
        self.assertEqual(self.client.put(f'/tasks/{own_id}', headers=self.headers,
                                         json={'title': 'Admin edited'}).status_code, 200)
        self.assertEqual(self.client.delete(f'/tasks/{own_id}', headers=headers).status_code, 200)
        self.assertEqual(self.client.delete(f'/tasks/{admin_task}', headers=self.headers).status_code, 200)

    def test_user_and_report_access_policy(self):
        user = self.client.post('/users', json={
            'name': 'Reader', 'email': 'reader@example.com', 'password': 'strong-reader-pass',
        }).get_json()
        token = self.client.post('/login', json={
            'email': 'reader@example.com', 'password': 'strong-reader-pass',
        }).get_json()['token']
        headers = {'Authorization': f'Bearer {token}'}
        for path in ('/users', '/users/1', '/users/1/tasks', '/reports/user/1', '/reports/summary'):
            self.assertEqual(self.client.get(path, headers=headers).status_code, 403, path)
        for path in (f"/users/{user['id']}", f"/users/{user['id']}/tasks", f"/reports/user/{user['id']}"):
            self.assertEqual(self.client.get(path, headers=headers).status_code, 200, path)
        self.assertEqual(self.client.post('/categories', headers=headers,
                                         json={'name': 'Forbidden'}).status_code, 403)

    def test_overdue_report_preserves_original_contract(self):
        from datetime import datetime, timedelta, timezone
        due = (datetime.now(timezone.utc) - timedelta(days=3)).strftime('%Y-%m-%d')
        created = self.client.post('/tasks', headers=self.headers, json={
            'title': 'Overdue task', 'user_id': 1, 'due_date': due,
        }).get_json()
        report = self.client.get('/reports/summary', headers=self.headers)
        self.assertEqual(report.status_code, 200)
        overdue = report.get_json()['overdue']
        self.assertEqual(overdue['count'], 1)
        self.assertEqual(overdue['tasks'], [{
            'id': created['id'], 'title': 'Overdue task',
            'due_date': due + ' 00:00:00', 'days_overdue': 3,
        }])


if __name__ == "__main__":
    unittest.main()
