import { Button, SvgIcon } from '@material-ui/core';
import { makeStyles, Theme } from '@material-ui/core/styles';
import axios from 'axios';
import * as React from 'react';
import MicrosoftLogin from 'react-microsoft-login';
import { useHistory } from 'react-router-dom';
import validEmailDomain from '../../utils/loginUtils';
import { CredentialsContext } from '../../contexts/credentialsContext';
import { LoginContext } from '../../types/common/types';

type OfficeUser = {
	accountIdentifier: string;
	userName: string;
	name: string;
};
const useStyles = makeStyles((theme: Theme) => ({
	button: {
		color: theme.palette.primary.contrastText,
		background: theme.palette.primary.main,
		margin: theme.spacing(1, 0, 1),
		width: '225px',
		borderRadius: '150px',
	},
}));
type LoginMicrosoftButtonProps = {
	onSetErrorMessage: (message: string) => void;
};

const base = process.env.REACT_APP_BASE_URL;

const LoginMicrosoftButton: React.FunctionComponent<LoginMicrosoftButtonProps> = ({
	onSetErrorMessage,
}: LoginMicrosoftButtonProps) => {
	const classes = useStyles();
	const CLIENT_ID = 'b2a1b1e3-1366-4e48-8ced-ca234d29ffd8';
	const { setEmail, setUserId, setIsAdmin, setIsLoggedIn, setOfficeInstance, setName, isLoggedIn } =
		React.useContext<LoginContext>(CredentialsContext);
	const history = useHistory();
	const authHandler = async (err: any, data: any, msal: any) => {
		if (!err && data && (await validEmailDomain(data.account.userName)) && !isLoggedIn) {
			setEmail(data.account.userName);
			setIsLoggedIn(true);
			setName!(data.account.name);
			postCredentials(data.account);
			if (msal) {
				setOfficeInstance!(msal);
			}
		} else {
			setEmail('');
			setUserId(0);
			setIsLoggedIn(false);
			setIsAdmin(false);
			onSetErrorMessage('El usuario no pertenece a la organización');
			console.log(err);
		}
	};
	const postCredentials = async ({ accountIdentifier, userName, name }: OfficeUser) => {
		await axios
			.post(`${base}/login`, {
				email: userName,
				domain_id: accountIdentifier,
				name,
			})
			.then((response) => {
				console.log(response);
				setUserId(response.data.data.id);
				setIsAdmin(response.data.data.admin);
				history.push('/home');
			})
			.catch((err) => {
				setEmail('');
				setUserId(0);
				setIsLoggedIn(false);
				setIsAdmin(false);
				onSetErrorMessage('El usuario no pertenece a la organización');
				console.log(err);
			});
	};

	return (
		<MicrosoftLogin clientId={CLIENT_ID} authCallback={authHandler}>
			<Button
				className={classes.button}
				startIcon={
					<SvgIcon>
						<path d="M11.55 21H3v-8.55h8.55V21zM21 21h-8.55v-8.55H21V21zm-9.45-9.45H3V3h8.55v8.55zm9.45 0h-8.55V3H21v8.55z" />
					</SvgIcon>
				}
			>
				Login con M365
			</Button>
		</MicrosoftLogin>
	);
};

export default LoginMicrosoftButton;
