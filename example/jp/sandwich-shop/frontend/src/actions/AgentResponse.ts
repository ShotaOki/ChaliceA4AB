import {
  AgentActionType,
  OrderSchemaType,
  StateSchemaType,
} from "../actionTypes/StateModelTypes";
import z from "zod";

const AgentActionSchema = z.object({
  action: z.union([
    z.literal(AgentActionType.APPEND_ORDER),
    z.literal(AgentActionType.UPDATE_JSON_PARTIAL),
    z.literal(AgentActionType.EXECUTE_JS),
    z.literal(AgentActionType.MESSAGE),
  ]),
  value: z.any(),
});

export class AgentResponse {
  private _action: string;
  private _value: any;

  constructor(value: string) {
    try {
      const agent = AgentActionSchema.parse(JSON.parse(value));
      this._action = agent.action;
      this._value = agent.value ?? {};
    } catch {
      this._action = AgentActionType.MESSAGE;
      this._value = value;
    }
  }

  get action() {
    return this._action;
  }

  get appendOrderValue(): OrderSchemaType | undefined {
    if (this._action !== AgentActionType.APPEND_ORDER) {
      return undefined;
    }
    return this._value as OrderSchemaType;
  }

  get jsonPartialValue(): StateSchemaType {
    if (this._action !== AgentActionType.UPDATE_JSON_PARTIAL) {
      return {};
    }
    return this._value as StateSchemaType;
  }

  get message(): string {
    if (this._action !== AgentActionType.MESSAGE) {
      return "-";
    }
    return this._value as string;
  }

  get jsCommand(): string {
    if (this._action !== AgentActionType.EXECUTE_JS) {
      return "-";
    }
    return this._value as string;
  }
}
