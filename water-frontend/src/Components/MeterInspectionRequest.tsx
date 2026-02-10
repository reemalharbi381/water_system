import { Waves, ArrowRight, Gauge, MapPin, Phone, FileText, Send } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { useState } from 'react';

interface MeterInspectionRequestProps {
  onBack: () => void;
}

export function MeterInspectionRequest({ onBack }: MeterInspectionRequestProps) {
  const [meterNumber, setMeterNumber] = useState('');
  const [location, setLocation] = useState('');
  const [contactNumber, setContactNumber] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    // الربط مع البايثون سيكون هنا لاحقاً
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC]" dir="rtl">
      <header className="bg-white p-6 border-b">
        <button onClick={onBack} className="flex items-center gap-2 text-[#0054A6]">
          <ArrowRight /> العودة للرئيسية
        </button>
      </header>
      <main className="max-w-4xl mx-auto p-6">
         {submitted ? <div className="p-6 bg-green-100 rounded-xl">تم إرسال طلب الفحص بنجاح!</div> : (
           <Card className="p-8">
             <form onSubmit={handleSubmit} className="space-y-6">
                <Label>رقم العداد</Label>
                <Input value={meterNumber} onChange={(e:any)=>setMeterNumber(e.target.value)} required />
                <Label>الموقع</Label>
                <Input value={location} onChange={(e:any)=>setLocation(e.target.value)} required />
                <Label>رقم التواصل</Label>
                <Input value={contactNumber} onChange={(e:any)=>setContactNumber(e.target.value)} required />
                <Button type="submit" className="w-full bg-[#0054A6] text-white p-4 rounded-xl">إرسال الطلب</Button>
             </form>
           </Card>
         )}
      </main>
    </div>
  );
}