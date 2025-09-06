import React from 'react';
import { isMockMode, isDevelopmentMode } from '../../constants/config';

export const DevelopmentBadge: React.FC = () => {
  if (!isDevelopmentMode()) {
    return null; // Không hiển thị trong production
  }

  return (
    <div className="fixed top-2 right-2 z-50">
      {/* <div className={`px-2 py-1 rounded text-xs font-mono text-white ${
        isMockMode() ? 'bg-green-500' : 'bg-orange-500'
      }`}>
        {isMockMode() ? '🎭 MOCK MODE' : '🔗 BACKEND MODE'}
      </div> */}
    </div>
  );
};
