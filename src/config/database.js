/* eslint-disable no-console */
const { Sequelize } = require('sequelize');
const constants = require('./constants');

const sequelize = new Sequelize(
  `mysql://${constants.default.DB_USER}:${constants.default.DB_PASSWORD}@${constants.default.DB_DOMAIN}:${constants.default.DB_PORT}/${constants.default.DB_NAME}`
);
sequelize
  .authenticate()
  .then(() => {
    console.log('Connection has been established successfully.');
  })
  .catch(err => {
    console.error('Unable to connect to the database:', err);
  });

module.exports = sequelize;
