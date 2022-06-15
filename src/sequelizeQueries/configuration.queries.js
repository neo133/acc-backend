import sequelize from '../config/database';
import initModels from '../models/init-models';

const models = initModels(sequelize);

export const insertPacker = async (machine_id, packer_type) =>
  await models.packer_master.create({
    machine_id,
    packer_type
  });

export const insertPrintingBelt = async machine_id =>
  await models.printing_belt_master.create({
    machine_id
  });

export const insertVehicle = async (machine_id, vehicle_type, container = null) =>
  await models.vehicle_master.create({
    machine_id,
    vehicle_type,
    container
  });

export const updatePrintingData = async (packer_id, id) =>
  await models.printing_belt_master.update(
    {
      packer_id
    },
    {
      where: {
        id
      }
    }
  );

export const updateVehicleData = async (printing_belt_id, id) =>
  await models.vehicle_master.update(
    {
      printing_belt_id
    },
    {
      where: {
        id
      }
    }
  );
