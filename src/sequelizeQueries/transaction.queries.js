import sequelize from '../config/database';
import initModels from '../models/init-models';

const models = initModels(sequelize);

export const fetchPrintingBelt = async () => await models.printing_belt_master.findAll();

export const fetchVehicle = async () => await models.vehicle_master.findAll();

export const createService = async data => await models.transaction_master.create(data);
