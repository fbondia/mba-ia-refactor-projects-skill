class CourseRepository {
    constructor(database) { this.database = database; }
    findActiveById(id) {
        return this.database.get('SELECT id, title, price FROM courses WHERE id = ? AND active = 1', [id]);
    }
}

class UserRepository {
    constructor(database) { this.database = database; }
    findByEmail(email) {
        return this.database.get('SELECT id, name, email, password_hash FROM users WHERE email = ?', [email]);
    }
    async create({ name, email, passwordHash }) {
        const result = await this.database.run(
            'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
            [name, email, passwordHash]
        );
        return result.lastID;
    }
    async delete(id) {
        return this.database.run('DELETE FROM users WHERE id = ?', [id]);
    }
}

class EnrollmentRepository {
    constructor(database) { this.database = database; }
    async create(userId, courseId) {
        const result = await this.database.run(
            'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [userId, courseId]
        );
        return result.lastID;
    }
}

class PaymentRepository {
    constructor(database) { this.database = database; }
    create(enrollmentId, amount, status) {
        return this.database.run(
            'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
            [enrollmentId, amount, status]
        );
    }
}

class AuditRepository {
    constructor(database) { this.database = database; }
    create(action) {
        return this.database.run(
            "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))", [action]
        );
    }
}

class ReportRepository {
    constructor(database) { this.database = database; }
    financialRows() {
        return this.database.all(`
            SELECT c.id AS course_id, c.title AS course, u.name AS student,
                   p.amount, p.status
            FROM courses c
            LEFT JOIN enrollments e ON e.course_id = c.id
            LEFT JOIN users u ON u.id = e.user_id
            LEFT JOIN payments p ON p.enrollment_id = e.id
            ORDER BY c.id, e.id
        `);
    }
}

module.exports = {
    AuditRepository, CourseRepository, EnrollmentRepository,
    PaymentRepository, ReportRepository, UserRepository,
};
