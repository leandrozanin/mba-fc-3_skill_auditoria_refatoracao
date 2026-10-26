module.exports = {
    port: Number.parseInt(process.env.PORT || '3000', 10),
    host: process.env.HOST || '127.0.0.1',
};
