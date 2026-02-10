import { useEffect, useState } from 'react';
import { ArrowRight, CreditCard } from 'lucide-react';

type Invoice = {
  acc: string;
  meter: string;
  bill: number;
  status: string;
};

type BillingDashboardProps = {
  customerId?: number;
  onBack: () => void;
};

const BillingDashboard = ({ customerId = 1, onBack }: BillingDashboardProps) => {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://localhost:8000/customer/${customerId}/full-data`)
      .then(res => res.json())
      .then(data => {
        setInvoices(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [customerId]);

  return (
    <div className="min-h-screen bg-[#F8FAFC]" dir="rtl">
      {/* Header */}
      <header className="bg-white border-b p-6 flex items-center gap-4">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-[#0054A6]"
        >
          <ArrowRight size={18} />
          رجوع
        </button>

        <h1 className="text-xl font-bold text-[#0054A6]">
          لوحة الفوترة
        </h1>
      </header>

      {/* Content */}
      <main className="p-6">
        {loading ? (
          <p className="text-gray-500">جاري تحميل الفواتير...</p>
        ) : invoices.length === 0 ? (
          <div className="bg-white p-6 rounded-xl shadow">
            <p className="text-gray-500">لا توجد فواتير حالياً</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {invoices.map((inv, index) => (
              <div
                key={index}
                className="bg-white p-6 rounded-xl shadow flex justify-between items-center"
              >
                <div>
                  <h3 className="font-bold mb-1">
                    حساب رقم: {inv.acc}
                  </h3>
                  <p className="text-sm text-gray-500">
                    العداد: {inv.meter || '—'}
                  </p>
                </div>

                <div className="text-left">
                  <p className="font-bold text-lg">
                    {inv.bill.toFixed(2)} ر.س
                  </p>
                  <span
                    className={`text-sm font-semibold px-3 py-1 rounded-full ${
                      inv.status === 'Unpaid'
                        ? 'bg-red-100 text-red-600'
                        : 'bg-green-100 text-green-600'
                    }`}
                  >
                    {inv.status === 'Unpaid' ? 'غير مدفوعة' : 'مدفوعة'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default BillingDashboard;