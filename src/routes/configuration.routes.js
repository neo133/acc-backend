import { Router } from 'express';

import { authJwt } from '../services/auth';
import {
  createPacker,
  createPrintingBelt,
  createVehicle,
  updatePrintingBelt,
  updateVehicle
} from '../controllers/configuration.controller';

const routes = new Router();

routes.post('/packer', authJwt, createPacker);
routes.post('/printing-belt', authJwt, createPrintingBelt);
routes.post('/vehicle', authJwt, createVehicle);

routes.put('/printing-belt', authJwt, updatePrintingBelt);
routes.put('/vehicle', authJwt, updateVehicle);

export default routes;
