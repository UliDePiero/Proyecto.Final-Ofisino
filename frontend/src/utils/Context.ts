const checkIfItIsInLocalStorage = (key: string) => {
	return localStorage.getItem(key) !== null;
};

type localStorageType = {
	[key: string]: string;
};

export const saveOnLocalStorage = (values: localStorageType[]) => {
	values.forEach(({ key, value }) => {
		localStorage.setItem(`Ofisino_${key}`, value);
	});
};
export default checkIfItIsInLocalStorage;
