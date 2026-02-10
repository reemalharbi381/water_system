import React from 'react';
import { Phone, Globe, Mail, Twitter, Instagram, Droplet } from 'lucide-react'; // تأكد من استيراد Droplet هنا

export const Footer = () => (
  <footer className="bg-[#111827] text-white pt-16 pb-8 font-[Arial]">
    <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-4 gap-12 text-right">
      <div className="md:col-span-1">
        <div className="flex items-center gap-3 mb-6 justify-end">
          <span className="font-bold text-2xl">بوابة قطرة</span>
          <div className="bg-blue-600 p-2 rounded-lg">
            <Droplet className="text-white fill-white" size={20} />
          </div>
        </div>
        <p className="text-gray-400 font-bold leading-relaxed">المنصة الموحدة لشركة المياه الوطنية لخدمة العملاء والموظفين.</p>
      </div>
      {/* باقي الأقسام هنا */}
    </div>
    <div className="text-center mt-12 border-t border-gray-800 pt-8 text-gray-500 font-bold">
      © 2026 NWC | All Rights Reserved
    </div>
  </footer>
);