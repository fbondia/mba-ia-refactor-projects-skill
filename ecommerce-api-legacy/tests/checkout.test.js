const test = require('node:test');
const assert = require('node:assert/strict');

process.env.ADMIN_TOKEN = 'test-admin-token';

const { createApp } = require('../src/compositionRoot');

test('checkout commits enrollment, payment and audit atomically', async () => {
    const { database } = await createApp();
    try {
        const { CheckoutService } = require('../src/services/checkoutService');
        const {
            AuditRepository, CourseRepository, EnrollmentRepository,
            PaymentRepository, UserRepository,
        } = require('../src/models/repositories');
        const service = new CheckoutService(
            database,
            {
                courses: new CourseRepository(database), users: new UserRepository(database),
                enrollments: new EnrollmentRepository(database), payments: new PaymentRepository(database),
                audits: new AuditRepository(database),
            },
            { authorize: async () => ({ status: 'PAID' }) }
        );
        const result = await service.execute({
            usr: 'Test User', eml: 'test@example.com', pwd: 'strong-pass', c_id: 2,
            card: '4111222233334444',
        });
        assert.ok(result.enrollment_id);
        const payment = await database.get(
            'SELECT status FROM payments WHERE enrollment_id = ?', [result.enrollment_id]
        );
        assert.equal(payment.status, 'PAID');
    } finally { await database.close(); }
});

test('checkout rolls back all writes after a transactional failure', async () => {
    const { database } = await createApp();
    try {
        const before = await database.get('SELECT COUNT(*) AS count FROM enrollments');
        await assert.rejects(
            database.transaction(async () => {
                await database.run('INSERT INTO enrollments (user_id, course_id) VALUES (1, 2)');
                throw new Error('injected failure');
            }),
            /injected failure/
        );
        const after = await database.get('SELECT COUNT(*) AS count FROM enrollments');
        assert.equal(after.count, before.count);
    } finally { await database.close(); }
});

test('database cascades enrollment and payment deletion with a user', async () => {
    const { database } = await createApp();
    try {
        await database.transaction(() => database.run('DELETE FROM users WHERE id = 1'));
        const enrollments = await database.get('SELECT COUNT(*) AS count FROM enrollments WHERE user_id = 1');
        const payments = await database.get('SELECT COUNT(*) AS count FROM payments');
        assert.equal(enrollments.count, 0);
        assert.equal(payments.count, 0);
    } finally { await database.close(); }
});
