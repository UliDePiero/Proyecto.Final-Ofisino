import React from 'react';

type headerProps = {
	greeting: string;
};
const Header: React.FunctionComponent<headerProps> = ({ greeting }: headerProps) => (
	<div>
		<h1>{greeting}</h1>
	</div>
);

export default Header;
