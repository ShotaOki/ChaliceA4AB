import "@chatscope/chat-ui-kit-styles/dist/default/styles.min.css";
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
} from "@chatscope/chat-ui-kit-react";
import React, { useEffect } from "react";
import useChat from "../actions/Chat";
import useStateModel from "../actions/StateModel";
import useState from "../actions/State";

const ChatArea: React.FC = () => {
  const chat = useChat();
  const state = useState();
  const stateModel = useStateModel();

  useEffect(() => {
    state.setState({});
    const proc = stateModel.readNextProc(state.state);

    chat.clear();
    if (proc) {
      chat.received(proc.aiMessage);
    }
  }, []);

  return (
    <div style={{ position: "relative", height: "100vh" }}>
      <MainContainer>
        <ChatContainer>
          <MessageList>
            {chat.chat.map((item) => (
              <Message model={item} key={`${item.sentTime}-${item.sender}`}>
                <Message.Header sender={item.sender} />
              </Message>
            ))}
          </MessageList>
          <MessageInput
            placeholder="Type message here"
            attachDisabled
            attachButton={false}
            onSend={(textContent) => {
              // チャットを送信する
              chat.send(textContent);
              // AIエージェントから結果を取得、更新する
              const nextAgent = stateModel.readNextProc(state.state);
              console.log(nextAgent?.agent);
              // FIXME: Received
              const current = state.appendState({
                order: [
                  {
                    id: new Date().toLocaleDateString(),
                    name: "BLTサンド",
                    count: 1,
                    bread: "ウィート",
                    dressing: "ビネガー",
                    topping: [],
                  },
                ],
              });
              // AIエージェントから結果を取得、更新する
              const proc = stateModel.readNextProc(current);
              if (proc) {
                chat.received(proc.aiMessage);
              } else {
                console.log("完了");
                chat.received(
                  "承りました。ありがとうございました。おまちください"
                );
              }
            }}
          />
        </ChatContainer>
      </MainContainer>
    </div>
  );
};

export default ChatArea;
