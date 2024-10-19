import React, { useState } from "react";
import mwaLogo from "../../static/img/logo/logo.png";
import SendOtpForm from "./auth/SendOtpForm";
import ResendOtpForm from "./auth/ResendOtpForm";
import ResetPasswordForm from "./auth/ResetPasswordForm";

function ForgetPassword() {
  const [step, setStep] = useState(1); // Manage the flow between the forms

  return (
    <div className="row m-0">
      <div className="col-12 p-0">
        <div className="login-card login-dark">
          <div>
            <div>
              <a className="logo" href="#">
                <img
                  className="img-fluid for-light"
                  src={mwaLogo}
                  height="120"
                  width="150"
                  alt="login page"
                />
              </a>
            </div>
            <div className="login-main">
              {/* Step 1: Form for sending OTP */}
              {step === 1 && <SendOtpForm setStep={setStep} />}

              {/* Step 2: Form for resending OTP */}
              {step === 2 && <ResendOtpForm setStep={setStep} />}

              {/* Step 3: Form for entering new password */}
              {step === 3 && <ResetPasswordForm />}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ForgetPassword;
