import * as React from 'react';
import { LoginContext } from '../types/common/types';
import checkIfItIsInLocalStorage from '../utils/Context';

export const CredentialsContext = React.createContext<LoginContext>({
	email: '',
	setEmail: () => null,
	userId: 0,
	setUserId: () => null,
	clientId: '',
	isLoggedIn: false,
	setIsLoggedIn: () => null,
	isAdmin: false,
	setIsAdmin: () => null,
	officeInstance: null,
	setOfficeInstance: () => null,
	name: '',
	setName: () => null,
	avatarUrl: '',
	setAvatarUrl: () => null,
});

const AuthProvider = ({ children }: any) => {
	const [email, setEmail] = React.useState<string>(
		checkIfItIsInLocalStorage('Ofisino_email') ? localStorage.getItem('Ofisino_email') || '' : ''
	);
	const [isLoggedIn, setIsLoggedIn] = React.useState<boolean>(
		checkIfItIsInLocalStorage('Ofisino_isLoggedIn')
			? JSON.parse(localStorage.getItem('Ofisino_isLoggedIn') || 'false')
			: ''
	);
	const [isAdmin, setIsAdmin] = React.useState<boolean>(
		checkIfItIsInLocalStorage('Ofisino_isAdmin')
			? JSON.parse(localStorage.getItem('Ofisino_isAdmin') || 'false')
			: ''
	);
	const [userId, setUserId] = React.useState<number>(
		checkIfItIsInLocalStorage('Ofisino_userId')
			? JSON.parse(localStorage.getItem('Ofisino_userId') || '0')
			: ''
	);
	const [officeInstance, setOfficeInstance] = React.useState<any>(
		checkIfItIsInLocalStorage('Ofisino_officeInstance')
			? JSON.parse(localStorage.getItem('Ofisino_officeInstance') || 'null')
			: ''
	);
	const [name, setName] = React.useState<string>(
		checkIfItIsInLocalStorage('Ofisino_name') ? localStorage.getItem('Ofisino_name') || '' : ''
	);
	const [avatarUrl, setAvatarUrl] = React.useState<string>(
		checkIfItIsInLocalStorage('Ofisino_avatarUrl')
			? localStorage.getItem('Ofisino_avatarUrl') || ''
			: ''
	);

	return (
		<CredentialsContext.Provider
			value={{
				email,
				setEmail,
				userId,
				setUserId,
				clientId: '1012702625756-q6l0rvjbhdj8r3vt78hhk95jq4iiq0j8.apps.googleusercontent.com',
				isLoggedIn,
				setIsLoggedIn,
				isAdmin,
				setIsAdmin,
				officeInstance,
				setOfficeInstance,
				name,
				setName,
				avatarUrl,
				setAvatarUrl,
			}}
		>
			{children}
		</CredentialsContext.Provider>
	);
};
export default AuthProvider;
