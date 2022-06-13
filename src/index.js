/* eslint-disable no-console */
import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
// import mongoose from 'mongoose';

import middlewaresConfig from './config/middleware';
import constants from './config/constants';
// import AccSchema from './schema/accSchema';

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, { cors: { origin: '*' } });
// const mongo_uri = `mongodb+srv://akshay:${constants.MONGODB_PASSWORD}@Cluster0.9izoo.mongodb.net/zen-frinks?retryWrites=true&w=majority`;

// mongoose
//   .connect(mongo_uri, {
//     useNewUrlParser: true,
//     useUnifiedTopology: true
//   })
//   .then(() => console.log('DB connected'))
//   .catch(err => console.log(`Error occured--${err}`));

// console.log('date', new Date().toLocaleDateString());
// new Date().getHours()
// new Date().getTime()

// const setData = (machineCode, data) => {
//   let updateObject;
//   const conditionalOptions = {
//     arrayFilters: [{ 'e1.end': undefined }],
//     new: true,
//     upsert: true
//   };
//   if (typeof data.working !== 'undefined') {
//     if (data.working) {
//       updateObject = { $set: { 'idleTime.$[e1].end': new Date().getTime() } };
//     } else {
//       updateObject = { $push: { idleTime: { start: new Date().getTime() } } };
//       delete conditionalOptions.arrayFilters;
//       delete conditionalOptions.new;
//     }
//   } else if (typeof data.cycle !== 'undefined') {
//     if (data.cycle) {
//       updateObject = { $push: { cycleTime: { start: new Date().getTime() } } };
//       delete conditionalOptions.arrayFilters;
//       delete conditionalOptions.new;
//     } else {
//       updateObject = { $set: { 'cycleTime.$[e1].end': new Date().getTime() } };
//     }
//   } else {
//     updateObject = { $set: { 'idleTime.$[e1].end': new Date().getTime() } };
//     updateObject = { $set: { 'cycleTime.$[e1].end': new Date().getTime() } };
//   }
//   AccSchema.updateOne(
//     { date: new Date().toLocaleDateString(), machineCode },
//     updateObject,
//     conditionalOptions
//   ).exec();
// };

io.on('connection', socket => {
  socket.on('label', data => {
    console.log(data);
    io.emit('label-react', data);
  });
  socket.on('wagon', data => {
    console.log(data);
    io.emit('wagon-react', data);
  });
  socket.on('truck', data => {
    console.log(data);
    io.emit('truck-react', data);
  });
  socket.on('analysis-started', data => {
    io.emit('start-analysis', data);
  });
});

middlewaresConfig(app);

app.get('/api/data', (req, res) => {
  try {
    // AccSchema.find({ date: new Date().toLocaleDateString() }, (err, data) => {
    //   if (err) {
    //     res.status(500).json({
    //       success: false,
    //       message: err,
    //       data
    //     });
    //   } else {
    //     res.status(200).json({
    //       success: true,
    //       message: 'Data found',
    //       data
    //     });
    //   }
    // });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: error.message,
      data: null
    });
  }
});

app.get('/images', (req, res) => {
  const filepath = `${req.query.basepath}/${req.query.params}`;
  res.sendFile(filepath);
});

app.get('/videos', (req, res) => {
  const filepath = `${req.query.basepath}/${req.query.params}`;
  res.sendFile(filepath);
});

if (!module.parent) {
  httpServer.listen(constants.PORT, err => {
    if (err) {
      console.log('Cannot run!');
    } else {
      console.log(`API server listening on port: ${constants.PORT}`);
    }
  });
}

export default app;
