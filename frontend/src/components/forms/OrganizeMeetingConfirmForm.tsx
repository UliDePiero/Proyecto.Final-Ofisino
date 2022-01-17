/* eslint-disable react/jsx-props-no-spreading */
import * as React from 'react';
import axios from 'axios';
import { makeStyles, Theme } from '@material-ui/core/styles';
import {
	Button,
	TextField,
	IconButton,
	Dialog,
	DialogTitle,
	DialogContent,
	DialogActions,
	Typography,
	Card,
	CardContent,
	Radio,
	FormLabel,
	Tooltip,
	Chip,
} from '@material-ui/core';
import { format } from 'date-fns';
import CloseIcon from '@material-ui/icons/Close';
import SaveOutlinedIcon from '@material-ui/icons/SaveOutlined';
import UndoOutlinedIcon from '@material-ui/icons/UndoOutlined';
import MeetingRoomIcon from '@material-ui/icons/MeetingRoom';
import AccessAlarmIcon from '@material-ui/icons/AccessAlarm';
import ScheduleIcon from '@material-ui/icons/Schedule';
import EventIcon from '@material-ui/icons/Event';
import ErrorIcon from '@material-ui/icons/Error';
import { OrganizationMember, OrganizeMeetingConfirm } from '../../types/common/types';
import MessageSnackbar from '../common/MessageSnackbar';
import errToMsg from '../../utils/helpers';

const useStyles = makeStyles((theme: Theme) => ({
	card: {
		display: 'flex',
		width: '100%',
		backgroundColor: theme.palette.primary.light,
		paddingBottom: '0px',
		minWidth: '22rem',
	},
	cardOne: {
		display: 'flex',
		minWidth: '22rem',
		margin: 'auto',
		backgroundColor: theme.palette.primary.light,
		paddingBottom: '0px',
	},
	content: {
		width: '100%',
	},
	button: {
		color: theme.palette.primary.main,
		background: theme.palette.primary.contrastText,
		margin: theme.spacing(1, 0, 1),
		borderRadius: '150px',
		'&:hover': {
			backgroundColor: theme.palette.grey[500],
		},
	},
	title: {
		color: theme.palette.primary.contrastText,
		fontWeight: 700,
		position: 'relative',
		top: '5px',
		left: '20px',
	},
	paper: {
		borderRadius: '34px',
		width: '800px',
		maxWidth: '800px',
	},
	closeButton: {
		position: 'absolute',
		margin: 0,
		padding: '3px',
		right: '10px',
		top: '10px',
		color: theme.palette.grey[500],
	},
	backButton: {
		position: 'absolute',
		margin: 0,
		padding: '3px',
		left: '10px',
		top: '10px',
		color: theme.palette.grey[500],
	},
	textField: {
		width: '100%',
		marginTop: theme.spacing(1),
		marginBottom: theme.spacing(1),
		marginLeft: theme.spacing(1),
		marginRight: theme.spacing(1),
	},
	input: {
		color: theme.palette.primary.contrastText,
		'&.Mui-focused': {
			color: theme.palette.primary.contrastText,
		},
		'&.MuiInputBase-input': {
			color: theme.palette.primary.contrastText,
		},
	},
	container: {
		display: 'flex',
		gap: '10px',
		marginTop: theme.spacing(2),
		marginBottom: theme.spacing(2),
	},
	formLabel: {
		color: theme.palette.primary.contrastText,
		flex: 'auto',
		fontSize: 'smaller',
	},
	cardLabel: {
		color: theme.palette.primary.contrastText,
		flex: 'auto',
		fontSize: 'medium',
		paddingRight: '10px',
		paddingLeft: '10px',
	},
	containerOneColumn: {
		color: theme.palette.primary.contrastText,
		paddingBottom: '10px',
	},
	containerTwoColumns: {
		color: theme.palette.primary.contrastText,
		marginBottom: theme.spacing(1),
		display: 'flex',
		flexDirection: 'row',
	},
	left: {
		width: '100%',
		display: 'inline-grid',
	},
	right: {
		width: '100%',
		display: 'inline-grid',
	},
	containerthreeColumns: {
		color: theme.palette.primary.contrastText,
		columnCount: 3,
		columns: 'auto',
		marginBottom: theme.spacing(1),
	},
	errorIcon: {
		color: 'red',
		fontSize: 'small',
	},
	chip: {
		margin: '3px',
		fontSize: 'medium',
		width: '75px',
		paddingTop: '0.5rem',
		paddingBottom: '0.5rem',
	},
	chipError: {
		paddingTop: '0.5rem',
		paddingBottom: '0.5rem',
		width: '75px',
		margin: '3px',
		backgroundColor: '#FFC8C8',
		fontSize: 'medium',
	},
}));

