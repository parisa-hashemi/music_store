import React, { useState } from 'react';
import { useRegistro } from '../hooks/useAuth';
import './Auth.css';

const Registro = ({ onVolver, onCambiarALogin }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: ''
  });

  const registroMutation = useRegistro();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    registroMutation.mutate(formData, {
      onSuccess: () => {
        alert('User registered successfully. You can now log in.');
        onCambiarALogin();
      }
    });
  };

  return (
    <div className="auth-container">
      <button onClick={onVolver} className="btn-volver">
        ← Back
      </button>

      <div className="auth-form">
        <h1>📝 Create Account</h1>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username:</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Email:</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Password:</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              minLength="6"
            />
          </div>

          <div className="form-group">
            <label>Confirm Password:</label>
            <input
              type="password"
              name="password_confirm"
              value={formData.password_confirm}
              onChange={handleChange}
              required
            />
          </div>

          <button
            type="submit"
            className="btn-submit"
            disabled={registroMutation.isPending}
          >
            {registroMutation.isPending ? 'Registering...' : 'Create Account'}
          </button>
        </form>

        {registroMutation.error && (
          <div className="error-message">
            {registroMutation.error.message}
          </div>
        )}

        <div className="auth-switch">
          <p>Already have an account?
            <button onClick={onCambiarALogin} className="btn-link">
              Log in here
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Registro;