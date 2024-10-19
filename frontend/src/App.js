import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoginForm from "./components/LoginForm";
import ForgetPassword from "./components/ForgetPassword";
import UserDashboard from "./components/UserDashboard";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/selfservice" element={<LoginForm />} />
        <Route
          path="/selfservice/forgot-password"
          element={<ForgetPassword />}
        />
        <Route path="/selfservice/user-dashboard" element={<UserDashboard />} />
      </Routes>
    </Router>
  );
};

export default App;
