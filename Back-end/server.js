const express = require("express");
const cors = require("cors");
const mongoose = require("mongoose");
const bodyParser = require("body-parser");
const nodemail = require("nodemailer");
const otpGenerator = require("otp-generator");

const app = express();
app.use(bodyParser.urlencoded({ extended: false }));
app.use(express.json());
app.use(cors());

const otpconfig = {
  upperCaseAlphabets: false,
  specialChars: false,
  lowerCaseAlphabets: false,
  digits: true,
};

const otpStorage = {};

const db = mongoose.connection;
db.on("error", console.error.bind(console, "connection error:"));
db.once("open", function () {
  console.log("MongoDB database connected successfully");
});

const transporter = nodemail.createTransport({
  service: "Gmail",
  auth: {
    user: "snekan13@gmail.com",
    pass: "ftyt rdxo rszv ctog",
  },
});

app.post("/send-otp", (req, res) => {
  const { phone } = req.body;
  patientdetailModel
    .findOne({ phone: phone })
    .then((user) => {
      if (user) {
        const { email } = user; // Extract email from the user document

        const otp = otpGenerator.generate(6, otpconfig);
        otpStorage[email] = otp;
        otpStorage[1] = phone;

        const mailoptions = {
          from: "snekan13@gmail.com",
          to: email,
          subject: "Sample OTP",
          text: "This is your OTP: " + otp,
        };

        transporter.sendMail(mailoptions, (error, info) => {
          if (error) {
            console.log("Email error:", error);
            res.json({ message: "Email send error" });
          } else {
            console.log("Email sent");
            console.log(otpStorage);
            res.json({ message: "Email sent" });
          }
        });
      } else {
        console.log("Patient doesn't exist");
        res.json({ message: "patient doesn't exist" });
      }
    })
    .catch((error) => {
      console.error("Error fetching user:", error);
      res.status(500).json({ message: "Internal Server Error" });
    });
});
