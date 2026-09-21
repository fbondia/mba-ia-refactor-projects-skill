class CheckoutController {
    constructor(service) { this.service = service; }
    create = async (request, response, next) => {
        try {
            response.status(200).json(await this.service.execute(request.body));
        } catch (error) { next(error); }
    };
}

module.exports = { CheckoutController };
