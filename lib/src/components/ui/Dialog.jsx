import React from 'react';
import './Dialog.css';

export default function Dialog({ isOpen, onClose, title, children, onBack, backText }) {
  if (!isOpen) return null;

  return (
    <div className="dialog-overlay" onClick={onClose}>
      <div className="dialog-content" onClick={e => e.stopPropagation()}>
        <header className="dialog-header">
          <div className="dialog-title-group">
            {onBack && (
              <button className="dialog-back-btn" onClick={onBack}>
                {backText || '← Back'}
              </button>
            )}
            <h2 className="dialog-title">{title}</h2>
          </div>
          <button className="dialog-close-btn" onClick={onClose}>✕</button>
        </header>
        <div className="dialog-body">
          {children}
        </div>
      </div>
    </div>
  );
}
