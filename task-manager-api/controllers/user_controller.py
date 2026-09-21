from services.user_service import UserService


class UserController:
    def __init__(self, service=None):
        self.service = service or UserService()

    def list_all(self): return self.service.list_all(), 200
    def get(self, user_id, actor): return self.service.get(user_id, actor), 200
    def create(self, payload): return self.service.create(payload), 201
    def update(self, user_id, payload, actor): return self.service.update(user_id, payload, actor), 200
    def delete(self, user_id, actor): return self.service.delete(user_id, actor), 200
    def login(self, payload): return self.service.login(payload), 200
