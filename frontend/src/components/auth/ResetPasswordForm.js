import React from "react";

function ResetPasswordForm() {
  const handlePasswordChange = (e) => {
    e.preventDefault();
    // Make an API call to reset password
  };

  return (
    <form className="theme-form" onSubmit={handlePasswordChange}>
      <h6 className="mt-4">Create Your Password</h6>
      <div className="form-group">
        <label className="col-form-label">New Password</label>
        <div className="form-input position-relative">
          <input
            className="form-control"
            type="password"
            required
            placeholder="*********"
          />
        </div>
      </div>
      <div className="form-group">
        <label className="col-form-label">Retype Password</label>
        <input
          className="form-control"
          type="password"
          required
          placeholder="*********"
        />
      </div>
      <div className="form-group mb-0">
        <div className="checkbox p-0">
          <input id="checkbox1" type="checkbox" />
          <label className="text-muted" htmlFor="checkbox1">
            Remember password
          </label>
        </div>
        <button className="btn btn-primary btn-block w-100" type="submit">
          Done
        </button>
      </div>
    </form>
  );
}

export default ResetPasswordForm;
