import { sendHttpResponse } from '../utils/createReponse';
import {
  createService,
  fetchPrintingBelt,
  fetchVehicle
} from '../sequelizeQueries/transaction.queries';
import io from '../index';

export const getPrintingBelts = async (req, res) => {
  try {
    const printingBelt = await fetchPrintingBelt();
    return sendHttpResponse(res, 'Success', printingBelt);
  } catch (err) {
    console.error('err --- user.controller --- getPrintingBelts:', err.message);
    return sendHttpResponse(res, err.message, {}, 500, false);
  }
};

export const getVehicles = async (req, res) => {
  try {
    const vehicleRes = await fetchVehicle();
    return sendHttpResponse(res, 'Success', vehicleRes);
  } catch (err) {
    console.error('err --- user.controller --- getVehicles:', err.message);
    return sendHttpResponse(res, err.message, {}, 500, false);
  }
};

export const createServiceEntry = async (req, res) => {
  try {
    const { printingId, loaderId, licenceNumber, bagType, bagCount } = req.body;
    const serviceRes = await createService({
      printing_belt_id: printingId,
      vehicle_id: loaderId,
      licence_number: licenceNumber,
      bag_type: bagType,
      bag_count: bagCount
    });
    // emit socket to python code with transaction id
    const { id, printing_belt_id, vehicle_id, bag_count } = serviceRes;
    io.emit('service_initiate', {
      transaction_id: id,
      belt_id: printing_belt_id,
      bag_count,
      vehicle_id
    });
    return sendHttpResponse(res, 'Success', serviceRes);
  } catch (err) {
    console.error('err --- user.controller --- createServiceEntry:', err.message);
    return sendHttpResponse(res, err.message, {}, 500, false);
  }
};
