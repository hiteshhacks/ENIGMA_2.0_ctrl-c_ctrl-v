import { motion, AnimatePresence } from 'motion/react';
import { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Sparkles, Loader2 } from 'lucide-react';
import { api } from '../../services/api';

export function AIChatAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai',
      text: "Hello! I'm your AI health assistant. I can help explain your reports, suggest tests, or answer medical questions. How can I help you today?"
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isOpen, isLoading]);

  const quickQuestions = [
    'Explain my latest report',
    'What tests should I take?',
    'Find an oncologist near me',
    'What do my symptoms mean?'
  ];

  const handleSend = async (textInput: string = input) => {
    if (!textInput.trim() || isLoading) return;

    const userMsg = { id: Date.now(), type: 'user', text: textInput };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await api.chat({ query: textInput, vision_score: 0 });
      let aiText = 'Sorry, I got an empty response.';

      if (typeof response === 'string') {
        aiText = response;
      } else if (response.reply || response.answer || response.response) {
        aiText = response.reply || response.answer || response.response;
      } else if (response.content) {
        aiText = response.content;
      } else {
        aiText = JSON.stringify(response);
      }

      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, type: 'ai', text: aiText }
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, type: 'ai', text: 'Error: ' + (err.message || 'Failed to get response') }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Floating Button */}
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 w-16 h-16 bg-gradient-to-br from-primary to-secondary rounded-full shadow-2xl flex items-center justify-center"
      >
        {isOpen ? (
          <X className="w-6 h-6 text-white" />
        ) : (
          <MessageCircle className="w-6 h-6 text-white" />
        )}
        <div className="absolute -top-1 -right-1 w-4 h-4 bg-[#10B981] rounded-full animate-pulse"></div>
      </motion.button>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ type: 'spring', damping: 25 }}
            className="fixed bottom-24 right-6 z-50 w-96 h-[600px] bg-card rounded-2xl shadow-2xl border border-border flex flex-col overflow-hidden"
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-primary to-secondary p-4 text-white">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-semibold">AI Health Assistant</h3>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-[#10B981] rounded-full"></div>
                    <span className="text-xs opacity-90">Online</span>
                  </div>
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
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl p-3 ${message.type === 'user'
                        ? 'bg-gradient-to-br from-primary to-secondary text-white'
                        : 'bg-muted text-foreground'
                      }`}
                  >
                    <p className="text-sm">{message.text}</p>
                  </div>
                </motion.div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-muted text-foreground p-3 rounded-2xl max-w-[80%] flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin text-secondary" />
                    <span className="text-sm">Thinking...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Quick Questions */}
            {messages.length === 1 && (
              <div className="px-4 pb-4">
                <p className="text-xs text-muted-foreground mb-2">Quick questions:</p>
                <div className="flex flex-wrap gap-2">
                  {quickQuestions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => {
                        handleSend(question);
                      }}
                      className="text-xs px-3 py-1.5 bg-muted hover:bg-muted/80 rounded-full text-foreground transition-all"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Input */}
            <div className="p-4 border-t border-border bg-background">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSend(input)}
                  placeholder="Type your message..."
                  className="flex-1 px-4 py-2 bg-muted border border-border rounded-xl focus:outline-none focus:ring-2 focus:ring-secondary text-sm"
                />
                <button
                  onClick={() => handleSend(input)}
                  disabled={isLoading || !input.trim()}
                  className="p-2 bg-gradient-to-br from-primary to-secondary text-white rounded-xl hover:shadow-lg transition-all disabled:opacity-50"
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
