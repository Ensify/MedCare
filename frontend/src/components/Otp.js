import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function Otp() {
  const [otp, setOtp] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log(otp);
    axios
      .post("http://13.201.194.131:5000/verifyotp", { otp: otp })
      .then((response) => {
        if (response.data.success) {
          console.log("OTP verified successfully");
          alert("Otp verified successfully");
          navigate("/patientCard");
        } else {
          alert("Invalid otp");
          console.log("Invalid OTP");
        }
      })
      .catch((err) => console.log(err));
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <section className="vh-100 gradient-custom outer-box">
          <div className="container py-5 h-100">
            <div className="row d-flex justify-content-center align-items-center h-100">
              <div className="col-12 col-md-8 col-lg-6 col-xl-5">
                <div
                  className="card bg-dark text-white"
                  style={{ borderRadius: "1rem" }}
                >
                  <div className="card-body p-5 text-center">
                    <div className="mt-md-4 pb-5">
                      <h2 className="fw-bold mb-2 text-uppercase">
                        Enter Your OTP
                      </h2>

                      <div className="form-outline form-white mb-4">
                        <label
                          className="form-label"
                          htmlFor="typeEmailX"
                        ></label>
                        <input
                          type="number"
                          id="typeEmailX"
                          className="form-control form-control-lg"
                          onChange={(e) => {
                            setOtp(e.target.value);
                          }}
                        />
                      </div>

                      <button
                        className="btn btn-outline-light btn-lg px-5 mt-5"
                        type="submit"
                      >
                        Submit
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </form>
    </div>
  );
}

export default Otp;
