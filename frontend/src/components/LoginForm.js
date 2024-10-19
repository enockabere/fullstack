import React, { useState } from "react";
import { useNavigate } from "react-router-dom"; // Import useNavigate
import mwaLogo from "../../static/img/logo/logo.png";

function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate(); // Initialize navigate

  const handleSubmit = async (event) => {
    event.preventDefault();

    const csrfToken = document
      .querySelector('meta[name="csrf-token"]')
      .getAttribute("content");

    try {
      const response = await fetch("/selfservice/login_view/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        const redirectUrl = data.redirect_url;
        // Navigate to the returned URL
        navigate(redirectUrl);
      } else {
        console.error("Login failed");
      }
    } catch (error) {
      console.error("Error submitting form:", error);
    }
  };

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
              <form className="theme-form" onSubmit={handleSubmit}>
                <h3>Sign in to account</h3>
                <p>Enter your email &amp; password to login</p>
                <div className="form-group">
                  <label className="col-form-label">Email Address</label>
                  <input
                    className="form-control"
                    type="email"
                    required
                    placeholder="Test@gmail.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label className="col-form-label">Password</label>
                  <div className="form-input position-relative">
                    <input
                      className="form-control"
                      type="password"
                      required
                      placeholder="*********"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                    />
                    <div className="show-hide">
                      <span className="show"></span>
                    </div>
                  </div>
                </div>
                <div className="form-group mb-0">
                  <div className="checkbox p-0">
                    <input id="checkbox1" type="checkbox" />
                    <label className="text-muted" htmlFor="checkbox1">
                      Remember password
                    </label>
                  </div>
                  <a className="link" href="forget-password.html">
                    Forgot password?
                  </a>
                  <div className="text-end mt-3">
                    <button
                      className="btn btn-primary btn-block w-100"
                      type="submit"
                    >
                      Sign in
                    </button>
                  </div>
                </div>
                <h6 className="text-muted mt-4 or">Or Sign in with</h6>
                <div className="social mt-4">
                  <div className="btn-showcase">
                    <a className="btn btn-light" href="#" target="_blank">
                      <i className="txt-linkedin" data-feather="linkedin"></i>{" "}
                      Microsoft Office 365
                    </a>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginForm;
