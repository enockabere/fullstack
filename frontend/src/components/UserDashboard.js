import React, { useEffect } from "react"; // Add useEffect import
import mwaLogo from "../../static/img/logo/logo.png";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function UserDashboard() {
  useEffect(() => {
    // Trigger the toast when the page loads
    toast.success("Welcome to the Dashboard!", {
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
            <h2>UserDashboard</h2>
            <ToastContainer />
          </div>
        </div>
      </div>
    </div>
  );
}

export default UserDashboard;
