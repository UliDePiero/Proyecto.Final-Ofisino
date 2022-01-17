import blueGrey from '@material-ui/core/colors/blueGrey';
import { createTheme } from '@material-ui/core/styles';

export const appTheme = createTheme({
	typography: {
		fontFamily: ['poppins'].join(','),
	},
	palette: {
		primary: {
			contrastText: '#424B73', //	font color
			light: '#FAFBFF', // bold white
			main: '#F6F5FC', // selected white
		},
	},
});

export const pickersTheme = createTheme({
	typography: {
		fontFamily: ['poppins'].join(','),
	},
	palette: {
		primary: blueGrey,
	},
});

export default appTheme;
