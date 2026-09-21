const express = require('express');
const { requireAdmin } = require('../middlewares/auth');

function buildRoutes({ checkoutController, adminController, adminToken }) {
    const router = express.Router();
    const admin = requireAdmin(adminToken);
    router.post('/api/checkout', checkoutController.create);
    router.get('/api/admin/financial-report', admin, adminController.financialReport);
    router.delete('/api/users/:id', admin, adminController.deleteUser);
    return router;
}

module.exports = { buildRoutes };
