import { Theme } from '@material-ui/core';
import { makeStyles } from '@material-ui/styles';
import React from 'react';
import CalendarMeeting from './CalendarMeeting';

type DefaultEventItemProps = {
	title: string;
	date: string;
	id: string;
};
const useStyles = makeStyles((theme: Theme) => ({
	liElement: {
		paddingTop: '0.2rem',
		paddingBottom: '0.2rem',
	},
	containerBox: {
		display: 'flex',
		justifyContent: 'space-between',
		backgroundColor: theme.palette.primary.main,
		borderRadius: '0.5rem',
		padding: '0.2rem',
	},
	containerMeeting: {
		display: 'flex',
		justifyContent: 'space-between',
		backgroundColor: 'rgba(254, 226, 226, 1)',
		borderRadius: '0.5rem',
		padding: '0.1rem',
	},
	title: {
		fontSize: '0.8rem',
		color: 'rgba(107, 114, 128, 1)',
		paddingLeft: '0.3rem',
	},
	date: {
		fontSize: '0.8rem',
		color: 'rgba(107, 114, 128, 1)',
	},
}));
const isABox = (title: string) => title.includes('B<^>');
const transformToEventToDisplay = (item: DefaultEventItemProps): DefaultEventItemProps => {
	const { title, id } = item;
	const isBox = isABox(title);
	if (isBox) {
		return {
			title: title.replace('B<^>', ''),
			date: '00:00',
			id,
		};
	}
	return item;
};
const MonthlyEventItem = ({ title, date, id }: DefaultEventItemProps) => {
	const classes = useStyles();
	const { title: eventTitle, date: eventDate } = transformToEventToDisplay({ title, date, id });
	return (
		<li className={classes.liElement}>
			{isABox(title) ? (
				<div className={classes.containerBox}>
					<h3 className={classes.title}>{eventTitle}</h3>
				</div>
			) : (
				<div className={classes.containerMeeting}>
					<CalendarMeeting eventTitle={eventTitle} eventStart={eventDate} eventId={id} />
				</div>
			)}
		</li>
	);
};
export default MonthlyEventItem;
