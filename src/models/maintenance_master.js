const Sequelize = require('sequelize');

module.exports = (sequelize, DataTypes) => {
  return sequelize.define(
    'maintenance_master',
    {
      id: {
        autoIncrement: true,
        type: DataTypes.INTEGER,
        allowNull: false,
        primaryKey: true
      },
      printing_belt_id: {
        type: DataTypes.INTEGER,
        allowNull: true,
        references: {
          model: 'printing_belt_master',
          key: 'id'
        }
      },
      loader_belt_id: {
        type: DataTypes.INTEGER,
        allowNull: true,
        references: {
          model: 'vehicle_master',
          key: 'id'
        }
      },
      reason: {
        type: DataTypes.STRING(100),
        allowNull: true
      },
      duration: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: Sequelize.Sequelize.fn('current_timestamp')
      },
      comment: {
        type: DataTypes.STRING(255),
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
      tableName: 'maintenance_master',
      timestamps: false,
      indexes: [
        {
          name: 'PRIMARY',
          unique: true,
          using: 'BTREE',
          fields: [{ name: 'id' }]
        },
        {
          name: 'maintenance_master_FK',
          using: 'BTREE',
          fields: [{ name: 'printing_belt_id' }]
        },
        {
          name: 'maintenance_master_FK_1',
          using: 'BTREE',
          fields: [{ name: 'loader_belt_id' }]
        }
      ]
    }
  );
};
