class ApplicationError extends Error {
    constructor(message, statusCode = 400) {
        super(message);
        this.statusCode = statusCode;
    }
}

class ValidationError extends ApplicationError {}
class AuthenticationError extends ApplicationError {
    constructor(message) { super(message, 401); }
}
class AuthorizationError extends ApplicationError {
    constructor(message) { super(message, 403); }
}
class NotFoundError extends ApplicationError {
    constructor(message) { super(message, 404); }
}

module.exports = {
    ApplicationError, ValidationError, AuthenticationError, AuthorizationError, NotFoundError,
};
