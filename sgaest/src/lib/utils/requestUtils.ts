import { browser } from '$app/env';
import { goto } from '$app/navigation';
import type { Token, UserResponse } from '$lib/interfaces/user.interface';
import type { CustomError } from '$lib/interfaces/error.interface';
import { userData } from '$lib/store/userStore';
import { variables } from '$lib/utils/constants';
import { formatText } from '$lib/formats/formatString';
import { decodeToken } from '$lib/utils/decodetoken';
import { loading } from '$lib/store/loadingStore';
import { addToast } from '$lib/store/toastStore';
import { pushNotifications, addNotifications } from '$lib/store/pushNotificationStore';
import { encodeQueryString } from '$lib/helpers/baseHelper';

const reload = async (page): Promise<void> => {
	loading.setLoading(true, 'Cargando, espere por favor...');
	if (page === undefined) {
		await window.location.reload();
	}
	await window.location.replace(page);
};

export const browserGet = (key: string): string | undefined => {
	if (browser) {
		const item = localStorage.getItem(key);
		if (item) {
			return item;
		}
	}
	return null;
};

export const browserSet = (key: string, value: string): void => {
	if (browser) {
		localStorage.setItem(key, value);
	}
};

export const apiPOST = async (
	fetch,
	url: string,
	body: unknown
): Promise<[object, Array<CustomError>]> => {
	try {
		const headers = {};
		if (!(body instanceof FormData)) {
			headers['Content-Type'] = 'application/json';
			body = JSON.stringify(body);
			const token = browserGet('accessToken');
			if (token) {
				headers['Authorization'] = `Bearer ${token}`;
			}
			const res = await fetch(`${variables.BASE_API_URI}/${url}`, {
				method: 'POST',
				body,
				headers
			});
			if (res.status >= 400) {
				const errors: Array<CustomError> = [];
				errors.push({ error: 'Usuario no identificado' });
				//addToast({ type: 'error', header: 'Ocurrio un error', body: 'Usuario no identificado' });
				goto('/lock-screen');
				//return [{}, errors];
			} else if (!res.ok) {
				const errors: Array<CustomError> = [];
				errors.push({ error: 'Error de conexión' });
				return [{}, errors];
			}

			const response = await res.json();
			if (!response.isSuccess && !response.module_access && response.redirect === 'changepass') {
				await goto('/changepass');
			}
			return [response, []];
		}
	} catch (error) {
		const errors: Array<CustomError> = [{ error: error }];
		return [{}, errors];
	}
};

export const apiPOSTFormData = async (
	fetch,
	url: string,
	body: FormData
): Promise<[object, Array<CustomError>]> => {
	try {
		const headers = {};
		const token = browserGet('accessToken');
		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}
		const res = await fetch(`${variables.BASE_API_URI}/${url}`, {
			method: 'POST',
			body,
			headers
		});
		if (res.status >= 400) {
			const errors: Array<CustomError> = [];
			errors.push({ error: 'Usuario no identificado' });
			//addToast({ type: 'error', header: 'Ocurrio un error', body: 'Usuario no identificado' });
			goto('/lock-screen');
			//return [{}, errors];
		} else if (!res.ok) {
			const errors: Array<CustomError> = [];
			errors.push({ error: 'Error de conexión' });
			return [{}, errors];
		}

		const response = await res.json();
		if (!response.isSuccess && !response.module_access && response.redirect === 'changepass') {
			await goto('/changepass');
		}
		return [response, []];
	} catch (error) {
		const errors: Array<CustomError> = [{ error: error }];
		return [{}, errors];
	}
};

export const apiGET = async (
	fetch,
	url: string,
	params: unknown
): Promise<[object, Array<CustomError>]> => {
	try {
		const headers = {};
		headers['Content-Type'] = 'application/json';
		const token = browserGet('accessToken');
		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}
		let newURL = '';
		if (params) {
			newURL = `${variables.BASE_API_URI}/${url}` + (await encodeQueryString(params));
		} else {
			newURL = `${variables.BASE_API_URI}/${url}`;
		}

		const res = await fetch(newURL, {
			headers: headers
		});
		if (res.status >= 400) {
			const errors: Array<CustomError> = [];
			errors.push({ error: 'Usuario no identificado' });
			//addToast({ type: 'error', header: 'Ocurrio un error', body: 'Usuario no identificado' });
			goto('/lock-screen');
			//return [{}, errors];
		} else if (!res.ok) {
			const errors: Array<CustomError> = [];
			errors.push({ error: 'Error de conexión' });
			return [{}, errors];
		}
		const response = await res.json();
		if (!response.isSuccess && !response.module_access && response.redirect === 'changepass') {
			await goto('/changepass');
		}
		return [response, []];
	} catch (error) {
		const errors: Array<CustomError> = [{ error: error }];
		return [{}, errors];
	}
};

