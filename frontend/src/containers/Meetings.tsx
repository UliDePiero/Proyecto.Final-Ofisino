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
import { format } from 'date-fns';
import { makeStyles, Theme } from '@material-ui/core/styles';
import { CredentialsContext } from '../contexts/credentialsContext';
import Drawer from '../components/common/Drawer';
import MessageCard from '../components/common/MessageCard';
import MessageSnackbar from '../components/common/MessageSnackbar';
import { LoginContext, Meeting } from '../types/common/types';

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
}));

const base = process.env.REACT_APP_BASE_URL;
const url = `${base}/meeting`;

const Meetings: React.FunctionComponent = () => {
	const classes = useStyles();

	const columns: GridColDef[] = [
		{ field: 'id', headerName: 'NRO', type: 'number', flex: 100, headerAlign: 'center' },
		{
			field: 'description',
			headerName: 'Agenda',
			type: 'string',
			flex: 100,
			headerAlign: 'center',
			valueGetter: (params) => params.row?.description,
		},
		{
			field: 'date',
			flex: 100,
			headerAlign: 'center',
			type: 'date',
			headerName: 'Fecha',
			valueFormatter: (params: GridValueFormatterParams) => {
				return format(new Date(params.row?.date), 'dd/MM/yyyy HH:mm');
			},
			valueGetter: (params: GridValueGetterParams) => {
				return params.row?.date;
			},
		},
		{
			field: 'duration',
			flex: 100,
			headerAlign: 'center',
			type: 'number',
			headerName: 'Duración [min]',
			valueGetter: (params) => params.row?.duration,
		},
	];
	const [sortModel, setSortModel] = React.useState<GridSortModel>([
		{
			field: 'date',
			sort: 'asc',
		},
	]);
	const [filterModel, setFilterModel] = React.useState<GridFilterModelState>({
		items: [
			{ columnField: 'date', operatorValue: 'onOrAfter', value: format(new Date(), 'yyyy-MM-dd') },
		],
	});

	const [MeetingRows, setMeetingRows] = React.useState<Meeting[]>([]);
	const [openErrorSnackbar, setOpenErrorSnackbar] = React.useState<boolean>(false);
	const [errorMessage, setErrorMessage] = React.useState<string>('');

	const handleCloseSnackbar = (reason: any) => {
		if (reason === 'clickaway') {
			return;
		}
		setOpenErrorSnackbar(false);
	};

	const loadMeetingRows = async () => {
		await axios
			.get(`${url}/where-im-member`)
			.then((response) => {
				setMeetingRows(response.data.data);
			})
			.catch((err) => {
				setErrorMessage('');
				setOpenErrorSnackbar(true);
				console.log(err);
			});
	};

	React.useEffect(() => {
		loadMeetingRows();
	}, []);

	return (
		<div className={classes.root}>
			<Drawer />
			<div className={classes.content}>
				<div className={classes.toolbar} />
				<MessageCard title="Mis Reuniones" message="" />
				<DataGrid
					className={classes.dataGrid}
					rows={MeetingRows}
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
			</div>
			<div className={classes.MessageSnackbar}>
				<MessageSnackbar
					open={openErrorSnackbar}
					onClose={handleCloseSnackbar}
					message={errorMessage}
					severity="error"
				/>
			</div>
		</div>
	);
};

export default Meetings;
