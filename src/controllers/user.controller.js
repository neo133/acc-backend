import { Joi } from 'express-validation';
import { sendHttpResponse } from '../utils/createReponse';
import { io } from '../index';

export const validation = {
  create: {
    body: Joi.object({
      first_name: Joi.string().min(3).max(20).required().messages({
        'string.empty': 'First name is required!'
      }),
      last_name: Joi.string().min(3).max(20).required().messages({
        'string.empty': 'Last name is required!'
      }),
      email: Joi.string().email().required().messages({
        'string.empty': 'Email is required!',
        'string.email': 'Please provide a valid email!'
      }),
      password: Joi.string().required().messages({
        'string.empty': 'Password is required!'
      }),
      phone_number: Joi.string().min(10).max(10).required().messages({
        'string.empty': 'Phone number is required!',
        'string.phone_number': 'Phone number length should be 10'
      })
    })
  }
};

export const me = async (req, res) => {
  try {
    if (req.user === null) {
      return sendHttpResponse(res, 'Please signup to continue', {}, 204, false);
    }
    const { id, first_name, last_name, email, phone_number, role } = req.user;
    io.sockets.emit('service_initiate', {
      data: {
        name: 'apple'
      }
    });
    io.emit('service_initiate', {
      data: {
        name: 'io'
      }
    });
    return sendHttpResponse(res, 'Success', {
      id,
      first_name,
      last_name,
      email,
      phone_number,
      role
    });
  } catch (err) {
    console.error('err --- user.controller --- me:', err.message);
    return sendHttpResponse(res, err.message, {}, 500, false);
  }
};

export const login = async (req, res) => {
  const { id, first_name, last_name, email, phone_number, role } = req.user.dataValues;
  const token = req.user.toAuthJSON();
  res.setHeader('Authorization', token);
  sendHttpResponse(res, 'Success', {
    id,
    first_name,
    last_name,
    email,
    phone_number,
    role
  });
};

export const deleteToken = async (req, res) => {
  try {
    res.removeHeader('Authorization');
    req.logout();
  } catch (err) {
    console.error('err --- jwt.js ---  deleteToken:', err.message);
  }
};

export const logout = async (req, res) => {
  await deleteToken(req, res);
  return sendHttpResponse(res, 'Logout successfull', {}, 200, true);
};
