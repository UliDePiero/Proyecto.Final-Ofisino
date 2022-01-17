import { Button, SvgIcon } from '@material-ui/core';
import { makeStyles, Theme } from '@material-ui/core/styles';
import * as React from 'react';
import axios from 'axios';
import GoogleLogin, { GoogleLoginResponse, GoogleLoginResponseOffline } from 'react-google-login';
import { useHistory } from 'react-router-dom';
import validEmailDomain from '../../utils/loginUtils';
import { CredentialsContext } from '../../contexts/credentialsContext';
import { LoginContext } from '../../types/common/types';
import refreshTokenSetup from '../../utils/refreshToken';
import { saveOnLocalStorage } from '../../utils/Context';

type UserCredentials = {
	email: string;
	domainId: string;
	name: string;
	avatarUrl: string;
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

interface LoginGoogleButtonProps {
	onsetErrorMessage: (message: string) => void;
}

const base = process.env.REACT_APP_BASE_URL;

const LoginGoogleButton: React.FunctionComponent<LoginGoogleButtonProps> = ({
	onsetErrorMessage,
}: LoginGoogleButtonProps) => {
	const classes = useStyles();
	const history = useHistory();
	const { clientId, setEmail, setUserId, setIsAdmin, setIsLoggedIn, setAvatarUrl, setName } =
		React.useContext<LoginContext>(CredentialsContext);
	const onSuccess = async (
		res: GoogleLoginResponse | GoogleLoginResponseOffline
	): Promise<void> => {
		const response = res as GoogleLoginResponse;
		if (await validEmailDomain(response.profileObj.email)) {
			console.log('[Login Success] currentUser:', response.profileObj);
			setEmail(response.profileObj.email);
			setIsLoggedIn(true);
			const { email, googleId, imageUrl, name } = response.profileObj;
			setAvatarUrl!(imageUrl);
			setName!(name);
			postCredentials({ email, domainId: googleId, name, avatarUrl: imageUrl });
			saveOnLocalStorage([
				// eslint-disable-next-line object-shorthand
				{ key: 'email', value: email },
				{ key: 'domainId', value: googleId },
				{ key: 'name', value: name },
				{ key: 'avatarUrl', value: imageUrl },
				{ key: 'isLoggedIn', value: 'true' },
			]);
			refreshTokenSetup(res);
		} else {
			setEmail('');
			setUserId(0);
			setIsLoggedIn(false);
			setIsAdmin(false);
			onsetErrorMessage('El usuario no pertenece a la organización');
		}
	};
	const postCredentials = async ({ email, domainId, name, avatarUrl }: UserCredentials) => {
		await axios
			.post(`${base}/login`, {
				email,
				domain_id: domainId,
				name,
				avatar_url: avatarUrl,
			})
			.then((response) => {
				setUserId(response.data.data.id);
				setIsAdmin(response.data.data.admin);
				saveOnLocalStorage([
					{ key: 'isAdmin', value: response.data.data.admin },
					{ key: 'userId', value: response.data.data.id },
				]);
				console.log(response);
				history.push('/home');
			})
			.catch((err) => {
				console.log(err);
			});
	};
	const onFailure = (res: GoogleLoginResponseOffline): void => {
		console.log('[Login failed] Error:', res);
	};

	return (
		<>
			<GoogleLogin
				clientId={clientId}
				render={(renderProps) => (
					<Button
						onClick={renderProps.onClick}
						disabled={renderProps.disabled}
						className={classes.button}
						startIcon={
							<SvgIcon>
								<path d="M20.283,10.356h-8.327v3.451h4.792c-0.446,2.193-2.313,3.453-4.792,3.453c-2.923,0-5.279-2.356-5.279-5.28	c0-2.923,2.356-5.279,5.279-5.279c1.259,0,2.397,0.447,3.29,1.178l2.6-2.599c-1.584-1.381-3.615-2.233-5.89-2.233	c-4.954,0-8.934,3.979-8.934,8.934c0,4.955,3.979,8.934,8.934,8.934c4.467,0,8.529-3.249,8.529-8.934	C20.485,11.453,20.404,10.884,20.283,10.356z" />
							</SvgIcon>
						}
					>
						Login con Google
					</Button>
				)}
				buttonText="Login"
				onSuccess={(res) => onSuccess(res)}
				onFailure={onFailure}
				cookiePolicy="single_host_origin"
				isSignedIn={false}
			/>
		</>
	);
};

export default LoginGoogleButton;
