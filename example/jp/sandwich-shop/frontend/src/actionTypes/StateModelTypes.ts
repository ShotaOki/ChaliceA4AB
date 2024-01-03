export type AgentInfo = {
  id: string;
  aliasId: string;
};

export type DialogInfo = {
  yes: (state: any) => StateSchemaType;
  no: (state: any) => StateSchemaType;
};

export type AgentModelParameter = {
  priority: number;
  aiMessage: string;
  agent?: AgentInfo;
  dialog?: DialogInfo;
};

export type OrderSchemaOptionType = {
  bread?: string;
  dressing?: string;
  topping?: string[];
};

export type OrderSchemaType = OrderSchemaOptionType & {
  id: string;
  name: string;
  count: number;
};

export type StateSchemaType = {
  eatIn?: boolean;
  order?: OrderSchemaType[];
  askFlg?: boolean;
  confirmed?: boolean;
};

export const AgentActionType = {
  APPEND_ORDER: "json_control.append_order",
  UPDATE_ORDER: "json_control.update_order",
  UPDATE_JSON_PARTIAL: "json_control.update_partial",
  EXECUTE_JS: "execute.javascript",
  MESSAGE: "message",
};
