function createLmsController(repository) {
    return {
        async checkout(req, res, next) {
            const { usr, eml, pwd, c_id: courseId, card } = req.body || {};
            if (typeof usr !== 'string' || !usr.trim()
                || typeof eml !== 'string' || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(eml)
                || typeof pwd !== 'string' || pwd.length < 1
                || !Number.isInteger(courseId) || courseId < 1
                || typeof card !== 'string' || !/^\d{12,19}$/.test(card)) {
                return res.status(400).send('Bad Request');
            }
            if (!card.startsWith('4')) return res.status(400).send('Pagamento recusado');
            try {
                const result = await repository.createCheckout({
                    name: usr.trim(),
                    email: eml.trim().toLowerCase(),
                    password: pwd,
                    courseId,
                    card,
                });
                return res.status(200).json({ msg: 'Sucesso', enrollment_id: result.enrollmentId });
            } catch (error) {
                if (error.statusCode === 404 || error.statusCode === 409) {
                    return res.status(error.statusCode).send(error.message);
                }
                return next(error);
            }
        },

        async financialReport(_req, res, next) {
            try {
                return res.status(200).json(await repository.getFinancialReport());
            } catch (error) {
                return next(error);
            }
        },

        async deleteUser(req, res, next) {
            try {
                const deleted = await repository.deleteUser(Number(req.params.id));
                if (!deleted) return res.status(404).send('Usuário não encontrado');
                return res.status(200).send('Usuário deletado, matrículas e pagamentos removidos.');
            } catch (error) {
                return next(error);
            }
        },
    };
}

module.exports = createLmsController;
