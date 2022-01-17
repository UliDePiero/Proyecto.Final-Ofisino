import React from 'react';
import clsx from 'clsx';
import { makeStyles, Theme } from '@material-ui/core/styles';
import {
	Drawer as MuiDrawer,
	AppBar,
	Toolbar,
	List,
	Divider,
	IconButton,
	ListItem,
	ListItemText,
	Avatar,
} from '@material-ui/core';
import MenuIcon from '@material-ui/icons/Menu';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import BookmarkBorderOutlinedIcon from '@material-ui/icons/BookmarkBorderOutlined';
import CalendarTodayOutlinedIcon from '@material-ui/icons/CalendarTodayOutlined';
import GroupWorkOutlinedIcon from '@material-ui/icons/GroupWorkOutlined';
import HomeWorkOutlinedIcon from '@material-ui/icons/HomeWorkOutlined';
import MeetingRoomOutlinedIcon from '@material-ui/icons/MeetingRoomOutlined';
import DesktopMacOutlinedIcon from '@material-ui/icons/DesktopMacOutlined';
import CloudDownloadOutlinedIcon from '@material-ui/icons/CloudDownloadOutlined';
import PeopleAltOutlinedIcon from '@material-ui/icons/PeopleAltOutlined';
import { useHistory } from 'react-router-dom';
import OfisinoImage from '../../icons/Logo_sin_fondo.png';
import { buttonMap, LoginContext } from '../../types/common/types';
import LogoutButton from '../login/LogoutButton';
import { CredentialsContext } from '../../contexts/credentialsContext';
import AvatarComponent from './AvatarComponent';

const drawerWidth: number = 240;
const buttons: buttonMap[] = [
	{
		text: 'Calendario',
		icon: <CalendarTodayOutlinedIcon />,
		path: '/home',
		isAdminOption: false,
	},
	{
		text: 'Mis Reservas',
		icon: <BookmarkBorderOutlinedIcon />,
		path: '/reservation',
		isAdminOption: false,
	},
	{
		text: 'Reuniones Organizadas',
		icon: <PeopleAltOutlinedIcon />,
		path: '/organizemeeting',
		isAdminOption: false,
	},
	{
		text: 'Edificios',
		icon: <HomeWorkOutlinedIcon />,
		path: '/building',
		isAdminOption: true,
	},
	{
		text: 'Espacios de Trabajo',
		icon: <GroupWorkOutlinedIcon />,
		path: '/workingspace',
		isAdminOption: true,
	},
	{
		text: 'Salas de Reunión',
		icon: <MeetingRoomOutlinedIcon />,
		path: '/meetingroom',
		isAdminOption: true,
	},
	{
		text: 'Boxes',
		icon: <DesktopMacOutlinedIcon />,
		path: '/box',
		isAdminOption: true,
	},
	{
		text: 'Reportes',
		icon: <CloudDownloadOutlinedIcon />,
		path: '/reports',
		isAdminOption: true,
	},
];
const useStyles = makeStyles((theme: Theme) => ({
	root: {
		display: 'flex',
	},
	appBar: {
		backgroundColor: theme.palette.primary.light,
		zIndex: theme.zIndex.drawer + 1,
		transition: theme.transitions.create(['width', 'margin'], {
			easing: theme.transitions.easing.sharp,
			duration: theme.transitions.duration.leavingScreen,
		}),
		'.&MuiToolbar-gutters': {
			paddingLeft: '0px',
		},
	},
	appBarShift: {
		marginLeft: drawerWidth,
		width: `calc(100% - ${drawerWidth}px)`,
		transition: theme.transitions.create(['width', 'margin'], {
			easing: theme.transitions.easing.sharp,
			duration: theme.transitions.duration.enteringScreen,
		}),
	},
	menuButton: {
		marginRight: 36,
		color: theme.palette.primary.contrastText,
	},
	iconsAndText: {
		color: theme.palette.primary.contrastText,
		alignItems: 'center',
	},
	imgOfisino: {
		height: '3rem',
		width: '3.5rem',
		marginLeft: 'auto',
	},
	hide: {
		display: 'none',
	},
	drawer: {
		backgroundColor: theme.palette.primary.light,
		width: drawerWidth,
		flexShrink: 0,
	},
	drawerOpen: {
		backgroundColor: theme.palette.primary.light,
		width: drawerWidth,
		whiteSpace: 'pre-line',
		transition: theme.transitions.create('width', {
			easing: theme.transitions.easing.sharp,
			duration: theme.transitions.duration.enteringScreen,
		}),
	},
	drawerClose: {
		backgroundColor: theme.palette.primary.light,
		transition: theme.transitions.create('width', {
			easing: theme.transitions.easing.sharp,
			duration: theme.transitions.duration.leavingScreen,
		}),
		whiteSpace: 'nowrap',
		overflowX: 'hidden',
		width: theme.spacing(7) + 1,
		[theme.breakpoints.up('sm')]: {
			width: theme.spacing(9) + 1,
		},
	},
	toolbar: {
		display: 'flex',
		alignItems: 'center',
		justifyContent: 'flex-end',
		padding: theme.spacing(0, 1),
		// necessary for content to be below app bar
		...theme.mixins.toolbar,
	},
	content: {
		flexGrow: 1,
		padding: theme.spacing(3),
	},
}));

const Drawer = () => {
	const history = useHistory();
	const { isAdmin } = React.useContext<LoginContext>(CredentialsContext);

	const redirect = (path: string) => {
		return () => {
			history.push(path);
		};
	};

	const classes = useStyles();
	const [open, setOpen] = React.useState<boolean>(false);

	const handleDrawerOpen = (): void => {
		setOpen(true);
	};

	const handleDrawerClose = (): void => {
		setOpen(false);
	};

	return (
		<div className={classes.root}>
			<AppBar
				position="fixed"
				className={clsx(classes.appBar, {
					[classes.appBarShift]: open,
				})}
			>
				<Toolbar>
					<IconButton
						color="inherit"
						onClick={handleDrawerOpen}
						edge="start"
						className={clsx(classes.menuButton, {
							[classes.hide]: open,
						})}
					>
						<MenuIcon />
					</IconButton>
					<img src={OfisinoImage} alt="OFISINO" className={classes.imgOfisino} />
				</Toolbar>
			</AppBar>
			<MuiDrawer
				variant="permanent"
				className={clsx(classes.drawer, {
					[classes.drawerOpen]: open,
					[classes.drawerClose]: !open,
				})}
				classes={{
					paper: clsx({
						[classes.drawerOpen]: open,
						[classes.drawerClose]: !open,
					}),
				}}
				onMouseEnter={handleDrawerOpen}
				onMouseLeave={handleDrawerClose}
			>
				<div className={classes.toolbar}>
					<IconButton onClick={handleDrawerClose}>
						<MenuIcon className={classes.iconsAndText} />
					</IconButton>
				</div>
				<Divider />
				<AvatarComponent />
				<Divider />
				<List>
					{buttons
						.filter((but) => isAdmin === but.isAdminOption || but.isAdminOption === false)
						.map(
							(button: buttonMap): React.ReactElement => (
								<ListItem
									button
									key={String(button.text)}
									onClick={redirect(button.path as string)}
								>
									<ListItemIcon className={classes.iconsAndText}>{button.icon}</ListItemIcon>
									<ListItemText primary={button.text} className={classes.iconsAndText} />
								</ListItem>
							)
						)}
				</List>
				<Divider />
				<LogoutButton />
			</MuiDrawer>
		</div>
	);
};

export default Drawer;
