import {
  AgentActionType,
  OrderSchemaOptionType,
  OrderSchemaType,
  StateSchemaType,
} from "../actionTypes/StateModelTypes";
import z from "zod";

const AgentActionSchema = z.object({
  action: z.union([
    z.literal(AgentActionType.APPEND_ORDER),
    z.literal(AgentActionType.UPDATE_JSON_PARTIAL),
    z.literal(AgentActionType.EXECUTE_JS),
    z.literal(AgentActionType.UPDATE_ORDER),
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

  get isAppendOrderAction() {
    if (this._action == AgentActionType.APPEND_ORDER) {
      return true;
    }
    return false;
  }

  get isUpdateOrderAction() {
    if (this._action == AgentActionType.UPDATE_ORDER) {
      return true;
    }
    return false;
  }

  get isUpdateJsonPartialAction() {
    if (this._action == AgentActionType.UPDATE_JSON_PARTIAL) {
      return true;
    }
    return false;
  }

  get isJsCommandAction() {
    if (this._action == AgentActionType.EXECUTE_JS) {
      return true;
    }
    return false;
  }

  get isMessageAction() {
    if (this._action == AgentActionType.MESSAGE) {
      return true;
    }
    return false;
  }

  get appendOrderValue(): OrderSchemaType | undefined {
    if (this._action !== AgentActionType.APPEND_ORDER) {
      return undefined;
    }
    return this._value as OrderSchemaType;
  }

  get updateOrderValue(): OrderSchemaOptionType | undefined {
    if (this._action !== AgentActionType.UPDATE_ORDER) {
      return undefined;
    }
    return this._value as OrderSchemaOptionType;
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
