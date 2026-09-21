const { createApp } = require('./compositionRoot');

async function start() {
    const { app, database, config } = await createApp();
    const server = app.listen(config.port, config.host, () => {
        console.log(`LMS API listening on http://${config.host}:${config.port}`);
    });

    const shutdown = () => server.close(() => database.close().finally(() => process.exit(0)));
    process.once('SIGINT', shutdown);
    process.once('SIGTERM', shutdown);
    return { server, database };
}

if (require.main === module) {
    start().catch((error) => {
        console.error('Failed to start LMS API', error.message);
        process.exit(1);
    });
}

module.exports = { start };
