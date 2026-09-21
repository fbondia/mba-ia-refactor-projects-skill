const express = require('express');

const { loadConfig } = require('./config');
const { AdminController } = require('./controllers/adminController');
const { CheckoutController } = require('./controllers/checkoutController');
const { Database } = require('./infrastructure/database');
const { PaymentGateway } = require('./infrastructure/paymentGateway');
const { errorHandler, notFoundHandler } = require('./middlewares/errorHandler');
const {
    AuditRepository, CourseRepository, EnrollmentRepository,
    PaymentRepository, ReportRepository, UserRepository,
} = require('./models/repositories');
const { buildRoutes } = require('./routes');
const { CheckoutService } = require('./services/checkoutService');

async function createApp(overrides = {}) {
    const config = { ...loadConfig(), ...(overrides.config || {}) };
    const database = overrides.database || new Database(config.databasePath);
    await database.initialize();

    const repositories = {
        courses: new CourseRepository(database),
        users: new UserRepository(database),
        enrollments: new EnrollmentRepository(database),
        payments: new PaymentRepository(database),
        audits: new AuditRepository(database),
        reports: new ReportRepository(database),
    };
    const checkoutService = new CheckoutService(
        database, repositories, overrides.paymentGateway || new PaymentGateway()
    );
    const checkoutController = new CheckoutController(checkoutService);
    const adminController = new AdminController(database, repositories);

    const app = express();
    app.disable('x-powered-by');
    app.use(express.json({ limit: '64kb' }));
    app.use(buildRoutes({ checkoutController, adminController, adminToken: config.adminToken }));
    app.use(notFoundHandler);
    app.use(errorHandler);
    return { app, database, config };
}

module.exports = { createApp };
