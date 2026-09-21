class AdminController {
    constructor(database, repositories) {
        this.database = database;
        this.repositories = repositories;
    }

    financialReport = async (_request, response, next) => {
        try {
            const rows = await this.repositories.reports.financialRows();
            const courses = new Map();
            for (const row of rows) {
                const course = courses.get(row.course_id) || {
                    course: row.course, revenue: 0, students: [],
                };
                if (row.student) {
                    if (row.status === 'PAID') course.revenue += row.amount;
                    course.students.push({ student: row.student, paid: row.amount || 0 });
                }
                courses.set(row.course_id, course);
            }
            response.json([...courses.values()]);
        } catch (error) { next(error); }
    };

    deleteUser = async (request, response, next) => {
        try {
            const result = await this.database.transaction(
                () => this.repositories.users.delete(Number(request.params.id))
            );
            if (result.changes === 0) return response.status(404).send('Usuário não encontrado');
            return response.send('Usuário deletado com dados relacionados removidos.');
        } catch (error) { return next(error); }
    };
}

module.exports = { AdminController };
