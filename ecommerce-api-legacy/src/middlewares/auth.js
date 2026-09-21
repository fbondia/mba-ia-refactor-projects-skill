const crypto = require('crypto');
const { AuthenticationError, AuthorizationError } = require('../errors');

function requireAdmin(expectedToken) {
    return (request, _response, next) => {
        const header = request.get('authorization') || '';
        const supplied = header.startsWith('Bearer ') ? header.slice(7) : '';
        if (!supplied) return next(new AuthenticationError('Autenticação obrigatória'));
        const expected = Buffer.from(expectedToken);
        const actual = Buffer.from(supplied);
        if (expected.length !== actual.length || !crypto.timingSafeEqual(expected, actual)) {
            return next(new AuthorizationError('Acesso administrativo negado'));
        }
        return next();
    };
}

module.exports = { requireAdmin };
