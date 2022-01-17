import * as React from 'react';
import { makeStyles, Theme } from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';

const useStyles = makeStyles((theme: Theme) => ({
	root: {
		display: 'flex',
		margin: 'auto',
		minWidth: 275,
		width: 400,
		backgroundColor: theme.palette.primary.light,
	},
	content: {
		width: '100%',
	},
	title: {
		color: theme.palette.primary.contrastText,
		fontWeight: 700,
		position: 'relative',
		top: '5px',
	},
}));
interface messageCardProps {
	title: string;
	message: string;
}

const MessageCard: React.FunctionComponent<messageCardProps> = ({
	title,
	message,
}: messageCardProps) => {
	const classes = useStyles();

	return (
		<Card className={classes.root}>
			<CardContent className={classes.content}>
				<Typography className={classes.title} gutterBottom>
					{title}
				</Typography>
				<Typography variant="h5" component="h5">
					{message}
				</Typography>
			</CardContent>
		</Card>
	);
};

export default MessageCard;
