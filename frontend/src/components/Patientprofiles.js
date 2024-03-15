import React, { useState } from "react";
import axios from "axios";
import "../css/Patientprofiles.css";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import Loading from "./Loading";
import docGif from "../assets/doctor.gif";

function Patientprofiles() {
  const [isLoading, setIsLoading] = useState(false);

  const [phone, setPhone] = useState("");
  const navigate = useNavigate();

  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setIsLoading(true);

      const response = await axios.post("http://13.201.194.131:5000/send-otp", {
        phone: phone,
      });

      if (response.data.message === "Email sent") {
        console.log("OTP sent successfully");
        setIsLoading(false);
        const success = await login(phone);
        if (success) {
          navigate("/otp");
        }
      } else if (response.data.message === "patient doesn't exist") {
        console.log("Invalid patient phone number ");

        setIsLoading(false);
        alert("patient Number doesnt exist");
      }
    } catch (error) {
      console.error("Error sending OTP:", error);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <section className="vh-100 gradient-custom outer-box">
          {isLoading ? <Loading /> : ""}

          <div className="container py-5 h-100">
            <div
              style={{ position: "relative", right: "130px" }}
              className="row d-flex justify-content-center align-items-center h-100"
            >
              <div className="col-12 col-md-8 col-lg-6 col-xl-5">
                <div
                  className="card bg-dark text-white"
                  style={{ borderRadius: "1rem", width: "150%" }}
                >
                  <div className="container">
                    <div className="row align-items-center">
                      <div className="col-md-6">
                        <div className="card-body p-5 text-center">
                          <div className="mt-md-4 pb-5">
                            <h2 className="fw-bold mb-2 text-uppercase">
                              Patient Details
                            </h2>
                            <p className="text-white-50 mb-5">
                              Please enter your Details!
                            </p>

                            <div className="form-outline form-white mb-4">
                              <label
                                className="form-label"
                                htmlFor="typeEmailX"
                              >
                                Phone No
                              </label>
                              <input
                                type="number"
                                id="typeEmailX"
                                className="form-control form-control-lg editable-field"
                                onChange={(e) => {
                                  setPhone(e.target.value);
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
                      <div className="col-md-6">
                        <img
                          src={docGif}
                          alt="doctor-gif"
                          className="img-fluid"
                        ></img>
                      </div>
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

export default Patientprofiles;
