import fs from 'fs';
import jwt from 'jsonwebtoken';
import Sequelize from 'sequelize';
import bcrypt from 'bcrypt-nodejs';
import constants from '../config/constants';

const privateKey = fs.readFileSync('./private.key', 'utf8');

const user = (sequelize, DataTypes) => {
  const UserSchema = sequelize.define(
    'user_master',
    {
      id: {
        autoIncrement: true,
        type: DataTypes.INTEGER,
        allowNull: false,
        primaryKey: true
      },
      first_name: {
        type: DataTypes.STRING(100),
        allowNull: false
      },
      last_name: {
        type: DataTypes.STRING(100),
        allowNull: false
      },
      email: {
        type: DataTypes.STRING(100),
        allowNull: false,
        unique: 'user_master_UN1'
      },
      phone_number: {
        type: DataTypes.STRING(10),
        allowNull: false,
        unique: 'user_master_UN2'
      },
      password: {
        type: DataTypes.STRING(100),
        allowNull: true,
        set(value) {
          this.setDataValue('password', bcrypt.hashSync(value));
        }
      },
      role: {
        type: DataTypes.STRING(10),
        allowNull: false,
        defaultValue: 'user'
      },
      created_at: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: Sequelize.Sequelize.fn('current_timestamp')
      },
      updated_at: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: Sequelize.Sequelize.fn('current_timestamp')
      }
    },
    {
      sequelize,
      tableName: 'user_master',
      timestamps: false,
      indexes: [
        {
          name: 'PRIMARY',
          unique: true,
          using: 'BTREE',
          fields: [{ name: 'id' }]
        },
        {
          name: 'email',
          unique: true,
          using: 'BTREE',
          fields: [{ name: 'email' }]
        },
        {
          name: 'phone_number',
          unique: true,
          using: 'BTREE',
          fields: [{ name: 'phone_number' }]
        }
      ]
    }
  );

  // eslint-disable-next-line func-names
  UserSchema.prototype.authenticateUser = function (password) {
    return bcrypt.compareSync(password, this.password);
  };

  // eslint-disable-next-line func-names
  UserSchema.prototype.createToken = function () {
    return jwt.sign(
      {
        email: this.email,
        phone_number: this.phone_number
      },
      privateKey,
      {
        issuer: 'Frinks',
        audience: `${this.id}`,
        expiresIn: constants.JWT_EXPIRATION,
        algorithm: 'RS256'
      }
    );
  };
  // eslint-disable-next-line func-names
  UserSchema.prototype.toAuthJSON = function () {
    return `Bearer ${this.createToken()}`;
  };
  return UserSchema;
};

export default user;
