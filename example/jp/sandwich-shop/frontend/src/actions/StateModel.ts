import z from "zod";
import {
  AgentInfo,
  AgentModelParameter,
  StateSchemaType,
} from "../actionTypes/StateModelTypes";

const addAgentModelIssue = (
  ctx: z.RefinementCtx,
  parameter: AgentModelParameter
) => {
  ctx.addIssue({
    code: z.ZodIssueCode.custom,
    message: parameter.aiMessage,
    aiMessage: parameter.aiMessage,
    priority: parameter.priority,
    agent: parameter.agent ?? {},
    dialog: parameter.dialog ?? null,
  } as any);
};

const AgentBooleanType = (parameter: { [key: string]: AgentModelParameter }) =>
  z
    .boolean()
    .optional()
    .superRefine((val, ctx) => {
      if (val === undefined) {
        addAgentModelIssue(ctx, parameter["required"]);
      }
    });

const AgentFlagType = (parameter: { [key: string]: AgentModelParameter }) =>
  z
    .boolean()
    .optional()
    .superRefine((val, ctx) => {
      if (val !== undefined && val == true) {
        addAgentModelIssue(ctx, parameter["true"]);
      }
    });

const AgentNumberType = (parameter: { [key: string]: AgentModelParameter }) =>
  z
    .number()
    .optional()
    .superRefine((val, ctx) => {
      if (val === undefined) {
        addAgentModelIssue(ctx, parameter["required"]);
        return z.INVALID;
      }
    });

const AgentStringType = (parameter: { [key: string]: AgentModelParameter }) =>
  z
    .string()
    .optional()
    .superRefine((val, ctx) => {
      if (val === undefined) {
        addAgentModelIssue(ctx, parameter["required"]);
        return z.INVALID;
      }
    });

const AgentOptionType = (parameter: { [key: string]: AgentModelParameter }) =>
  z
    .array(z.string())
    .optional()
    .superRefine((val, ctx) => {
      if (val === undefined) {
        addAgentModelIssue(ctx, parameter["required"]);
        return z.INVALID;
      }
    });

const AgentOrderType = (
  schema: any,
  parameter: { [key: string]: AgentModelParameter }
) =>
  z
    .array(schema)
    .optional()
    .superRefine((val, ctx) => {
      if (val === undefined) {
        addAgentModelIssue(ctx, parameter["required"]);
        return z.INVALID;
      }
      if (val?.length === 0) {
        addAgentModelIssue(ctx, parameter["waiting"]);
        return z.INVALID;
      }
    });

const AGENT_ASK_TO_ORDER: AgentInfo = {
  id: import.meta.env.VITE_ASK_TO_ORDER_AGENTID,
  aliasId: import.meta.env.VITE_ASK_TO_ORDER_AGENTALIASID,
};
const AGENT_ASK_TO_BREAD_TYPE: AgentInfo = {
  id: import.meta.env.VITE_ASK_TO_BREAD_TYPE_AGENTID,
  aliasId: import.meta.env.VITE_ASK_TO_BREAD_TYPE_AGENTALIASID,
};
const AGENT_ASK_TO_DRESSING: AgentInfo = {
  id: import.meta.env.VITE_ASK_TO_DRESSING_AGENTID,
  aliasId: import.meta.env.VITE_ASK_TO_DRESSING_AGENTALIASID,
};
const AGENT_CONFIRM_TO_ORDER: AgentInfo = {
  id: import.meta.env.VITE_ASK_TO_OPTIONS_AGENTID,
  aliasId: import.meta.env.VITE_ASK_TO_OPTIONS_AGENTALIASID,
};

const OrderSchema = z.object({
  id: z.string(),
  name: z.string(),
  count: z.number().gte(1),
  bread: AgentStringType({
    required: {
      priority: 11,
      aiMessage: "パンの種類を選んでください",
      agent: AGENT_ASK_TO_BREAD_TYPE,
    },
  }),
  dressing: AgentStringType({
    required: {
      priority: 12,
      aiMessage: "ドレッシングの種類を選んでください",
      agent: AGENT_ASK_TO_DRESSING,
    },
  }),
});

const StateSchema = z.object({
  eatIn: AgentBooleanType({
    required: {
      priority: 99999,
      aiMessage: "店内のご利用でよろしいですか？",
      dialog: {
        yes(state: any) {
          const update: StateSchemaType = {
            eatIn: true,
          };
          return state.appendState(update);
        },
        no(state: any) {
          const update: StateSchemaType = {
            eatIn: false,
          };
          return state.appendState(update);
        },
      },
    },
  }),
  commitOrder: AgentBooleanType({
    required: {
      priority: 999999,
      aiMessage:
        "ご注文を承りました。料金はxxxx円となります。お間違いがなければ、「はい」とお答えをお願いします。",
      agent: AGENT_CONFIRM_TO_ORDER,
    },
  }),
  order: AgentOrderType(OrderSchema, {
    required: {
      priority: 1,
      aiMessage: "ご注文をどうぞ",
      agent: AGENT_ASK_TO_ORDER,
    },
    waiting: {
      priority: 2,
      aiMessage: "ご注文はございませんか？",
      agent: AGENT_ASK_TO_ORDER,
    },
  }),
  ephemeral: z
    .object({
      askFlg: AgentFlagType({
        true: {
          priority: 9900,
          aiMessage: "ご注文をどうぞ",
          agent: AGENT_ASK_TO_ORDER,
        },
      }),
    })
    .optional(),
  confirmed: AgentBooleanType({
    required: {
      priority: 9999,
      aiMessage: "ご注文は以上でよろしいでしょうか",
      dialog: {
        yes(state: any) {
          const update: StateSchemaType = {
            confirmed: true,
          };
          return state.appendState(update);
        },
        no(state: any) {
          const update: StateSchemaType = {
            ephemeral: {
              askFlg: true,
            },
          };
          return state.appendState(update);
        },
      },
    },
  }),
});

type ReadNextProcResult = AgentModelParameter & {
  path: any[];
};

const useStateModel = () => {
  return {
    readNextProc(state: any): ReadNextProcResult | undefined {
      try {
        StateSchema.parse(state);
      } catch (e: any) {
        const issues: AgentModelParameter[] = e.issues;
        const issueList = issues
          .filter((issue) => (issue.priority ?? 0) >= 1)
          .sort((a, b) => a.priority - b.priority);
        if (issueList.length >= 1) {
          return issueList[0] as any;
        }
      }
      return undefined;
    },
  };
};

export default useStateModel;
