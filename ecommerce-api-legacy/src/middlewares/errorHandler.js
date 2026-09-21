const { ApplicationError } = require('../errors');

function notFoundHandler(_request, response) {
    response.status(404).json({ error: 'Endpoint não encontrado' });
}

function errorHandler(error, _request, response, _next) {
    if (error instanceof ApplicationError) {
        return response.status(error.statusCode).json({ error: error.message });
    }
    console.error('Unhandled request error', error.message);
    return response.status(500).json({ error: 'Erro interno' });
}

module.exports = { errorHandler, notFoundHandler };
