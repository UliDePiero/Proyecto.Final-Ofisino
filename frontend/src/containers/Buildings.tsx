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
import BuildingForm from '../components/forms/BuildingForm';
import ConfirmDelete from '../components/common/ConfirmDelete';
import { Building } from '../types/common/types';
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
const url = `${base}/building`;

const Buildings: React.FunctionComponent = () => {
	const classes = useStyles();

	const columns: GridColDef[] = [
		{ field: 'id', headerName: 'NRO', type: 'number', flex: 200, hide: true },
		{
			field: 'name',
			headerName: 'Nombre',
			type: 'string',
			flex: 200,
			valueGetter: (params) => params.row?.name,
		},
		{
			field: 'location',
			headerName: 'Dirección',
			type: 'string',
			flex: 200,
			valueGetter: (params) => params.row?.location,
		},
		{
			field: 'description',
			headerName: 'Descripción',
			type: 'string',
			flex: 200,
			valueGetter: (params) => params.row?.description,
		},
		{
			field: 'actions',
			headerName: 'Acciones',
			sortable: false,
			align: 'center',
			headerAlign: 'center',
			flex: 200,
			renderCell: (params) => {
				const handleDelete = () => {
					setForm({
						...form,
						id: params.row?.id,
					});
					setOpenConfirmBuildingForm(true);
				};

				const handleEdit = () => {
					setForm({
						id: params.row?.id,
						organization: params.row?.organization,
						name: params.row?.name,
						location: params.row?.location,
						description: params.row?.description,
					});
					setFormType('edit');
					setOpenBuildingForm(true);
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

	const [openBuildingForm, setOpenBuildingForm] = React.useState<boolean>(false);
	const [openConfirmBuildingForm, setOpenConfirmBuildingForm] = React.useState<boolean>(false);
	const [BuildingRows, setBuildingRows] = React.useState<Building[]>([]);

	const [form, setForm] = React.useState<Building>({
		name: '',
		location: '',
		description: '',
	});

	const [formType, setFormType] = React.useState<string>('create');
	const [openSnackbar, setOpenSnackbar] = React.useState<boolean>(false);
	const [message, setMessage] = React.useState<string>('');
	const [openErrorSnackbar, setOpenErrorSnackbar] = React.useState<boolean>(false);
	const [errorMessage, setErrorMessage] = React.useState<string>('');
	const [openBackdrop, setOpenBackdrop] = React.useState(false);

	const handleCloseSnackbar = (reason: any) => {
		if (reason === 'clickaway') {
			return;
		}
		setOpenSnackbar(false);
		setOpenErrorSnackbar(false);
	};

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
		setForm({ ...form, name: '', location: '', description: '' });
		setOpenBuildingForm(true);
	};

	const loadBuildingRows = async () => {
		await axios
			.get(`${url}`)
			.then((response) => {
				setBuildingRows(response.data.data);
			})
			.catch((err) => {
				setErrorMessage('Fallo cargando los edificios.');
				setOpenErrorSnackbar(true);
				console.log(err);
			});
	};

	const peticionDelete = async () => {
		setOpenBackdrop(true);
		await axios
			.delete(`${url}?id=${form.id}`)
			.then(() => {
				onSetMessage('El edificio se ha eliminado con éxito!!');
				setOpenConfirmBuildingForm(false);
				loadBuildingRows();
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
		loadBuildingRows();
	}, []);

	return (
		<div className={classes.root}>
			<Drawer />
			<div className={classes.content}>
				<div className={classes.toolbar} />
				<MessageCard title="Edificios" message="" />
				<IconButton aria-label="close" className={classes.button} onClick={handleClickCreate}>
					<AddCircleOutlineIcon />
				</IconButton>
				<DataGrid
					className={classes.dataGrid}
					rows={BuildingRows}
					columns={columns}
					pageSize={5}
					autoHeight
					/* checkboxSelection */
					disableSelectionOnClick
					localeText={(esES as LocalizationV4).props.MuiDataGrid.localeText}
				/>
				<BuildingForm
					open={openBuildingForm}
					onClose={() => {
						setOpenBuildingForm(false);
					}}
					loadBuildingRows={loadBuildingRows}
					formType={formType}
					form={form}
					onSetForm={onSetForm}
					onSetMessage={onSetMessage}
					onSetOpenBackdrop={(flag: boolean) => {
						setOpenBackdrop(flag);
					}}
				/>
				<ConfirmDelete
					open={openConfirmBuildingForm}
					onClose={() => {
						setOpenConfirmBuildingForm(false);
					}}
					peticionDelete={peticionDelete}
					modelo="el edificio"
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

export default Buildings;
