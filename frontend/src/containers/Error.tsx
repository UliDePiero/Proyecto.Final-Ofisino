import { makeStyles, Theme, Typography } from '@material-ui/core';
import * as React from 'react';
import errorImg from '../icons/Recurso 2Cal triste.png';

interface errorProps {
	label: string;
}

const useStyles = makeStyles((theme: Theme) => ({
	title: {
		margin: theme.spacing(7, 0, 1),
		alignItems: 'center',
	},
	image: {
		margin: theme.spacing(8, 0, 1),
	},
}));
const Error: React.FunctionComponent<errorProps> = ({ label }: errorProps) => {
	const classes = useStyles();
	return (
		<>
			<img src={errorImg} alt="Error" className={classes.image} />
			<Typography variant="h3" className={classes.title}>
				{label}
			</Typography>
		</>
	);
};

export default Error;
