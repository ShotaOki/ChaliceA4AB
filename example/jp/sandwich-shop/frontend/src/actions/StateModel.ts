import z from "zod";

type AgentInfo = {
  id: string;
  aliasId: string;
};

type AgentModelParameter = {
  priority: number;
  aiMessage: string;
  agent?: AgentInfo;
};

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

const OrderSchema = z.object({
  id: z.string(),
  name: z.string(),
  count: z.number().gte(1),
  bread: AgentStringType({
    required: {
      priority: 11,
      aiMessage: "パンの種類を選んでください",
    },
  }),
  dressing: AgentStringType({
    required: {
      priority: 12,
      aiMessage: "ドレッシングの種類を選んでください",
    },
  }),
  topping: AgentOptionType({
    required: {
      priority: 13,
      aiMessage: "トッピングの希望はございますか",
    },
  }),
});

const StateSchema = z.object({
  eatIn: AgentBooleanType({
    required: {
      priority: 99999,
      aiMessage: "店内のご利用でよろしいですか？",
    },
  }),
  order: AgentOrderType(OrderSchema, {
    required: {
      priority: 1,
      aiMessage: "ご注文をどうぞ",
    },
    waiting: {
      priority: 2,
      aiMessage: "ご注文はございませんか？",
    },
  }),
  confirmed: AgentBooleanType({
    required: {
      priority: 9999,
      aiMessage: "ご注文は以上でよろしいでしょうか",
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
