function errorHandler(error, _req, res, _next) {
    if (error.type === 'entity.parse.failed') {
        return res.status(400).send('Bad Request');
    }
    if (error.status === 413) {
        return res.status(413).send('Payload Too Large');
    }
    return res.status(500).send('Erro interno');
}

module.exports = errorHandler;
