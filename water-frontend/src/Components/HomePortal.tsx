import React from 'react';
import { Droplet, User, ShieldCheck, Briefcase } from 'lucide-react';

export const HomePortal = ({ onSelectRole }: any) => {
  const roles = [
    { id: 'client', title: 'بوابة العميل', icon: User, desc: 'خدمات الفواتير والبلاغات', color: 'from-blue-600 to-blue-400' },
    { id: 'employee', title: 'بوابة الموظف', icon: Briefcase, desc: 'إدارة المهام الميدانية', color: 'from-slate-700 to-slate-500' },
    { id: 'admin', title: 'بوابة المسؤول', icon: ShieldCheck, desc: 'لوحة التحكم وإدارة النظام', color: 'from-blue-900 to-slate-800' },
  ];

  return (
    <div className="min-h-screen flex flex-col justify-center items-center px-6 nwc-gradient py-20">
      <div className="text-center text-white mb-16 animate-slide-up">
        <div className="bg-white p-5 rounded-[30px] inline-block mb-8 shadow-2xl">
          <Droplet className="text-blue-600 fill-blue-600" size={60} />
        </div>
        <h1 className="text-6xl font-black mb-4 tracking-tighter">بوابة قـطـرة</h1>
        <p className="text-xl text-blue-100">المنصة الرقمية الموحدة لشركة المياه الوطنية NWC</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-10 max-w-6xl w-full">
        {roles.map((r) => (
          <div 
            key={r.id} 
            onClick={() => onSelectRole(r.id)}
            className="group cursor-pointer bg-white/10 backdrop-blur-2xl border border-white/20 p-10 rounded-[45px] hover:bg-white transition-all duration-500 hover:-translate-y-5 shadow-2xl"
          >
            <div className={`w-20 h-20 rounded-3xl mb-8 flex items-center justify-center bg-gradient-to-br ${r.color} text-white group-hover:scale-110 transition-all shadow-lg`}>
              <r.icon size={40} />
            </div>
            <h3 className="text-3xl font-black mb-4 text-white group-hover:text-slate-900 transition-colors">{r.title}</h3>
            <p className="text-blue-100 group-hover:text-slate-500 transition-colors text-lg font-medium leading-relaxed">{r.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
};