import express from 'express';
import './config/database';
import middlewaresConfig from './config/middlewares';
import constants from './config/constants';
import ApiRoutes from './routes';

const app = express();
const http = require('http').Server(app);
const io = require('socket.io')(http);

middlewaresConfig(app);

io.on('connect', socket => {
  console.log('connected');
  socket.on('disconnect', () => {
    console.log('disconnected');
  });
});

app.use('/api', ApiRoutes);
if (!module.parent) {
  http.listen(constants.PORT, err => {
    if (err) {
      console.log('Cannot run!');
    } else {
      console.log(`API server listening on port: ${constants.PORT}`);
    }
  });
}

export default app;
