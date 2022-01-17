import axios from 'axios';

const getMeetingData = async (id: string) => {
	const base = process.env.REACT_APP_BASE_URL;
	const response = await axios.get(`${base}/meeting?id=${id}`);
	return response.data;
};

export const formatDate = (dateStart: string, dateEnd: string) => {
	const options: Intl.DateTimeFormatOptions = {
		weekday: 'long',
		year: 'numeric',
		month: 'long',
		day: 'numeric',
	};
	const startDate = new Date(dateStart);
	const endDate = new Date(dateEnd);
	const startingMinutes =
		startDate.getMinutes() < 10 ? `0${startDate.getMinutes()}` : `${startDate.getMinutes()}`;
	const finishingMinutes =
		endDate.getMinutes() < 10 ? `0${endDate.getMinutes()}` : `${endDate.getMinutes()}`;
	const startHour = `${startDate.getHours()}:${startingMinutes}`;
	const endHour = `${endDate.getHours()}:${finishingMinutes}`;
	if (areTheSameDay(startDate, endDate)) {
		const day = startDate.toLocaleDateString('es-ES', options);
		return `${day} · ${startHour} - ${endHour}`;
	}
	const startDay = startDate.toLocaleDateString('es-ES', options);
	const endDay = endDate.toLocaleDateString('es-ES', options);
	return `${startDay} - ${endDay} · ${startHour} - ${endHour}`;
};

const areTheSameDay = (date1: Date, date2: Date) => {
	return (
		date1.getFullYear() === date2.getFullYear() &&
		date1.getMonth() === date2.getMonth() &&
		date1.getDate() === date2.getDate()
	);
};

export default getMeetingData;