export const getCurrentUser = async (
	fetch,
	refreshUrl: string,
	userUrl: string
): Promise<[object, Array<CustomError>]> => {
	const jsonRes = await fetch(refreshUrl, {
		method: 'POST',
		mode: 'cors',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			refresh: `${browserGet('refreshToken')}`
		})
	});
	const accessRefresh: Token = await jsonRes.json();
	if (accessRefresh.access) {
		const res = await fetch(userUrl, {
			headers: {
				Authorization: `Bearer ${accessRefresh.access}`
			}
		});
		if (res.status === 400) {
			const data = await res.json();
			const error = data.user.error[0];
			return [{}, error];
		}
		const response = await res.json();
		return [response.user, []];
	} else {
		return [{}, [{ error: 'Refresh token is invalid...' }]];
	}
};

export const getCurrentRefresh = async (
	fetch,
	refreshUrl: string
): Promise<[object, Array<CustomError>]> => {
	const response = await fetch(refreshUrl, {
		method: 'POST',
		mode: 'cors',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${browserGet('accessToken')}`
		},
		body: JSON.stringify({
			refresh: `${browserGet('refreshToken')}`
		})
	});

	return response;
};

export const loginIn = async (
	fetch,
	url: string,
	body: unknown
): Promise<[object, Array<CustomError>]> => {
	try {
		const headers = {};
		if (!(body instanceof FormData)) {
			headers['Content-Type'] = 'application/json';
			body = JSON.stringify(body);
			const token = browserGet('refreshToken');
			if (token) {
				headers['Authorization'] = `Bearer ${token}`;
			}
			const res = await fetch(`${variables.BASE_API_URI}/${url}`, {
				method: 'POST',
				body,
				headers
			});
			//console.log(res);
			const response = await res.json();
			//console.log(response);
			if (res.status >= 400) {
				const errors: Array<CustomError> = [];
				if (response.message) {
					errors.push({ error: response.message });
				} else {
					errors.push({ error: 'Usuario no identificado' });
				}

				return [{}, errors];
			} else if (!res.ok) {
				const errors: Array<CustomError> = [];
				errors.push({ error: 'Error de conexión' });
				return [{}, errors];
			}

			//const response = await res.json();
			return [response, []];
		}
	} catch (error) {
		const errors: Array<CustomError> = [{ error: 'Conexión no establecida' }];
		return [{}, errors];
	}
};

export const logOutUser = async (): Promise<void> => {
	loading.setLoading(true, 'Cargando, espere por favor...');
	const res = await fetch(`${variables.BASE_API_URI}/token/refresh`, {
		method: 'POST',
		mode: 'cors',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			refresh: `${browserGet('refreshToken')}`
		})
	});
	if (res.status >= 400 || res.ok === false) {
		//addNotification({title: 'Cerror sesión correctamente', type: 'info', icon: 'info'});
		//addToast({ header: 'Notificación', body: `Cerro sesión correctamente.`, type: 'success' });
		const ds = browserGet('dataSession');
		loading.setLoading(true, 'Cargando, espere por favor...');
		const dataSession = JSON.parse(ds);
		const templatebasesetting = dataSession['templatebasesetting'];
		window.localStorage.clear();
		userData.set({});
		if (!templatebasesetting.use_api) {
			window.open(`${variables.BASE_API}/logout`, '_self');
		} else {
			return reload('/login');
		}
	}
	const json = decodeToken(await res.json());
	browserSet('refreshToken', json['tokens'].refresh);
	browserSet('accessToken', json['tokens'].access);
	browserSet('dataSession', JSON.stringify(json));
	userData.set(json);

	await fetch(`${variables.BASE_API_URI}/logout`, {
		method: 'POST',
		mode: 'cors',
		headers: {
			Authorization: `Bearer ${browserGet('accessToken')}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			refresh: `${browserGet('refreshToken')}`
		})
	});

	//addNotification({title: 'Cerror sesión correctamente', type: 'info', icon: 'info'});
	//addToast({ header: 'Notificación', body: `Cerro sesión correctamente.`, type: 'success' });
	const ds = browserGet('dataSession');
	loading.setLoading(true, 'Cargando, espere por favor...');
	const dataSession = JSON.parse(ds);
	const templatebasesetting = dataSession['templatebasesetting'];
	window.localStorage.clear();
	userData.set({});
	if (!templatebasesetting.use_api) {
		window.open(`${variables.BASE_API}/logout`, '_self');
	} else {
		return reload('/login');
	}
};

