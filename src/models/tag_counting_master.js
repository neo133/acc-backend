const Sequelize = require('sequelize');

module.exports = (sequelize, DataTypes) => {
  return sequelize.define(
    'tag_counting_master',
    {
      id: {
        autoIncrement: true,
        type: DataTypes.INTEGER,
        allowNull: false,
        primaryKey: true
      },
      printing_belt_id: {
        type: DataTypes.INTEGER,
        allowNull: false,
        references: {
          model: 'printing_belt_master',
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
      is_labled: {
        type: DataTypes.TINYINT,
        allowNull: false,
        defaultValue: 1
      },
      local_image_location: {
        type: DataTypes.STRING(300),
        allowNull: true
      },
      api_status: {
        type: DataTypes.INTEGER,
        allowNull: true
      },
      s3_image_location: {
        type: DataTypes.STRING(300),
        allowNull: true
      },
      created_at: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: Sequelize.Sequelize.fn('current_timestamp')
      },
      is_false_alert: {
        type: DataTypes.TINYINT,
        allowNull: false,
        defaultValue: 0
      }
    },
    {
      sequelize,
      tableName: 'tag_counting_master',
      timestamps: false,
      indexes: [
        {
          name: 'PRIMARY',
          unique: true,
          using: 'BTREE',
          fields: [{ name: 'id' }]
        },
        {
          name: 'tag_counting_master_FK',
          using: 'BTREE',
          fields: [{ name: 'printing_belt_id' }]
        },
        {
          name: 'tag_counting_master_FK_1',
          using: 'BTREE',
          fields: [{ name: 'transaction_id' }]
        }
      ]
    }
  );
};
