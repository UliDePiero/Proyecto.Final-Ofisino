import * as React from 'react';
import { ThemeProvider } from '@material-ui/styles';
import { Switch, Route, BrowserRouter } from 'react-router-dom';
import Error from './containers/Error';
import Calendar from './containers/Calendar';
import './App.css';
import AuthProvider from './contexts/credentialsContext';
import Login from './containers/Login';
import Reservations from './containers/Reservations';
import Buildings from './containers/Buildings';
import WorkingSpaces from './containers/WorkingSpaces';
import MeetingRooms from './containers/MeetingRooms';
import OrganizeMeetings from './containers/OrganizeMeetings';
import Boxes from './containers/Boxes';
import ProtectedRoute from './components/ProtectedRoute';
import appTheme from './themes/themes';
import Meetings from './containers/Meetings';
import Reports from './containers/Reports';

const App: React.FunctionComponent = () => {
	return (
		<ThemeProvider theme={appTheme}>
			<AuthProvider>
				<div className="App">
					<BrowserRouter>
						<Switch>
							<Route path="/" component={Login} exact />
							<ProtectedRoute path="/home" component={Calendar} />
							<ProtectedRoute path="/meeting" component={Meetings} />
							<ProtectedRoute path="/reservation" component={Reservations} />
							<ProtectedRoute path="/organizemeeting" component={OrganizeMeetings} />
							<ProtectedRoute path="/building" component={Buildings} />
							<ProtectedRoute path="/workingspace" component={WorkingSpaces} />
							<ProtectedRoute path="/meetingroom" component={MeetingRooms} />
							<ProtectedRoute path="/box" component={Boxes} />
							<ProtectedRoute path="/reports" component={Reports} />
							<Route>
								<Error label="Ups... página no encontrada" />
							</Route>
						</Switch>
					</BrowserRouter>
				</div>
			</AuthProvider>
		</ThemeProvider>
	);
};

export default App;
