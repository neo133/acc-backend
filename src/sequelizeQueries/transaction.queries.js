import Sequelize, { Op } from 'sequelize';
import sequelize from '../config/database';
import initModels from '../models/init-models';

const models = initModels(sequelize);

export const fetchPrintingBelt = async () =>
  await models.printing_belt_master.findAll({
    order: [['id', 'ASC']]
  });

export const fetchVehicle = async id =>
  await models.vehicle_master.findAll({
    where: {
      printing_belt_id: id
    },
    order: [['id', 'ASC']]
  });

export const createService = async data => await models.transaction_master.create(data);

export const fetchBeltsIds = async type => {
  if (type === 0) {
    return await models.printing_belt_master.findAll();
  }
  return await models.vehicle_master.findAll();
};

export const insertMaintenaceEntry = async data => await models.maintenance_master.create(data);

export const insertBagEntry = async data => await models.bag_counting_master.create(data);

export const insertTagEntry = async data => await models.tag_counting_master.create(data);

export const fetchUsedPrintingBeltIds = async () =>
  await models.transaction_master.findAll({
    attributes: [[Sequelize.fn('DISTINCT', Sequelize.col('printing_belt_id')), 'printing_belt_id']],
    where: {
      is_active: 1
    },
    order: [['printing_belt_id', 'ASC']]
  });

export const fetchUsedVehicleBeltIds = async () =>
  await models.transaction_master.findAll({
    attributes: [[Sequelize.fn('DISTINCT', Sequelize.col('vehicle_id')), 'vehicle_id']],
    where: {
      is_active: 1
    },
    order: [['vehicle_id', 'ASC']]
  });

export const fetchActiveBagTransaction = async () =>
  await models.transaction_master.findAll({
    where: {
      is_active: 1
    },
    include: [
      {
        model: models.bag_counting_master,
        as: 'bag_counting_masters',
        attributes: ['id']
      },
      {
        model: models.vehicle_master,
        as: 'vehicle',
        attributes: ['machine_id', 'container', 'vehicle_type']
      }
    ]
  });

export const fetchActiveTagTransaction = async () =>
  await models.transaction_master.findAll({
    where: {
      is_active: 1
    },
    include: [
      {
        model: models.tag_counting_master,
        as: 'tag_counting_masters',
        attributes: ['is_labled', 'local_image_location', 'created_at'],
        group: ['is_labled']
      },
      {
        model: models.printing_belt_master,
        as: 'printing_belt',
        attributes: ['machine_id']
      }
    ]
  });

export const modifyBagCount = async (id, bag_count) =>
  await models.transaction_master.update(
    {
      bag_count
    },
    {
      where: {
        id
      }
    }
  );

export const getTransaction = async id => await models.transaction_master.findByPk(id);

export const stopTransactionLocal = async id =>
  await models.transaction_master.update(
    {
      is_active: 0,
      stopped_at: new Date()
    },
    {
      where: {
        id
      }
    }
  );

export const getServiceDetails = async id =>
  await models.transaction_master.findOne({
    where: {
      id
    },
    include: [
      {
        model: models.vehicle_master,
        as: 'vehicle',
        attributes: ['machine_id', 'container', 'vehicle_type']
      },
      {
        model: models.printing_belt_master,
        as: 'printing_belt',
        attributes: ['machine_id']
      }
    ]
  });

const TODAY_START = new Date().setHours(0, 0, 0, 0);
const NOW = new Date();

export const fetchMissingLabels = async () =>
  await models.tag_counting_master.findAll({
    attributes: ['transaction_id', 'local_image_location', 'created_at', 'id'],
    where: {
      created_at: {
        [Op.gt]: TODAY_START,
        [Op.lt]: NOW
      },
      is_labled: 0
    }
  });
