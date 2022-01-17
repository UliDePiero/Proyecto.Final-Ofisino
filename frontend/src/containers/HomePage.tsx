import * as React from 'react';
import { makeStyles, Theme } from '@material-ui/core/styles';
import Drawer from '../components/common/Drawer';
import { CredentialsContext } from '../contexts/credentialsContext';

const useStyles = makeStyles((theme: Theme) => ({
	toolbar: {
		display: 'flex',
		alignItems: 'center',
		justifyContent: 'flex-end',
		padding: theme.spacing(0, 1),
		// necessary for content to be below app bar
		...theme.mixins.toolbar,
	},
}));

const getCalendarUrl = (email: string): string => {
	console.log(`https://calendar.google.com/calendar/embed?src=${encodeURI(email)}`);
	return `https://calendar.google.com/calendar/embed?src=${encodeURI(email)}`;
};

const HomePage: React.FunctionComponent = () => {
	const classes = useStyles();
	return (
		<>
			<Drawer />
			<div className={classes.toolbar} />
			<CredentialsContext.Consumer>
				{({ email }) => (
					<iframe title="Calendar" src={getCalendarUrl(email)} width="90%" height="650" />
				)}
			</CredentialsContext.Consumer>
		</>
	);
};

export default HomePage;
