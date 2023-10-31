import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";

const router = createBrowserRouter([
  {
    path: "/react-test",
    element: <App />,
  },
  {
    path: "/react-routing-test",
    element: <div>Wow this worked</div>
  },
  {
    path: "*",
    element:
      <div style={{ textAlign: 'center' }}>
        <br /><br />
        <h1 style={{ color: "#621ae7" }}>404</h1>
        <h1>Page not found.</h1><br />
        <a href="/">Home Page</a>
      </div>
  }
]);

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
