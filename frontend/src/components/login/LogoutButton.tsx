import { ListItem, ListItemIcon, ListItemText } from '@material-ui/core';
import axios from 'axios';
import { makeStyles, Theme } from '@material-ui/core/styles';
import * as React from 'react';
import ExitToAppOutlinedIcon from '@material-ui/icons/ExitToAppOutlined';
import { useGoogleLogout } from 'react-google-login';
import { useHistory } from 'react-router-dom';
import { CredentialsContext } from '../../contexts/credentialsContext';
import { LoginContext } from '../../types/common/types';

const useStyles = makeStyles((theme: Theme) => ({
	button: {
		color: theme.palette.primary.contrastText,
		alignItems: 'center',
	},
}));

const base = process.env.REACT_APP_BASE_URL;

const getToLogOutInBackend = async () => {
	await axios
		.get(`${base}/logout`)
		.then((response: any) => {
			console.log(response);
		})
		.catch((err: any) => {
			console.log(err);
		});
};

const LogoutButton: React.FunctionComponent = () => {
	const classes = useStyles();
	const history = useHistory();
	const {
		setEmail,
		setUserId,
		clientId,
		setIsLoggedIn,
		setIsAdmin,
		officeInstance,
		setName,
		setAvatarUrl,
	} = React.useContext<LoginContext>(CredentialsContext);
	const onLogoutSuccess = (): void => {
		console.log('[Logout Success]');
		setEmail('');
		setUserId(0);
		setIsLoggedIn(false);
		setIsAdmin(false);
		setName!('');
		setAvatarUrl!('');
		getToLogOutInBackend();
		history.push('/');
	};
	const onFailure = (): void => {
		console.log('[Logout failed] Error');
	};
	const { signOut } = useGoogleLogout({
		clientId,
		onLogoutSuccess,
		onFailure,
	});
	const signOutHandler = (): void => {
		const states = ['email', 'userId', 'isLoggedIn', 'isAdmin', 'name', 'avatarUrl', 'domainId'];
		states.forEach((state) => {
			localStorage.removeItem(`Ofisino_${state}`);
		});
		if (officeInstance) {
			officeInstance.logout();
			getToLogOutInBackend();
		} else {
			signOut();
		}
	};

	return (
		<ListItem button onClick={signOutHandler}>
			<ListItemIcon className={classes.button}>
				<ExitToAppOutlinedIcon />
			</ListItemIcon>
			<ListItemText primary="Salir" className={classes.button} />
		</ListItem>
	);
};

export default LogoutButton;
