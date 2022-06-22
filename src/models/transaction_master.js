const Sequelize = require('sequelize');

module.exports = (sequelize, DataTypes) => {
  return sequelize.define(
    'transaction_master',
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
      vehicle_id: {
        type: DataTypes.INTEGER,
        allowNull: true,
        references: {
          model: 'vehicle_master',
          key: 'id'
        }
      },
      licence_number: {
        type: DataTypes.STRING(100),
        allowNull: true
      },
      bag_type: {
        type: DataTypes.STRING(100),
        allowNull: true
      },
      bag_count: {
        type: DataTypes.INTEGER,
        allowNull: true
      },
      is_active: {
        type: DataTypes.TINYINT,
        allowNull: true,
        defaultValue: 1
      },
      created_at: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: Sequelize.Sequelize.fn('current_timestamp')
      },
      stopped_at: {
        type: DataTypes.DATE,
        allowNull: true
      },
      is_listed: {
        type: DataTypes.TINYINT,
        allowNull: false,
        defaultValue: 1
      },
      count_finished_at: {
        type: DataTypes.DATE,
        allowNull: true
      }
    },
    {
      sequelize,
      tableName: 'transaction_master',
      timestamps: false,
      indexes: [
        {
          name: 'PRIMARY',
          unique: true,
          using: 'BTREE',
          fields: [{ name: 'id' }]
        },
        {
          name: 'transaction_master_FK',
          using: 'BTREE',
          fields: [{ name: 'printing_belt_id' }]
        },
        {
          name: 'transaction_master_FK_1',
          using: 'BTREE',
          fields: [{ name: 'vehicle_id' }]
        }
      ]
    }
  );
};
