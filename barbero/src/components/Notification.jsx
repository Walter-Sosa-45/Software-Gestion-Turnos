import React from 'react';
import '../styles/Notification.css'; // CSS separado si querés

const NotificationPanel = ({ notifications, onClose }) => {
  return (
    <div className="notifications-container">
      <div className="notifications-header">
        <h4>Notificaciones</h4>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>
      {notifications.length === 0 ? (
        <p className="no-notifications">No hay notificaciones</p>
      ) : (
        notifications.map(n => (
          <div key={n.id} className="notification-card">
            {n.mensaje}
          </div>
        ))
      )}
    </div>
  );
};

export default NotificationPanel;
