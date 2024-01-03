import {
  BedrockAgentRuntimeClient,
  InvokeAgentCommand,
} from "@aws-sdk/client-bedrock-agent-runtime";
import { AgentInfo } from "../actionTypes/StateModelTypes";
import { Auth } from "aws-amplify";
import { AgentResponse } from "./AgentResponse";
import { v4 } from "uuid";
import {
  BedrockRuntimeClient,
  InvokeModelCommand,
} from "@aws-sdk/client-bedrock-runtime";

const useAgentsForAmazonBedrock = () => {
  const getClient = async () => {
    const creds = await Auth.currentUserCredentials();
    return new BedrockAgentRuntimeClient({
      region: import.meta.env.VITE_APP_A4AB_SANDWICH_SHOP_BACKEND_REGION,
      credentials: creds,
    });
  };
  const getInstantClient = async () => {
    const creds = await Auth.currentUserCredentials();
    return new BedrockRuntimeClient({
      region: import.meta.env.VITE_APP_A4AB_SANDWICH_SHOP_BACKEND_REGION,
      credentials: creds,
    });
  };

  return {
    async send(inputText: string, agent: AgentInfo) {
      let result = "";
      const client = await getClient();
      // エージェントにリクエストを送信する
      const { sessionId, completion } = await client.send(
        new InvokeAgentCommand({
          agentId: agent.id,
          agentAliasId: agent.aliasId,
          sessionId: v4(),
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
    async instant(
      ask: string,
      body: string,
      modelId: string = "anthropic.claude-instant-v1"
    ) {
      const prompt = [
        "Human: あなたは受け取った返事が「はい」か「いいえ」かを分類することができます。",
        "ユーザーの入力が「はい」、または肯定ならば、結果は以下のフォーマットで返してください",
        "result:y",
        "ユーザーの入力が「いいえ」、または否定ならば、結果は以下のフォーマットで返してください",
        "result:n",
        "",
        "<ask></ask>タグ内の質問に対して、<content></content>タグ内の応答がありました。",
        "contentの質問が「はい」か「いいえ」かを判定してください。",
        "<ask>",
        ask,
        "</ask>",
        "<content>",
        body,
        "</content>",
        "",
        "",
        "Assistant:",
      ].join("\n");

      const client = await getInstantClient();
      const command = new InvokeModelCommand({
        body: JSON.stringify({
          prompt: prompt,
          max_tokens_to_sample: 300,
          temperature: 0,
          top_k: 250,
          top_p: 0.999,
          stop_sequences: ["\n\nHuman:"],
          anthropic_version: "bedrock-2023-05-31",
        }),
        modelId: modelId,
        contentType: "application/json",
        accept: "application/json",
      });
      const response = await client.send(command);
      // 結果を取得する
      const decoder = new TextDecoder();
      const jsonData = decoder.decode(response.body.buffer).toLowerCase();
      const result = JSON.parse(jsonData)["completion"];
      // yから始まるとき
      if (result.startsWith("y")) {
        return true;
      }
      // ｎから始まるとき
      if (result.startsWith("n")) {
        return false;
      }
      // ｙまたはnのどちらかを含むとき
      if (result.includes("y") != result.includes("n")) {
        return result.includes("y");
      }
      // yとnを含むとき
      if (result.includes("y")) {
        return result.indexOf("y") < result.indexOf("n") ? true : false;
      }
      // どちらも回答がないとき
      return undefined;
    },
  };
};

export default useAgentsForAmazonBedrock;
