import fs from 'fs';
import AWS from 'aws-sdk';
import { sendHttpResponse } from '../utils/createReponse';
import {
  createService,
  fetchActiveBagTransaction,
  fetchActiveTagTransaction,
  fetchBeltsIds,
  fetchPrintingBelt,
  fetchUsedPrintingBeltIds,
  fetchUsedVehicleBeltIds,
  fetchVehicle,
  insertBagEntry,
  insertMaintenaceEntry,
  insertTagEntry,
  modifyBagCount,
  getTransaction,
  stopTransactionLocal,
  getServiceDetails,
  fetchMissingLabels
} from '../sequelizeQueries/transaction.queries';
import constants from '../config/constants';
import { io } from '../index';

const s3 = new AWS.S3({
  accessKeyId: constants.accessKeyId,
  secretAccessKey: constants.secretAccessKey
});

export const getPrintingBelts = async (req, res) => {
  try {
    const [printingBelt, usedPrintingBeltIds] = await Promise.all([
      fetchPrintingBelt(),
      fetchUsedPrintingBeltIds()
    ]);
    const allBelts = printingBelt.map(e => {
      return {
        id: e.id,
        machine_id: e.machine_id
      };
    });
    const usedBelts = new Set(usedPrintingBeltIds.map(e => e.printing_belt_id));
    const resArr = allBelts.filter(e => {
      // return those elements not in the namesToDeleteSet
      return !usedBelts.has(e.id);
    });
    return sendHttpResponse(res, 'Success', resArr);
  } catch (err) {
    console.error('err --- user.controller --- getPrintingBelts:', err.message);
    return sendHttpResponse(res, err.message, {}, 500, false);
  }
};

export const getVehicles = async (req, res) => {
  try {
    const [vehicleBelt, usedVehicleBeltIds] = await Promise.all([
      fetchVehicle(req.query.id),
      fetchUsedVehicleBeltIds()
    ]);
    const allBelts = vehicleBelt.map(e => {
      return {
        id: e.id,
        machine_id: e.machine_id,
        is_active: e.is_active
      };
    });
    const usedBelts = new Set(usedVehicleBeltIds.map(e => e.printing_belt_id));
    const resArr = allBelts.filter(e => {
      // return those elements not in the namesToDeleteSet
      return !usedBelts.has(e.id);
    });
    return sendHttpResponse(res, 'Success', resArr);
  } catch (err) {
    console.error('err --- user.controller --- getVehicles:', err.message);
    return sendHttpResponse(res, err.message, {}, 500, false);
  }
};

export const createServiceEntry = async (req, res) => {
  try {
    const { printingId, loaderId, licenceNumber, bagType, bagCount } = req.body;
    const [serviceRes] = await Promise.all([
      createService({
        printing_belt_id: printingId,
        vehicle_id: loaderId,
        licence_number: licenceNumber,
        bag_type: bagType,
        bag_count: bagCount
      })
    ]);
    const serviceDetails = await getServiceDetails(serviceRes.id);
    const resData = {
      id: serviceDetails.id,
      bag_count: 0,
      bag_belt_id: serviceDetails?.vehicle_id,
      limit: serviceDetails?.bag_count,
      bag_type: serviceDetails?.bag_type,
      created_at: serviceDetails?.created_at,
      stopped_at: null,
      tag_count: 0,
      printing_belt_id: serviceDetails?.printing_belt_id,
      missed_labels: 0,
      missed_data: [],
      tag_machine_id: serviceDetails?.printing_belt?.machine_id,
      bag_machine_id: serviceDetails?.vehicle?.machine_id,
      container_count: serviceDetails?.vehicle?.container,
      vehicle_type: serviceDetails?.vehicle?.vehicle_type
    };
    // emit socket to python code with transaction id
    const { id, printing_belt_id, vehicle_id, bag_count } = serviceRes;
    io.sockets.emit('service', {
      transaction_id: id,
      printing_belt_id,
      bag_count_limit: bag_count,
      bag_counting_belt_id: vehicle_id
    });
    return sendHttpResponse(res, 'Success', resData);
  } catch (err) {
    console.error('err --- user.controller --- createServiceEntry:', err.message);
    return sendHttpResponse(res, err.message, {}, 500, false);
  }
};

export const getBeltIds = async (req, res) => {
  try {
    const beltRes = await fetchBeltsIds(parseInt(req.query.type, 10));
    return sendHttpResponse(res, 'Success', beltRes);
  } catch (err) {
    console.error('err --- user.controller --- getBeltIds:', err.message);
    return sendHttpResponse(res, err.message, {}, 500, false);
  }
};

export const createMaintenanceEntry = async (req, res) => {
  try {
    const { machine_type, belt_id, reason, comments, down_till } = req.body;
    const insertionData = {
      reason,
      comment: comments,
      duration: down_till
    };
    if (machine_type === 0) {
      insertionData.printing_belt_id = belt_id;
    } else {
      insertionData.loader_belt_id = belt_id;
    }
    const beltRes = await insertMaintenaceEntry(insertionData);
    return sendHttpResponse(res, 'Success', beltRes);
  } catch (err) {
    console.error('err --- user.controller --- createMaintenanceEntry:', err.message);
    return sendHttpResponse(res, err.message, {}, 500, false);
  }
};

