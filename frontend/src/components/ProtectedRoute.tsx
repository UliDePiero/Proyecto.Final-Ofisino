/* eslint-disable react/jsx-props-no-spreading */
import * as React from 'react';
import { Redirect, Route, RouteProps } from 'react-router-dom';
import { CredentialsContext } from '../contexts/credentialsContext';
import { LoginContext } from '../types/common/types';

interface ProtectedRouteProps extends RouteProps {}
const ProtectedRoute: React.FunctionComponent<ProtectedRouteProps> = ({ ...routeProps }) => {
	const { isLoggedIn } = React.useContext<LoginContext>(CredentialsContext);
	return isLoggedIn ? <Route {...routeProps} /> : <Redirect to="/" />;
};

export default ProtectedRoute;