export const changeProfile = async (url: string, data: object, type: number): Promise<void> => {
	loading.setLoading(true, 'Cargando, espere por favor...');
	data['refresh'] = `${browserGet('refreshToken')}`;
	const res = await fetch(`${variables.BASE_API_URI}/${url}`, {
		method: 'POST',
		mode: 'cors',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});
	if (res.status >= 400 || res.ok === false) {
		window.localStorage.clear();
		userData.set({});
		//addNotification({title: 'Su sesión expiro, vuelva a iniciar sesión', type: 'info', icon: 'info'});
		//addToast({ header: 'Tiempo de sesión', body: `Su sesión expiro, vuelva a iniciar sesión.`, type: 'info' });
		return await goto('/login');
	}
	const json = decodeToken(await res.json());
	browserSet('refreshToken', json['tokens'].refresh);
	browserSet('accessToken', json['tokens'].access);
	browserSet('dataSession', JSON.stringify(json));
	userData.set(json);
	loading.setLoading(false, 'Cargando, espere por favor...');
	if (type === 1) {
		addToast({
			header: 'Notificación',
			body: 'Se cambio correctamente de periodo académico',
			type: 'success'
		});
	} else if (type === 2) {
		addToast({
			header: 'Notificación',
			body: 'Se cambio correctamente de carrera',
			type: 'success'
		});
	} else if (type === 3) {
		addToast({
			header: 'Notificación',
			body: 'Se actualizó correctamente la imagen de perfil',
			type: 'success'
		});
	}
	loading.setLoading(true, 'Cargando, espere por favor...');
	await setTimeout(() => {
		return reload('/');
	}, 3600);
};

export const handlePostRequestsWithPermissions = async (
	fetch,
	targetUrl: string,
	body: unknown,
	method = 'POST'
): Promise<[object, Array<CustomError>]> => {
	const res = await fetch(`${variables.BASE_API_URI}/token/refresh/`, {
		method: 'POST',
		mode: 'cors',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			refresh: `${browserGet('refreshToken')}`
		})
	});
	const accessRefresh = await res.json();
	const jres = await fetch(targetUrl, {
		method: method,
		mode: 'cors',
		headers: {
			Authorization: `Bearer ${accessRefresh.access}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(body)
	});

	if (method === 'PATCH') {
		if (jres.status !== 200) {
			const data = await jres.json();
			console.error(`Data: ${data}`);
			const errs = data.errors;
			console.error(errs);
			return [{}, errs];
		}
		return [await jres.json(), []];
	} else if (method === 'POST') {
		if (jres.status !== 201) {
			const data = await jres.json();
			console.error(`Data: ${data}`);
			const errs = data.errors;
			console.error(errs);
			return [{}, errs];
		}
		return [jres.json(), []];
	}
};

export const UpdateField = async (
	fieldName: string,
	fieldValue: string,
	url: string
): Promise<[object, Array<CustomError>]> => {
	const userObject: UserResponse = { user: {} };
	let formData: UserResponse | any;
	if (url.includes('/user/')) {
		formData = userObject;
		formData['user'][`${fieldName}`] = fieldValue;
	} else {
		formData[`${fieldName}`] = fieldValue;
	}

	const [response, err] = await handlePostRequestsWithPermissions(fetch, url, formData, 'PATCH');
	if (err.length > 0) {
		return [{}, err];
	}
	addToast({
		header: '',
		body: `${formatText(fieldName)} has been updated successfully.`,
		type: 'success'
	});
	//addNotification({title: `${formatText(fieldName)} has been updated successfully.`, type: 'success', icon: 'success', text: null});
	return [response, []];
};

export const loadNotifications = async (): Promise<void> => {
	const ds = browserGet('dataSession');
	if (ds != null || ds != undefined) {
		const dataSession = JSON.parse(ds);
		const [res, errors] = await apiPOST(fetch, 'alumno/general/data', {
			action: 'detail_notifcations_student'
		});
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			logOutUser();
		} else {
			const eNotificaciones = res.data.eNotificaciones;
			addNotifications(eNotificaciones);
		}
	}
};
