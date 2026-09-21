from services.task_service import TaskService


class TaskController:
    def __init__(self, service=None):
        self.service = service or TaskService()

    def list_all(self, actor): return self.service.list_all(actor), 200
    def get(self, task_id, actor): return self.service.get(task_id, actor), 200
    def create(self, payload, actor): return self.service.create(payload, actor)
    def update(self, task_id, payload, actor): return self.service.update(task_id, payload, actor)
    def delete(self, task_id, actor): return self.service.delete(task_id, actor), 200
    def search(self, filters, actor): return self.service.search(filters, actor), 200
    def stats(self, actor): return self.service.stats(actor), 200
