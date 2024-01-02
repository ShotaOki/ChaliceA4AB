import { MessageModel } from "@chatscope/chat-ui-kit-react";
import { MessageDirection } from "@chatscope/chat-ui-kit-react/src/types/unions";
import { create } from "zustand";

const useChatState = create<{
  chat: MessageModel[];
  clear: () => void;
  appendChat: (s: MessageModel) => void;
}>((set, get) => {
  return {
    chat: [],
    clear() {
      set(() => {
        return {
          chat: [],
        };
      });
    },
    appendChat(s: MessageModel) {
      set(() => {
        return {
          chat: [...get().chat, s],
        };
      });
    },
  };
});

const useChat = () => {
  const { chat, clear, appendChat } = useChatState();
  const send = (text: string, sender: string, direction: MessageDirection) => {
    appendChat({
      message: text,
      sentTime: new Date().toLocaleString(),
      sender: sender,
      direction: direction,
      position: "single",
    });
  };
  return {
    chat,
    clear() {
      clear();
    },
    send(text: string) {
      send(text, "あなた", "outgoing");
    },
    received(text: string) {
      send(text, "店員", "incoming");
    },
  };
};

export default useChat;
