import React from 'react';
import { Avatar, Typography, Theme } from '@material-ui/core';
import { makeStyles } from '@material-ui/styles';
import { LoginContext } from '../../types/common/types';
import { CredentialsContext } from '../../contexts/credentialsContext';
import NonAvatar from '../../icons/user.png';

const useStyles = makeStyles((theme: Theme) => ({
	container: {
		padding: '0.8rem',
		display: 'flex',
	},
	avatar: {
		width: '40px',
		height: '40px',
		textAlign: 'left',
	},
	name: {
		paddingLeft: '1.2rem',
		color: theme.palette.primary.contrastText,
		alignItems: 'center',
		fontSize: '16px',
		fontWeight: 'bold',
		margin: 'auto 0',
	},
}));

const AvatarComponent = () => {
	const { avatarUrl, name } = React.useContext<LoginContext>(CredentialsContext);
	const classes = useStyles();
	return (
		<div className={classes.container}>
			<Avatar alt={name} src={avatarUrl ?? NonAvatar} className={classes.avatar} />
			<Typography variant="h6" noWrap className={classes.name}>
				{name}
			</Typography>
		</div>
	);
};
export default AvatarComponent;
