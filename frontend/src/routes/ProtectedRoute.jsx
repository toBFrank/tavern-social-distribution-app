import React from 'react';
import { Route, Navigate } from 'react-router-dom';
import Cookie from 'js-cookie';

const ProtectedRoute = ({ children }) => {
  const isAuthenticated = !!Cookie.get('author_id');
  if (!isAuthenticated) {
    // Redirect to login page if not authenticated
    return <Navigate to="/login" />;
  }

  // Render the protected page if authenticated
  return children;
};

export default ProtectedRoute;
