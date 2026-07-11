import React, { useEffect, useState } from 'react';
import './UsuariosVIP.css';

const UsuariosVIP = () => {
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/usuarios-vip/', {
      credentials: 'include'
    })
      .then(res => res.json())
      .then(data => {
        setUsuarios(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error:', error);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="loading">Loading VIP users...</div>;

  return (
    <div className="usuarios-vip">
      <h2>✨ VIP Users</h2>
      <p className="descripcion">Users who have purchased 5 or more albums</p>

      {usuarios.length === 0 ? (
        <p className="sin-usuarios">No VIP users yet</p>
      ) : (
        <div className="tabla-usuarios">
          <table>
            <thead>
              <tr>
                <th>User</th>
                <th>Email</th>
                <th>Total Albums</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {usuarios.map(usuario => (
                <tr key={usuario.id}>
                  <td>{usuario.username}</td>
                  <td>{usuario.email}</td>
                  <td>{usuario.total_albums}</td>
                  <td>
                    <span className="badge-vip">✨ VIP</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default UsuariosVIP;
