import * as React from 'react';
import TextField from '@material-ui/core/TextField';
import Autocomplete from '@material-ui/lab/Autocomplete';
/* Example of data */
const topEvents = [
	{ eventTitle: 'The Shawshank Redemption', date: '2021-07-08' },
	{ eventTitle: 'The Godfather', date: '2021-07-08' },
	{ eventTitle: 'The Godfather: Part II', date: '2021-07-08' },
	{ eventTitle: 'The Dark Knight', date: '2021-07-08' },
	{ eventTitle: '12 Angry Men', date: '2021-07-08' },
	{ eventTitle: "Schindler's List", date: '2021-07-08' },
	{ eventTitle: 'Pulp Fiction', date: '2021-07-08' },
];

const SearchBar = () => {
	return (
		<div style={{ width: 300 }}>
			<Autocomplete
				id="free-solo-demo"
				freeSolo
				options={topEvents.map((option) => option.eventTitle)}
				renderInput={(params: any) => (
					<TextField label="freeSolo" margin="normal" variant="outlined" />
				)}
			/>
		</div>
	);
};

export default SearchBar;
