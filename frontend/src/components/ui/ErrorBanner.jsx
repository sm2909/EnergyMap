import React from 'react';
import './ErrorBanner.css';

export default function ErrorBanner({ message, onRetry }) {
  return (
    <div className="errorBanner" role="alert">
      <div className="errorBanner__content">
        <div className="errorBanner__icon" aria-hidden="true">⚠️</div>
        <div>
          <div className="errorBanner__title">Failed to load data</div>
          <div className="errorBanner__message">{message}</div>
        </div>
      </div>
      {onRetry ? (
        <button className="errorBanner__retry" type="button" onClick={onRetry}>
          Retry
        </button>
      ) : null}
    </div>
  );
}
