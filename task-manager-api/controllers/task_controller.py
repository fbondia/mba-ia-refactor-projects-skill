from services.task_service import TaskService


class TaskController:
    def __init__(self, service=None):
        self.service = service or TaskService()

    def list_all(self): return self.service.list_all(), 200
    def get(self, task_id): return self.service.get(task_id), 200
    def create(self, payload): return self.service.create(payload)
    def update(self, task_id, payload): return self.service.update(task_id, payload)
    def delete(self, task_id): return self.service.delete(task_id), 200
    def search(self, filters): return self.service.search(filters), 200
    def stats(self): return self.service.stats(), 200
