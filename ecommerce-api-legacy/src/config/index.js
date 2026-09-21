function loadConfig() {
    const adminToken = process.env.ADMIN_TOKEN;
    if (!adminToken) throw new Error('ADMIN_TOKEN is required');
    return {
        adminToken,
        databasePath: process.env.DATABASE_PATH || ':memory:',
        host: process.env.HOST || '127.0.0.1',
        port: Number(process.env.PORT || 3000),
    };
}

module.exports = { loadConfig };
