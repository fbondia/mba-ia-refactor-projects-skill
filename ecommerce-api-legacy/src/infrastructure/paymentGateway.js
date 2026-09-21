const { ValidationError } = require('../errors');

class PaymentGateway {
    async authorize(card) {
        const normalized = String(card || '').replace(/\s+/g, '');
        if (!/^\d{12,19}$/.test(normalized)) throw new ValidationError('Cartão inválido');
        return { status: normalized.startsWith('4') ? 'PAID' : 'DENIED' };
    }
}

module.exports = { PaymentGateway };
