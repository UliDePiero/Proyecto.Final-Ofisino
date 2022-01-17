import { Theme, Typography, Button, Popover } from '@material-ui/core';
import { makeStyles } from '@material-ui/styles';
import React from 'react';
import { CalendarMeetingProps } from '../../types/calendar';
import getMeetingData from '../../utils/Calendar';
import EventContent from './EventContent';

const useStyles = makeStyles((theme: Theme) => ({
	root: {
		minWidth: 275,
	},
	bullet: {
		margin: '0 2px',
		padding: '0 2px',
	},
	pos: {
		marginBottom: 12,
	},
	title: {
		fontSize: '0.8rem',
		color: 'rgba(107, 114, 128, 1)',
		paddingLeft: '0.5rem',
		paddingRight: '0',
		paddingTop: '0',
		paddingBottom: '0',
		justifyContent: 'flex-start',
		textTransform: 'none',
		'button:focus': {
			outline: 'none',
		},
	},
	date: {
		fontSize: '0.8rem',
		color: 'rgba(107, 114, 128, 1)',
		paddingRight: '0.2rem',
	},
}));

const CalendarMeeting = ({ eventTitle, eventStart, eventId }: CalendarMeetingProps) => {
	const classes = useStyles();
	const [anchorEl, setAnchorEl] = React.useState<HTMLButtonElement | null>(null);
	const [meetingData, setMeetingData] = React.useState<any>({});

	const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
		getMeetingData(eventId).then((data) => {
			setMeetingData(data);
		});
		setAnchorEl(event.currentTarget);
	};

	const handleClose = () => {
		setAnchorEl(null);
	};

	const open = Boolean(anchorEl);
	const id = open ? 'simple-popover' : undefined;
	return (
		<>
			<Button onClick={handleClick} className={classes.title}>
				{eventTitle}
			</Button>
			<h3 className={classes.date}>{eventStart}</h3>
			<Popover
				id={id}
				open={open}
				anchorEl={anchorEl}
				onClose={handleClose}
				anchorOrigin={{
					vertical: 'top',
					horizontal: 'left',
				}}
				transformOrigin={{
					vertical: 'center',
					horizontal: 'right',
				}}
			>
				<EventContent meetingData={meetingData} />
			</Popover>
		</>
	);
};

export default CalendarMeeting;
