module.exports = (sequelize, DataTypes) => {
  return sequelize.define(
    'packer_master',
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
        unique: 'packer_master_UN1'
      },
      packer_type: {
        type: DataTypes.TINYINT,
        allowNull: false,
        defaultValue: 0
      }
    },
    {
      sequelize,
      tableName: 'packer_master',
      timestamps: false,
      indexes: [
        {
          name: 'PRIMARY',
          unique: true,
          using: 'BTREE',
          fields: [{ name: 'id' }]
        },
        {
          name: 'packer_master_UN1',
          unique: true,
          using: 'BTREE',
          fields: [{ name: 'machine_id' }]
        }
      ]
    }
  );
};
