import React from 'react';
import { Droplet, ArrowRight, Lock, Mail } from 'lucide-react';

export const Login = ({ role, onLogin, onBack }: any) => (
  <div className="min-h-screen flex items-center justify-center px-4 bg-[#F2F2F7]">
    <div className="max-w-md w-full bg-white p-10 rounded-[45px] shadow-2xl animate-slide-up border border-gray-100">
      <button onClick={onBack} className="flex items-center gap-2 text-blue-600 font-bold mb-8 hover:opacity-70">
        <ArrowRight size={20} /> العودة للرئيسية
      </button>

      <div className="text-center mb-10">
        <h2 className="text-3xl font-black text-gray-900">دخول {role === 'admin' ? 'الإدارة' : role === 'employee' ? 'الموظفين' : 'العملاء'}</h2>
        <p className="text-gray-400 mt-2 font-medium">شركة المياه الوطنية NWC</p>
      </div>

      <div className="space-y-6 text-right">
        <div className="bg-gray-100 p-4 rounded-2xl flex items-center gap-4 flex-row-reverse border border-transparent focus-within:border-blue-500 focus-within:bg-white transition-all">
          <Mail className="text-gray-400" size={24} />
          <input className="bg-transparent border-0 outline-none w-full text-right font-bold" placeholder="البريد الإلكتروني" />
        </div>
        <div className="bg-gray-100 p-4 rounded-2xl flex items-center gap-4 flex-row-reverse border border-transparent focus-within:border-blue-500 focus-within:bg-white transition-all">
          <Lock className="text-gray-400" size={24} />
          <input type="password" className="bg-transparent border-0 outline-none w-full text-right font-bold" placeholder="كلمة المرور" />
        </div>
        <button onClick={onLogin} className="w-full bg-blue-600 text-white font-black p-5 rounded-2xl shadow-xl hover:bg-blue-700 active:scale-95 transition-all">
          تسجيل الدخول
        </button>
      </div>
    </div>
  </div>
);