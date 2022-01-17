/* eslint-disable react/no-danger */
import * as React from 'react';
import Snackbar from '@material-ui/core/Snackbar';
import MuiAlert, { Color } from '@material-ui/lab/Alert';

interface messageSnackbarProps {
	open: boolean;
	onClose: (reason: any) => void;
	message: string;
	severity: Color;
}

const MessageSnackbar: React.FunctionComponent<messageSnackbarProps> = ({
	open,
	onClose,
	message,
	severity,
}: messageSnackbarProps) => {
	return (
		<Snackbar
			anchorOrigin={{
				vertical: 'bottom',
				horizontal: 'left',
			}}
			open={open}
			autoHideDuration={4000}
			onClose={onClose}
		>
			<MuiAlert elevation={6} variant="filled" severity={severity}>
				<div dangerouslySetInnerHTML={{ __html: message }} />
			</MuiAlert>
		</Snackbar>
	);
};

export default MessageSnackbar;
