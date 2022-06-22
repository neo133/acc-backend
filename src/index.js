import express from 'express';
import './config/database';
import { createServer } from 'http';
import { Server } from 'socket.io';
import middlewaresConfig from './config/middlewares';
import constants from './config/constants';
import ApiRoutes from './routes';
import { createBagEntry, createTagEntry } from './controllers/transaction.controller';
import { stopTransactionLocal } from './sequelizeQueries/transaction.queries';

const app = express();
const httpServer = createServer(app);

middlewaresConfig(app);

app.use('/api', ApiRoutes);

if (!module.parent) {
  httpServer.listen(constants.PORT, err => {
    if (err) {
      console.log('Cannot run!');
    } else {
      console.log(`API server listening on port: ${constants.PORT}`);
    }
  });
}

export const io = new Server(httpServer, { cors: { origin: '*' } });

io.on('connection', socket => {
  console.log(socket.id);
  socket.on('bag-entry', data => {
    // call transaction controlled function
    io.sockets.emit('entry', data);
    createBagEntry(data);
  });
  socket.on('tag-entry', data => {
    // call transaction controlled function
    io.sockets.emit('entry', data);
    createTagEntry(data);
  });
  socket.on('limit-stop', data => {
    io.sockets.emit('stop', data);
    stopTransactionLocal(data.transaction_id);
  });
});

export default app;
