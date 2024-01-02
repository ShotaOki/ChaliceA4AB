import { MessageModel } from "@chatscope/chat-ui-kit-react";
import { MessageDirection } from "@chatscope/chat-ui-kit-react/src/types/unions";
import { create } from "zustand";

const useChatState = create<{
  isConnecting: boolean;
  chat: MessageModel[];
  clear: () => void;
  appendChat: (s: MessageModel) => void;
  startLoading: () => void;
  stopLoading: () => void;
}>((set, get) => {
  return {
    isConnecting: false,
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
    startLoading() {
      set(() => {
        return {
          isConnecting: true,
        };
      });
    },
    stopLoading() {
      set(() => {
        return {
          isConnecting: false,
        };
      });
    },
  };
});

const useChat = () => {
  const { chat, isConnecting, clear, appendChat, startLoading, stopLoading } =
    useChatState();
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
    isConnecting,
    clear() {
      clear();
    },
    send(text: string) {
      send(text, "あなた", "outgoing");
    },
    received(text: string) {
      send(text, "店員", "incoming");
    },
    startLoading,
    stopLoading,
  };
};

export default useChat;
