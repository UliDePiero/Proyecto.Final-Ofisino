import * as React from 'react';
import { makeStyles, Theme } from '@material-ui/core/styles';
import {
	Button,
	Dialog,
	DialogTitle,
	DialogContent,
	DialogContentText,
	DialogActions,
	Typography,
} from '@material-ui/core';

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

interface confirmDeleteProps {
	modelo: string;
	open: boolean;
	onClose: () => void;
	peticionDelete: () => void;
}

const ConfirmDelete: React.FunctionComponent<confirmDeleteProps> = ({
	modelo,
	open,
	onClose,
	peticionDelete,
}: confirmDeleteProps) => {
	const classes = useStyles();

	return (
		<Dialog
			PaperProps={{
				className: classes.paper,
			}}
			open={open}
			onClose={onClose}
		>
			<DialogTitle>
				<Typography variant="h6" className={classes.title}>
					Esta seguro que desea eliminar {modelo}
				</Typography>
			</DialogTitle>
			<DialogContent dividers>
				<DialogContentText>Esta acción es irreversible.</DialogContentText>
			</DialogContent>
			<DialogActions>
				<Button onClick={onClose} className={classes.button} autoFocus>
					Cancelar
				</Button>
				<Button onClick={peticionDelete} className={classes.button}>
					Eliminar
				</Button>
			</DialogActions>
		</Dialog>
	);
};

export default ConfirmDelete;
