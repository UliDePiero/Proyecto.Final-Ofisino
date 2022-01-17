const errToMsg = (
	err: any,
	defaultMsg: string = '<b>¡OH NO! ¡Ofisino está mareado!</b><br />Volvé a intentar o contactate con el administrador.'
) => {
	const map: any = {
		id: 'General',
		working_space_id: 'Espacio de trabajo',
		name: 'Nombre',
		description: 'Descripción',
		location: 'Ubicación',
		organization_id: 'Organización',
		user_id: 'Usuario',
		meeting_room_id: 'Sala de reunión',
		meeting_request_id: 'Solicitud de reunión',
		date: 'Fecha',
		duration: 'Duración',
		event: 'Evento',
		conditions: 'Condiciones',
		capacity: 'Capacidad',
		features: 'Características',
		calendar: 'Calendario',
		building_id: 'Edificio',
		box_id: 'Box',
		domain_id: 'Id de la cuenta',
		email: 'Email',
		avatar_url: 'URL del avatar',
		admin: 'Admin',
		area: 'Área',
		square_meters_per_box: 'Metros cuadrados por box',
		_schema: 'General',
	};
	let newMsg: string = '<b>¡ESTUVISTE CERCA!</b> Revisá los siguientes mensajes.</b><br />';
	try {
		Object.entries(err?.response?.data?.errors?.json ?? {}).forEach(([key, value]) => {
			newMsg = `${newMsg} <li><b>${map[key] ?? ''}: </b>`;
			if (Array.isArray(value)) {
				(value as any).forEach((row: any) => {
					newMsg = `${newMsg}${row}<br />`;
				});
			} else {
				Object.entries(value as object).forEach(([subKey, subValue]) => {
					newMsg = `${newMsg}.${subKey}`;
					(subValue as any).forEach((subRow: any) => {
						newMsg = `${newMsg}${subRow}<br />`;
					});
				});
			}
			newMsg = `${newMsg} </li>`;
		});
		Object.entries(err?.response?.data?.errors?.query ?? {}).forEach(([key, value]) => {
			newMsg = `${newMsg} <li><b>${map[key] ?? ''}: </b>`;
			if (Array.isArray(value)) {
				(value as any).forEach((row: any) => {
					newMsg = `${newMsg}${row}<br />`;
				});
			} else {
				Object.entries(value as object).forEach(([subKey, subValue]) => {
					newMsg = `${newMsg}.${subKey}`;
					(subValue as any).forEach((subRow: any) => {
						newMsg = `${newMsg}${subRow}<br />`;
					});
				});
			}
			newMsg = `${newMsg} </li>`;
		});
	} catch (error) {
		console.log(err?.response);
		newMsg = defaultMsg;
	}
	return newMsg;
};

export default errToMsg;
