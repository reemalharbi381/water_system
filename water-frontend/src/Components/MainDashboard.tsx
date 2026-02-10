import { useState } from 'react';
import {
  Droplet,
  Users,
  CreditCard,
  Wrench,
  LogOut,
} from 'lucide-react';

import MaintenanceReport from './MaintenanceReport';

/* =======================
   TYPES
======================= */

type Page =
  | 'dashboard'
  | 'maintenance'
  | 'billing'
  | 'technicians';

type Permissions = {
  can_view_billing?: boolean;
  can_field_tasks?: boolean;
  can_manage_technicians?: boolean;
};

type MainDashboardProps = {
  role: string;
  permissions: Permissions;
  onLogout: () => void;
};

/* =======================
   COMPONENT
======================= */

const MainDashboard = ({
  role,
  permissions,
  onLogout,
}: MainDashboardProps) => {
  const [activePage, setActivePage] = useState<Page>('dashboard');

  /* ===== PAGE ROUTING (SAFE) ===== */
  if (activePage === 'maintenance') {
    return (
      <MaintenanceReport
        onBack={() => setActivePage('dashboard')}
      />
    );
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC]" dir="rtl">
      {/* Header */}
      <header className="bg-white border-b p-6 flex justify-between items-center">
        <h1 className="text-xl font-bold text-[#0054A6]">
          لوحة التحكم – نظام المياه
        </h1>

        <button
          onClick={onLogout}
          className="flex items-center gap-2 text-red-600"
        >
          <LogOut size={18} />
          تسجيل الخروج
        </button>
      </header>

      {/* Dashboard Cards */}
      <main className="p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Maintenance */}
        <div
          onClick={() => setActivePage('maintenance')}
          className="cursor-pointer bg-white p-6 rounded-xl shadow hover:shadow-lg transition"
        >
          <Wrench className="text-[#0054A6] mb-3" />
          <h3 className="font-bold">بلاغات الصيانة</h3>
          <p className="text-sm text-gray-500">
            إنشاء ومتابعة البلاغات الميدانية
          </p>
        </div>

        {/* Billing */}
        {permissions.can_view_billing && (
          <div className="bg-white p-6 rounded-xl shadow">
            <CreditCard className="text-[#0054A6] mb-3" />
            <h3 className="font-bold">الفواتير</h3>
            <p className="text-sm text-gray-500">
              إدارة الفواتير والشرائح
            </p>
          </div>
        )}

        {/* Technicians */}
        {permissions.can_manage_technicians && (
          <div className="bg-white p-6 rounded-xl shadow">
            <Users className="text-[#0054A6] mb-3" />
            <h3 className="font-bold">الفنيين</h3>
            <p className="text-sm text-gray-500">
              إدارة الفرق الفنية الميدانية
            </p>
          </div>
        )}
      </main>
    </div>
  );
};

export default MainDashboard;