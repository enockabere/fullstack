import React, { useState, useEffect } from "react";

function ResendOtpForm({ setStep }) {
  useEffect(() => {
    // Trigger the toast when the page loads
    toast.success("Validation email sent successfully!", {
      position: "top-right",
      autoClose: 5000, // Toast will disappear after 5 seconds
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      progress: undefined,
      style: {
        backgroundColor: "#4caf50",
        color: "#fff", // Change the text color
      },
    });
  }, []);
  const [otp, setOtp] = useState(["", "", ""]);

  // Handle OTP input change
  const handleOtpChange = (index, e) => {
    const newOtp = [...otp];
    newOtp[index] = e.target.value;
    setOtp(newOtp);

    // Move to the next input field if 2 characters are entered
    if (e.target.value.length === 2 && index < otp.length - 1) {
      document.getElementById(`otp-input-${index + 1}`).focus();
    }
  };

  // Handle resend OTP action
  const handleResendOtp = (e) => {
    e.preventDefault();
    const csrfToken = document
      .querySelector('meta[name="csrf-token"]')
      .getAttribute("content");

    // Clear previous errors
    setError(null);
    console.log("Resend OTP triggered");

    fetch("/selfservice/resend-otp/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          // Move to OTP form if OTP is sent successfully
          useEffect(() => {
            // Trigger the toast when the page loads
            toast.success("Validation email sent successfully!", {
              position: "top-right",
              autoClose: 5000, // Toast will disappear after 5 seconds
              hideProgressBar: false,
              closeOnClick: true,
              pauseOnHover: true,
              draggable: true,
              progress: undefined,
              style: {
                backgroundColor: "#4caf50",
                color: "#fff", // Change the text color
              },
            });
          }, []);
        } else {
          // Handle error (e.g., invalid email)
          setError(data.message);
        }
      })
      .catch((error) => {
        setError("An error occurred. Please try again.");
      });
  };

  // Handle submitting OTP
  const handleSubmitOtp = (e) => {
    e.preventDefault();
    // Validate OTP and then move to password reset form
    setStep(3); // Move to password reset form
  };

  return (
    <div>
      {/* Resend OTP link styled as a button */}
      <div className="mt-4 mb-4">
        <span className="reset-password-link">
          If you didn't receive the OTP?&nbsp;&nbsp;
          <a
            href="#"
            className="btn-link text-danger"
            onClick={handleResendOtp}
          >
            Resend OTP
          </a>
        </span>
      </div>
      <ToastContainer />
      {/* OTP Form */}
      <form className="theme-form" onSubmit={handleSubmitOtp}>
        <div className="form-group">
          <label className="col-form-label pt-0">Enter OTP</label>
          <div className="row">
            {otp.map((digit, index) => (
              <div className="col" key={index}>
                <input
                  id={`otp-input-${index}`}
                  className="form-control text-center opt-text"
                  type="text"
                  value={digit}
                  maxLength="2"
                  onChange={(e) => handleOtpChange(index, e)}
                />
              </div>
            ))}
          </div>
        </div>
        <div className="form-group mb-0">
          <button className="btn btn-primary btn-block w-100" type="submit">
            Verify OTP
          </button>
        </div>
      </form>
    </div>
  );
}

export default ResendOtpForm;
