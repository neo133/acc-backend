const Sequelize = require('sequelize');

module.exports = (sequelize, DataTypes) => {
  return sequelize.define(
    'bag_counting_master',
    {
      id: {
        autoIncrement: true,
        type: DataTypes.INTEGER,
        allowNull: false,
        primaryKey: true
      },
      vehicle_id: {
        type: DataTypes.INTEGER,
        allowNull: false,
        references: {
          model: 'vehicle_master',
          key: 'id'
        }
      },
      transaction_id: {
        type: DataTypes.INTEGER,
        allowNull: false,
        references: {
          model: 'transaction_master',
          key: 'id'
        }
      },
      api_status: {
        type: DataTypes.INTEGER,
        allowNull: true
      },
      created_at: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: Sequelize.Sequelize.fn('current_timestamp')
      }
    },
    {
      sequelize,
      tableName: 'bag_counting_master',
      timestamps: false,
      indexes: [
        {
          name: 'PRIMARY',
          unique: true,
          using: 'BTREE',
          fields: [{ name: 'id' }]
        },
        {
          name: 'bag_counting_master_FK',
          using: 'BTREE',
          fields: [{ name: 'vehicle_id' }]
        },
        {
          name: 'bag_counting_master_FK_1',
          using: 'BTREE',
          fields: [{ name: 'transaction_id' }]
        }
      ]
    }
  );
};
