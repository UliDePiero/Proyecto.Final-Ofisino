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
import MeetingRoomForm from '../components/forms/MeetingRoomForm';
import ConfirmDelete from '../components/common/ConfirmDelete';
import { MeetingRoom, MeetingRoomFeatures } from '../types/common/types';
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
const url = `${base}/meetingroom`;

const MeetingRooms: React.FunctionComponent = () => {
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
			field: 'capacity',
			headerName: 'Capacidad',
			type: 'number',
			flex: 200,
			headerAlign: 'center',
			valueGetter: (params) => params.row?.capacity,
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
					setOpenConfirmMeetingRoomForm(true);
				};

				const handleEdit = () => {
					setForm({
						id: params.row?.id,
						building: params.row?.building,
						name: params.row?.name,
						capacity: params.row?.capacity,
						features: {
							aireAcondicionado: params.row?.features?.aire_acondicionado,
							computadoras: params.row?.features?.computadoras,
							proyector: params.row?.features?.proyector,
							ventanas: params.row?.features?.ventanas,
							sillas: params.row?.features?.sillas,
							mesas: params.row?.features?.mesas,
						},
						description: params.row?.description,
					});
					setFormType('edit');
					setOpenMeetingRoomForm(true);
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

	const [openMeetingRoomForm, setOpenMeetingRoomForm] = React.useState<boolean>(false);
	const [openConfirmMeetingRoomForm, setOpenConfirmMeetingRoomForm] =
		React.useState<boolean>(false);
	const [MeetingRoomRows, setMeetingRoomRows] = React.useState<MeetingRoom[]>([]);

	const [form, setForm] = React.useState<MeetingRoom>({
		name: '',
		capacity: 0,
		features: {
			aireAcondicionado: 0,
			computadoras: 0,
			proyector: 0,
			ventanas: 0,
			sillas: 0,
			mesas: 0,
		},
		description: '',
	});

	const [formType, setFormType] = React.useState<string>('create');
	const [openSnackbar, setOpenSnackbar] = React.useState<boolean>(false);
	const [openErrorSnackbar, setOpenErrorSnackbar] = React.useState<boolean>(false);
	const [message, setMessage] = React.useState<string>('');
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
		const keyForm: string[] = fieldName.split('.');

		if (keyForm.length > 1 && keyForm[0] === 'features') {
			let newKey: MeetingRoomFeatures | undefined = form.features;
			newKey = { ...newKey, [keyForm[1]]: fieldValue };
			setForm({ ...form, [keyForm[0]]: newKey });
		} else {
			setForm({ ...form, [fieldName]: fieldValue });
		}
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
			capacity: 0,
			features: {
				aireAcondicionado: 0,
				computadoras: 0,
				proyector: 0,
				ventanas: 0,
				sillas: 0,
				mesas: 0,
			},
			description: '',
		});
		setOpenMeetingRoomForm(true);
	};

	const loadMeetingRoomRows = async () => {
		await axios
			.get(`${url}`)
			.then((response) => {
				setMeetingRoomRows(response.data.data);
			})
			.catch((err) => {
				setErrorMessage('Fallo cargando las reuniones.');
				setOpenErrorSnackbar(true);
				console.log(err);
			});
	};

	const peticionDelete = async () => {
		setOpenBackdrop(true);
		await axios
			.delete(`${url}?id=${form.id}`)
			.then(() => {
				onSetMessage('La sala de reunión se ha eliminado con éxito!!');
				setOpenConfirmMeetingRoomForm(false);
				loadMeetingRoomRows();
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
		loadMeetingRoomRows();
	}, []);

	return (
		<div className={classes.root}>
			<Drawer />
			<div className={classes.content}>
				<div className={classes.toolbar} />

				<MessageCard title="Salas de reunión" message="" />
				<IconButton aria-label="close" className={classes.button} onClick={handleClickCreate}>
					<AddCircleOutlineIcon />
				</IconButton>
				<DataGrid
					className={classes.dataGrid}
					rows={MeetingRoomRows}
					columns={columns}
					pageSize={5}
					autoHeight
					/* checkboxSelection */
					disableSelectionOnClick
					localeText={(esES as LocalizationV4).props.MuiDataGrid.localeText}
				/>
				<MeetingRoomForm
					open={openMeetingRoomForm}
					onClose={() => {
						setOpenMeetingRoomForm(false);
					}}
					loadMeetingRoomRows={loadMeetingRoomRows}
					formType={formType}
					form={form}
					onSetForm={onSetForm}
					onSetMessage={onSetMessage}
					onSetOpenBackdrop={(flag: boolean) => {
						setOpenBackdrop(flag);
					}}
				/>
				<ConfirmDelete
					open={openConfirmMeetingRoomForm}
					onClose={() => {
						setOpenConfirmMeetingRoomForm(false);
					}}
					peticionDelete={peticionDelete}
					modelo="la sala de reunión"
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

export default MeetingRooms;
