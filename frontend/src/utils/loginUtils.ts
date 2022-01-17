import axios from 'axios';
import { OrganizationMember } from '../types/common/types';

const base = process.env.REACT_APP_BASE_URL;

const validEmailDomain = async (email: string): Promise<Boolean> => {
	const promise = await axios
		.get(`${base}/orgmembers`)
		.then((response) => {
			console.log(email);
			console.log(
				response.data.data
					.map((organizationMember: OrganizationMember) => {
						return organizationMember.email;
					})
					.flat()
			);
			return response.data.data
				.map((organizationMember: OrganizationMember) => {
					return organizationMember.email;
				})
				.flat()
				.includes(email);
		})
		.catch((err) => {
			console.log(err);
			return false;
		});
	return promise;
};

export default validEmailDomain;
