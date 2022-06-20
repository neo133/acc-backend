import { Router } from 'express';

import {
  getPrintingBelts,
  getVehicles,
  createServiceEntry,
  getBeltIds,
  createMaintenanceEntry,
  createBagEntry,
  createTagEntry,
  getActiveTransaction,
  changeBagCount,
  stopBelt,
  getMissingLabels
} from '../controllers/transaction.controller';

const routes = new Router();

routes.get('/printing-belt', getPrintingBelts);
routes.get('/vehicle', getVehicles);
routes.get('/beltIds', getBeltIds);
routes.get('/', getActiveTransaction);
routes.get('/missing-labels', getMissingLabels);

routes.post('/service', createServiceEntry);
routes.post('/maintenance', createMaintenanceEntry);
routes.post('/bag-entry', createBagEntry);
routes.post('/tag-entry', createTagEntry);
routes.post('/bag-change', changeBagCount);
routes.post('/belt-stop', stopBelt);

export default routes;
