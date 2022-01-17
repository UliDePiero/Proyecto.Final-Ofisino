import * as React from 'react';
import axios from 'axios';
import { format, subHours, startOfMonth, parse } from 'date-fns';
import { es } from 'date-fns/locale';
import { MonthlyBody, MonthlyCalendar, DefaultMonthlyEventItem } from '@zach.codes/react-calendar';
import '@zach.codes/react-calendar/dist/calendar-tailwind.css';
import { makeStyles, Theme } from '@material-ui/core/styles';
import Drawer from '../components/common/Drawer';
import MessageSnackbar from '../components/common/MessageSnackbar';
import { Meeting, Reservation } from '../types/common/types';
import CalendarNavBar from '../components/calendar/CalendarNavBar';
import CalendarMonthlyDay from '../components/calendar/CalendarMonthlyDay';
import MonthlyEventItem from '../components/calendar/MonthlyEventItem';

type Event = {
	name: string;
	date: Date;
};
const useStyles = makeStyles((theme: Theme) => ({
	root: {
		display: 'flex',
		height: '100%',
	},
	content: {
		flexGrow: 1,
		padding: theme.spacing(3),
		marginTop: theme.spacing(10),
		height: 'calc(100% - 80px)',
	},
	button: {
		color: theme.palette.primary.contrastText,
		margin: theme.spacing(1, 0, 1),
		borderRadius: '150px',
		display: 'flex',
		marginLeft: 'auto',
		'&:hover': {
			backgroundColor: theme.palette.primary.main,
		},
	},
	dataGrid: {
		height: '100%',
		width: '100%',
		margin: theme.spacing(1, 0, 1),
	},
	toolbar: {
		display: 'flex',
		alignItems: 'center',
		justifyContent: 'flex-end',
		padding: theme.spacing(0, 1),
		// necessary for content to be below app bar
		...theme.mixins.toolbar,
	},
	MessageSnackbar: {
		textAlign: 'left',
	},
}));

const base = process.env.REACT_APP_BASE_URL;

const Calendar: React.FunctionComponent = () => {
	const classes = useStyles();
	const [currentMonth, setCurrentMonth] = React.useState<Date>(startOfMonth(new Date()));
	const [events, setEvents] = React.useState<Event[]>([]);
	const [openErrorSnackbar, setOpenErrorSnackbar] = React.useState<boolean>(false);
	const getDataOfEventsAndReservations = () => {
		axios
			.all([axios.get(`${base}/meeting/where-im-member`), axios.get(`${base}/reservation/own`)])
			.then(
				axios.spread((...responses) => {
					const meetings = (responses[0] as any).data?.data?.map((meeting: Meeting) => ({
						title: meeting.summary ?? meeting.description,
						date: new Date(meeting.date),
						id: meeting.id,
					}));
					const reservations = (responses[1] as any).data?.data?.map(
						(reservation: Reservation) => ({
							title: `B<^>Reserva: ${reservation.box?.name}` ?? 'Box',
							date: parse(String(reservation.date), 'yyyy-MM-dd', new Date()),
						})
					);
					setEvents([...reservations, ...meetings]);
				})
			)
			.catch((errors) => {
				setOpenErrorSnackbar(true);
				console.log(errors);
			});
	};
	const handleCloseSnackbar = (reason: any) => {
		if (reason === 'clickaway') {
			return;
		}
		setOpenErrorSnackbar(false);
	};

	React.useEffect(() => {
		getDataOfEventsAndReservations();
	}, []);

	return (
		<div className={classes.root}>
			<Drawer />
			<div className={classes.content}>
				<MonthlyCalendar
					currentMonth={currentMonth}
					onCurrentMonthChange={(date) => setCurrentMonth(date)}
					locale={es}
				>
					<CalendarNavBar />
					<MonthlyBody events={events} omitDays={[0, 6]}>
						<CalendarMonthlyDay
							renderDay={(data) =>
								data.map((item: any, index) => (
									<MonthlyEventItem
										key={String(index)}
										title={item.title}
										date={format(item.date, 'k:mm')}
										id={item.id}
									/>
								))
							}
						/>
					</MonthlyBody>
				</MonthlyCalendar>
				<MessageSnackbar
					open={openErrorSnackbar}
					onClose={handleCloseSnackbar}
					message="No se pudieron cargar los eventos."
					severity="error"
				/>
			</div>
		</div>
	);
};

export default Calendar;
