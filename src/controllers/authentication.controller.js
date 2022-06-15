/* eslint-disable prettier/prettier */
import { Joi } from 'express-validation';

export const validation = {
  login: {
    body: Joi.object({
      email: Joi.string().email().required().messages({
        'string.empty': 'Email is required!',
        'string.email': 'Please provide a valid email!',
      }),
      password: Joi.string().required().messages({
        'string.empty': 'Password is required!',
      }),
    }),
  },
};
