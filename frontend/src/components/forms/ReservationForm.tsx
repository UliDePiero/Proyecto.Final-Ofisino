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
	Checkbox,
	FormControlLabel,
} from '@material-ui/core';
import DateFnsUtils from '@date-io/date-fns';
import esLocale from 'date-fns/locale/es';
import { format } from 'date-fns';
import { DatePicker, MuiPickersUtilsProvider } from '@material-ui/pickers';
import { Autocomplete } from '@material-ui/lab';
import CloseIcon from '@material-ui/icons/Close';
import SaveOutlinedIcon from '@material-ui/icons/SaveOutlined';
import { Reservation, Box, Building, WorkingSpace } from '../../types/common/types';
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
		width: '500px',
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
	rootCheckbox: {
		'&$checked': {
			color: theme.palette.primary.contrastText,
		},
	},
	checkedCheckbox: {},
	checkboxRow: {
		color: theme.palette.primary.contrastText,
		flex: 'auto',
	},
	boxTextField: {
		width: '100%',
		flex: 'auto',
		marginTop: theme.spacing(1),
		marginBottom: theme.spacing(1),
	},
	container: {
		display: 'flex',
	},
	dialogActionsTypography: {
		color: theme.palette.primary.contrastText,
		flex: 'auto',
		fontSize: 'smaller',
	},
}));

interface reservationFormProps {
	open: boolean;
	onClose: () => void;
	loadReservationRows: () => void;
	futureReservationDateRows: string[];
	formType: string;
	form: Reservation | undefined;
	onSetMessage: (message: string) => void;
	onSetOpenBackdrop: (flag: boolean) => void;
}

if (esLocale && esLocale.options) {
	esLocale.options.weekStartsOn = 0;
}

const base = process.env.REACT_APP_BASE_URL;
const url = `${base}/reservation`;