export const createBagEntry = async data => {
  try {
    const { belt_id, transaction_id } = data;
    insertBagEntry({
      vehicle_id: parseInt(belt_id, 10),
      transaction_id: parseInt(transaction_id, 10)
    });
    // send data to AWS server
  } catch (err) {
    console.error('err --- user.controller --- createBagEntry:', err.message);
  }
};

export const createTagEntry = async data => {
  try {
    const { belt_id, transaction_id, is_labeled, image_location } = data;
    if (!is_labeled) {
      // upload image to s3 and save link generated
      const localImagePath = `${constants.BASE_PATH}/${belt_id}/${image_location}`;
      fs.readFile(localImagePath, (e, obj) => {
        if (e) throw e;
        const params = {
          Key: image_location,
          Body: JSON.stringify(obj, null, 2),
          Bucket: `acc-defects/${belt_id}`,
          ContentEncoding: 'base64',
          ACL: 'public-read'
        };
        s3.upload(params, (s3Err, info) => {
          if (s3Err) throw s3Err;
          console.log(`File uploaded successfully at ${info.Location}`);
          insertTagEntry({
            printing_belt_id: parseInt(belt_id, 10),
            transaction_id: parseInt(transaction_id, 10),
            is_labeled: 1,
            local_image_location: localImagePath,
            s3_image_location: info.Location
          });
        });
      });
    } else {
      insertTagEntry({
        printing_belt_id: parseInt(belt_id, 10),
        transaction_id: parseInt(transaction_id, 10),
        is_labeled: 1
      });
    }
    // send data to AWS server
  } catch (err) {
    console.error('err --- user.controller --- createTagEntry:', err.message);
  }
};

const getMissedLabels = data => {
  let missingCount = 0;
  data.forEach(e => {
    if (e?.dataValues?.is_labled === 0) {
      missingCount++;
    }
  });
  return missingCount;
};

const getMissedLabelsPaths = data => {
  const missedData = [];
  data.forEach(e => {
    if (e?.dataValues?.is_labled === 0) {
      missedData.push({
        image: e?.dataValues?.local_image_location,
        created_at: e?.dataValues?.created_at
      });
    }
  });
  return missedData;
};

export const getActiveTransaction = async (req, res) => {
  try {
    const [bagTransactionRes, tagTransactionRes] = await Promise.all([
      fetchActiveBagTransaction(),
      fetchActiveTagTransaction()
    ]);
    const transactionRes = {};
    bagTransactionRes?.forEach(e => {
      if (e?.id) {
        transactionRes[e?.id] = {
          bag_count: e?.bag_counting_masters?.length,
          bag_belt_id: e?.vehicle_id,
          limit: e?.bag_count,
          bag_type: e?.bag_type,
          created_at: e?.created_at,
          bag_machine_id: e?.vehicle?.machine_id,
          vehicle_type: e?.vehicle?.vehicle_type,
          container_count: e?.vehicle?.container,
          stopped_at: e?.stopped_at,
          count_fininshed_at: e?.count_fininshed_at,
          is_listed: e?.is_listed,
          is_active: e?.is_active,
          ...transactionRes[e?.id]
        };
      }
    });
    tagTransactionRes.forEach(e => {
      if (e?.id) {
        transactionRes[e?.id] = {
          tag_count: e?.tag_counting_masters?.length,
          printing_belt_id: e?.printing_belt_id,
          limit: e?.bag_count,
          bag_type: e?.bag_type,
          created_at: e?.created_at,
          missed_labels: getMissedLabels(e?.tag_counting_masters),
          missed_data: getMissedLabelsPaths(e?.tag_counting_masters),
          tag_machine_id: e?.printing_belt?.machine_id,
          stopped_at: e?.stopped_at,
          count_fininshed_at: e?.count_fininshed_at,
          is_listed: e?.is_listed,
          is_active: e?.is_active,
          ...transactionRes[e?.id]
        };
      }
    });
    return sendHttpResponse(res, 'Success', transactionRes);
  } catch (err) {
    console.error('err --- user.controller --- getActiveTransaction:', err.message);
    return sendHttpResponse(res, err.message, {}, 500, false);
  }
};

export const changeBagCount = async (req, res) => {
  try {
    const { transaction_id, new_bag_count } = req.body;
    await Promise.all([modifyBagCount(transaction_id, new_bag_count)]);
    io.sockets.emit('update', {
      transaction_id,
      new_limit: new_bag_count
    });
    sendHttpResponse(res, 'Success', {});
  } catch (err) {
    console.error('err --- user.controller --- changeBagCount:', err.message);
  }
};

export const stopBelt = async (req, res) => {
  try {
    const { transaction_id } = req.body;
    const transRes = await getTransaction(transaction_id);
    const { printing_belt_id, vehicle_id } = transRes;
    await Promise.all([stopTransactionLocal(transaction_id)]);
    io.sockets.emit('stop', {
      printing_belt_id,
      bag_counting_belt_id: vehicle_id
    });
    sendHttpResponse(res, 'Success', {});
  } catch (err) {
    console.error('err --- user.controller --- stopBelt:', err.message);
  }
};

export const getMissingLabels = async (req, res) => {
  try {
    const missingRes = await fetchMissingLabels();
    console.log(missingRes);
    sendHttpResponse(res, 'Success', {});
  } catch (err) {
    console.error('err --- user.controller --- getMissingLabels:', err.message);
  }
};
