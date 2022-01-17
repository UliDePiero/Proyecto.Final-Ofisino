/* eslint-disable react/jsx-props-no-spreading */
import * as React from 'react';
import axios from 'axios';
import { ThemeProvider, makeStyles, Theme } from '@material-ui/core/styles';
import {
	Button,
	TextField,
	IconButton,
	Dialog,
	DialogTitle,
	DialogContent,
	DialogActions,
	Typography,
	FormLabel,
	Grid,
	Checkbox,
} from '@material-ui/core';
import { Autocomplete } from '@material-ui/lab';
import DateFnsUtils from '@date-io/date-fns';
import { format } from 'date-fns';
import esLocale from 'date-fns/locale/es';
import { DatePicker, TimePicker, MuiPickersUtilsProvider } from '@material-ui/pickers';
import CloseIcon from '@material-ui/icons/Close';
import SaveOutlinedIcon from '@material-ui/icons/SaveOutlined';
import {
	Building,
	OrganizeMeeting,
	MeetingRoomType,
	OrganizeMeetingConfirm,
	OrganizationMember,
} from '../../types/common/types';
import MessageSnackbar from '../common/MessageSnackbar';
import { pickersTheme } from '../../themes/themes';
import errToMsg from '../../utils/helpers';

const useStyles = makeStyles((theme: Theme) => ({
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
	},
	paper: {
		borderRadius: '34px',
		width: '600px',
	},
	closeButton: {
		position: 'absolute',
		margin: 0,
		padding: '3px',
		right: '10px',
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
	},
	formLabel: {
		color: theme.palette.primary.contrastText,
		flex: 'auto',
		fontSize: 'smaller',
		marginTop: theme.spacing(1),
		marginBottom: theme.spacing(1),
		marginLeft: theme.spacing(1),
		marginRight: theme.spacing(1),
	},
	grid: {
		margin: 'auto',
		marginLeft: theme.spacing(1),
		padding: theme.spacing(1),
		fontSize: 'xx-large',
	},
	checkBox: {
		width: '100%',
		marginTop: theme.spacing(1),
		marginBottom: theme.spacing(1),
	},
}));

interface OrganizeMeetingFormProps {
	open: boolean;
	onClose: () => void;
	onOpenConfirm: () => void;
	formType: string;
	form: OrganizeMeeting;
	onSetForm: (fieldName: string, fieldValue: any) => void;
	onSetConfirmForm: (array: OrganizeMeetingConfirm[]) => void;
	onSetOpenBackdrop: (flag: boolean) => void;
}

const base = process.env.REACT_APP_BASE_URL;
const url = `${base}/organizemeeting`;

