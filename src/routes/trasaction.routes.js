import { Router } from 'express';

import { authJwt } from '../services/auth';
import { getPrintingBelts, getVehicles } from '../controllers/transaction.controller';

const routes = new Router();

routes.get('/printing-belt', authJwt, getPrintingBelts);
routes.get('/vehicle', authJwt, getVehicles);

export default routes;
