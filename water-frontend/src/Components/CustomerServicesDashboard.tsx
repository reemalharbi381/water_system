import { Waves, User, Settings, LogOut } from 'lucide-react';

export function CustomerServicesDashboard({ username, onOpenChat }: any) {
  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      <nav className="bg-[#0054A6] p-4 text-white flex justify-between">
        <div className="flex items-center gap-2"><Waves /> <span className="font-bold">قطرة للخدمات</span></div>
        <div className="flex items-center gap-4">
          <span>{username}</span>
          <button className="bg-white/20 p-2 rounded-full"><Settings size={18} /></button>
        </div>
      </nav>
      <main className="p-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">مرحباً بك في لوحة التحكم</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-2xl shadow-sm">
             <h3 className="font-bold border-b pb-2 mb-4">آخر الفواتير</h3>
             <p className="text-gray-500">لا توجد فواتير مستحقة حالياً.</p>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-sm">
             <h3 className="font-bold border-b pb-2 mb-4">طلباتك الحالية</h3>
             <p className="text-gray-500">لديك طلب (فحص عداد) تحت المراجعة.</p>
          </div>
        </div>
      </main>
    </div>
  );
}