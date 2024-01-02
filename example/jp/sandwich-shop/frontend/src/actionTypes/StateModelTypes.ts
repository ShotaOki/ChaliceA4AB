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
