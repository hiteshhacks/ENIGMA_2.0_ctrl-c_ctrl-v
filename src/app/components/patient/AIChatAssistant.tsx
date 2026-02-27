import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { MessageSquare, X, Send, Bot, User } from 'lucide-react';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

const aiResponses = [
  "I understand your concern. Based on your recent test results, your risk levels are within the normal range. However, I recommend discussing this with your doctor for a comprehensive evaluation.",
  "Your symptoms are noted. I suggest logging them in the Symptom Logger for better tracking. Would you like me to help you with that?",
  "Early detection is key in cancer prevention. Your current screening schedule is appropriate, but if you notice any new symptoms, please report them immediately.",
  "Your genome analysis shows no concerning markers at this time. Continue with your healthy lifestyle and scheduled check-ups.",
  "I can help explain your test results. Which specific aspect would you like to understand better?"
];

export default function AIChatAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Hello! I'm your AI health assistant. How can I help you today? I can explain your reports, answer health questions, or help you log symptoms.",
      sender: 'ai',
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (!inputText.trim()) return;

    const userMessage: Message = {
      id: messages.length + 1,
      text: inputText,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages([...messages, userMessage]);
    setInputText('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: Message = {
        id: messages.length + 2,
        text: aiResponses[Math.floor(Math.random() * aiResponses.length)],
        sender: 'ai',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1500);
  };

  return (
    <>
      {/* Chat Button */}
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-gradient-to-r from-[#0B3C5D] to-[#1CA7A6] text-white shadow-2xl hover:shadow-3xl transition-all hover:scale-110 flex items-center justify-center"
      >
        {isOpen ? <X className="w-6 h-6" /> : <MessageSquare className="w-6 h-6" />}
      </motion.button>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-24 right-6 z-50 w-96 max-w-[calc(100vw-3rem)] h-[600px] max-h-[calc(100vh-8rem)] rounded-2xl shadow-2xl overflow-hidden bg-white dark:bg-slate-800 border border-border flex flex-col"
          >
            {/* Header */}
            <div className="p-4 bg-gradient-to-r from-[#0B3C5D] to-[#1CA7A6] text-white">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                  <Bot className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-semibold">AI Health Assistant</h3>
                  <p className="text-xs text-white/80">Always here to help</p>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex gap-3 ${message.sender === 'user' ? 'flex-row-reverse' : ''}`}
                >
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                    message.sender === 'ai' 
                      ? 'bg-gradient-to-br from-[#0B3C5D] to-[#1CA7A6] text-white' 
                      : 'bg-muted'
                  }`}>
                    {message.sender === 'ai' ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
                  </div>
                  <div className={`flex-1 ${message.sender === 'user' ? 'flex justify-end' : ''}`}>
                    <div className={`inline-block p-3 rounded-2xl max-w-[85%] ${
                      message.sender === 'ai'
                        ? 'bg-muted rounded-tl-none'
                        : 'bg-gradient-to-r from-[#0B3C5D] to-[#1CA7A6] text-white rounded-tr-none'
                    }`}>
                      <p className="text-sm leading-relaxed">{message.text}</p>
                      <p className={`text-xs mt-1 ${
                        message.sender === 'ai' ? 'text-muted-foreground' : 'text-white/70'
                      }`}>
                        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}

              {isTyping && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex gap-3"
                >
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#0B3C5D] to-[#1CA7A6] flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className="bg-muted p-3 rounded-2xl rounded-tl-none">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Quick Actions */}
            <div className="px-4 py-2 border-t border-border overflow-x-auto">
              <div className="flex gap-2">
                {['Explain my report', 'Log symptoms', 'Find doctor'].map((action) => (
                  <button
                    key={action}
                    onClick={() => {
                      setInputText(action);
                      handleSend();
                    }}
                    className="px-3 py-1.5 text-xs rounded-full bg-muted hover:bg-muted/80 transition-colors whitespace-nowrap"
                  >
                    {action}
                  </button>
                ))}
              </div>
            </div>

            {/* Input */}
            <div className="p-4 border-t border-border">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="Type your message..."
                  className="flex-1 px-4 py-2 rounded-xl border border-border bg-input-background focus:outline-none focus:ring-2 focus:ring-primary transition-all"
                />
                <button
                  onClick={handleSend}
                  disabled={!inputText.trim()}
                  className="w-10 h-10 rounded-xl bg-gradient-to-r from-[#0B3C5D] to-[#1CA7A6] text-white flex items-center justify-center hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
