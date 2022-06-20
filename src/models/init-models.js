import { DataTypes } from 'sequelize';
import _user_master from './user_master';
import _packer_master from './packer_master';
import _printing_belt_master from './printing_belt_master';
import _vehicle_master from './vehicle_master';
import _transaction_master from './transaction_master';
import _maintenance_master from './maintenance_master';
import _bag_counting_master from './bag_counting_master';
import _tag_counting_master from './tag_counting_master';

function initModels(sequelize) {
  const packer_master = _packer_master(sequelize, DataTypes);
  const printing_belt_master = _printing_belt_master(sequelize, DataTypes);
  const user_master = _user_master(sequelize, DataTypes);
  const vehicle_master = _vehicle_master(sequelize, DataTypes);
  const transaction_master = _transaction_master(sequelize, DataTypes);
  const maintenance_master = _maintenance_master(sequelize, DataTypes);
  const bag_counting_master = _bag_counting_master(sequelize, DataTypes);
  const tag_counting_master = _tag_counting_master(sequelize, DataTypes);

  maintenance_master.belongsTo(printing_belt_master, {
    as: 'printing_belt',
    foreignKey: 'printing_belt_id'
  });
  printing_belt_master.hasMany(maintenance_master, {
    as: 'maintenance_masters',
    foreignKey: 'printing_belt_id'
  });
  maintenance_master.belongsTo(vehicle_master, { as: 'loader_belt', foreignKey: 'loader_belt_id' });
  vehicle_master.hasMany(maintenance_master, {
    as: 'maintenance_masters',
    foreignKey: 'loader_belt_id'
  });
  printing_belt_master.belongsTo(packer_master, { as: 'packer', foreignKey: 'packer_id' });
  packer_master.hasMany(printing_belt_master, {
    as: 'printing_belt_masters',
    foreignKey: 'packer_id'
  });
  vehicle_master.belongsTo(printing_belt_master, {
    as: 'printing_belt',
    foreignKey: 'printing_belt_id'
  });
  printing_belt_master.hasMany(vehicle_master, {
    as: 'vehicle_masters',
    foreignKey: 'printing_belt_id'
  });
  transaction_master.belongsTo(printing_belt_master, {
    as: 'printing_belt',
    foreignKey: 'printing_belt_id'
  });
  printing_belt_master.hasMany(transaction_master, {
    as: 'transaction_masters',
    foreignKey: 'printing_belt_id'
  });
  transaction_master.belongsTo(vehicle_master, { as: 'vehicle', foreignKey: 'vehicle_id' });
  vehicle_master.hasMany(transaction_master, {
    as: 'transaction_masters',
    foreignKey: 'vehicle_id'
  });
  bag_counting_master.belongsTo(transaction_master, {
    as: 'transaction',
    foreignKey: 'transaction_id'
  });
  transaction_master.hasMany(bag_counting_master, {
    as: 'bag_counting_masters',
    foreignKey: 'transaction_id'
  });
  bag_counting_master.belongsTo(vehicle_master, { as: 'vehicle', foreignKey: 'vehicle_id' });
  vehicle_master.hasMany(bag_counting_master, {
    as: 'bag_counting_masters',
    foreignKey: 'vehicle_id'
  });
  tag_counting_master.belongsTo(printing_belt_master, {
    as: 'printing_belt',
    foreignKey: 'printing_belt_id'
  });
  printing_belt_master.hasMany(tag_counting_master, {
    as: 'tag_counting_masters',
    foreignKey: 'printing_belt_id'
  });
  tag_counting_master.belongsTo(transaction_master, {
    as: 'transaction',
    foreignKey: 'transaction_id'
  });
  transaction_master.hasMany(tag_counting_master, {
    as: 'tag_counting_masters',
    foreignKey: 'transaction_id'
  });

  return {
    packer_master,
    printing_belt_master,
    user_master,
    vehicle_master,
    transaction_master,
    maintenance_master,
    bag_counting_master,
    tag_counting_master
  };
}
export default initModels;
