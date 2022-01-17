import * as React from 'react';
import { makeStyles, Theme } from '@material-ui/core/styles';
import { Grid, Typography, Paper } from '@material-ui/core';
import LoginGoogleButton from '../components/login/LoginGoogleButton';
import logo from '../icons/Logo_sin_fondo.png';
import LoginMicrosoftButton from '../components/login/LoginMicrosoftButton';
import MessageSnackbar from '../components/common/MessageSnackbar';

const useStyles = makeStyles((theme: Theme) => ({
	button: {
		color: theme.palette.primary.contrastText,
		background: theme.palette.primary.main,
		margin: theme.spacing(1, 0, 1),
		width: '225px',
		borderRadius: '150px',
	},
	grid: {
		minHeight: '35vh',
	},
	logo: {
		widht: '250px',
		height: '250px',
		position: 'relative',
		top: '15px',
		margin: 'auto',
	},
	title: {
		color: 'black',
		position: 'relative',
		top: '10px',
	},
	MessageSnackbar: {
		textAlign: 'left',
	},
}));

const Login: React.FunctionComponent = () => {
	const [errorMessage, setErrorMessage] = React.useState<string>('');
	const [openErrorSnackbar, setOpenErrorSnackbar] = React.useState<boolean>(false);
	const handleCloseSnackbar = (reason: any) => {
		if (reason === 'clickaway') {
			return;
		}
		setOpenErrorSnackbar(false);
	};

	const onsetErrorMessage = (text: string) => {
		setErrorMessage(text);
		setOpenErrorSnackbar(true);
	};
	const classes = useStyles();
	return (
		<>
			<>
				<img className={classes.logo} src={logo} alt="Bosch Logo" />
				<Typography variant="h6" className={classes.title}>
					OFISINO
				</Typography>
			</>
			<Grid
				container
				spacing={0}
				direction="column"
				alignItems="center"
				justify="center"
				className={classes.grid}
			>
				<Paper elevation={3} />
				<LoginGoogleButton onsetErrorMessage={onsetErrorMessage} />
				{/* <LoginMicrosoftButton onSetErrorMessage={onsetErrorMessage} /> */}
			</Grid>
			<div className={classes.MessageSnackbar}>
				<MessageSnackbar
					open={openErrorSnackbar}
					onClose={handleCloseSnackbar}
					message={errorMessage}
					severity="error"
				/>
			</div>
		</>
	);
};

export default Login;
