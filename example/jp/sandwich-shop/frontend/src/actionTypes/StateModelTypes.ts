export type AgentInfo = {
  id: string;
  aliasId: string;
};

export type AgentModelParameter = {
  priority: number;
  aiMessage: string;
  agent?: AgentInfo;
};

export type OrderSchemaType = {
  id: string;
  name: string;
  count: number;
  bread?: string;
  dressing?: string;
  topping?: string[];
};

export type StateSchemaType = {
  eatIn?: boolean;
  order?: OrderSchemaType[];
  confirmed?: boolean;
};

export const AgentActionType = {
  APPEND_ORDER: "json_control.append_order",
  UPDATE_JSON_PARTIAL: "json_control.update_partial",
  EXECUTE_JS: "execute.javascript",
  MESSAGE: "message",
};
