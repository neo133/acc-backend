module.exports = (sequelize, DataTypes) => {
  return sequelize.define(
    'vehicle_master',
    {
      id: {
        autoIncrement: true,
        type: DataTypes.INTEGER,
        allowNull: false,
        primaryKey: true
      },
      machine_id: {
        type: DataTypes.STRING(10),
        allowNull: false,
        unique: 'vehicle_master_UN1'
      },
      vehicle_type: {
        type: DataTypes.TINYINT,
        allowNull: false,
        defaultValue: 0
      },
      container: {
        type: DataTypes.INTEGER,
        allowNull: true
      },
      printing_belt_id: {
        type: DataTypes.INTEGER,
        allowNull: true,
        references: {
          model: 'printing_belt_master',
          key: 'id'
        }
      },
      is_active: {
        type: DataTypes.TINYINT,
        allowNull: true,
        defaultValue: 1
      }
    },
    {
      sequelize,
      tableName: 'vehicle_master',
      timestamps: false,
      indexes: [
        {
          name: 'PRIMARY',
          unique: true,
          using: 'BTREE',
          fields: [{ name: 'id' }]
        },
        {
          name: 'vehicle_master_UN1',
          unique: true,
          using: 'BTREE',
          fields: [{ name: 'machine_id' }]
        },
        {
          name: 'vehicle_master_FK',
          using: 'BTREE',
          fields: [{ name: 'printing_belt_id' }]
        }
      ]
    }
  );
};
