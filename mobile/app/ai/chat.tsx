import { Ionicons } from "@expo/vector-icons";
import { useMutation } from "@tanstack/react-query";
import { useRef, useState } from "react";
import {
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  Text,
  TextInput,
  View,
} from "react-native";

import { Avatar, Header } from "@/components";
import { colors, radius } from "@/constants/theme";
import { api } from "@/lib/api";
import type { ChatMessage } from "@/types";

export default function AIChatScreen() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hello! I'm your EstateOS AI concierge. I can help with billing, visitors, facilities, maintenance, and community questions.",
      created_at: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState("");
  const listRef = useRef<FlatList>(null);

  const chatMutation = useMutation({
    mutationFn: (message: string) => api.sendChatMessage(message),
    onSuccess: (data, message) => {
      const userMsg: ChatMessage = {
        id: `user-${Date.now()}`,
        role: "user",
        content: message,
        created_at: new Date().toISOString(),
      };
      const assistantMsg: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: data.reply,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg, assistantMsg]);
      setInput("");
      setTimeout(() => listRef.current?.scrollToEnd({ animated: true }), 100);
    },
  });

  const send = () => {
    const trimmed = input.trim();
    if (!trimmed || chatMutation.isPending) return;
    chatMutation.mutate(trimmed);
  };

  return (
    <KeyboardAvoidingView
      style={{ flex: 1, backgroundColor: colors.light.muted }}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
      keyboardVerticalOffset={0}
    >
      <Header title="AI Concierge" showBack subtitle="Powered by EstateOS" />

      <FlatList
        ref={listRef}
        data={messages}
        keyExtractor={(item) => item.id}
        contentContainerStyle={{ padding: 16, gap: 12 }}
        renderItem={({ item }) => {
          const isUser = item.role === "user";
          return (
            <View
              style={{
                flexDirection: "row",
                justifyContent: isUser ? "flex-end" : "flex-start",
                gap: 8,
              }}
            >
              {!isUser ? (
                <View
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: radius.full,
                    backgroundColor: colors.light.primary,
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <Ionicons name="sparkles" size={16} color="#FFF" />
                </View>
              ) : null}
              <View
                style={{
                  maxWidth: "78%",
                  backgroundColor: isUser ? colors.light.primary : colors.light.card,
                  borderRadius: radius.lg,
                  padding: 12,
                  borderWidth: isUser ? 0 : 1,
                  borderColor: colors.light.border,
                }}
              >
                <Text
                  style={{
                    color: isUser
                      ? colors.light.primaryForeground
                      : colors.light.foreground,
                    fontSize: 15,
                    lineHeight: 22,
                  }}
                >
                  {item.content}
                </Text>
              </View>
              {isUser ? <Avatar name="You" size={32} /> : null}
            </View>
          );
        }}
      />

      <View
        style={{
          flexDirection: "row",
          padding: 12,
          gap: 8,
          borderTopWidth: 1,
          borderTopColor: colors.light.border,
          backgroundColor: colors.light.background,
        }}
      >
        <TextInput
          value={input}
          onChangeText={setInput}
          placeholder="Ask anything about your estate..."
          placeholderTextColor={colors.light.mutedForeground}
          style={{
            flex: 1,
            height: 44,
            borderWidth: 1,
            borderColor: colors.light.border,
            borderRadius: radius.md,
            paddingHorizontal: 12,
            fontSize: 15,
            color: colors.light.foreground,
          }}
          multiline
          maxLength={500}
        />
        <Pressable
          onPress={send}
          disabled={!input.trim() || chatMutation.isPending}
          style={{
            width: 44,
            height: 44,
            borderRadius: radius.md,
            backgroundColor: colors.light.primary,
            alignItems: "center",
            justifyContent: "center",
            opacity: !input.trim() || chatMutation.isPending ? 0.5 : 1,
          }}
        >
          <Ionicons name="send" size={20} color="#FFF" />
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}
