import sequelize from '../config/database';
import initModels from '../models/init-models';

const models = initModels(sequelize);

export const getUser = async obj =>
  await models.user_master.findOne({
    where: {
      ...obj
    }
  });

export const updatePassword = async (email, obj) =>
  await models.user_master.update(obj, { where: { email } });
