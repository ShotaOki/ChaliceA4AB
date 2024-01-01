import React from 'react';
import { Authenticator } from '@aws-amplify/ui-react';
import { Amplify } from 'aws-amplify';
import '@aws-amplify/ui-react/styles.css';

const App: React.FC = () => {

  Amplify.configure({
    Auth: {
      userPoolId: import.meta.env.VITE_APP_A4AB_SANDWICH_SHOP_BACKEND_USERPOOLIDOUTPUT,
      userPoolWebClientId: import.meta.env.VITE_APP_A4AB_SANDWICH_SHOP_BACKEND_APPLICATIONCLIENTOUTPUT,
      identityPoolId: import.meta.env.VITE_APP_A4AB_SANDWICH_SHOP_BACKEND_IDENTITYPOOLOUTPUT,
      authenticationFlowType: 'USER_SRP_AUTH',
    },
  });

  return (
    <Authenticator>
      {() => (
        <div>
          Data
        </div>
      )}
    </Authenticator>
  );
};

export default App;