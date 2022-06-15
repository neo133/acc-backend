import sequelize from '../config/database';
import initModels from '../models/init-models';

const models = initModels(sequelize);

export const fetchPrintingBelt = async () => await models.printing_belt_master.findAll();

export const fetchVehicle = async id =>
  await models.vehicle_master.findAll({
    where: {
      printing_belt_id: id
    }
  });
