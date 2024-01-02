import {
  BedrockAgentRuntimeClient,
  InvokeAgentCommand,
} from "@aws-sdk/client-bedrock-agent-runtime";
import { AgentInfo } from "../actionTypes/StateModelTypes";
import { Auth } from "aws-amplify";
import { AgentResponse } from "./AgentResponse";

const useAgentsForAmazonBedrock = () => {
  const getClient = async () => {
    const creds = await Auth.currentUserCredentials();
    return new BedrockAgentRuntimeClient({
      region: "us-east-1",
      credentials: creds,
    });
  };

  return {
    async send(inputText: string, agent: AgentInfo) {
      let result = "";
      const time = new Date().getTime() % 10000;
      const client = await getClient();
      // エージェントにリクエストを送信する
      const { sessionId, completion } = await client.send(
        new InvokeAgentCommand({
          agentId: agent.id,
          agentAliasId: agent.aliasId,
          sessionId: `${time}`,
          endSession: false,
          inputText: inputText,
        })
      );
      if (completion) {
        // 結果を取得する
        const decoder = new TextDecoder();
        for await (const itr of completion) {
          result += decoder.decode(itr.chunk?.bytes, {
            stream: true,
          });
        }
      }
      // セッションを終了する
      await client.send(
        new InvokeAgentCommand({
          agentId: agent.id,
          agentAliasId: agent.aliasId,
          sessionId: sessionId,
          endSession: true,
          inputText: "close session",
        })
      );
      return new AgentResponse(result);
    },
  };
};

export default useAgentsForAmazonBedrock;
