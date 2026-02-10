import { useState } from "react";
import { ArrowRight } from "lucide-react";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Input } from "./ui/input";
import { Label } from "./ui/label";

type MaintenanceReportProps = {
  onBack: () => void;
};

export default function MaintenanceReport({ onBack }: MaintenanceReportProps) {
  // -------------------- STATES --------------------
  const [issueType, setIssueType] = useState<string>("تسرب مياه");
  const [description, setDescription] = useState<string>("");
  const [submitted, setSubmitted] = useState<boolean>(false);
  const [requestCode, setRequestCode] = useState<string>("");

  // -------------------- HANDLER --------------------
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    try {
      const response = await fetch("http://127.0.0.1:8000/field-service/request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_id: 1,       // ضع هنا رقم العميل الصحيح
          account_id: 123,      // ضع هنا رقم الحساب الصحيح
          service_type: issueType,
          description: description,
          lang: "ar",
        }),
      });

      const data = await response.json();

      if (data.status === "success") {
        setSubmitted(true);
        setRequestCode(data.request_code);
      } else {
        alert("حدث خطأ أثناء إرسال البلاغ");
      }
    } catch (err) {
      console.error(err);
      alert("حدث خطأ في الاتصال بالسيرفر");
    }
  };

  // -------------------- JSX --------------------
  return (
    <div className="min-h-screen bg-[#F8FAFC]" dir="rtl">
      {/* Header */}
      <header className="bg-white px-6 py-4 border-b flex items-center gap-4">
        <button onClick={onBack} className="text-[#0054A6] hover:opacity-80">
          <ArrowRight />
        </button>
        <h1 className="text-xl font-bold text-[#0054A6]">بلاغ صيانة جديد</h1>
      </header>

      {/* Content */}
      <main className="max-w-4xl mx-auto p-6">
        {submitted ? (
          <div className="bg-green-100 text-green-800 p-6 rounded-xl font-semibold">
            ✅ تم إرسال بلاغ الصيانة بنجاح
            <div className="mt-2 text-sm font-normal">
              رقم البلاغ: <span className="font-bold">{requestCode}</span>
            </div>
          </div>
        ) : (
          <Card className="p-8 shadow-md">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* نوع المشكلة */}
              <div>
                <Label className="mb-2 block">نوع المشكلة</Label>
                <select
                  value={issueType}
                  onChange={(e) => setIssueType(e.target.value)}
                  className="w-full p-3 border rounded-lg bg-white"
                >
                  <option>تسرب مياه</option>
                  <option>انقطاع المياه</option>
                  <option>ضعف ضغط المياه</option>
                  <option>مشكلة في عداد المياه</option>
                </select>
              </div>

              {/* وصف المشكلة */}
              <div>
                <Label className="mb-2 block">وصف المشكلة</Label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full p-3 border rounded-lg bg-white"
                  placeholder="صف مشكلتك هنا"
                  required
                />
              </div>

              {/* رقم التواصل */}
              <div>
                <Label className="mb-2 block">رقم التواصل</Label>
                <Input
                  type="tel"
                  placeholder="05xxxxxxxx"
                  required
                />
              </div>

              <Button
                type="submit"
                className="w-full bg-[#0054A6] hover:bg-[#003f7d]"
              >
                إرسال البلاغ
              </Button>
            </form>
          </Card>
        )}
      </main>
    </div>
  );
}