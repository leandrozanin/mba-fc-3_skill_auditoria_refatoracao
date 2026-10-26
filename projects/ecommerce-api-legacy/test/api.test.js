const assert = require('node:assert/strict');
const { afterEach, beforeEach, test } = require('node:test');

const { createApp } = require('../src/app');

let app;
let server;
let baseUrl;

beforeEach(async () => {
    app = await createApp({ database: ':memory:' });
    server = app.listen(0, '127.0.0.1');
    await new Promise((resolve) => server.once('listening', resolve));
    baseUrl = `http://127.0.0.1:${server.address().port}`;
});

afterEach(async () => {
    if (server) await new Promise((resolve) => server.close(resolve));
    if (app) await app.locals.repository.close();
});

test('financial report returns the existing response shape', async () => {
    const response = await fetch(`${baseUrl}/api/admin/financial-report`);
    const report = await response.json();

    assert.equal(response.status, 200);
    assert.ok(Array.isArray(report));
    assert.equal(report[0].course, 'Clean Architecture');
    assert.ok(Array.isArray(report[0].students));
});

test('checkout validates input and never reflects card data', async () => {
    const response = await fetch(`${baseUrl}/api/checkout`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ usr: 'Test', eml: 'test@example.com', pwd: 'secret', c_id: 1, card: 4111 }),
    });
    const body = await response.text();

    assert.equal(response.status, 400);
    assert.doesNotMatch(body, /4111|secret/);
});

test('checkout persists a valid enrollment and returns its identifier', async () => {
    const response = await fetch(`${baseUrl}/api/checkout`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
            usr: 'New Student',
            eml: 'new@example.com',
            pwd: 'strong-password',
            c_id: 2,
            card: '4111111111111111',
        }),
    });
    const body = await response.json();

    assert.equal(response.status, 200);
    assert.equal(body.msg, 'Sucesso');
    assert.ok(body.enrollment_id);
});

test('deleting a user removes linked enrollments and payments', async () => {
    await fetch(`${baseUrl}/api/checkout`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
            usr: 'Delete Me', eml: 'delete@example.com', pwd: 'strong-password',
            c_id: 1, card: '4111111111111111',
        }),
    });
    const response = await fetch(`${baseUrl}/api/users/1`, { method: 'DELETE' });
    const body = await response.text();
    const report = await fetch(`${baseUrl}/api/admin/financial-report`).then((result) => result.json());

    assert.equal(response.status, 200);
    assert.match(body, /Usuário deletado/);
    assert.deepEqual(report[0].students, []);
});

