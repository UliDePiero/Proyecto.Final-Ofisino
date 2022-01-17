import { Button, Theme } from '@material-ui/core';
import { styles } from '@material-ui/pickers/views/Calendar/Calendar';
import { makeStyles } from '@material-ui/styles';
import { useMonthlyCalendar } from '@zach.codes/react-calendar';
import { addMonths, subMonths, getMonth } from 'date-fns';
import React from 'react';

const useStyles = makeStyles((theme: Theme) => ({
	container: {
		display: 'flex',
		justifyContent: 'space-between',
		alignItems: 'center',
		padding: '0.5rem',
	},
	currentMonth: {
		fontSize: '1.5rem',
		textAlign: 'center',
	},
	currentYear: {
		fontSize: '1rem',
		display: 'flex',
		justifyContent: 'center',
		color: theme.palette.grey[500],
	},
	previousMonth: {
		fontSize: '1.5rem',
		fontWeight: 'bold',
		color: '#ccc',
	},
	button: {
		color: theme.palette.primary.main,
		background: theme.palette.primary.contrastText,
		margin: theme.spacing(1, 0, 1),
		borderRadius: '150px',
		'&:hover': {
			backgroundColor: theme.palette.grey[500],
		},
		textTransform: 'none',
	},
}));
const mapMonths = (month: number) => {
	switch (month) {
		case 0:
			return 'Enero';
		case 1:
			return 'Febrero';
		case 2:
			return 'Marzo';
		case 3:
			return 'Abril';
		case 4:
			return 'Mayo';
		case 5:
			return 'Junio';
		case 6:
			return 'Julio';
		case 7:
			return 'Agosto';
		case 8:
			return 'Septiembre';
		case 9:
			return 'Octubre';
		case 10:
			return 'Noviembre';
		case 11:
			return 'Diciembre';
		default:
			return 'N/A';
	}
};

export const MonthlyNav = () => {
	const { currentMonth, onCurrentMonthChange } = useMonthlyCalendar();
	const classes = useStyles();

	return (
		<div className={classes.container}>
			<Button
				type="button"
				onClick={() => onCurrentMonthChange(subMonths(currentMonth, 1))}
				className={classes.button}
			>
				Anterior
			</Button>
			<div className={classes.currentMonth} aria-label="Mes Actual">
				{mapMonths(getMonth(currentMonth))}
				<span className={classes.currentYear}>{currentMonth.getFullYear()}</span>
			</div>
			<Button
				type="button"
				onClick={() => onCurrentMonthChange(addMonths(currentMonth, 1))}
				className={classes.button}
			>
				Siguiente
			</Button>
		</div>
	);
};
export default MonthlyNav;
