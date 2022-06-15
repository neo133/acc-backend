import fs from 'fs';
import passport from 'passport';
import LocalStrategy from 'passport-local';
import { Strategy as JWTStrategy, ExtractJwt } from 'passport-jwt';
import { getUser, updatePassword } from '../sequelizeQueries/auth.queries';
import { sendHttpResponse } from '../utils/createReponse';
/**
 * Local Strategy Auth
 */
const localOpts = { usernameField: 'email' };
const publicKey = fs.readFileSync('./public.key', 'utf8');

// local authentication middleware for login takes email and password as parameters and checks if user exists in db or not if exists then sends the user object
const localAuthentication = new LocalStrategy(localOpts, async (email, password, done) => {
  try {
    const user = await getUser({ email });
    if (!user) {
      // user does not exist
      return done({ message: 'Please signup to continue' }, false);
    }
    if (!user.authenticateUser(password)) {
      // authentication failed, password does not matched
      return done({ message: 'Password Does Not Match' }, false);
    }
    return done(null, user);
  } catch (e) {
    return done(e, false);
  }
});

const jwtOptions = {
  jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
  secretOrKey: publicKey,
  issuer: 'Frinks',
  algorithm: ['RS256']
};

// jwt strategy to check if user exists in database through user_id passed as parameter
const jwtAuthentication = new JWTStrategy(jwtOptions, async (payload, done) => {
  try {
    const user = await getUser({ id: parseInt(payload.aud, 10) });
    if (!user) {
      return done(null, false);
    }
    return done(null, user);
  } catch (e) {
    return done(e, false);
  }
});

passport.use(localAuthentication);
passport.use(jwtAuthentication);

// passport local authentication middleware for login
export const authLocal = (req, res, next) => {
  passport.authenticate('local', { session: false }, (err, user) => {
    if (err) {
      return sendHttpResponse(res, err.message, {}, 400, false);
    }
    return req.login(user, error => {
      if (error) {
        return sendHttpResponse(res, 'Failed to login, try again', {}, 500, false);
      }
      return next(null, user);
    });
  })(req, res, next);
};

export const authJwt = (req, res, next) => {
  passport.authenticate('jwt', { session: false }, async (err, user) => {
    if (err) {
      return sendHttpResponse(res, 'Failed to login, try again', {}, 500, false);
    }
    if (!user) {
      return sendHttpResponse(res, 'Please signUp to move forward', {}, 401, false);
    }
    req.user = user;
    return next();
  })(req, res, next);
};

// function checks if the user already exists in databse or not
// used before login to find user by providing email or phone
export const checkUser = async (req, res) => {
  try {
    const user = await getUser({ email: req.body.email });
    if (!user) {
      return sendHttpResponse(res, 'Please signup to continue', {}, 400, false);
    }
    return sendHttpResponse(res, 'Success', {}, 200, true);
  } catch (err) {
    return sendHttpResponse(res, err.message, {}, 500, false);
  }
};

export const authorize = (roles = []) => {
  if (typeof roles === 'string') {
    roles = [roles];
  }
  return [
    // authorize based on user role
    (req, res, next) => {
      if (roles.length && !roles.includes(req.user.role)) {
        // user's role is not authorized
        return sendHttpResponse(res, 'You are not authorized to use this resource', {}, 401, false);
      }

      // authentication and authorization successful
      return next();
    }
  ];
};

export const passwordReset = async (req, res) => {
  try {
    const { email, new_password } = req.body;
    const [updateRes] = await updatePassword(email, { password: new_password });
    if (updateRes > 0) {
      return sendHttpResponse(res, 'Password reset successfully', {});
    }
    return sendHttpResponse(res, 'Could not reset password', {}, 500, false);
  } catch (err) {
    return sendHttpResponse(res, err.message, {}, 500, false);
  }
};
