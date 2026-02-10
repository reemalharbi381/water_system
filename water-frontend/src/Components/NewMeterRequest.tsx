import { ArrowRight, Gauge, FileText, User, Send } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { useState } from 'react';

export function NewMeterRequest({ onBack }: { onBack: () => void }) {
  const [propertyType, setPropertyType] = useState('سكني');
  const [submitted, setSubmitted] = useState(false);

  return (
    <div className="min-h-screen bg-[#F8FAFC]" dir="rtl">
      <header className="bg-white p-6 border-b flex items-center gap-4">
        <button onClick={onBack} className="text-[#0054A6]"><ArrowRight /></button>
        <h1 className="text-xl font-bold text-[#0054A6]">طلب تركيب عداد جديد</h1>
      </header>
      <main className="max-w-4xl mx-auto p-6">
        {submitted ? (
          <div className="bg-blue-100 p-6 rounded-2xl text-[#0054A6] font-bold">تم استلام طلبك لتركيب عداد جديد، جارِ المراجعة.</div>
        ) : (
          <Card className="p-8 shadow-lg">
            <form onSubmit={(e) => { e.preventDefault(); setSubmitted(true); }} className="space-y-6">
              <Label>نوع العقار</Label>
              <div className="flex gap-4">
                <button type="button" onClick={() => setPropertyType('سكني')} className={`flex-1 p-4 rounded-xl border-2 ${propertyType === 'سكني' ? 'border-[#0054A6] bg-blue-50' : ''}`}>سكني</button>
                <button type="button" onClick={() => setPropertyType('تجاري')} className={`flex-1 p-4 rounded-xl border-2 ${propertyType === 'تجاري' ? 'border-[#0054A6] bg-blue-50' : ''}`}>تجاري</button>
              </div>
              <Label>رقم الهوية / السجل التجاري</Label>
              <Input placeholder="أدخل الرقم" required />
              <Label>رقم الصك أو رخصة البناء</Label>
              <Input placeholder="أدخل رقم المستند" required />
              <Button type="submit" className="w-full bg-gradient-to-r from-[#00C2FF] to-[#0054A6] text-white p-4">تقديم الطلب</Button>
            </form>
          </Card>
        )}
      </main>
    </div>
  );
}