interface OrganizeMeetingConfirmFormProps {
	open: boolean;
	onClose: () => void;
	onParentOpen: () => void;
	loadOrganizeMeetingRows: () => void;
	formType: string;
	form: OrganizeMeetingConfirm[];
	onSetMessage: (message: string) => void;
	onSetOpenBackdrop: (flag: boolean) => void;
}

const base = process.env.REACT_APP_BASE_URL;
const url = `${base}/organizemeeting/confirm`;

const OrganizeMeetingConfirmForm: React.FunctionComponent<OrganizeMeetingConfirmFormProps> = ({
	open,
	onClose,
	onParentOpen,
	loadOrganizeMeetingRows,
	formType,
	form,
	onSetMessage,
	onSetOpenBackdrop,
}: OrganizeMeetingConfirmFormProps) => {
	const classes = useStyles();

	const [errorMessage, setErrorMessage] = React.useState<string>('');
	const [summary, setSummary] = React.useState<string>();
	const [description, setDescription] = React.useState<string>();
	const [openSnackbar, setOpenSnackbar] = React.useState<boolean>(false);

	const [selectedOption, setSelectedOption] = React.useState<number>(0);

	const handleCloseSnackbar = (reason: any) => {
		if (reason === 'clickaway') {
			return;
		}
		setOpenSnackbar(false);
	};

	const handleBack = async () => {
		onSetOpenBackdrop(true);
		if (form[0]?.meetingRequestId) {
			await axios
				.post(`${base}/organizemeeting/cancel`, {
					meeting_request_id: form[0]?.meetingRequestId,
				})
				.then(() => {
					onParentOpen();
					onClose();
				})
				.catch((err) => {
					const newMsg: string = errToMsg(err);
					setErrorMessage(newMsg);
					setOpenSnackbar(true);
					console.log(err);
				});
		} else {
			onParentOpen();
			onClose();
		}
		onSetOpenBackdrop(false);
	};

	const peticionPost = async () => {
		onSetOpenBackdrop(true);
		const selectedForm: OrganizeMeetingConfirm = form[selectedOption];
		await axios
			.post(url, {
				start: selectedForm.start,
				end: selectedForm.end,
				duration: selectedForm.duration,
				emails: selectedForm.emails,
				meeting_room_type: selectedForm.meetingRoomType,
				meeting_room_id: selectedForm.meetingRoom?.id,
				meeting_request_id: selectedForm.meetingRequestId,
				members_conflicts: selectedForm.membersConflicts!.map((member) => member.email),
				description,
				summary,
			})
			.then(() => {
				onSetMessage('La Solicitud de organización de reunión se ha agregado con éxito!!');
				onClose();
				loadOrganizeMeetingRows();
			})
			.catch((err) => {
				const newMsg: string = errToMsg(err);
				setErrorMessage(newMsg);
				setOpenSnackbar(true);
				console.log(err);
			});
		onSetOpenBackdrop(false);
	};

	React.useEffect(() => {
		setSelectedOption(0);
		setSummary(undefined);
		setDescription(undefined);
	}, [open]);

	return (
		<div>
			<Dialog
				PaperProps={{
					className: classes.paper,
				}}
				open={open}
				onClose={onClose}
			>
				<DialogTitle>
					<IconButton
						title="Volver"
						aria-label="back"
						className={classes.backButton}
						onClick={handleBack}
					>
						<UndoOutlinedIcon />
					</IconButton>
					<Typography variant="h5" className={classes.title}>
						Confirmar Reunión
					</Typography>
					<IconButton
						title="Salir"
						aria-label="close"
						className={classes.closeButton}
						onClick={onClose}
					>
						<CloseIcon />
					</IconButton>
				</DialogTitle>
				<DialogContent dividers>
					<MessageSnackbar
						open={openSnackbar}
						onClose={handleCloseSnackbar}
						message={errorMessage}
						severity="error"
					/>
					{form.length > 0 ? (
						<form noValidate>
							{form.length > 1 ? (
								<FormLabel className={classes.formLabel}>Seleccioná una alternativa</FormLabel>
							) : (
								<FormLabel className={classes.formLabel}>Detalle de la reunión</FormLabel>
							)}
							<div className={classes.container}>
								{form.map(
									(option: OrganizeMeetingConfirm, index: number): React.ReactElement => (
										<Card className={form.length > 1 ? classes.card : classes.cardOne}>
											<CardContent className={classes.content}>
												<Typography
													variant="body1"
													className={classes.containerOneColumn}
													gutterBottom
												>
													{form.length > 1 && (
														<Radio
															checked={selectedOption === Number(index)}
															onChange={(event) => {
																setSelectedOption(Number(event.target.value));
															}}
															value={index}
															color="default"
															name="option"
															inputProps={{ 'aria-label': 'E' }}
															size="small"
														/>
													)}
													<b>
														{(() => {
															switch (option.kind) {
																case 'ok':
																	return 'Está es tu mejor opción';
																case 'missing_features':
																	return 'Faltan características';
																case 'conflicts':
																	return (
																		<>
																			Conflictos de Calendario{' '}
																			<Tooltip
																				title="Dependerá de si aceptan los invitados con conflictos"
																				placement="top"
																			>
																				<ErrorIcon className={classes.errorIcon} />
																			</Tooltip>
																		</>
																	);
																default:
																	return '';
															}
														})()}
													</b>
												</Typography>
												<Typography variant="body2">
													<div className={classes.containerTwoColumns}>
														<div className={classes.left}>
															<Tooltip title="Fecha" placement="right">
																<FormLabel className={classes.cardLabel}>
																	<EventIcon /> {format(new Date(option?.start), 'dd/MM/yyyy')}
																</FormLabel>
															</Tooltip>
															<Tooltip title="Duración" placement="right">
																<FormLabel className={classes.cardLabel}>
																	<AccessAlarmIcon /> {option?.duration} min.
																</FormLabel>
															</Tooltip>
														</div>
														<div className={classes.right}>
															<Tooltip title="Hora" placement="right">
																<FormLabel className={classes.cardLabel}>
																	<ScheduleIcon /> {format(new Date(option?.start), 'HH:mm')}
																</FormLabel>
															</Tooltip>
															<Tooltip title="Sala de Reunión" placement="right">
																<FormLabel className={classes.cardLabel}>
																	<MeetingRoomIcon />{' '}
																	{option?.meetingRoomType !== 'virtual'
																		? option?.meetingRoom?.name
																		: 'Virtual'}
																</FormLabel>
															</Tooltip>
														</div>
													</div>
													{option?.meetingRoomType !== 'virtual' && (
														<div className={classes.containerthreeColumns}>
															<Tooltip
																title={`Aires Acondicionados ${
																	(option?.missingFeatures?.aireAcondicionado ?? 0) >= 1
																		? ` - Querias ${option?.missingFeatures?.aireAcondicionado} mas.`
																		: ''
																}`}
																placement="right"
															>
																<Chip
																	className={
																		(option?.missingFeatures?.aireAcondicionado ?? 0) >= 1
																			? classes.chipError
																			: classes.chip
																	}
																	variant="outlined"
																	size="small"
																	label={`🥶 : ${
																		Number(option?.meetingRoom?.features?.aireAcondicionado) === 1
																			? '✅'
																			: '❌'
																	}`}
																/>
															</Tooltip>
															<br />
															<Tooltip
																title={`Computadoras ${
																	(option?.missingFeatures?.computadoras ?? 0) >= 1
																		? ` - Querias ${option?.missingFeatures?.computadoras} mas.`
																		: ''
																}`}
																placement="right"
															>
																<Chip
																	className={
																		(option?.missingFeatures?.computadoras ?? 0) >= 1
																			? classes.chipError
																			: classes.chip
																	}
																	variant="outlined"
																	size="small"
																	label={`💻 : ${option?.meetingRoom?.features?.computadoras}`}
																/>
															</Tooltip>
															<br />
															<Tooltip
																title={`Mesas ${
																	(option?.missingFeatures?.mesas ?? 0) >= 1
																		? ` - Querias ${option?.missingFeatures?.mesas} mas.`
																		: ''
																}`}
																placement="right"
															>
																<Chip
																	className={
																		(option?.missingFeatures?.mesas ?? 0) >= 1
																			? classes.chipError
																			: classes.chip
																	}
																	variant="outlined"
																	size="small"
																	label={`🟫 : ${option?.meetingRoom?.features?.mesas}`}
																/>
															</Tooltip>
															<br />
															<Tooltip
																title={`Proyectores ${
																	(option?.missingFeatures?.proyector ?? 0) >= 1
																		? ` - Querias ${option?.missingFeatures?.proyector} mas.`
																		: ''
																}`}
																placement="right"
															>
																<Chip
																	className={
																		(option?.missingFeatures?.proyector ?? 0) >= 1
																			? classes.chipError
																			: classes.chip
																	}
																	variant="outlined"
																	size="small"
																	label={`📽 : ${
																		Number(option?.meetingRoom?.features?.proyector) === 1
																			? '✅'
																			: '❌'
																	}`}
																/>
															</Tooltip>
															<br />
															<Tooltip
																title={`Sillas ${
																	(option?.missingFeatures?.sillas ?? 0) >= 1
																		? ` - Querias ${option?.missingFeatures?.sillas} mas.`
																		: ''
																}`}
																placement="right"
															>
																<Chip
																	className={
																		(option?.missingFeatures?.sillas ?? 0) >= 1
																			? classes.chipError
																			: classes.chip
																	}
																	variant="outlined"
																	size="small"
																	label={`🪑 : ${option?.meetingRoom?.features?.sillas}`}
																/>
															</Tooltip>
															<br />
															<Tooltip
																title={`Ventanas ${
																	(option?.missingFeatures?.ventanas ?? 0) >= 1
																		? ` - Querias ${option?.missingFeatures?.ventanas} mas.`
																		: ''
																}`}
																placement="right"
															>
																<Chip
																	className={
																		(option?.missingFeatures?.ventanas ?? 0) >= 1
																			? classes.chipError
																			: classes.chip
																	}
																	variant="outlined"
																	size="small"
																	label={`🪟 : ${option?.meetingRoom?.features?.ventanas}`}
																/>
															</Tooltip>
														</div>
													)}
													{option.kind === 'conflicts' && (
														<div className={classes.containerOneColumn}>
															<Tooltip
																title="Se intentará resolver el conflicto de calendario con las siguientes personas."
																placement="bottom"
															>
																<FormLabel className={classes.cardLabel}>
																	{option?.membersConflicts?.map(
																		(member: OrganizationMember): React.ReactElement => (
																			<>
																				<ErrorIcon className={classes.errorIcon} />{' '}
																				{`${member.name} <${member.email}>`}
																				<br />
																			</>
																		)
																	)}
																</FormLabel>
															</Tooltip>
														</div>
													)}
												</Typography>
											</CardContent>
										</Card>
									)
								)}
							</div>
							<TextField
								id="summary"
								name="summary"
								label="Tema / Motivo / Título"
								className={classes.textField}
								InputLabelProps={{
									shrink: true,
									className: classes.input,
								}}
								InputProps={{
									className: classes.input,
								}}
								onChange={(event) => setSummary(event.target.value)}
								value={summary}
							/>
							<TextField
								id="description"
								name="description"
								label="Agenda de la reunión"
								multiline
								rows={3}
								className={classes.textField}
								InputLabelProps={{
									shrink: true,
									className: classes.input,
								}}
								InputProps={{
									className: classes.input,
								}}
								onChange={(event) => {
									setDescription(event.target.value);
								}}
								value={description}
							/>
						</form>
					) : (
						<Typography variant="body1" className={classes.containerOneColumn}>
							OH! NO! Ofisino no pudo encontrar ninguna alternativa. Volvé atras y probá con otras
							condiciones.
						</Typography>
					)}
				</DialogContent>
				<DialogActions>
					{formType === 'create' && form.length > 0 && (
						<>
							<Button title="Guardar" onClick={peticionPost} className={classes.button}>
								<SaveOutlinedIcon />
							</Button>
						</>
					)}
				</DialogActions>
			</Dialog>
		</div>
	);
};

export default OrganizeMeetingConfirmForm;
