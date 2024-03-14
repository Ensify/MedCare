const otpGenerator = require("otp-generator");

module.exports.generateOTP = () => {
  const otp = otpGenerator.generate(6, otpconfig);
  return otp;
};

const otpconfig = {
  upperCaseAlphabets: true,
  specialChars: false,
};
