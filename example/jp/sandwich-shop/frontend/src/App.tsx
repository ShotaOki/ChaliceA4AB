import React from "react";
import { Authenticator } from "@aws-amplify/ui-react";
import { Amplify } from "aws-amplify";
import Grid from "@cloudscape-design/components/grid";
import ChatArea from "./components/ChatArea";
import OrderArea from "./components/OrderArea";
import "@aws-amplify/ui-react/styles.css";
import "./App.css";

const App: React.FC = () => {
  Amplify.configure({
    Auth: {
      region: import.meta.env.VITE_APP_A4AB_SANDWICH_SHOP_BACKEND_REGION,
      identityPoolRegion: import.meta.env
        .VITE_APP_A4AB_SANDWICH_SHOP_BACKEND_REGION,
      userPoolId: import.meta.env
        .VITE_APP_A4AB_SANDWICH_SHOP_BACKEND_USERPOOLIDOUTPUT,
      userPoolWebClientId: import.meta.env
        .VITE_APP_A4AB_SANDWICH_SHOP_BACKEND_APPLICATIONCLIENTOUTPUT,
      identityPoolId: import.meta.env
        .VITE_APP_A4AB_SANDWICH_SHOP_BACKEND_IDENTITYPOOLOUTPUT,
      authenticationFlowType: "USER_SRP_AUTH",
    },
  });

  return (
    <Authenticator>
      {() => (
        <div style={{ width: "100%" }}>
          <Grid
            gridDefinition={[{ colspan: 6 }, { colspan: 6 }]}
            disableGutters
          >
            <div>
              <ChatArea></ChatArea>
            </div>
            <div>
              <OrderArea></OrderArea>
            </div>
          </Grid>
        </div>
      )}
    </Authenticator>
  );
};

export default App;
