const express = require('express');
const createLmsController = require('../controllers/lmsController');

function createRoutes(repository) {
    const router = express.Router();
    const controller = createLmsController(repository);
    router.post('/checkout', controller.checkout);
    router.get('/admin/financial-report', controller.financialReport);
    router.delete('/users/:id', controller.deleteUser);
    return router;
}

module.exports = createRoutes;
