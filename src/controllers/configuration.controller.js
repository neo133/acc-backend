import { sendHttpResponse } from '../utils/createReponse';
import {
  insertPacker,
  insertPrintingBelt,
  insertVehicle,
  updatePrintingData,
  updateVehicleData
} from '../sequelizeQueries/configuration.queries';

import { Vehicle } from '../utils/globalConstants';

export const createPacker = async (req, res) => {
  try {
    const { machine_id, packer_type } = req.body;
    const packerRes = await insertPacker(machine_id, packer_type);
    if (packerRes) {
      return sendHttpResponse(res, 'Success', {});
    }
    return sendHttpResponse(res, 'Failed to create, please retry', {});
  } catch (err) {
    console.error('err --- configuration.controller --- createPacker:', err.message);
    return sendHttpResponse(res, err.message, {}, 500, false);
  }
};

export const createPrintingBelt = async (req, res) => {
  try {
    const { machine_id } = req.body;
    const printingRes = await insertPrintingBelt(machine_id);
    if (printingRes) {
      return sendHttpResponse(res, 'Success', {});
    }
    return sendHttpResponse(res, 'Failed to create, please retry', {});
  } catch (err) {
    console.error('err --- configuration.controller --- createPrintingBelt:', err.message);
    return sendHttpResponse(res, err.message, {}, 500, false);
  }
};

export const createVehicle = async (req, res) => {
  try {
    const { machine_id, container, vehicle_type } = req.body;
    let vehicleRes;
    if (vehicle_type === Vehicle.truck) {
      // if vehicle is of type truck then skip inserting containers
      vehicleRes = await insertVehicle(machine_id, vehicle_type);
    } else {
      // insert container number
      vehicleRes = await insertVehicle(machine_id, vehicle_type, container);
    }
    if (vehicleRes) {
      return sendHttpResponse(res, 'Success', {});
    }
    return sendHttpResponse(res, 'Failed to create, please retry', {});
  } catch (err) {
    console.error('err --- configuration.controller --- createVehicle:', err.message);
    return sendHttpResponse(res, err.message, {}, 500, false);
  }
};

export const updatePrintingBelt = async (req, res) => {
  try {
    const { packer_id, id } = req.body;
    const [updateRes] = await updatePrintingData(packer_id, id);
    if (updateRes > 0) {
      return sendHttpResponse(res, 'Success', {});
    }
    return sendHttpResponse(res, 'Failed to update, please retry', {});
  } catch (err) {
    console.error('err --- configuration.controller --- updatePrintingBelt:', err.message);
    return sendHttpResponse(res, err.message, {}, 500, false);
  }
};

export const updateVehicle = async (req, res) => {
  try {
    const { printing_belt_id, id } = req.body;
    const [updateRes] = await updateVehicleData(printing_belt_id, id);
    if (updateRes > 0) {
      return sendHttpResponse(res, 'Success', {});
    }
    return sendHttpResponse(res, 'Failed to update, please retry', {});
  } catch (err) {
    console.error('err --- configuration.controller --- updateVehicle:', err.message);
    return sendHttpResponse(res, err.message, {}, 500, false);
  }
};
