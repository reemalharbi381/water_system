import React from 'react';

// أضفنا export لكل شيء لحل مشكلة isolatedModules
export const Card = ({ children, className, onClick }: any) => (
  <div 
    onClick={onClick} 
    className={`bg-white rounded-[35px] shadow-xl shadow-gray-200/50 hover:-translate-y-3 transition-all duration-500 cursor-pointer border border-gray-100 group ${className}`}
  >
    {children}
  </div>
);

export const CardContent = ({ children, className }: any) => (
  <div className={`p-10 flex flex-col items-center text-center ${className}`}>
    {children}
  </div>
);