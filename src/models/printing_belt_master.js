module.exports = (sequelize, DataTypes) => {
  return sequelize.define(
    'printing_belt_master',
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
        unique: 'printing_belt_master_UN1'
      },
      packer_id: {
        type: DataTypes.INTEGER,
        allowNull: true,
        references: {
          model: 'packer_master',
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
      tableName: 'printing_belt_master',
      timestamps: false,
      indexes: [
        {
          name: 'PRIMARY',
          unique: true,
          using: 'BTREE',
          fields: [{ name: 'id' }]
        },
        {
          name: 'printing_belt_master_UN1',
          unique: true,
          using: 'BTREE',
          fields: [{ name: 'machine_id' }]
        },
        {
          name: 'printing_belt_master_FK',
          using: 'BTREE',
          fields: [{ name: 'packer_id' }]
        }
      ]
    }
  );
};
