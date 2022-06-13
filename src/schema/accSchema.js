import mongoose from 'mongoose';

const { Schema } = mongoose;

const accSchema = new Schema({
  cycleTime: {
    type: Array,
    required: true
  },
  idleTime: {
    type: Array,
    required: true
  },
  date: {
    type: String,
    required: true
  },
  machineCode: {
    type: String,
    required: true
  }
});

const AccSchema = mongoose.model('acc', accSchema);
export default AccSchema;
