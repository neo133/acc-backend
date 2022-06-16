import { Router } from 'express';

import { authJwt } from '../services/auth';
import {
  getPrintingBelts,
  getVehicles,
  createServiceEntry
} from '../controllers/transaction.controller';

const routes = new Router();

routes.get('/printing-belt', authJwt, getPrintingBelts);
routes.get('/vehicle', authJwt, getVehicles);

routes.post('/service', authJwt, createServiceEntry);

export default routes;
