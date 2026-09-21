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


test('HTTP endpoints preserve checkout and report contracts and enforce admin access', async () => {
    const { app, database } = await createApp();
    const server = app.listen(0, '127.0.0.1');
    try {
        await new Promise((resolve, reject) => {
            server.once('listening', resolve);
            server.once('error', reject);
        });
        const base = `http://127.0.0.1:${server.address().port}`;
        const admin = { Authorization: 'Bearer test-admin-token' };
        const request = (path, options) => fetch(base + path, options);
        for (const [headers, status] of [[{}, 401], [{ Authorization: 'Bearer invalid-token' }, 403]]) {
            assert.equal((await request('/api/admin/financial-report', { headers })).status, status);
            assert.equal((await request('/api/users/1', { method: 'DELETE', headers })).status, status);
        }
        const checkout = await request('/api/checkout', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usr: 'HTTP User', eml: 'http@example.com', pwd: 'strong-pass',
                c_id: 2, card: '4111222233334444' }),
        });
        assert.equal(checkout.status, 200);
        const payload = await checkout.json();
        assert.equal(payload.msg, 'Sucesso');
        assert.ok(Number.isInteger(payload.enrollment_id));
        const report = await request('/api/admin/financial-report', { headers: admin });
        assert.equal(report.status, 200);
        const rows = await report.json();
        assert.deepEqual(rows.find(row => row.course === 'Docker'), {
            course: 'Docker', revenue: 497, students: [{ student: 'HTTP User', paid: 497 }],
        });
        const user = await database.get('SELECT id FROM users WHERE email = ?', ['http@example.com']);
        const deleted = await request(`/api/users/${user.id}`, { method: 'DELETE', headers: admin });
        assert.equal(deleted.status, 200);
        assert.match(await deleted.text(), /Usuário deletado/);
        const missing = await database.get('SELECT id FROM users WHERE id = ?', [user.id]);
        assert.equal(missing, undefined);
        const bad = await request('/api/checkout', {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}',
        });
        assert.equal(bad.status, 400);
    } finally {
        if (server.closeAllConnections) server.closeAllConnections();
        await new Promise(resolve => server.close(resolve));
        await database.close();
    }
});
