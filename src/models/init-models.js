import { DataTypes } from 'sequelize';
import _user_master from './user_master';
import _rtsp_master from './rtsp_master';
import _packer_master from './packer_master';
import _printing_belt_master from './printing_belt_master';
import _vehicle_master from './vehicle_master';
import _transaction_master from './transaction_master';

function initModels(sequelize) {
  const packer_master = _packer_master(sequelize, DataTypes);
  const printing_belt_master = _printing_belt_master(sequelize, DataTypes);
  const rtsp_master = _rtsp_master(sequelize, DataTypes);
  const user_master = _user_master(sequelize, DataTypes);
  const vehicle_master = _vehicle_master(sequelize, DataTypes);
  const transaction_master = _transaction_master(sequelize, DataTypes);

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

  return {
    packer_master,
    printing_belt_master,
    rtsp_master,
    user_master,
    vehicle_master,
    transaction_master
  };
}
export default initModels;
