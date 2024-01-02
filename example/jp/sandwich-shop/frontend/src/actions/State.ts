import { create } from "zustand";
import { StateSchemaType } from "../actionTypes/StateModelTypes";

const useStateContent = create<{
  state: StateSchemaType;
  setState: (s: StateSchemaType) => void;
  appendState: (s: StateSchemaType) => StateSchemaType;
}>((set, get) => {
  return {
    state: {},
    setState(s: any) {
      set(() => {
        return {
          state: s,
        };
      });
    },
    appendState(s: any) {
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
  const { state, setState, appendState } = useStateContent();
  return {
    state,
    setState,
    appendState,
  };
};

export default useState;
