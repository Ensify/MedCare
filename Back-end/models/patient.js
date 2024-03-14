const mongoose = require("mongoose");

const patientSchema = new mongoose.Schema({
  email: String,
  password: String,
});

const patientModel = mongoose.model("patient", patientSchema);

module.exports = patientModel;
