require('dotenv').config();

const config = {
  PORT: process.env.PORT || 9000,
  REDIS_ENDPOINT: process.env.REDIS_ENDPOINT,
  REDIS_PORT: process.env.REDIS_PORT,
  REDIS_PASSWORD: process.env.REDIS_PASSWORD,
  REDIS_EXPIRY: process.env.REDIS_EXPIRY,
  MONGODB_PASSWORD: process.env.MONGODB_PASSWORD,
  MONGODB_USER: process.env.MONGODB_USER
};
export default config;
