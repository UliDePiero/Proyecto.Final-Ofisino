import * as React from 'react';
import axios from 'axios';
import { DataGrid, GridColDef, LocalizationV4, esES, GridSortModel } from '@material-ui/data-grid';
import { makeStyles, Theme } from '@material-ui/core/styles';
import { Button, IconButton, Backdrop } from '@material-ui/core';
import CircularProgress from '@material-ui/core/CircularProgress';
import AddCircleOutlineIcon from '@material-ui/icons/AddCircleOutline';
import DeleteIcon from '@material-ui/icons/Delete';
import EditIcon from '@material-ui/icons/Edit';
import Drawer from '../components/common/Drawer';
import MessageCard from '../components/common/MessageCard';
import MessageSnackbar from '../components/common/MessageSnackbar';
import BoxForm from '../components/forms/BoxForm';
import ConfirmDelete from '../components/common/ConfirmDelete';
import { Box } from '../types/common/types';
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
const url = `${base}/box`;

const Boxes: React.FunctionComponent = () => {
	const classes = useStyles();

	const columns: GridColDef[] = [
		{ field: 'id', headerName: 'NRO', type: 'number', flex: 200, hide: true },
		{
			field: 'workingSpace',
			headerName: 'Espacio de trabajo',
			type: 'string',
			flex: 200,
			valueGetter: (params) => params.row?.working_space?.name,
		},
		{
			field: 'name',
			headerName: 'Nombre',
			type: 'string',
			flex: 200,
			valueGetter: (params) => params.row?.name,
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
					setOpenConfirmBoxForm(true);
				};

				const handleEdit = () => {
					setForm({
						id: params.row?.id,
						name: params.row?.name,
						description: params.row?.description,
						workingSpace: {
							id: params.row?.working_space?.id,
							buildingId: params.row?.working_space?.building_id,
							name: params.row?.working_space?.name,
							area: params.row?.working_space?.area,
							squareMetersPerBox: params.row?.working_space?.square_meters_per_box,
							description: params.row?.working_space?.description,
						},
					});
					setFormType('edit');
					setOpenBoxForm(true);
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

	const [sortModel, setSortModel] = React.useState<GridSortModel>([
		{
			field: 'name',
			sort: 'asc',
		},
	]);

	const [openBoxForm, setOpenBoxForm] = React.useState<boolean>(false);
	const [openConfirmBoxForm, setOpenConfirmBoxForm] = React.useState<boolean>(false);
	const [BoxRows, setBoxRows] = React.useState<Box[]>([]);

	const [form, setForm] = React.useState<Box>({
		name: '',
		description: '',
	});

	const [formType, setFormType] = React.useState<string>('create');
	const [message, setMessage] = React.useState<string>('');
	const [errorMessage, setErrorMessage] = React.useState<string>('');
	const [openSnackbar, setOpenSnackbar] = React.useState<boolean>(false);
	const [openErrorSnackbar, setOpenErrorSnackbar] = React.useState<boolean>(false);
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
		setForm({
			name: '',
			description: '',
		});
		setOpenBoxForm(true);
	};

	const loadBoxRows = async () => {
		await axios
			.get(`${url}`)
			.then((response) => {
				setBoxRows(response.data.data);
			})
			.catch((err) => {
				setErrorMessage('Fallo cargando los boxes.');
				setOpenErrorSnackbar(true);
				console.log(err);
			});
	};

	const peticionDelete = async () => {
		setOpenBackdrop(true);
		await axios
			.delete(`${url}?id=${form.id}`)
			.then(() => {
				onSetMessage('El box se ha eliminado con éxito!!');
				setOpenConfirmBoxForm(false);
				loadBoxRows();
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
		loadBoxRows();
	}, []);

	return (
		<div className={classes.root}>
			<Drawer />
			<div className={classes.content}>
				<div className={classes.toolbar} />

				<MessageCard title="Boxes" message="" />
				<IconButton aria-label="close" className={classes.button} onClick={handleClickCreate}>
					<AddCircleOutlineIcon />
				</IconButton>
				<DataGrid
					className={classes.dataGrid}
					rows={BoxRows}
					columns={columns}
					pageSize={5}
					autoHeight
					/* checkboxSelection */
					disableSelectionOnClick
					localeText={(esES as LocalizationV4).props.MuiDataGrid.localeText}
					sortModel={sortModel}
					onSortModelChange={(newSortModel) => {
						if (newSortModel[0] !== sortModel[0]) {
							setSortModel(newSortModel);
						}
					}}
				/>
				<BoxForm
					open={openBoxForm}
					onClose={() => {
						setOpenBoxForm(false);
					}}
					loadBoxRows={loadBoxRows}
					formType={formType}
					form={form}
					onSetForm={onSetForm}
					onSetMessage={onSetMessage}
					onSetOpenBackdrop={(flag: boolean) => {
						setOpenBackdrop(flag);
					}}
				/>
				<ConfirmDelete
					open={openConfirmBoxForm}
					onClose={() => {
						setOpenConfirmBoxForm(false);
					}}
					peticionDelete={peticionDelete}
					modelo="el box"
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

export default Boxes;
