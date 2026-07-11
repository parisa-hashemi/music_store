import React, { useState, useEffect } from 'react';
import './UserProfile.css';
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const UserProfile = ({ onVolver }) => {
  const [user, setUser] = useState(null);
  const [userStats, setUserStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({ username: '', email: '' });
  const [message, setMessage] = useState('');

  // Fetch user data from localStorage (or the API)
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        // Get data from localStorage
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
          const userData = JSON.parse(storedUser);
          setUser(userData);
          setFormData({ username: userData.username || '', email: userData.email || '' });
        }

        // Fetch purchase stats from the API
        const response = await fetch(`${API_URL}/api/user/stats/`, {
          credentials: 'include'
        });
        if (response.ok) {
          const stats = await response.json();
          setUserStats(stats);
        }
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };
    fetchUserData();
  }, []);

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setFormData({ username: user?.username || '', email: user?.email || '' });
    setMessage('');
  };

  const handleSave = async () => {
    try {
      const response = await fetch(`${API_URL}/api/user/profile/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        const updatedUser = await response.json();
        setUser(updatedUser);
        localStorage.setItem('user', JSON.stringify(updatedUser));
        setIsEditing(false);
        setMessage('Profile updated successfully');
        setTimeout(() => setMessage(''), 3000);
      } else {
        setMessage('Error updating profile');
      }
    } catch (error) {
      setMessage('Error connecting to the server');
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  if (loading) return <div className="profile-loading">Loading...</div>;

  return (
    <div className="user-profile">
      <button onClick={onVolver} className="profile-back-btn">← Back</button>

      <div className="profile-container">
        <div className="profile-header">
          <div className="profile-avatar">
            <span className="avatar-icon">👤</span>
          </div>
          <h2>User Profile</h2>
        </div>

        {message && <div className="profile-message">{message}</div>}

        <div className="profile-info">
          <div className="info-row">
            <label>Username:</label>
            {isEditing ? (
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className="profile-input"
              />
            ) : (
              <span>{user?.username || '—'}</span>
            )}
          </div>

          <div className="info-row">
            <label>Email:</label>
            {isEditing ? (
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="profile-input"
              />
            ) : (
              <span>{user?.email || '—'}</span>
            )}
          </div>

          <div className="info-row vip-status">
            <label>VIP Status:</label>
            <span className={user?.es_vip ? 'vip-badge-active' : 'vip-badge-inactive'}>
              {user?.es_vip ? '✨ VIP Member' : 'Regular Member'}
            </span>
          </div>
        </div>

        <div className="profile-stats">
          <h3>📊 Purchase Stats</h3>
          <div className="stats-grid">
            <div className="stat-card">
              <span className="stat-number">{userStats?.total_orders || 0}</span>
              <span className="stat-label">Total Orders</span>
            </div>
            <div className="stat-card">
              <span className="stat-number">${userStats?.total_spent || 0}</span>
              <span className="stat-label">Total Spent</span>
            </div>
            <div className="stat-card">
              <span className="stat-number">{userStats?.avg_order || 0}</span>
              <span className="stat-label">Average per Order</span>
            </div>
          </div>
        </div>

        <div className="profile-actions">
          {isEditing ? (
            <>
              <button onClick={handleSave} className="save-btn">💾 Save Changes</button>
              <button onClick={handleCancel} className="cancel-btn">❌ Cancel</button>
            </>
          ) : (
            <button onClick={handleEdit} className="edit-btn">✏️ Edit Profile</button>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserProfile;