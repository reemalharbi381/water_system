import React, { useState } from 'react';
import MainDashboard from './Components/MainDashboard';
import ChatbotInterface from './Components/ChatbotInterface';
import { Footer } from './Components/Footer';

export default function App() {
  const [role, setRole] = useState('admin');

  return (
    <div className="min-h-screen relative overflow-x-hidden">
      <MainDashboard
        role={role}
        permissions={{
        can_view_billing : true,
        can_field_tasks : true,
        can_manage_technicians : true,

        }}

        onLogout={() => console.log('Log out')}
      />

      <ChatbotInterface />

      <Footer />
    </div>
  );
}