from services.report_service import CategoryService, ReportService


class ReportController:
    def summary(self): return ReportService.summary(), 200
    def user(self, user_id, actor): return ReportService.user_report(user_id, actor), 200


class CategoryController:
    def list_all(self): return CategoryService.list_all(), 200
    def create(self, payload): return CategoryService.create(payload), 201
    def update(self, category_id, payload): return CategoryService.update(category_id, payload), 200
    def delete(self, category_id): return CategoryService.delete(category_id), 200
