const { NotFoundError, ValidationError } = require('../errors');
const { hashPassword } = require('./passwordService');

class CheckoutService {
    constructor(database, repositories, paymentGateway) {
        this.database = database;
        this.repositories = repositories;
        this.paymentGateway = paymentGateway;
    }

    async execute(input) {
        const command = this.validate(input);
        const course = await this.repositories.courses.findActiveById(command.courseId);
        if (!course) throw new NotFoundError('Curso não encontrado');

        const authorization = await this.paymentGateway.authorize(command.card);
        if (authorization.status !== 'PAID') throw new ValidationError('Pagamento recusado');

        return this.database.transaction(async () => {
            let user = await this.repositories.users.findByEmail(command.email);
            let userId = user && user.id;
            if (!userId) {
                userId = await this.repositories.users.create({
                    name: command.name,
                    email: command.email,
                    passwordHash: hashPassword(command.password),
                });
            }
            const enrollmentId = await this.repositories.enrollments.create(userId, course.id);
            await this.repositories.payments.create(enrollmentId, course.price, authorization.status);
            await this.repositories.audits.create(`Checkout course ${course.id} by user ${userId}`);
            return { msg: 'Sucesso', enrollment_id: enrollmentId };
        });
    }

    validate(input) {
        if (!input || typeof input !== 'object') throw new ValidationError('Bad Request');
        const command = {
            name: String(input.usr || '').trim(),
            email: String(input.eml || '').trim().toLowerCase(),
            password: String(input.pwd || ''),
            courseId: Number(input.c_id),
            card: input.card,
        };
        if (!command.name || !command.email || !command.password || !command.courseId || !command.card) {
            throw new ValidationError('Bad Request');
        }
        if (command.password.length < 8) throw new ValidationError('Senha deve ter no mínimo 8 caracteres');
        return command;
    }
}

module.exports = { CheckoutService };
