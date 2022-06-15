import { Router } from 'express';
import HTTPStatus from 'http-status';

import APIError from '../services/error';
import logErrorService from '../services/log';

import UserRoutes from './user.routes';
import ConfigurationRoutes from './configuration.routes';
import TransactionRoutes from './trasaction.routes';

const routes = new Router();

routes.use('/users', UserRoutes);
routes.use('/configuration', ConfigurationRoutes);
routes.use('/transaction', TransactionRoutes);

routes.all('*', (req, res, next) =>
  next(new APIError('Route Not Found!', HTTPStatus.NOT_FOUND, true))
);

routes.use(logErrorService);

export default routes;