const ReservationForm: React.FunctionComponent<reservationFormProps> = ({
	open,
	onClose,
	loadReservationRows,
	futureReservationDateRows,
	formType,
	form,
	onSetMessage,
	onSetOpenBackdrop,
}: reservationFormProps) => {
	const classes = useStyles();

	const [errorMessage, setErrorMessage] = React.useState<string>('');
	const [buildingRows, setBuildingRows] = React.useState<Building[]>([]);
	const [building, setBuilding] = React.useState<Building | null>();
	const [workingSpaceRows, setWorkingSpaceRows] = React.useState<WorkingSpace[]>([]);
	const [boxRows, setBoxRows] = React.useState<Box[]>([]);
	const [openSnackbar, setOpenSnackbar] = React.useState<boolean>(false);
	const [disabledBox, setDisabledBox] = React.useState<boolean>(false);
	const [selectedDate, setSelectedDate] = React.useState<Date | null | undefined>();
	const [selectedWorkingSpace, setSelectedWorkingSpace] = React.useState<
		WorkingSpace | null | undefined
	>();
	const [selectedBox, setSelectedBox] = React.useState<Box | null | undefined>();

	function disableDates(date: any) {
		console.log(futureReservationDateRows);
		console.log(format(date as Date, 'yyyy-MM-dd'));
		return (
			date.getDay() === 0 ||
			date.getDay() === 6 ||
			futureReservationDateRows.includes(format(date as Date, 'yyyy-MM-dd'))
		);
	}

	const handleCloseSnackbar = (reason: any) => {
		if (reason === 'clickaway') {
			return;
		}
		setOpenSnackbar(false);
	};

	const handleChangeCheckbox = () => {
		setSelectedBox(null);
		setDisabledBox(!disabledBox);
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

	const loadWorkingSpaceRows = async (buildingId: number | undefined) => {
		if (buildingId !== undefined) {
			await axios
				.get(`${base}/workingspace?building_id=${buildingId}`)
				.then((response) => {
					setWorkingSpaceRows(response.data.data);
				})
				.catch((err) => {
					const newMsg: string = errToMsg(err, 'Oh no! Fallo cargando los espacios de trabajo.');
					setErrorMessage(newMsg);
					setOpenSnackbar(true);
					console.log(err);
				});
		} else {
			setWorkingSpaceRows([]);
			setBoxRows([]);
		}
	};

	const loadBoxRows = async (date: Date | null | undefined, workingSpaceId: number | undefined) => {
		if (workingSpaceId !== undefined) {
			await axios
				.get(
					`${base}/box/available?working_space_id=${workingSpaceId}&date=${format(
						date as Date,
						'yyyy-MM-dd'
					)}`
				)
				.then((response) => {
					setBoxRows(response.data.data);
				})
				.catch((err) => {
					const newMsg: string = errToMsg(err, 'Oh no! Fallo cargando los boxes.');
					setErrorMessage(newMsg);
					setOpenSnackbar(true);
					console.log(err);
				});
		} else {
			setBoxRows([]);
		}
	};

	const loadNestedBox = async () => {
		setSelectedBox(form?.box);
		await axios
			.get(`${base}/workingspace?id=${form?.box?.workingSpaceId}`)
			.then((workingSpaceResponse) => {
				setSelectedWorkingSpace(workingSpaceResponse.data.data);
				axios
					.get(`${base}/building?id=${workingSpaceResponse.data.data?.building?.id}`)
					.then((buildingResponse) => {
						setBuilding(buildingResponse.data.data);
					})
					.catch((err) => {
						const newMsg: string = errToMsg(err, 'Oh no! Fallo cargando el edificio.');
						setErrorMessage(newMsg);
						setOpenSnackbar(true);
						console.log(err);
					});
			})
			.catch((err) => {
				const newMsg: string = errToMsg(err, 'Oh no! Fallo cargando el espacio de trabajo.');
				setErrorMessage(newMsg);
				setOpenSnackbar(true);
				console.log(err);
			});
	};

	const peticionPost = async () => {
		onSetOpenBackdrop(true);
		const auxForm = {
			date: format((selectedDate as Date) ?? new Date(), 'yyyy-MM-dd'),
			box_id: selectedBox?.id,
			working_space_id: selectedWorkingSpace?.id,
		};
		if (disabledBox) {
			delete auxForm.box_id;
		} else {
			delete auxForm.working_space_id;
		}

		await axios
			.post(url, auxForm)
			.then(() => {
				onSetMessage('La reserva se ha agregado con éxito!!');
				onClose();
				loadReservationRows();
			})
			.catch((err) => {
				const newMsg: string = errToMsg(err);
				setErrorMessage(newMsg);
				setOpenSnackbar(true);
			});
		onSetOpenBackdrop(false);
	};

	const peticionPut = async () => {
		onSetOpenBackdrop(true);
		if (selectedBox && selectedDate) {
			await axios
				.put(`${url}?id=${form?.id}`, {
					id: form?.id,
					date: format(selectedDate as Date, 'yyyy-MM-dd'),
					box_id: selectedBox?.id,
				})
				.then(() => {
					onSetMessage('La reserva se ha modificado con éxito!!');
					onClose();
					loadReservationRows();
				})
				.catch((err) => {
					const newMsg: string = errToMsg(err);
					setErrorMessage(newMsg);
					setOpenSnackbar(true);
					console.log(err);
				});
		} else {
			const newMsg: string = errToMsg({
				response: {
					data: {
						errors: {
							json: {
								_schema: ['Los campos marcados con asteriscos son obligatorios.'],
							},
						},
					},
				},
			});
			setErrorMessage(newMsg);
			setOpenSnackbar(true);
			setOpenSnackbar(true);
		}
		onSetOpenBackdrop(false);
	};

	React.useEffect(() => {
		loadBuildingRows();
	}, []);

	React.useEffect(() => {
		if (open) {
			if (formType === 'edit') {
				setSelectedDate(form?.date);
				loadNestedBox();
				loadBoxRows(form?.date, form?.box?.workingSpaceId);
				setDisabledBox(false);
			} else {
				setSelectedDate(null);
				setBuilding(null);
				setSelectedWorkingSpace(null);
				setSelectedBox(null);
				loadBuildingRows();
				loadWorkingSpaceRows(undefined);
				setDisabledBox(true);
			}
		}
	}, [open, formType]);

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
						Reserva
					</Typography>
					<Typography variant="subtitle1" className={classes.title}>
						{!selectedDate && '¿Que día queres ir?'}
						{selectedDate && !selectedWorkingSpace && '¿A qué espacio de trabajo?'}
						{selectedWorkingSpace && formType === 'create' && '¿Cualquier Box o eligís uno?'}
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
						<ThemeProvider theme={pickersTheme}>
							<MuiPickersUtilsProvider utils={DateFnsUtils} locale={esLocale}>
								<DatePicker
									id="date"
									name="date"
									label="Día *"
									format="dd/MM/yyyy"
									autoOk
									value={selectedDate}
									shouldDisableDate={disableDates}
									disablePast
									onChange={(newValue: any) => {
										setSelectedDate(newValue);
										if (selectedWorkingSpace) {
											loadBoxRows(newValue, selectedWorkingSpace.id);
											setSelectedBox(null);
										}
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
							</MuiPickersUtilsProvider>
						</ThemeProvider>
						{selectedDate && (
							<>
								<Autocomplete
									disabled={formType === 'edit'}
									id="buildingId"
									value={building}
									onChange={(_, newValue: Building | null) => {
										setSelectedWorkingSpace(null);
										setSelectedBox(null);
										setBuilding(newValue);
										loadWorkingSpaceRows(newValue?.id);
									}}
									options={buildingRows}
									getOptionLabel={(option) => option.name}
									renderInput={(params) => (
										<TextField
											{...params}
											label="Edificio *"
											className={classes.textField}
											InputLabelProps={{
												className: classes.input,
											}}
											value={building ? building.name : null}
										/>
									)}
								/>

								<Autocomplete
									disabled={formType === 'edit'}
									id="workingSpaceId"
									value={selectedWorkingSpace}
									onChange={(_, newValue: WorkingSpace | null) => {
										setSelectedWorkingSpace(newValue);
										setSelectedBox(null);
										loadBoxRows(selectedDate, newValue?.id);
									}}
									options={workingSpaceRows}
									getOptionLabel={(option) => option.name}
									noOptionsText="Primero tenés que elegir un edificio"
									renderInput={(params) => (
										<TextField
											{...params}
											label="Espacio de trabajo *"
											className={classes.textField}
											InputLabelProps={{
												className: classes.input,
											}}
											value={selectedWorkingSpace ? selectedWorkingSpace.name : undefined}
										/>
									)}
								/>
							</>
						)}
						{selectedWorkingSpace && (
							<div className={classes.container}>
								<Autocomplete
									className={classes.boxTextField}
									id="idBox"
									value={selectedBox}
									disabled={disabledBox}
									options={boxRows}
									onChange={(_, newValue: Box | null) => setSelectedBox(newValue)}
									getOptionLabel={(option) => option.name}
									noOptionsText="No hay boxes disponibles para el espacio seleccionado"
									renderInput={(params) => (
										<TextField
											{...params}
											label="Box *"
											className={classes.textField}
											InputLabelProps={{
												className: classes.input,
											}}
											value={selectedBox ? selectedBox.name : undefined}
										/>
									)}
								/>
								{formType === 'create' && (
									<FormControlLabel
										value="Aleatorio"
										control={
											<Checkbox
												onChange={handleChangeCheckbox}
												style={{ color: '#424B73' }}
												checked={disabledBox}
											/>
										}
										label="Automatico"
										labelPlacement="top"
										className={classes.checkboxRow}
									/>
								)}
							</div>
						)}
					</form>
				</DialogContent>
				<DialogActions>
					<Typography className={classes.dialogActionsTypography}>* Campos obligatorios</Typography>
					{formType === 'create' ? (
						<Button
							title="Guardar"
							onClick={peticionPost}
							className={classes.button}
							disabled={!(selectedWorkingSpace && formType === 'create')}
						>
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

export default ReservationForm;
