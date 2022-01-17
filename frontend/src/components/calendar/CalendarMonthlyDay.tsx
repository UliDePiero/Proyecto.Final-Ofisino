import { Theme } from '@material-ui/core';
import { makeStyles } from '@material-ui/styles';
import { useMonthlyBody, useMonthlyCalendar } from '@zach.codes/react-calendar';
import { format } from 'date-fns';
import * as React from 'react';

type DayData = {
	title: string;
	date: Date;
};

type CalendarMonthlyDayProps = {
	renderDay: (events: DayData[]) => React.ReactNode;
};
const useStyles = makeStyles((theme: Theme) => ({
	root: {
		minHeight: '6rem',
		padding: '0.5rem',
		border: '1px solid #eaeaea',
	},
	containerDay: {
		display: 'flex',
		justifyContent: 'space-between',
	},
	dayNumber: {
		fontSize: '1.5rem',
		fontWeight: 'bold',
	},
	containerEvents: {
		display: 'block',
	},
	font: {
		fontWeight: 'bold',
	},
	eventsList: {
		listStyle: 'none',
		overflow: 'hidden',
		overflowY: 'auto',
		padding: '0',
	},
	button: {
		color: theme.palette.primary.main,
		background: theme.palette.primary.contrastText,
		borderRadius: '150px',
		'&:hover': {
			backgroundColor: theme.palette.grey[500],
		},
		textTransform: 'none',
	},
}));

const CalendarMonthlyDay = ({ renderDay }: CalendarMonthlyDayProps) => {
	const { locale } = useMonthlyCalendar();
	const { day, events } = useMonthlyBody<DayData>();
	const dayNumber = format(day, 'd');
	const classes = useStyles();

	return (
		<div aria-label={`Events for day ${dayNumber}`} className={classes.root}>
			<div className={classes.containerDay}>
				<div className={classes.font}>{dayNumber}</div>
			</div>
			<ul className={classes.eventsList}>{renderDay(events)}</ul>
		</div>
	);
};

export default CalendarMonthlyDay;
