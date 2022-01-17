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
	Checkbox,
	Grid,
} from '@material-ui/core';
import { Autocomplete } from '@material-ui/lab';
import CloseIcon from '@material-ui/icons/Close';
import SaveOutlinedIcon from '@material-ui/icons/SaveOutlined';
import { Building, MeetingRoom } from '../../types/common/types';
import MessageSnackbar from '../common/MessageSnackbar';
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

interface MeetingRoomFormProps {
	open: boolean;
	onClose: () => void;
	loadMeetingRoomRows: () => void;
	formType: string;
	form: MeetingRoom;
	onSetForm: (fieldName: string, fieldValue: any) => void;
	onSetMessage: (message: string) => void;
	onSetOpenBackdrop: (flag: boolean) => void;
}

const base = process.env.REACT_APP_BASE_URL;
const url = `${base}/meetingroom`;

const MeetingRoomForm: React.FunctionComponent<MeetingRoomFormProps> = ({
	open,
	onClose,
	loadMeetingRoomRows,
	formType,
	form,
	onSetForm,
	onSetMessage,
	onSetOpenBackdrop,
}: MeetingRoomFormProps) => {
	const classes = useStyles();

	const [errorMessage, setErrorMessage] = React.useState<string>('');
	const [buildingRows, setBuildingRows] = React.useState<Building[]>([]);
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
				building_id: form.building?.id,
				name: form.name,
				capacity: form.capacity,
				features: {
					aire_acondicionado: form.features?.aireAcondicionado,
					computadoras: form.features?.computadoras,
					proyector: form.features?.proyector,
					ventanas: form.features?.ventanas,
					sillas: form.features?.sillas,
					mesas: form.features?.mesas,
				},
				description: form.description,
			})
			.then(() => {
				onSetMessage('La sala de reunión se ha agregado con éxito!!');
				onClose();
				loadMeetingRoomRows();
			})
			.catch((err) => {
				const newMsg: string = errToMsg(err);
				setErrorMessage(newMsg);
				setOpenSnackbar(true);
				console.log(err);
			});
		onSetOpenBackdrop(false);
	};

	const peticionPut = async () => {
		onSetOpenBackdrop(true);
		await axios
			.put(`${url}?id=${form.id}`, {
				id: form.id,
				name: form.name,
				capacity: form.capacity,
				features: {
					aire_acondicionado: form.features?.aireAcondicionado,
					computadoras: form.features?.computadoras,
					proyector: form.features?.proyector,
					ventanas: form.features?.ventanas,
					sillas: form.features?.sillas,
					mesas: form.features?.mesas,
				},
				description: form.description,
			})
			.then(() => {
				onSetMessage('La sala de reunión se ha modificado con éxito!!');
				onClose();
				loadMeetingRoomRows();
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
						Sala de reunión
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
						<TextField
							id="name"
							name="name"
							label="Nombre"
							className={classes.textField}
							InputLabelProps={{
								shrink: true,
								className: classes.input,
							}}
							InputProps={{
								className: classes.input,
							}}
							onChange={handleChange}
							value={form.name}
						/>
						<TextField
							id="capacity"
							name="capacity"
							label="Capacidad [Personas]"
							type="number"
							className={classes.textField}
							InputLabelProps={{
								shrink: true,
								className: classes.input,
							}}
							InputProps={{
								className: classes.input,
							}}
							onChange={handleChange}
							value={form.capacity}
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
						<TextField
							id="description"
							name="description"
							label="Descripción"
							multiline
							rows={2}
							className={classes.textField}
							InputLabelProps={{
								shrink: true,
								className: classes.input,
							}}
							InputProps={{
								className: classes.input,
							}}
							onChange={handleChange}
							value={form.description}
						/>
					</form>
				</DialogContent>
				<DialogActions>
					{formType === 'create' ? (
						<Button title="Guardar" onClick={peticionPost} className={classes.button}>
							<SaveOutlinedIcon />
						</Button>
					) : (
						<Button title="Modificar" onClick={peticionPut} className={classes.button}>
							<SaveOutlinedIcon />
						</Button>
					)}
				</DialogActions>
			</Dialog>
		</div>
	);
};

export default MeetingRoomForm;
