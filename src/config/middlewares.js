import express from 'express';
import morgan from 'morgan';
import compression from 'compression';
import passport from 'passport';
import expressWinston from 'express-winston';
import methodOverride from 'method-override';
import helmet from 'helmet';
import cors from 'cors';
import cookieParser from 'cookie-parser';
import winstonInstance from './winston';
import constants from './constants';

export default app => {
  app.use(compression());
  app.use(express.json());
  app.use(helmet());
  app.use(cors());
  app.use(cookieParser());
  app.use(passport.initialize());
  app.use(passport.session());
  app.use(methodOverride());
  passport.serializeUser((user, cb) => {
    cb(null, user);
  });
  passport.deserializeUser((obj, cb) => {
    cb(null, obj);
  });
  // eslint-disable-next-line no-unused-expressions
  if (constants.isDev) {
    app.use(morgan('dev'));
    expressWinston.requestWhitelist.push('body');
    expressWinston.responseWhitelist.push('body');
    app.use(
      expressWinston.logger({
        winstonInstance,
        meta: true,
        msg: 'HTTP {{req.method}} {{req.url}} {{res.statusCode}} {{res.responseTime}}ms',
        colorStatus: true
      })
    );
  }
};
