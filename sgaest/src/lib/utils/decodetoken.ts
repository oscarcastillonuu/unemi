import jwt_decode from 'jwt-decode';

export const decodeToken = (token: string): object | undefined => {
	if (token != undefined && token['refresh'] != undefined && token['access'] != undefined) {
		if (token['refresh'] != undefined && token['access'] != undefined) {
			const tokenAccess = jwt_decode(token['access']);
			const dataJson = {
				tokens: { refresh: token['refresh'], access: token['access'] },
				user: { ...tokenAccess['user'] },
				inscripcion: { ...tokenAccess['inscripcion'] },
				matricula: { ...tokenAccess['matricula'] },
				perfilprincipal: { ...tokenAccess['perfilprincipal'] },
				periodo: { ...tokenAccess['periodo'] },
				persona: { ...tokenAccess['persona'] },
				perfiles: { ...tokenAccess['perfiles'] },
				periodos: { ...tokenAccess['periodos'] },
				coordinacion: { ...tokenAccess['coordinacion'] },
				app: tokenAccess['app'],
				connectionToken: tokenAccess['connectionToken'],
				templatebasesetting: { ...tokenAccess['templatebasesetting'] },
				websocket: { ...tokenAccess['websocket'] }
			};
			return dataJson;
		}
	}
	return {};
};
