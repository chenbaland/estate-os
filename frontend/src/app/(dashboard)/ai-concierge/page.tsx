"use client";

import { Bot, Send } from "lucide-react";
import { useState } from "react";

import { ModulePage } from "@/components/shared/ModulePage";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MODULE_DESCRIPTIONS, MODULE_ICONS } from "@/lib/navigation";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const INITIAL_MESSAGES: Message[] = [
  {
    role: "assistant",
    content:
      "Hello! I'm your EstateOS AI Concierge. I can help with visitor passes, facility bookings, billing questions, and more. How can I assist you today?",
  },
];

export default function AIConciergePage() {
  const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);
  const [input, setInput] = useState("");

  function handleSend(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [
      ...prev,
      { role: "user", content: userMessage },
      {
        role: "assistant",
        content:
          "I'm connecting to the EstateOS AI backend. Once the `/api/v1/ai/` endpoints are live, I'll provide real-time assistance tailored to your estate.",
      },
    ]);
  }

  return (
    <ModulePage
      title="AI Concierge"
      description={MODULE_DESCRIPTIONS["ai-concierge"]}
      iconKey="ai-concierge"
      badge="Beta"
    >
      <Card className="flex h-[calc(100vh-16rem)] flex-col">
        <CardContent className="flex flex-1 flex-col p-0">
          <ScrollArea className="flex-1 p-4">
            <div className="space-y-4">
              {messages.map((message, i) => (
                <div
                  key={i}
                  className={`flex gap-3 ${message.role === "user" ? "justify-end" : ""}`}
                >
                  {message.role === "assistant" && (
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
                      <Bot className="h-4 w-4" />
                    </div>
                  )}
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm ${
                      message.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted"
                    }`}
                  >
                    {message.content}
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
          <form
            onSubmit={handleSend}
            className="flex gap-2 border-t p-4"
          >
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about billing, visitors, facilities..."
              aria-label="Message to AI concierge"
            />
            <Button type="submit" size="icon" aria-label="Send message">
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </CardContent>
      </Card>
    </ModulePage>
  );
}
