import { create } from "zustand";
import {
  OrderSchemaType,
  StateSchemaType,
} from "../actionTypes/StateModelTypes";

const useStateContent = create<{
  state: StateSchemaType;
  setState: (s: StateSchemaType) => void;
  appendOrder: (s: OrderSchemaType) => StateSchemaType;
  appendState: (s: StateSchemaType) => StateSchemaType;
}>((set, get) => {
  return {
    state: {},
    setState(s: StateSchemaType) {
      set(() => {
        return {
          state: s,
        };
      });
    },
    appendOrder(s: OrderSchemaType) {
      const current = get().state;
      const response = current;
      if (response.order) {
        response.order.push(s);
      } else {
        response.order = [s];
      }
      set(() => {
        return {
          state: response,
        };
      });
      return response;
    },
    appendState(s: StateSchemaType) {
      const current = get().state;
      set(() => {
        return {
          state: {
            ...current,
            ...s,
          },
        };
      });
      return {
        ...current,
        ...s,
      };
    },
  };
});

const useState = () => {
  const { state, setState, appendOrder, appendState } = useStateContent();
  return {
    state,
    setState,
    appendState,
    appendOrder,
  };
};

export default useState;
