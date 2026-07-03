"use client";

import { useState } from "react";
import { useAuth } from "@clerk/nextjs";

type Message = {
  id: number;
  role: "user" | "assistant";
  text: string;
};

export default function ChatArea() {
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, role: "assistant", text: "Hi! Upload a PDF and ask me anything." },
  ]);
  const { userId } = useAuth();
  const [sessionId] = useState(() => crypto.randomUUID());
  const [input, setInput] = useState("");
  const [rateLimited, setRateLimited] = useState(false);

  const handleUpgrade = async () => {
    const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/payment/create-checkout-session`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId }),
    });
    const { url } = await res.json();
    window.location.href = url;
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessage: Message = {
      id: Date.now(),
      role: "user",
      text: input,
    };

    setMessages((prev) => [...prev, newMessage]);
    setInput("");

    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/chat/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: input,
        USERID: userId,
        SESSIONID: sessionId,
      }),
    });

    if (!response.ok) {
      console.error(await response.text());
      throw new Error(`HTTP ${response.status}`);
    }

    const contentType = response.headers.get("content-type");
    if (contentType?.includes("application/json")) {
      const data = await response.json();
      if (data.error === "Daily limit exceeded") {
        setRateLimited(true);
        return;
      }
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error("No response body");

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split(/\r?\n\r?\n/);
      buffer = events.pop() || "";

      for (const event of events) {
        const lines = event.split(/\r?\n/);

        const eventType = lines
          .find((line) => line.startsWith("event:"))
          ?.replace("event:", "")
          .trim();

        const dataLine = lines
          .find((line) => line.startsWith("data:"))
          ?.replace("data:", "")
          .trim();

        if (!dataLine) continue;

        const data = JSON.parse(dataLine);

        switch (eventType) {
          case "token":
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              if (last && last.role === "assistant") {
                updated[updated.length - 1] = {
                  ...last,
                  text: last.text + data.chunk,
                };
              } else {
                updated.push({
                  id: Date.now(),
                  role: "assistant",
                  text: data.chunk,
                });
              }
              return updated;
            });
            break;
          case "complete":
            console.log("Streaming complete");
            break;
        }
      }
    }
  };

  return (
    <div className="flex h-full w-full flex-col bg-zinc-50 dark:bg-black">
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm shadow-sm ${
                msg.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-white text-zinc-900 border border-zinc-200 dark:bg-zinc-900 dark:text-white dark:border-zinc-800"
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
      </div>

      {rateLimited && (
        <div className="border-t border-zinc-200 dark:border-zinc-800 p-4 text-center">
          <p className="text-sm text-zinc-500 dark:text-zinc-400 mb-3">
            You've reached your daily limit of 5 queries.
          </p>
          <button
            onClick={handleUpgrade}
            className="rounded-xl bg-purple-600 px-6 py-2 text-sm font-medium text-white hover:bg-purple-700 transition"
          >
            Upgrade to Pro
          </button>
        </div>
      )}

      <div className="border-t border-zinc-200 dark:border-zinc-800 p-3">
        <div className="flex items-center gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Ask something about your PDF..."
            disabled={rateLimited}
            className="flex-1 rounded-xl border border-zinc-300 bg-white px-4 py-2 text-sm outline-none focus:border-blue-500 dark:border-zinc-700 dark:bg-zinc-900 dark:text-white disabled:opacity-50"
          />
          <button
            onClick={sendMessage}
            disabled={rateLimited}
            className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}