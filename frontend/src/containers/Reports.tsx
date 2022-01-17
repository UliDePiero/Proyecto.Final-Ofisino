import * as React from 'react';
import axios from 'axios';
import { makeStyles, Theme } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import PeopleAltOutlinedIcon from '@material-ui/icons/PeopleAltOutlined';
import DesktopMacOutlinedIcon from '@material-ui/icons/DesktopMacOutlined';
import ArrowCircleDownOutlinedIcon from '@material-ui/icons/ArrowDownwardOutlined';
import Drawer from '../components/common/Drawer';
import MessageCard from '../components/common/MessageCard';
import MessageSnackbar from '../components/common/MessageSnackbar';

const useStyles = makeStyles((theme: Theme) => ({
	root: {
		display: 'flex',
		height: '100%',
	},
	button: {
		margin: 'auto',
	},
	buttons: {
		display: 'flex',
		marginTop: '5rem',
		padding: '0 8rem',
	},
	image: {
		display: 'flex',
		height: '50%',
		margin: 'auto',
		width: '50%',
		color: theme.palette.primary.contrastText,
		borderRadius: '20%',
		marginBottom: '2rem',
	},
	content: {
		flexGrow: 1,
		padding: theme.spacing(3),
	},
	buttonDownload: {
		color: theme.palette.primary.main,
		background: theme.palette.primary.contrastText,
		borderRadius: '150px',
		'&:hover': {
			backgroundColor: theme.palette.grey[500],
		},
		textTransform: 'none',
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

const Reports: React.FunctionComponent = () => {
	const classes = useStyles();
	const base = process.env.REACT_APP_BASE_URL;
	const [message, setMessage] = React.useState<string>('');
	const [errorMessage, setErrorMessage] = React.useState<string>('');
	const [openSnackbar, setOpenSnackbar] = React.useState<boolean>(false);
	const [openErrorSnackbar, setOpenErrorSnackbar] = React.useState<boolean>(false);

	const handleCloseSnackbar = (reason: any) => {
		if (reason === 'clickaway') {
			return;
		}
		setOpenSnackbar(false);
		setOpenErrorSnackbar(false);
	};

	const onSetMessage = (text: string) => {
		setMessage(text);
		setOpenSnackbar(true);
	};

	const downloadXLS = (fileName: string, data: any) => {
		const url = window.URL.createObjectURL(data);
		const link = document.createElement('a');
		link.href = url;
		link.setAttribute('download', `${fileName}`);
		document.body.appendChild(link);
		link.click();
	};

	const downloadReservationsDataAsCSV = async () => {
		await axios
			.get(`${base}/data/reservation`, { responseType: 'blob' })
			.then((response) => {
				downloadXLS('reservations.xlsx', response.data);
			})
			.catch((error) => {
				setErrorMessage(error);
				setOpenErrorSnackbar(true);
			});
	};

	const downloadMeetingRequestsDataAsCSV = async () => {
		await axios
			.get(`${base}/data/meetingrequest`, { responseType: 'blob' })
			.then((response) => {
				downloadXLS('meetingRequest.xlsx', response.data);
			})
			.catch((error) => {
				setErrorMessage(error);
				setOpenErrorSnackbar(true);
			});
	};

	return (
		<div className={classes.root}>
			<Drawer />
			<div className={classes.content}>
				<div className={classes.toolbar} />
				<MessageCard title="Reportes" message="" />
				<div className={classes.buttons}>
					<div className={classes.button}>
						<PeopleAltOutlinedIcon className={classes.image} />
						<Button
							color="inherit"
							onClick={downloadMeetingRequestsDataAsCSV}
							className={classes.buttonDownload}
							startIcon={<ArrowCircleDownOutlinedIcon />}
						>
							Descargar Reuniones
						</Button>
					</div>
					<div className={classes.button}>
						<DesktopMacOutlinedIcon className={classes.image} />
						<Button
							color="inherit"
							onClick={downloadReservationsDataAsCSV}
							className={classes.buttonDownload}
							startIcon={<ArrowCircleDownOutlinedIcon />}
						>
							Descargar Reservas
						</Button>
					</div>
				</div>
				<div className={classes.MessageSnackbar}>
					<MessageSnackbar
						open={openSnackbar}
						onClose={handleCloseSnackbar}
						message={message}
						severity="success"
					/>
					<MessageSnackbar
						open={openErrorSnackbar}
						onClose={handleCloseSnackbar}
						message={errorMessage}
						severity="error"
					/>
				</div>
			</div>
		</div>
	);
};

export default Reports;
