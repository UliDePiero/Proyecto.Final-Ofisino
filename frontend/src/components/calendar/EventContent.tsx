import React from 'react';
import {
	Card,
	CardContent,
	Theme,
	Typography,
	makeStyles,
	IconButton,
	Button,
	Avatar,
} from '@material-ui/core';
import KeyboardArrowDownIcon from '@material-ui/icons/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@material-ui/icons/KeyboardArrowUp';
import SubjectIcon from '@material-ui/icons/Subject';
import PeopleAltIcon from '@material-ui/icons/PeopleAlt';
import TodayIcon from '@material-ui/icons/Today';
import MeetingRoomIcon from '@material-ui/icons/MeetingRoom';
import VideoCallIcon from '@material-ui/icons/VideoCall';
import NonAvatar from '../../icons/user.png';
import { formatDate } from '../../utils/Calendar';

const useStyles = makeStyles((theme: Theme) => ({
	root: {
		minWidth: 275,
	},
	pos: {
		marginBottom: 12,
	},
	arrows: {
		marginLeft: 'auto',
	},
	icons: {
		marginRight: 20,
	},
	but: {
		width: '100%',
	},
	title: {
		fontSize: '1rem',
		color: 'rgba(107, 114, 128, 1)',
	},
	date: {
		fontSize: '1rem',
		color: 'rgba(107, 114, 128, 1)',
	},
	actionButton: {
		backgrounColor: 'rgba(107, 114, 128, 1)',
		marginRight: 'auto',
		border: '1px solid rgba(107, 114, 128, 1)',
		textTransform: 'none',
	},
	avatar: {
		width: '20px',
		height: '20px',
		marginLeft: '5px',
		alignItems: 'center',
		display: 'inline-block',
		marginRight: '10px',
	},
}));
const EventContent = ({ meetingData }: any) => {
	const classes = useStyles();
	const { data } = meetingData;
	const [expanded, setExpanded] = React.useState(false);
	const hasAttendees = data?.attendees?.length > 0;
	return (
		<Card className={classes.root}>
			<CardContent>
				<Typography variant="h4" gutterBottom>
					{data?.summary}
				</Typography>
				<Typography variant="subtitle2" color="textSecondary" gutterBottom>
					<TodayIcon fontSize="small" className={classes.icons} />
					{formatDate(data?.date_start, data?.date_end)}
				</Typography>
				{hasAttendees && (
					<IconButton
						aria-label="showMore"
						size="small"
						className={classes.but}
						onClick={() => setExpanded(!expanded)}
						style={{ padding: '0px', marginBottom: '0.35em' }}
					>
						<Typography variant="subtitle2" color="textSecondary">
							<PeopleAltIcon fontSize="small" className={classes.icons} />
							Mostrar invitados
						</Typography>
						{!expanded && <KeyboardArrowDownIcon fontSize="medium" className={classes.arrows} />}
						{expanded && <KeyboardArrowUpIcon fontSize="medium" className={classes.arrows} />}
					</IconButton>
				)}
				{expanded &&
					hasAttendees &&
					data?.attendees.map((attendee: any) => (
						<Typography variant="subtitle2" color="textSecondary" gutterBottom>
							<Avatar
								alt={attendee.name}
								src={attendee.avatar_url ?? NonAvatar}
								className={classes.avatar}
							/>
							{`${attendee.name} <${attendee.email}>`}
						</Typography>
					))}
				{data?.meeting_room && (
					<Typography variant="subtitle2" color="textSecondary" gutterBottom>
						<MeetingRoomIcon fontSize="small" className={classes.icons} />
						{data?.meeting_room?.name}
					</Typography>
				)}
				<Typography variant="subtitle2" color="textSecondary" gutterBottom>
					<SubjectIcon fontSize="small" className={classes.icons} />
					{data?.description}
				</Typography>
				{data?.event && (
					<Typography variant="subtitle2" color="textSecondary">
						<Button
							aria-label="goToCall"
							size="small"
							onClick={() => window.open(data?.event, '_blank')}
							style={{
								padding: '0px',
								textTransform: 'none',
							}}
						>
							<Typography variant="subtitle2">
								<VideoCallIcon fontSize="small" style={{ marginRight: '20px' }} />
								Unirse a la reunión
							</Typography>
						</Button>
					</Typography>
				)}
			</CardContent>
		</Card>
	);
};

export default EventContent;
