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
	GridFilterModelState,
} from '@material-ui/data-grid';
import { parse, format } from 'date-fns';
import { makeStyles, Theme } from '@material-ui/core/styles';
import { Button, IconButton, Backdrop } from '@material-ui/core';
import CircularProgress from '@material-ui/core/CircularProgress';
import DeleteIcon from '@material-ui/icons/Delete';
import AddCircleOutlineIcon from '@material-ui/icons/AddCircleOutline';
import Drawer from '../components/common/Drawer';
import MessageCard from '../components/common/MessageCard';
import MessageSnackbar from '../components/common/MessageSnackbar';
import OrganizeMeetingForm from '../components/forms/OrganizeMeetingForm';
import OrganizeMeetingConfirmForm from '../components/forms/OrganizeMeetingConfirmForm';
import ConfirmDelete from '../components/common/ConfirmDelete';
import {
	OrganizeMeeting,
	MeetingRoomFeatures,
	OrganizeMeetingConfirm,
	LoginContext,
} from '../types/common/types';
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
const url = `${base}/organizemeeting`;

const OrganizeMeetings: React.FunctionComponent = () => {
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
			headerName: 'Reunión',
			field: 'summary',
			flex: 200,
			headerAlign: 'center',
			type: 'string',
			valueGetter: (params) => params.row?.summary,
		},
		{
			field: 'start',
			flex: 200,
			headerAlign: 'center',
			type: 'date',
			headerName: 'Fecha Desde',
			valueFormatter: (params: GridValueFormatterParams) => {
				return format(parse(params.row?.conditions?.start, 'yyyy-MM-dd', new Date()), 'dd/MM/yyyy');
			},
			valueGetter: (params: GridValueGetterParams) =>
				parse(params.row?.conditions?.start, 'yyyy-MM-dd', new Date()),
		},
		{
			field: 'end',
			flex: 200,
			headerAlign: 'center',
			type: 'date',
			headerName: 'Fecha hasta',
			valueFormatter: (params: GridValueFormatterParams) => {
				return format(parse(params.row?.conditions?.end, 'yyyy-MM-dd', new Date()), 'dd/MM/yyyy');
			},
			valueGetter: (params: GridValueGetterParams) =>
				parse(params.row?.conditions?.end, 'yyyy-MM-dd', new Date()),
		},
		{
			field: 'timeStart',
			flex: 200,
			headerAlign: 'center',
			type: 'date',
			headerName: 'Hora Desde',
			valueFormatter: (params: GridValueFormatterParams) => {
				return format(parse(params.row?.conditions?.time_start, 'HH:mm', new Date()), 'HH:mm');
			},
			valueGetter: (params: GridValueGetterParams) =>
				parse(params.row?.conditions?.time_start, 'HH:mm', new Date()),
		},
		{
			field: 'timeEnd',
			flex: 200,
			headerAlign: 'center',
			type: 'date',
			headerName: 'Hora hasta',
			valueFormatter: (params: GridValueFormatterParams) => {
				return format(parse(params.row?.conditions?.time_end, 'HH:mm', new Date()), 'HH:mm');
			},
			valueGetter: (params: GridValueGetterParams) =>
				parse(params.row?.conditions?.time_end, 'HH:mm', new Date()),
		},
		{
			field: 'duration',
			flex: 200,
			headerAlign: 'center',
			type: 'number',
			headerName: 'Duración [min]',
			valueGetter: (params) => params.row?.conditions?.duration,
		},
		{
			headerName: 'Estado',
			field: 'status',
			flex: 200,
			headerAlign: 'center',
			type: 'string',
			valueGetter: (params) => params.row?.status,
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
					setOpenConfirmOrganizeMeetingForm(true);
				};

				return (
					// eslint-disable-next-line react/destructuring-assignment
					parse(params.row?.conditions?.end, 'yyyy-MM-dd', new Date()) >= new Date() && (
						<>
							<Button title="Eliminar" onClick={handleDelete}>
								<DeleteIcon />
							</Button>
						</>
					)
				);
			},
		},
	];

	const [sortModel, setSortModel] = React.useState<GridSortModel>([
		{
			field: 'end',
			sort: 'asc',
		},
	]);
	const [filterModel, setFilterModel] = React.useState<GridFilterModelState>({
		items: [
			{ columnField: 'end', operatorValue: 'onOrAfter', value: format(new Date(), 'yyyy-MM-dd') },
		],
	});

	const [openOrganizeMeetingForm, setOpenOrganizeMeetingForm] = React.useState<boolean>(false);
	const [openOrganizeMeetingConfirmForm, setOpenOrganizeMeetingConfirmForm] =
		React.useState<boolean>(false);
	const [openConfirmOrganizeMeetingForm, setOpenConfirmOrganizeMeetingForm] =
		React.useState<boolean>(false);
	const [OrganizeMeetingRows, setOrganizeMeetingRows] = React.useState<OrganizeMeeting[]>([]);

	const [form, setForm] = React.useState<OrganizeMeeting>({
		start: new Date(),
		end: new Date(),
		timeStart: new Date(),
		timeEnd: new Date(),
		duration: 45,
		members: [],
		description: '',
		summary: '',
	});

	const [confirmForm, setConfirmForm] = React.useState<OrganizeMeetingConfirm[]>([]);
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

	const onSetConfirmForm = (array: OrganizeMeetingConfirm[]) => {
		setConfirmForm(array);
		console.log(confirmForm);
	};

	const onSetMessage = (text: string) => {
		setMessage(text);
		setOpenSnackbar(true);
	};

	const handleClickCreate = () => {
		setFormType('create');
		setForm({
			start: new Date(Date.now() + 3600 * 1000 * 24),
			end: new Date(Date.now() + 3600 * 1000 * 72),
			timeStart: parse('09:00', 'HH:mm', new Date()),
			timeEnd: parse('18:00', 'HH:mm', new Date()),
			duration: 45,
			members: [],
			description: '',
			summary: '',
			features: {
				aireAcondicionado: 0,
				computadoras: 0,
				proyector: 0,
				ventanas: 0,
				sillas: 0,
				mesas: 0,
			},
		});
		setOpenOrganizeMeetingForm(true);
	};

	const loadOrganizeMeetingRows = async () => {
		await axios
			.get(`${url}/by-me`)
			.then((response) => {
				setOrganizeMeetingRows(
					response.data.data.filter(
						(item: any) => item.status !== 'En proceso' && item.status !== 'Sin resultados'
					)
				);
			})
			.catch((err) => {
				setErrorMessage('');
				setOpenErrorSnackbar(true);
				console.log(err);
			});
	};

	const peticionDelete = async () => {
		await axios
			.delete(`${url}?id=${form.id}`)
			.then(() => {
				onSetMessage('La solicitud de organización de reunión se ha eliminado con éxito!!');
				setOpenConfirmOrganizeMeetingForm(false);
				loadOrganizeMeetingRows();
			})
			.catch((err) => {
				const newMsg: string = errToMsg(err);
				setErrorMessage(newMsg);
				setOpenErrorSnackbar(true);
				console.log(err);
			});
	};

	React.useEffect(() => {
		loadOrganizeMeetingRows();
	}, []);

	return (
		<div className={classes.root}>
			<Drawer />
			<div className={classes.content}>
				<div className={classes.toolbar} />

				<MessageCard title="Solicitudes de Organización de Reuniones" message="" />
				<IconButton aria-label="close" className={classes.button} onClick={handleClickCreate}>
					<AddCircleOutlineIcon />
				</IconButton>
				<DataGrid
					className={classes.dataGrid}
					rows={OrganizeMeetingRows}
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
				<OrganizeMeetingForm
					open={openOrganizeMeetingForm}
					onClose={() => {
						setOpenOrganizeMeetingForm(false);
					}}
					onOpenConfirm={() => {
						setOpenOrganizeMeetingConfirmForm(true);
					}}
					formType={formType}
					form={form}
					onSetForm={onSetForm}
					onSetConfirmForm={onSetConfirmForm}
					onSetOpenBackdrop={(flag: boolean) => {
						setOpenBackdrop(flag);
					}}
				/>
				<OrganizeMeetingConfirmForm
					open={openOrganizeMeetingConfirmForm}
					onClose={() => {
						setOpenOrganizeMeetingConfirmForm(false);
					}}
					onParentOpen={() => {
						setOpenOrganizeMeetingForm(true);
					}}
					loadOrganizeMeetingRows={loadOrganizeMeetingRows}
					formType={formType}
					form={confirmForm}
					onSetMessage={onSetMessage}
					onSetOpenBackdrop={(flag: boolean) => {
						setOpenBackdrop(flag);
					}}
				/>
				<ConfirmDelete
					open={openConfirmOrganizeMeetingForm}
					onClose={() => {
						setOpenConfirmOrganizeMeetingForm(false);
					}}
					peticionDelete={peticionDelete}
					modelo="la solicitud de organización de reunión"
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

export default OrganizeMeetings;
