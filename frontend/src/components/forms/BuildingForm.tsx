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
	DialogContentText,
	DialogActions,
	Typography,
} from '@material-ui/core';
import { Autocomplete } from '@material-ui/lab';
import CloseIcon from '@material-ui/icons/Close';
import SaveOutlinedIcon from '@material-ui/icons/SaveOutlined';
import { Building, Organization } from '../../types/common/types';
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

interface BuildingFormProps {
	open: boolean;
	onClose: () => void;
	loadBuildingRows: () => void;
	formType: string;
	form: Building;
	onSetForm: (fieldName: string, fieldValue: any) => void;
	onSetMessage: (message: string) => void;
	onSetOpenBackdrop: (flag: boolean) => void;
}

const base = process.env.REACT_APP_BASE_URL;
const url = `${base}/building`;

const BuildingForm: React.FunctionComponent<BuildingFormProps> = ({
	open,
	onClose,
	loadBuildingRows,
	formType,
	form,
	onSetForm,
	onSetMessage,
	onSetOpenBackdrop,
}: BuildingFormProps) => {
	const classes = useStyles();

	const [errorMessage, setErrorMessage] = React.useState<string>('');
	const [organizationRows, setOrganizationRows] = React.useState<Organization[]>([]);
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

	const loadOrganizationRows = async () => {
		await axios
			.get(`${base}/organization`)
			.then((response) => {
				setOrganizationRows(response.data.data);
				console.log(response.data.data[0]);
				onSetForm('organization', response.data.data[0]);
			})
			.catch((err) => {
				const newMsg: string = errToMsg(err, 'Oh no! Fallo cargando la organización.');
				setErrorMessage(newMsg);
				setOpenSnackbar(true);
				console.log(err);
			});
	};

	const peticionPost = async () => {
		onSetOpenBackdrop(true);
		await axios
			.post(url, {
				organization_id: form?.organization?.id,
				name: form.name,
				location: form.location,
				description: form.description,
			})
			.then(() => {
				onSetMessage('El edificio se ha agregado con éxito!!');
				onClose();
				loadBuildingRows();
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
				location: form.location,
				description: form.description,
			})
			.then(() => {
				onSetMessage('El edificio se ha modificado con éxito!!');
				onClose();
				loadBuildingRows();
			})
			.catch((err) => {
				const newMsg: string = errToMsg(err);
				setErrorMessage(newMsg);
				setOpenSnackbar(true);
			});
		onSetOpenBackdrop(false);
	};

	React.useEffect(() => {
		loadOrganizationRows();
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
						Edificio
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
							id="organizationId"
							value={form.organization}
							disableClearable
							onChange={(event: any, newValue: Organization | null) => {
								onSetForm('organization', newValue);
							}}
							options={organizationRows}
							getOptionLabel={(option) => option.name}
							renderInput={(params) => (
								<TextField
									{...params}
									label="Organización"
									className={classes.textField}
									InputLabelProps={{
										className: classes.input,
									}}
									value={form.organization ? form.organization.name : undefined}
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
							id="location"
							name="location"
							label="Dirección"
							className={classes.textField}
							InputLabelProps={{
								shrink: true,
								className: classes.input,
							}}
							InputProps={{
								className: classes.input,
							}}
							onChange={handleChange}
							value={form.location}
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

export default BuildingForm;
