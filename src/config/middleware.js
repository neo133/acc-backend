import express from 'express';
import cors from 'cors';

// const allowedDomains = ['http://localhost:3000'];

export default app => {
  app.use(express.json());
  app.use(cors());
};