const OrganizeMeetingForm: React.FunctionComponent<OrganizeMeetingFormProps> = ({
	open,
	onClose,
	onOpenConfirm,
	formType,
	form,
	onSetForm,
	onSetConfirmForm,
	onSetOpenBackdrop,
}: OrganizeMeetingFormProps) => {
	const classes = useStyles();

	const [errorMessage, setErrorMessage] = React.useState<string>('');
	const [buildingRows, setBuildingRows] = React.useState<Building[]>([]);
	const [organizationMemberRows, setOrganizationMemberRows] = React.useState<OrganizationMember[]>(
		[]
	);
	const [meetingRoomTypeRows, setMeetingRoomTypeRows] = React.useState<MeetingRoomType[]>([
		{ name: 'Virtual', code: 'virtual' },
		{ name: 'Fisica', code: 'physical' },
	]);
	const [openSnackbar, setOpenSnackbar] = React.useState<boolean>(false);

	const handleCloseSnackbar = (reason: any) => {
		if (reason === 'clickaway') {
			return;
		}
		setOpenSnackbar(false);
	};

	const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		const { currentTarget } = e;
		onSetForm(currentTarget.name, currentTarget.value);
	};

	const loadOrganizationMemberRows = async () => {
		await axios
			.get(`${base}/orgmembers`)
			.then((response) => {
				setOrganizationMemberRows(response.data.data);
			})
			.catch((err) => {
				const newMsg: string = errToMsg(err, 'Oh no! Fallo cargando los mails de los usuarios.');
				setErrorMessage(newMsg);
				setOpenSnackbar(true);
				console.log(err);
			});
	};

	const loadBuildingRows = async () => {
		await axios
			.get(`${base}/building`)
			.then((response) => {
				setBuildingRows(response.data.data);
			})
			.catch((err) => {
				const newMsg: string = errToMsg(err, 'Oh no! Fallo cargando los edificios.');
				setErrorMessage(newMsg);
				setOpenSnackbar(true);
				console.log(err);
			});
	};

	const peticionPost = async () => {
		onSetOpenBackdrop(true);
		await axios
			.post(url, {
				start: format(form.start, 'yyyy-MM-dd'),
				end: format(form.end, 'yyyy-MM-dd'),
				time_start: format(form.timeStart, 'HH:mm'),
				time_end: format(form.timeEnd, 'HH:mm'),
				timezone: new window.Intl.DateTimeFormat().resolvedOptions().timeZone,
				meeting_room_type: form.meetingRoomType?.code,
				duration: Number(form.duration),
				building_id: form.building?.id,
				emails: form.members
					.map((organizationMember) => {
						return organizationMember.email;
					})
					.flat(),
				features:
					form.meetingRoomType?.code === 'physical'
						? {
								aire_acondicionado: form.features?.aireAcondicionado,
								computadoras: form.features?.computadoras,
								proyector: form.features?.proyector,
								ventanas: form.features?.ventanas,
								sillas: form.features?.sillas,
								mesas: form.features?.mesas,
						  }
						: {},
			})
			.then((response) => {
				const auxData: OrganizeMeetingConfirm[] = [];
				Object.entries(response.data.data).forEach(([key, value]: any) => {
					auxData[key] = {
						...value,
						meetingRoomType: value.meeting_room_type,
						meetingRoom: {
							...value.meeting_room,
							features: {
								aireAcondicionado: value.meeting_room?.features?.aire_acondicionado,
								computadoras: value.meeting_room?.features?.computadoras,
								proyector: value.meeting_room?.features?.proyector,
								ventanas: value.meeting_room?.features?.ventanas,
								sillas: value.meeting_room?.features?.sillas,
								mesas: value.meeting_room?.features?.mesas,
							},
						},
						meetingRequestId: value.meeting_request_id,
						missingFeatures: {
							aireAcondicionado: value.missing_features?.aire_acondicionado,
							computadoras: value.missing_features?.computadoras,
							proyector: value.missing_features?.proyector,
							ventanas: value.missing_features?.ventanas,
							sillas: value.missing_features?.sillas,
							mesas: value.missing_features?.mesas,
						},
						membersConflicts: value.members_conflicts,
					};
				});
				console.log(auxData);
				onSetConfirmForm(auxData);
				onClose();
				onOpenConfirm();
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
		loadOrganizationMemberRows();
		loadBuildingRows();
	}, []);

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
					<Typography variant="h5" className={classes.title}>
						Organizar Reunion
					</Typography>
					<Typography variant="subtitle1" className={classes.title}>
						{form.members?.length < 2 && '¿A quienes vas a invitar?'}
						{form.members?.length >= 2 &&
							!form.meetingRoomType &&
							'¿Entre que fechas y horarios? ¿Duración? ¿Virtual o Fisica?'}
						{form.meetingRoomType &&
							form.meetingRoomType?.code === 'physical' &&
							'¿Que necesitas que tenga la sala?'}
					</Typography>
					<IconButton aria-label="close" className={classes.closeButton} onClick={onClose}>
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
					<form noValidate>
						<div className={classes.container}>
							<FormLabel className={classes.formLabel}>
								<b>Invitados a la reunión</b> (minimo 2 participantes)
							</FormLabel>
						</div>
						<Autocomplete
							multiple
							disabled={formType === 'edit'}
							id="emails"
							value={form.members}
							onChange={(event: any, newValue: OrganizationMember[] | []) => {
								onSetForm('members', newValue);
							}}
							options={organizationMemberRows}
							getOptionLabel={(option) => `${option.name} <${option.email}>`}
							className={classes.textField}
							renderInput={(params) => (
								<TextField
									{...params}
									label="Participantes"
									InputLabelProps={{
										className: classes.input,
									}}
									value={form.members ? form.members : []}
								/>
							)}
						/>
						{form.members?.length >= 2 && (
							<>
								<div className={classes.container}>
									<FormLabel className={classes.formLabel}>
										<b>Fechas, Horarios y tipo de reunión</b>
									</FormLabel>
								</div>
								<ThemeProvider theme={pickersTheme}>
									<MuiPickersUtilsProvider utils={DateFnsUtils} locale={esLocale}>
										<div className={classes.container}>
											<DatePicker
												id="start"
												name="start"
												label="Fecha desde"
												autoOk
												format="dd/MM/yyyy"
												value={form.start}
												onChange={(newValue: any) => {
													onSetForm('start', newValue);
												}}
												InputLabelProps={{
													shrink: true,
													className: classes.input,
												}}
												InputProps={{
													className: classes.input,
												}}
												className={classes.textField}
											/>
											<DatePicker
												id="end"
												name="end"
												label="Fecha hasta"
												autoOk
												format="dd/MM/yyyy"
												value={form.end}
												onChange={(newValue: any) => {
													onSetForm('end', newValue);
												}}
												InputLabelProps={{
													shrink: true,
													className: classes.input,
												}}
												InputProps={{
													className: classes.input,
												}}
												className={classes.textField}
											/>
											<TimePicker
												id="timeStart"
												name="start"
												label="Hora Desde"
												todayLabel="now"
												autoOk
												value={form.timeStart}
												minutesStep={15}
												onChange={(newValue: any) => {
													onSetForm('timeStart', newValue);
												}}
												InputLabelProps={{
													shrink: true,
													className: classes.input,
												}}
												InputProps={{
													className: classes.input,
												}}
												className={classes.textField}
											/>
											<TimePicker
												id="timeEnd"
												name="end"
												label="Hora hasta"
												todayLabel="now"
												autoOk
												value={form.timeEnd}
												minutesStep={15}
												onChange={(newValue: any) => {
													onSetForm('timeEnd', newValue);
												}}
												InputLabelProps={{
													shrink: true,
													className: classes.input,
												}}
												InputProps={{
													className: classes.input,
												}}
												className={classes.textField}
											/>
										</div>
									</MuiPickersUtilsProvider>
								</ThemeProvider>
								<div className={classes.container}>
									<TextField
										id="duration"
										name="duration"
										label="Duración [min]"
										type="number"
										className={classes.textField}
										InputLabelProps={{
											shrink: true,
											className: classes.input,
										}}
										InputProps={{
											className: classes.input,
											inputProps: {
												min: 15,
												step: 15,
											},
										}}
										onChange={handleChange}
										value={form.duration}
									/>
									<Autocomplete
										disabled={formType === 'edit'}
										id="meetingRoomType"
										value={form.meetingRoomType}
										disableClearable
										onChange={(event: any, newValue: MeetingRoomType | null) => {
											onSetForm('meetingRoomType', newValue);
										}}
										options={meetingRoomTypeRows}
										getOptionLabel={(option) => option.name}
										className={classes.textField}
										renderInput={(params) => (
											<TextField
												{...params}
												label="Tipo de Sala"
												InputLabelProps={{
													className: classes.input,
												}}
												value={form.meetingRoomType ? form.meetingRoomType.name : undefined}
											/>
										)}
									/>
								</div>
							</>
						)}
						{form.meetingRoomType?.code === 'physical' ? (
							<>
								<div className={classes.container}>
									<FormLabel className={classes.formLabel}>
										<b>Caracteristicas Mínimas de la sala</b>
									</FormLabel>
								</div>
								<Autocomplete
									disabled={formType === 'edit'}
									id="buildingId"
									value={form.building}
									onChange={(event: any, newValue: Building | null) => {
										onSetForm('building', newValue);
									}}
									options={buildingRows}
									getOptionLabel={(option) => option.name}
									renderInput={(params) => (
										<TextField
											{...params}
											label="Edificio"
											className={classes.textField}
											InputLabelProps={{
												className: classes.input,
											}}
											value={form.building ? form.building.name : undefined}
										/>
									)}
								/>
								<div className={classes.container}>
									<Grid className={classes.container}>
										<Grid className={classes.grid}>💻</Grid>
										<Grid>
											<TextField
												id="features.computadoras"
												name="features.computadoras"
												label="Computadoras"
												type="number"
												className={classes.textField}
												InputLabelProps={{
													shrink: true,
													className: classes.input,
												}}
												InputProps={{
													className: classes.input,
													inputProps: {
														min: 0,
													},
												}}
												onChange={handleChange}
												value={form.features?.computadoras}
											/>
										</Grid>
									</Grid>
									<Grid className={classes.container}>
										<Grid className={classes.grid}>🪟</Grid>
										<Grid>
											<TextField
												id="features.ventanas"
												name="features.ventanas"
												label="Ventanas"
												type="number"
												className={classes.textField}
												InputLabelProps={{
													shrink: true,
													className: classes.input,
												}}
												InputProps={{
													className: classes.input,
													inputProps: {
														min: 0,
													},
												}}
												onChange={handleChange}
												value={form.features?.ventanas}
											/>
										</Grid>
									</Grid>
									<Grid className={classes.container}>
										<Grid className={classes.grid}>🥶</Grid>
										<Grid>
											<Checkbox
												id="features.aireAcondicionado"
												name="features.aireAcondicionado"
												className={classes.checkBox}
												onChange={handleChange}
												checked={Boolean(Number(form.features?.aireAcondicionado))}
												value={Number(form.features?.aireAcondicionado) === 0 ? 1 : 0}
											/>
										</Grid>
									</Grid>
								</div>
								<div className={classes.container}>
									<Grid className={classes.container}>
										<Grid className={classes.grid}>🪑</Grid>
										<Grid>
											<TextField
												id="features.sillas"
												name="features.sillas"
												label="Sillas"
												type="number"
												className={classes.textField}
												InputLabelProps={{
													shrink: true,
													className: classes.input,
												}}
												InputProps={{
													className: classes.input,
													inputProps: {
														min: 0,
													},
												}}
												onChange={handleChange}
												value={form.features?.sillas}
											/>
										</Grid>
									</Grid>
									<Grid className={classes.container}>
										<Grid className={classes.grid}>🟫</Grid>
										<Grid>
											<TextField
												id="features.mesas"
												name="features.mesas"
												label="Mesas"
												type="number"
												className={classes.textField}
												InputLabelProps={{
													shrink: true,
													className: classes.input,
												}}
												InputProps={{
													className: classes.input,
													inputProps: {
														min: 0,
													},
												}}
												onChange={handleChange}
												value={form.features?.mesas}
											/>
										</Grid>
									</Grid>
									<Grid className={classes.container}>
										<Grid className={classes.grid}>📽</Grid>
										<Grid>
											<Checkbox
												id="features.proyector"
												name="features.proyector"
												className={classes.checkBox}
												onChange={handleChange}
												checked={Boolean(Number(form.features?.proyector))}
												value={Number(form.features?.proyector) === 0 ? 1 : 0}
											/>
										</Grid>
									</Grid>
								</div>
							</>
						) : null}
					</form>
				</DialogContent>
				<DialogActions>
					{formType === 'create' ? (
						<Button
							title="Guardar"
							onClick={peticionPost}
							className={classes.button}
							disabled={!form.meetingRoomType}
						>
							<SaveOutlinedIcon />
						</Button>
					) : null}
				</DialogActions>
			</Dialog>
		</div>
	);
};

export default OrganizeMeetingForm;
