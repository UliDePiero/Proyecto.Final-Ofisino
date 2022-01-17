import * as React from 'react';
import axios from 'axios';
import { DataGrid, GridColDef, LocalizationV4, esES } from '@material-ui/data-grid';
import { makeStyles, Theme } from '@material-ui/core/styles';
import { Button, IconButton, Backdrop } from '@material-ui/core';
import CircularProgress from '@material-ui/core/CircularProgress';
import AddCircleOutlineIcon from '@material-ui/icons/AddCircleOutline';
import DeleteIcon from '@material-ui/icons/Delete';
import EditIcon from '@material-ui/icons/Edit';
import Drawer from '../components/common/Drawer';
import MessageCard from '../components/common/MessageCard';
import MessageSnackbar from '../components/common/MessageSnackbar';
import WorkingSpaceForm from '../components/forms/WorkingSpaceForm';
import ConfirmDelete from '../components/common/ConfirmDelete';
import { WorkingSpace } from '../types/common/types';
import errToMsg from '../utils/helpers';

const useStyles = makeStyles((theme: Theme) => ({
	root: {
		display: 'flex',
		height: '100%',
	},
	content: {
		flexGrow: 1,
		padding: theme.spacing(3),
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
	backdrop: {
		zIndex: theme.zIndex.modal + 1,
		color: '#fff',
	},
}));
const base = process.env.REACT_APP_BASE_URL;
const url = `${base}/workingspace`;

const WorkingSpaces: React.FunctionComponent = () => {
	const classes = useStyles();

	const columns: GridColDef[] = [
		{
			field: 'id',
			headerName: 'NRO',
			type: 'number',
			flex: 200,
			headerAlign: 'center',
			hide: true,
		},
		{
			field: 'building',
			headerName: 'Edificio',
			type: 'string',
			flex: 200,
			headerAlign: 'center',
			valueGetter: (params) => params.row?.building?.name,
		},
		{
			field: 'name',
			headerName: 'Nombre',
			type: 'string',
			flex: 200,
			headerAlign: 'center',
			valueGetter: (params) => params.row?.name,
		},
		{
			field: 'area',
			headerName: 'Area [m2]',
			type: 'number',
			flex: 200,
			headerAlign: 'center',
			valueGetter: (params) => params.row?.area,
		},
		{
			field: 'squareMetersPerBox',
			headerName: 'Espacio minimo por BOX [m2]',
			type: 'number',
			flex: 200,
			headerAlign: 'center',
			valueGetter: (params) => params.row?.square_meters_per_box,
		},
		{
			field: 'description',
			headerName: 'Descripción',
			type: 'string',
			flex: 200,
			headerAlign: 'center',
			valueGetter: (params) => params.row?.description,
		},
		{
			field: 'actions',
			headerName: 'Acciones',
			sortable: false,
			align: 'center',
			flex: 200,
			headerAlign: 'center',
			renderCell: (params) => {
				const handleDelete = () => {
					setForm({
						...form,
						id: params.row?.id,
					});
					setOpenConfirmWorkingSpaceForm(true);
				};

				const handleEdit = () => {
					setForm({
						id: params.row?.id,
						building: params.row?.building,
						name: params.row?.name,
						area: params.row?.area,
						squareMetersPerBox: params.row?.square_meters_per_box,
						description: params.row?.description,
					});
					setFormType('edit');
					setOpenWorkingSpaceForm(true);
				};

				return (
					<>
						<Button title="Modificar" onClick={handleEdit}>
							<EditIcon />
						</Button>
						<Button title="Eliminar" onClick={handleDelete}>
							<DeleteIcon />
						</Button>
					</>
				);
			},
		},
	];

	const [openWorkingSpaceForm, setOpenWorkingSpaceForm] = React.useState<boolean>(false);
	const [openConfirmWorkingSpaceForm, setOpenConfirmWorkingSpaceForm] =
		React.useState<boolean>(false);
	const [WorkingSpaceRows, setWorkingSpaceRows] = React.useState<WorkingSpace[]>([]);

	const handleCloseSnackbar = (reason: any) => {
		if (reason === 'clickaway') {
			return;
		}
		setOpenSnackbar(false);
		setOpenErrorSnackbar(false);
	};

	const [form, setForm] = React.useState<WorkingSpace>({
		name: '',
		area: 0,
		squareMetersPerBox: 0,
		description: '',
	});

	const [formType, setFormType] = React.useState<string>('create');
	const [openSnackbar, setOpenSnackbar] = React.useState<boolean>(false);
	const [message, setMessage] = React.useState<string>('');
	const [openErrorSnackbar, setOpenErrorSnackbar] = React.useState<boolean>(false);
	const [errorMessage, setErrorMessage] = React.useState<string>('');
	const [openBackdrop, setOpenBackdrop] = React.useState(false);

	const onSetForm = (fieldName: string, fieldValue: any) => {
		setForm({ ...form, [fieldName]: fieldValue });
		console.log(form);
	};

	const onSetMessage = (text: string) => {
		setMessage(text);
		setOpenSnackbar(true);
	};

	const handleClickCreate = () => {
		setFormType('create');
		setForm({
			name: '',
			area: 0,
			squareMetersPerBox: 0,
			description: '',
		});
		setOpenWorkingSpaceForm(true);
	};

	const loadWorkingSpaceRows = async () => {
		await axios
			.get(`${url}`)
			.then((response) => {
				setWorkingSpaceRows(response.data.data);
			})
			.catch((err) => {
				setErrorMessage('No se pudo cargar los espacios de trabajo.');
				setOpenErrorSnackbar(true);
				console.log(err);
			});
	};

	const peticionDelete = async () => {
		setOpenBackdrop(true);
		await axios
			.delete(`${url}?id=${form.id}`)
			.then(() => {
				onSetMessage('El espacio de trabajo se ha eliminado con éxito!!');
				setOpenConfirmWorkingSpaceForm(false);
				loadWorkingSpaceRows();
			})
			.catch((err) => {
				const newMsg: string = errToMsg(err);
				setErrorMessage(newMsg);
				setOpenErrorSnackbar(true);
				console.log(err);
			});
		setOpenBackdrop(false);
	};

	React.useEffect(() => {
		loadWorkingSpaceRows();
	}, []);

	return (
		<div className={classes.root}>
			<Drawer />
			<div className={classes.content}>
				<div className={classes.toolbar} />

				<MessageCard title="Espacios de Trabajo" message="" />
				<IconButton aria-label="close" className={classes.button} onClick={handleClickCreate}>
					<AddCircleOutlineIcon />
				</IconButton>
				<DataGrid
					className={classes.dataGrid}
					rows={WorkingSpaceRows}
					columns={columns}
					pageSize={5}
					autoHeight
					/* checkboxSelection */
					disableSelectionOnClick
					localeText={(esES as LocalizationV4).props.MuiDataGrid.localeText}
				/>
				<WorkingSpaceForm
					open={openWorkingSpaceForm}
					onClose={() => {
						setOpenWorkingSpaceForm(false);
					}}
					loadWorkingSpaceRows={loadWorkingSpaceRows}
					formType={formType}
					form={form}
					onSetForm={onSetForm}
					onSetMessage={onSetMessage}
					onSetOpenBackdrop={(flag: boolean) => {
						setOpenBackdrop(flag);
					}}
				/>
				<ConfirmDelete
					open={openConfirmWorkingSpaceForm}
					onClose={() => {
						setOpenConfirmWorkingSpaceForm(false);
					}}
					peticionDelete={peticionDelete}
					modelo="el espacio de trabajo"
				/>
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
			<Backdrop className={classes.backdrop} open={openBackdrop}>
				<CircularProgress color="inherit" />
			</Backdrop>
		</div>
	);
};

export default WorkingSpaces;
