import { sendHttpResponse } from '../utils/createReponse';
import { fetchPrintingBelt, fetchVehicle } from '../sequelizeQueries/transaction.queries';

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
    const vehicleRes = await fetchVehicle(req.body.id);
    return sendHttpResponse(res, 'Success', vehicleRes);
  } catch (err) {
    console.error('err --- user.controller --- getVehicles:', err.message);
    return sendHttpResponse(res, err.message, {}, 500, false);
  }
};
