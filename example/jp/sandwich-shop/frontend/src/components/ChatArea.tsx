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
import useAgentsForAmazonBedrock from "../actions/AgentsForAmazonBedrock";

const ChatArea: React.FC = () => {
  const chat = useChat();
  const state = useState();
  const stateModel = useStateModel();
  const agent = useAgentsForAmazonBedrock();

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
              if (nextAgent?.agent) {
                agent.send(textContent, nextAgent.agent).then((response) => {
                  let current = undefined;
                  // 注文を追加する
                  if (response.isAppendOrderAction) {
                    current = state.appendOrder(
                      response.appendOrderValue as any
                    );
                  }
                  // 注文にオプション情報を追記する
                  if (response.isUpdateOrderAction) {
                    current = state.updateOrder(
                      response.updateOrderValue as any,
                      nextAgent.path[1] // [order.0.optionName]の形式でパスが入る。
                    );
                  }
                  // 注文以外の情報（店内飲食、人数など）を更新する
                  if (response.isUpdateJsonPartialAction) {
                    current = state.appendState(response.jsonPartialValue);
                  }
                  // JavaScriptを実行する
                  if (response.isJsCommandAction) {
                    // JavaScriptを実行する
                    chat.received(nextAgent.aiMessage);
                    return;
                  }
                  // メッセージをチャットに表示する
                  if (response.isMessageAction) {
                    // メッセージを受信する
                    chat.received(response.message);
                    return;
                  }
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
                });
              }
            }}
          />
        </ChatContainer>
      </MainContainer>
    </div>
  );
};

export default ChatArea;
