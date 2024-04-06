import { variables } from '$lib/utils/constants';
import type { CustomError } from '$lib/interfaces/error.interface';
import { encodeQueryString } from '$lib/helpers/baseHelper';
import { browserGet } from './requestUtils';

const api = async (fetch, url: string, params: unknown): Promise<[object, Array<CustomError>]> => {
	try {
		const headers = {};
		headers['Content-Type'] = 'application/json';
		let newURL = '';
		const token = browserGet('accessToken');
		if (token) {
			headers['token'] = token;
		}
		if (params) {
			newURL = `${url}` + (await encodeQueryString(params));
		} else {
			newURL = `${url}`;
		}

		const res = await fetch(newURL, {
			headers: headers
		});

		if (res.status >= 400) {
			const errors: Array<CustomError> = [];
			errors.push({ error: 'Acción no identificada' });
		} else if (!res.ok) {
			const errors: Array<CustomError> = [];
			errors.push({ error: 'Error de conexión' });
			return [{}, errors];
		}
		const response = await res.json();
		return [response, []];
	} catch (error) {
		const errors: Array<CustomError> = [{ error: error }];
		return [{}, errors];
	}
};

const loadAjax = async (data, url) =>
	new Promise(async (resolve, reject) => {
		const [res, errors] = await api(fetch, url, data);
		if (errors.length > 0) {
			reject({
				error: true,
				message: errors[0].error
			});
		} else {
			resolve({
				error: false,
				value: res
			});
		}
	});

export async function getEstadoCivil() {
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/estadoscivil.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getSexos() {
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/sexos.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getTitulos(q, c) {
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				q: q,
				c: c
			},
			'/api/titulos.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getAreasTitulos(q) {
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				q: q
			},
			'/api/areastitulos.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getColegios(q) {
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				q: q
			},
			'/api/colegios.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getInstitucionesEducacionSuperiores(q) {
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				q: q
			},
			'/api/institucioneseducacionsuperiores.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getParentescos() {
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/parentescos.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getNivelesTitulacion() {
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/nivelestitulacion.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getFormasTrabajo() {
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/formastrabajo.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getDiscapacidades() {
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/discapacidades.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getInstitucionesDiscapacidad() {
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/institucionesdiscapacidad.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getPaises(q) {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				q: q
			},
			'/api/paises.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getProvinicias(p, q) {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				p: p,
				q: q
			},
			'/api/provincias.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getCantones(p, q) {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				p: p,
				q: q
			},
			'/api/cantones.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getParroquias(c, q) {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				c: c,
				q: q
			},
			'/api/parroquias.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getTipoHogar() {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/tiposhogar.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getPersonaCubreGasto() {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/personascubregasto.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getNivelesEstudio() {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/nivelesestudio.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getOcupacionesJefeHogar() {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/ocupacionesjefehogar.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getMatriculaCompanero(q, c, p) {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				q: q,
				c: c,
				p: p
			},
			'/api/matriculacompanero.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getTiposViviendas() {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/tiposviviendas.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getTiposViviendasPro() {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/tiposviviendaspro.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getMaterialesParedes() {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/materialesparedes.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getMaterialesPisos() {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/materialespisos.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getCantidadesBanioDuchas() {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/cantidadesbanioduchas.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getTiposServiciosHigienicos() {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/tiposservicioshigienicos.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getCantidadesTVColorHogar() {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/cantidadestvcolorhogar.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getCantidadesVehiculosHogar() {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/cantidadesvehiculoshogar.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getCantidadesCelularesHogar() {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/cantidadescelulareshogar.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getProveedoresInternet(q) {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				q: q
			},
			'/api/proveedoresinternet.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getRazas() {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/razas.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getNacionalidadesIndigenas() {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/nacionalidadesindigenas.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getTiposSangres() {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/tipossangres.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getEnfermedades(q) {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				q: q
			},
			'/api/enfermedades.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getTiposVacunaCovid() {
	// q = q ? q.replace(' ', '_') : '';
	return new Promise((resolve, reject) => {
		loadAjax({}, '/api/tiposvacunacovid.json')
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getTiposCursos(q) {
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				q: q
			},
			'/api/tiposcursos.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getTiposCertificaciones(q) {
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				q: q
			},
			'/api/tiposcertificaciones.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getTiposParticipaciones(q) {
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				q: q
			},
			'/api/tiposparticipaciones.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getTiposCapacitaciones(q) {
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				q: q
			},
			'/api/tiposcapacitaciones.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getContextosCapacitaciones(q) {
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				q: q
			},
			'/api/contextoscapacitaciones.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getDetalleContextosCapacitaciones(q) {
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				q: q
			},
			'/api/detallecontextoscapacitaciones.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getAreasConocimientoTitulacion(q) {
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				q: q
			},
			'/api/areasconocimientotitulacion.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getSubAreasConocimientoTitulacion(q, a) {
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				q: q,
				a: a
			},
			'/api/subareasconocimientotitulacion.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getSubAreasEspecificaConocimientoTitulacion(q, s) {
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				q: q,
				s: s
			},
			'/api/subareasespecificaconocimientotitulacion.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getInstitucionesCertificadoras(q) {
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				q: q
			},
			'/api/institucionescertificadoras.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getNivelesSuficiencias(q) {
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				q: q
			},
			'/api/nivelessuficiencias.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getIdiomas(q) {
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				q: q
			},
			'/api/idiomas.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getCamposArtisticos() {
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				q: ''
			},
			'/api/campoartistico.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getDisciplinasDeportivas() {
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				q: ''
			},
			'/api/disciplinasdeportivas.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}

export async function getInstitucionesBecas(q) {
	return new Promise((resolve, reject) => {
		loadAjax(
			{
				q: q
			},
			'/api/institucionesbecas.json'
		)
			.then((response) => {
				//console.log(response);
				if (!response.error) {
					resolve(response.value.slice(0, 1000));
				} else {
					reject([]);
				}
			})
			.catch((error) => {
				reject([]);
			});
	});
}
