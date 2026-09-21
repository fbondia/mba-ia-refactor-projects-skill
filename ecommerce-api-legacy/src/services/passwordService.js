const crypto = require('crypto');

function hashPassword(password) {
    const salt = crypto.randomBytes(16).toString('hex');
    const hash = crypto.scryptSync(password, salt, 64).toString('hex');
    return `scrypt:${salt}:${hash}`;
}

function verifyPassword(password, encoded) {
    const [algorithm, salt, expected] = String(encoded).split(':');
    if (algorithm !== 'scrypt' || !salt || !expected) return false;
    const actual = crypto.scryptSync(password, salt, 64);
    return crypto.timingSafeEqual(actual, Buffer.from(expected, 'hex'));
}

module.exports = { hashPassword, verifyPassword };
