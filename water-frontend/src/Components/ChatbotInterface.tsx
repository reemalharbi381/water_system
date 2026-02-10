import { useState } from 'react';
import { Send, Bot, User, X } from 'lucide-react';

const API_URL = "http://127.0.0.1:8000/chatbot";

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

export default function ChatbotInterface() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'مرحباً! أنا مساعدك قطرة 💧 كيف أقدر أساعدك؟',
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userText = input;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: userText,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch(
        `${API_URL}?inquiry=${encodeURIComponent(userText)}`,
        {
          method: 'GET',
          headers: { Accept: 'application/json' },
        }
      );

      const data = await res.json();

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.reply ?? 'ما قدرت ألقى إجابة واضحة، بحوّلك لموظف 👩‍💼',
        sender: 'bot',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 2).toString(),
          text: 'صار خطأ في الاتصال بالسيرفر. تأكدي إن FastAPI شغال.',
          sender: 'bot',
          timestamp: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* زر الشات العائم */}
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 bg-gradient-to-r from-cyan-500 to-blue-600 text-white p-4 rounded-full shadow-lg z-50"
      >
        <Bot className="w-6 h-6" />
      </button>

      {/* نافذة الشات */}
      {open && (
        <div className="fixed bottom-24 right-6 w-[380px] h-[520px] bg-white rounded-xl shadow-2xl z-50 overflow-hidden flex flex-col">
          {/* Header */}
          <div className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white p-4 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <Bot className="w-6 h-6" />
              <div>
                <h2 className="font-bold">المساعد الآلي</h2>
                <p className="text-xs text-cyan-100">
                  {loading ? 'يكتب...' : 'متصل الآن'}
                </p>
              </div>
            </div>
            <button onClick={() => setOpen(false)}>
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.sender === 'user'
                    ? 'justify-start'
                    : 'justify-end'
                }`}
              >
                <div
                  className={`flex items-end gap-2 max-w-[75%] ${
                    message.sender === 'user'
                      ? 'flex-row-reverse'
                      : 'flex-row'
                  }`}
                >
                  <div
                    className={`rounded-full p-2 ${
                      message.sender === 'user'
                        ? 'bg-cyan-100'
                        : 'bg-gray-200'
                    }`}
                  >
                    {message.sender === 'user' ? (
                      <User className="w-4 h-4 text-cyan-600" />
                    ) : (
                      <Bot className="w-4 h-4 text-gray-600" />
                    )}
                  </div>

                  <div>
                    <div
                      className={`rounded-2xl px-4 py-3 ${
                        message.sender === 'user'
                          ? 'bg-cyan-500 text-white rounded-br-none'
                          : 'bg-gray-200 text-gray-800 rounded-bl-none'
                      }`}
                    >
                      <p className="text-sm">{message.text}</p>
                    </div>
                    <p className="text-[10px] text-gray-500 mt-1 px-2">
                      {message.timestamp.toLocaleTimeString('ar-SA', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Input */}
          <div className="border-t p-3 bg-white">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="اكتب رسالتك..."
                disabled={loading}
                className="flex-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-cyan-500"
              />
              <button
                onClick={handleSend}
                disabled={loading}
                className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white px-4 rounded-lg disabled:opacity-50"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}