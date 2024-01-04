import {
  Card,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from "@aws-amplify/ui-react";
import React from "react";
import ColumnLayout from "@cloudscape-design/components/column-layout";
import useState from "../actions/State";

const OrderArea: React.FC = () => {
  const state = useState();

  return (
    <div style={{ position: "relative", height: "100vh", padding: "1rem" }}>
      <Card>
        {state.state.order === undefined && <div>注文を待っています...</div>}
        {state.state.order && (
          <Table caption="" highlightOnHover={false} variation="bordered">
            <TableHead>
              <TableRow>
                <TableCell as="th">品名</TableCell>
                <TableCell as="th">オプション</TableCell>
                <TableCell as="th">数量</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(state.state.order ?? []).map((item) => (
                <TableRow key={item.id}>
                  <TableCell>{item.name}</TableCell>
                  <TableCell>
                    <ColumnLayout
                      borders="horizontal"
                      columns={2}
                      disableGutters
                    >
                      {item.bread && <div>パン：{item.bread}</div>}
                      {item.dressing && (
                        <div>ドレッシング：{item.dressing}</div>
                      )}
                      {(item.topping ?? []).map((topping) => (
                        <div key={topping}>トッピング：{topping}</div>
                      ))}
                    </ColumnLayout>
                  </TableCell>
                  <TableCell>{item.count ?? " - "}個</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>
    </div>
  );
};

export default OrderArea;
