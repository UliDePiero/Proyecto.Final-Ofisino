import * as React from 'react';
import axios from 'axios';
import {
	DataGrid,
	GridColDef,
	LocalizationV4,
	esES,
	GridValueFormatterParams,
	GridValueGetterParams,
	GridSortModel,
	GridFilterModel,
} from '@material-ui/data-grid';
import { makeStyles, Theme } from '@material-ui/core/styles';
import { Button, IconButton, Backdrop } from '@material-ui/core';
import CircularProgress from '@material-ui/core/CircularProgress';
import AddCircleOutlineIcon from '@material-ui/icons/AddCircleOutline';
import DeleteIcon from '@material-ui/icons/Delete';
import EditIcon from '@material-ui/icons/Edit';
import { parse, format } from 'date-fns';
import Drawer from '../components/common/Drawer';
import MessageCard from '../components/common/MessageCard';
import MessageSnackbar from '../components/common/MessageSnackbar';
import ReservationForm from '../components/forms/ReservationForm';
import ConfirmDelete from '../components/common/ConfirmDelete';
import { CredentialsContext } from '../contexts/credentialsContext';
import { Reservation, LoginContext } from '../types/common/types';
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
const url = `${base}/reservation`;

const Reservations: React.FunctionComponent = () => {
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
			field: 'date',
			type: 'date',
			headerName: 'Fecha',
			flex: 200,
			headerAlign: 'center',
			valueFormatter: (params: GridValueFormatterParams) => {
				return format(parse(params.row?.date, 'yyyy-MM-dd', new Date()), 'dd/MM/yyyy');
			},
			valueGetter: (params: GridValueGetterParams) =>
				parse(params.row?.date, 'yyyy-MM-dd', new Date()),
		},
		{
			field: 'username',
			headerName: 'Nombre',
			type: 'string',
			flex: 200,
			headerAlign: 'center',
			valueGetter: (params) => params.row?.user?.name,
		},
		{
			field: 'box',
			headerName: 'Box',
			type: 'string',
			flex: 200,
			headerAlign: 'center',
			valueGetter: (params) => params.row?.box?.name,
		},
		{
			field: 'actions',
			headerName: 'Acciones',
			sortable: false,
			align: 'center',
			flex: 200,
			headerAlign: 'center',
			renderCell: (params) => {
				const { row } = params;
				const handleDelete = () => {
					setForm({
						...form,
						date: parse(row?.date, 'yyyy-MM-dd', new Date()),
						id: row?.id,
					});
					setOpenConfirmReservationForm(true);
				};

				const handleEdit = () => {
					setForm({
						id: row?.id,
						date: parse(row?.date, 'yyyy-MM-dd', new Date()),
						box: {
							id: row?.box?.id,
							name: row?.box?.name,
							description: row?.box?.description,
							workingSpaceId: row?.box?.working_space_id,
						},
					});
					setFormType('edit');
					setOpenReservationForm(true);
				};

				return (
					parse(row?.date, 'yyyy-MM-dd', new Date()) >= new Date() && (
						<>
							<Button title="Modificar" onClick={handleEdit}>
								<EditIcon />
							</Button>
							<Button title="Eliminar" onClick={handleDelete}>
								<DeleteIcon />
							</Button>
						</>
					)
				);
			},
		},
	];

	const { userId } = React.useContext<LoginContext>(CredentialsContext);

	const [sortModel, setSortModel] = React.useState<GridSortModel>([
		{
			field: 'date',
			sort: 'asc',
		},
	]);
	const [filterModel, setFilterModel] = React.useState<GridFilterModel>({
		items: [
			{ columnField: 'date', operatorValue: 'onOrAfter', value: format(new Date(), 'yyyy-MM-dd') },
		],
	});

	const [openReservationForm, setOpenReservationForm] = React.useState<boolean>(false);
	const [openConfirmReservationForm, setOpenConfirmReservationForm] =
		React.useState<boolean>(false);
	const [reservationRows, setReservationRows] = React.useState<Reservation[]>([]);

	const [form, setForm] = React.useState<Reservation>();

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

	const onSetMessage = (text: string) => {
		setMessage(text);
		setOpenSnackbar(true);
	};

	const handleClickCreate = () => {
		setFormType('create');
		setOpenReservationForm(true);
	};

	const loadReservationRows = async () => {
		await axios
			.get(`${url}`)
			.then((response) => {
				setReservationRows(response.data.data);
			})
			.catch((err) => {
				setErrorMessage('No se pudieron cargar las reservas.');
				setOpenErrorSnackbar(true);
				console.log(err);
			});
	};

	const peticionDelete = async () => {
		setOpenBackdrop(true);
		await axios
			.delete(`${url}?id=${form?.id}`)
			.then(() => {
				onSetMessage('La reserva se ha eliminado con éxito!!');
				setOpenConfirmReservationForm(false);
				loadReservationRows();
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
		loadReservationRows();
	}, []);

	return (
		<div className={classes.root}>
			<Drawer />
			<div className={classes.content}>
				<div className={classes.toolbar} />

				<MessageCard title="Reservas" message="" />
				<IconButton aria-label="close" className={classes.button} onClick={handleClickCreate}>
					<AddCircleOutlineIcon />
				</IconButton>
				<DataGrid
					className={classes.dataGrid}
					rows={reservationRows}
					columns={columns}
					pageSize={5}
					autoHeight
					/* checkboxSelection */
					disableSelectionOnClick
					localeText={(esES as LocalizationV4).props.MuiDataGrid.localeText}
					filterModel={filterModel}
					onFilterModelChange={(newFilterModel) => setFilterModel(newFilterModel)}
					sortModel={sortModel}
					onSortModelChange={(newSortModel) => {
						if (newSortModel[0] !== sortModel[0]) {
							setSortModel(newSortModel);
						}
					}}
				/>
				<ReservationForm
					open={openReservationForm}
					onClose={() => {
						setOpenReservationForm(false);
					}}
					loadReservationRows={loadReservationRows}
					futureReservationDateRows={reservationRows
						.filter(
							(reservation) =>
								parse(reservation.date.toString(), 'yyyy-MM-dd', new Date()) >= new Date() &&
								reservation?.user?.id === userId
						)
						.map((reservation) => {
							return reservation.date.toString();
						})}
					formType={formType}
					form={form}
					onSetMessage={onSetMessage}
					onSetOpenBackdrop={(flag: boolean) => {
						setOpenBackdrop(flag);
					}}
				/>
				<ConfirmDelete
					open={openConfirmReservationForm}
					onClose={() => {
						setOpenConfirmReservationForm(false);
					}}
					peticionDelete={peticionDelete}
					modelo="la reserva"
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

export default Reservations;
