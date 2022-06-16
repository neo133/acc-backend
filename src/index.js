import express from 'express';
import './config/database';
import { createServer } from 'http';
import { Server } from 'socket.io';
import middlewaresConfig from './config/middlewares';
import constants from './config/constants';
import ApiRoutes from './routes';

const app = express();
const httpServer = createServer(app);
export const io = new Server(httpServer, { cors: { origin: '*' } });

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

export default app;
