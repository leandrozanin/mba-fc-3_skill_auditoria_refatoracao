const express = require('express');
const settings = require('./config/settings');
const errorHandler = require('./middlewares/errorHandler');
const LmsRepository = require('./models/lmsRepository');
const createRoutes = require('./views/routes');

async function createApp(options = {}) {
    const repository = new LmsRepository(options.database || ':memory:');
    await repository.initialize();

    const app = express();
    app.locals.repository = repository;
    app.use(express.json({ limit: '32kb' }));
    app.use('/api', createRoutes(repository));
    app.use(errorHandler);
    return app;
}

async function startServer() {
    const app = await createApp({ database: process.env.DATABASE_PATH || ':memory:' });
    return app.listen(settings.port, settings.host, () => {
        console.log(`LMS API listening at http://${settings.host}:${settings.port}`);
    });
}

if (require.main === module) {
    startServer().catch(() => {
        console.error('Application startup failed');
        process.exitCode = 1;
    });
}

module.exports = { createApp, startServer };
