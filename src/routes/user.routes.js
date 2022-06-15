import { Router } from 'express';
import { validate } from 'express-validation';
import * as ROLES from '../utils/roles';

import * as UserController from '../controllers/user.controller';
import * as AuthenticationController from '../controllers/authentication.controller';

import { authLocal, authJwt, authorize, passwordReset } from '../services/auth';

const routes = new Router();

routes.post(
  '/login',
  validate(AuthenticationController.validation.login, { keyByField: true }, { abortEarly: false }),
  authLocal,
  UserController.login
);

routes.put('/password-reset', authJwt, authorize([ROLES.Admin]), passwordReset);

routes.get('/check/auth', authJwt, UserController.me);

routes.post('/logout', authJwt, UserController.logout);

export default routes;
