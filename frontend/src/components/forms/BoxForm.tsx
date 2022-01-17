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
} from '@material-ui/core';
import { Autocomplete } from '@material-ui/lab';
import CloseIcon from '@material-ui/icons/Close';
import SaveOutlinedIcon from '@material-ui/icons/SaveOutlined';
import { Building, Box, WorkingSpace } from '../../types/common/types';
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
}));

interface BoxFormProps {
	open: boolean;
	onClose: () => void;
	loadBoxRows: () => void;
	formType: string;
	form: Box;
	onSetForm: (fieldName: string, fieldValue: any) => void;
	onSetMessage: (message: string) => void;
	onSetOpenBackdrop: (flag: boolean) => void;
}
const base = process.env.REACT_APP_BASE_URL;
const url = `${base}/box`;

const BoxForm: React.FunctionComponent<BoxFormProps> = ({
	open,
	onClose,
	loadBoxRows,
	formType,
	form,
	onSetForm,
	onSetMessage,
	onSetOpenBackdrop,
}: BoxFormProps) => {
	const classes = useStyles();

	const [errorMessage, setErrorMessage] = React.useState<string>('');
	const [buildingRows, setBuildingRows] = React.useState<Building[]>([]);
	const [building, setBuilding] = React.useState<Building | null>(null);
	const [workingSpaceRows, setWorkingSpaceRows] = React.useState<WorkingSpace[]>([]);
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
		}
	};

	const loadNestedWorkingSpace = async () => {
		await axios
			.get(`${base}/building?id=${form.workingSpace?.buildingId}`)
			.then((buildingResponse) => {
				setBuilding(buildingResponse.data.data);
			})
			.catch((err) => {
				const newMsg: string = errToMsg(err, 'Oh no! Fallo cargando el edificio.');
				setErrorMessage(newMsg);
				setOpenSnackbar(true);
				console.log(err);
			});
	};

	const peticionPost = async () => {
		onSetOpenBackdrop(true);
		await axios
			.post(url, {
				working_space_id: form.workingSpace?.id,
				name: form.name,
				description: form.description,
			})
			.then(() => {
				onSetMessage('El box se ha agregado con éxito!!');
				onClose();
				loadBoxRows();
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
		await axios
			.put(`${url}?id=${form.id}`, {
				id: form.id,
				name: form.name,
				description: form.description,
			})
			.then(() => {
				onSetMessage('El box se ha modificado con éxito!!');
				onClose();
				loadBoxRows();
			})
			.catch((err) => {
				const newMsg: string = errToMsg(err);
				setErrorMessage(newMsg);
				setOpenSnackbar(true);
			});
		onSetOpenBackdrop(false);
	};

	React.useEffect(() => {
		loadBuildingRows();
	}, []);

	React.useEffect(() => {
		if (open) {
			if (formType === 'edit') {
				loadNestedWorkingSpace();
			} else {
				setBuilding(null);
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
						Box
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
							value={building}
							onChange={(_, newValue: Building | null) => {
								setBuilding(newValue);
								onSetForm('workingSpace', null);
								onSetForm('box', null);
								loadWorkingSpaceRows(newValue?.id);
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
									value={building ? building.name : undefined}
								/>
							)}
						/>
						<Autocomplete
							disabled={formType === 'edit'}
							id="workingSpaceId"
							value={form.workingSpace}
							onChange={(event: any, newValue: WorkingSpace | null) => {
								onSetForm('workingSpace', newValue);
							}}
							options={workingSpaceRows}
							getOptionLabel={(option) => option.name}
							renderInput={(params) => (
								<TextField
									{...params}
									label="Espacio de Trabajo"
									className={classes.textField}
									InputLabelProps={{
										className: classes.input,
									}}
									value={form.workingSpace ? form.workingSpace.name : undefined}
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

export default BoxForm;
