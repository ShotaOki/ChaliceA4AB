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
import { Button, Spinner } from "@cloudscape-design/components";
import { Flex } from "@aws-amplify/ui-react";
import { StateSchemaType } from "../actionTypes/StateModelTypes";

const ChatArea: React.FC = () => {
  const chat = useChat();
  const state = useState();
  const stateModel = useStateModel();
  const agent = useAgentsForAmazonBedrock();

  useEffect(() => {
    const initialState: StateSchemaType = {};
    state.setState(initialState);
    const proc = stateModel.readNextProc(initialState);

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
            {chat.isConnecting && (
              <Message
                model={{
                  direction: "incoming",
                  type: "custom",
                  position: "first",
                }}
              >
                <Message.Header sender="店員" />
                <Message.CustomContent>
                  <Spinner></Spinner>
                  お待ち下さい...
                </Message.CustomContent>
              </Message>
            )}
          </MessageList>
          <MessageInput
            disabled={chat.isConnecting}
            placeholder="Type message here"
            attachDisabled
            attachButton={false}
            onSend={(textContent) => {
              // 通知: 完了した
              const onFinished = () => {
                chat.received(
                  "ご注文を承りました。ありがとうございました。お席でおまちください"
                );
              };
              // チャットを送信する
              chat.send(textContent);
              // AIエージェントから結果を取得、更新する
              const nextAgent = stateModel.readNextProc(state.state);
              if (nextAgent?.dialog) {
                chat.startLoading();
                agent
                  .instant(nextAgent.aiMessage, textContent)
                  .then((result) => {
                    let current = undefined;
                    if (result === true && nextAgent.dialog) {
                      current = nextAgent.dialog.yes(state);
                    } else if (result === false && nextAgent.dialog) {
                      current = nextAgent.dialog.no(state);
                    } else {
                      chat.received(
                        "判断がつきませんでした。もう一度お願いします"
                      );
                    }
                    if (current) {
                      // AIエージェントから結果を取得、更新する
                      const proc = stateModel.readNextProc(current);
                      if (proc) {
                        chat.received(proc.aiMessage);
                      } else {
                        onFinished();
                      }
                    }
                  })
                  .finally(() => {
                    chat.stopLoading();
                  });
              } else if (nextAgent?.agent) {
                chat.startLoading();
                agent
                  .send(textContent, nextAgent.agent)
                  .then((response) => {
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
                      onFinished();
                    }
                  })
                  .finally(() => {
                    chat.stopLoading();
                  });
              } else {
                onFinished();
              }
            }}
          />
        </ChatContainer>
      </MainContainer>
    </div>
  );
};

export default ChatArea;
