import { create } from "zustand";
import {
  OrderSchemaOptionType,
  OrderSchemaType,
  StateSchemaType,
} from "../actionTypes/StateModelTypes";

const useStateContent = create<{
  state: StateSchemaType;
  setState: (s: StateSchemaType) => void;
  appendOrder: (s: OrderSchemaType) => StateSchemaType;
  updateOrder: (s: OrderSchemaOptionType, index: number) => StateSchemaType;
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
      // Ephemeral領域をクリアする
      response.ephemeral = undefined;
      set(() => {
        return {
          state: response,
        };
      });
      return response;
    },
    updateOrder(s: OrderSchemaOptionType, index: number) {
      const current = get().state;
      const response = current;
      if (response.order) {
        response.order[index] = {
          ...response.order[index],
          ...s,
        };
      }
      // Ephemeral領域をクリアする
      response.ephemeral = undefined;
      set(() => {
        return {
          state: response,
        };
      });
      return response;
    },
    appendState(s: StateSchemaType) {
      const current = get().state;
      // Ephemeral領域をクリアする
      current.ephemeral = undefined;
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
  const { state, setState, appendOrder, appendState, updateOrder } =
    useStateContent();
  return {
    state,
    setState,
    appendState,
    appendOrder,
    updateOrder,
  };
};

export default useState;
