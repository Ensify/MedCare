const mongoose = require("mongoose");

const patientDetailSchema = new mongoose.Schema({
  phone: Number,
  patientName: String,
  email: String,
  patientId: Number,
});
patientDetailSchema.pre("save", async function (next) {
  try {
    if (!this.isNew) {
      return next();
    }
    const lastPatient = await this.constructor.findOne(
      {},
      { patientId: 1 },
      { sort: { patientId: -1 } }
    );
    const newPatientId =
      lastPatient && lastPatient.patientId ? lastPatient.patientId + 1 : 1;
    this.patientId = newPatientId;
    next();
  } catch (error) {
    next(error);
  }
});

const patientDetailModel = mongoose.model("patient-data", patientDetailSchema);

module.exports = patientDetailModel;
