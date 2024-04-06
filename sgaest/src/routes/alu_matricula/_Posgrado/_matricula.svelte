<script lang="ts">
	import { apiGET, apiPOST, browserGet, changeProfile, logOutUser } from '$lib/utils/requestUtils';
	import { variables } from '$lib/utils/constants';
	import { addToast } from '$lib/store/toastStore';
	import { afterUpdate, onMount } from 'svelte';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import ComponentCalendario from '$components/Alumno/Matricula/Calendario.svelte';
	import ComponentRequisitosTitulacion from '$components/Alumno/Matricula/DetalleRequisitosTitulacion.svelte';
	import DetalleValoresPendientes from '$components/Alumno/Matricula/DetalleValoresPendientes.svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Tooltip, Icon } from 'sveltestrap';
	//import ModuleError from '../_Error.svelte';
	import { Spinner } from 'sveltestrap';
	import { goto } from '$app/navigation';
	import { loading } from '$lib/store/loadingStore';
	import Swal from 'sweetalert2';
	import { converToAscii } from '$lib/formats/formatString';
	import { addNotification } from '$lib/store/notificationStore';
	import { converToDecimal } from '$lib/formats/formatDecimal';
	const DEBUG = import.meta.env.DEV;
	let itemsBreadCrumb = [{ text: 'Matriculación', active: true, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };
	let load = true;
	let Title = 'Matriculación Online';
	let search = '';
	let ePersona = undefined;
	let eInscripcion = undefined;
	let isItinerarios = false;
	let listItinerarios = [];
	let itinerario = 0;
	let itinerario_aux = 0;
	let eCarrera = undefined;
	let eMalla = undefined;
	let ePeriodoMatricula = undefined;
	let ePreMatricula = undefined;
	let ePreMatriculaAsignaturas = [];
	let ePeriodo = undefined;
	let eNivelMalla = undefined;
	let vaUltimaMatricula = false;
	let eNivelesMalla = [];
	let FichaSocioEconomicaINEC = undefined;
	let eNivel = undefined;
	let asignaturasmalla = [];
	let nivelesmalla = [];
	let eMaterias = [];
	let eAsignatura = {};
	let eMateria = {};
	let eCasoUltimaMatricula = {};
	let clases = [];
	let puede_matricularse = false;
	let total_asignaturas_aperturadas = 0;
	let total_asignaturas_aperturadas_seleccionada = 0;
	let total_eMaterias = 0;
	let total_horas_contanto_docente = 0;
	let total_horas_semanales = 0;
	let cobro = 0;
	let tipo_matricula = 0;
	let perdida_gratuidad = false;
	let mensaje_gratuidad = '';
	let nivelmalla_matricula = '';
	let nivelmalla_matricula_id = 0;
	let matricula_id = 0;
	let periodo_id_aux = 0;
	let acept_t = false;
	let mOpenAsignatura = false;
	let mOpenAsignaturaPractica = false;
	let mOpenConfirmarMatricula = false;
	//let mOpenConfirmarDiferido = false;
	let mOpenConfirmarCaso = false;
	let mSizeConfirmarMatricula = 'sm';
	//let mensajeConfirmarDiferido = '';
	let num_materias_maxima = 0;
	let count_max_last_roll = 0;
	let count_select_last_roll = 0;
	let count_select_pre_matricula = 0;
	let count_repet_subject = 0;
	//let maxhoras_contactodocente_matricula = 0;
	//let maxhoras_semanal_matricula = 0;
	let tiene_valores_pendientes = false;
	let msg_valores_pendientes = '';
	let casoSelected = undefined;
	let mOpenModal = false;
	let mTitleModal = '';
	let modalContent;
	let aDataModal = {};
	const mToggleAsignatura = () => (mOpenAsignatura = !mOpenAsignatura);
	const mToggleAsignaturaPractica = () => (mOpenAsignaturaPractica = !mOpenAsignaturaPractica);
	const mToggleConfirmarMatricula = () => (mOpenConfirmarMatricula = !mOpenConfirmarMatricula);
	//const mToggleConfirmarDiferido = () => (mOpenConfirmarDiferido = !mOpenConfirmarDiferido);
	const mToggleConfirmarCaso = () => (mOpenConfirmarCaso = !mOpenConfirmarCaso);
	const mToggleModal = () => (mOpenModal = !mOpenModal);
	export let aData;

	$: {
		//console.log('itinerario_aux:', itinerario_aux);
		//total_eMaterias = eMaterias.length;
	}

	onMount(async () => {
		if (aData !== undefined) {
			console.log('py de matricula: onMount se EJEMCUTA ');
			Title = aData.Title;			
			tiene_valores_pendientes = aData.tiene_valores_pendientes;
			msg_valores_pendientes = aData.msg_valores_pendientes;
			ePersona = aData.ePersona;
			eInscripcion = aData.eInscripcion;
			itinerario = aData.itinerario;
			eCarrera = aData.eCarrera;
			eMalla = aData.eMalla;
			//maxhoras_contactodocente_matricula = eMalla.maxhoras_contactodocente_matricula;
			//maxhoras_semanal_matricula = eMalla.maxhoras_semanal_matricula;
			ePeriodoMatricula = aData.ePeriodoMatricula;			
			acept_t = ePeriodoMatricula.valida_terminos;		
			ePreMatricula = aData.ePreMatricula;
			ePreMatriculaAsignaturas =
				ePreMatricula && ePreMatricula.prematriculaasignatura
					? ePreMatricula.prematriculaasignatura
					: [];
			ePeriodo = aData.ePeriodoMatricula.periodo;
			eNivelMalla = aData.eNivelMalla;
			FichaSocioEconomicaINEC = aData.FichaSocioEconomicaINEC;
			eCasoUltimaMatricula = aData.eCasoUltimaMatricula;
			if (eCasoUltimaMatricula) {
				casoSelected = eCasoUltimaMatricula.id;
			}
			eNivel = aData.eNivel;
			eNivelesMalla = aData.eNivelesMalla;
			vaUltimaMatricula = aData.vaUltimaMatricula;
			isItinerarios = aData.isItinerarios;
			listItinerarios = aData.listItinerarios;
			if (aData.vaUltimaMatricula) {
				num_materias_maxima = ePeriodoMatricula.num_materias_maxima_ultima_matricula;
				if (aData.numVaUltimaMatricula > num_materias_maxima) {
					count_max_last_roll = num_materias_maxima;
				} else {
					count_max_last_roll = aData.numVaUltimaMatricula;
				}
			} else {
				num_materias_maxima = ePeriodoMatricula.num_materias_maxima;
				count_max_last_roll = 0;
			}			

			const [res, errors] = await apiPOST(fetch, 'alumno/matricula/posgrado', {
				action: 'loadInitialData',
				nid: eNivel.id
			});
			
			if (errors.length > 0) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				goto('/');
			} else {
				if (!res.isSuccess) {
					addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
					window.location.href = '/';
				} else {					
					asignaturasmalla = res.data;										
					res.data.forEach(function (am, index) {
						let isExit = false;
						for (let i in nivelesmalla) {
							if (nivelesmalla[i]['id'] == am.nivelmalla_id) {
								isExit = true;
								return false;
							}
						}
						if (!isExit) {
							nivelesmalla.push({
								id: am.nivelmalla_id,
								nombre: am.nivelmalla
							});
						}
					});
				}
			}
		}
		load = false;
	});

	afterUpdate(async () => {
		if (tiene_valores_pendientes) {
			const elementActionViewPendingValues = document.getElementsByClassName(
				'action-view-pending-values'
			);
			//console.log('element: ', element);
			if (elementActionViewPendingValues.length > 0) {
				elementActionViewPendingValues[0].addEventListener('click', viewDetailRubros);
			}

			const elementActionPayPendingValues = document.getElementsByClassName(
				'action-pay-pending-values'
			);
			//console.log('element: ', elementActionPayPendingValues);
			if (elementActionPayPendingValues.length > 0) {
				elementActionPayPendingValues[0].addEventListener('click', payRubros);
			}
		}
	});

	const actionRun = (event) => {
		//aDataModal = {mensaje: 'Hola mundo 2'};
		//console.log(event.detail);
	};

	const viewDetailRubros = async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const url = `alumno/general/data`;
		const [res, errors] = await apiPOST(fetch, url, {
			action: 'detail_pending_values',
			id: eNivel.id
		});
		loading.setLoading(false, 'Cargando, espere por favor...');
		if (errors.length > 0) {
			addNotification({
				msg: errors[0].error,
				type: 'error'
			});
		} else {
			if (!res.isSuccess) {
				addNotification({
					msg: res.message,
					type: 'error'
				});
			} else {
				//console.log(res.data);
				aDataModal = res.data;
				modalContent = DetalleValoresPendientes;
				mOpenModal = !mOpenModal;
				mTitleModal = 'Detalle de valores pendientes';
			}
		}
	};

	const payRubros = async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const url = `alumno/matricula/posgrado`;
		const [res, errors] = await apiPOST(fetch, url, {
			action: 'pay_pending_values',
			id: ePersona.id
		});
		loading.setLoading(false, 'Cargando, espere por favor...');
		if (errors.length > 0) {
			addNotification({
				msg: errors[0].error,
				type: 'error'
			});
		} else {
			
			if (!res.isSuccess) {
				addNotification({
					msg: res.message,
					type: 'error'
				});
			}else{
				console.log('res.redirect');
				if (!res.module_access) {
					if (res.redirect) {
						console.log(res.redirect);
						if (res.token) {
							window.open(`${res.redirect}`, '_blank');																						
						} else {
							addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });							
							return;
						}
					} else {
						addNotification({
							msg: res.message,
							type: 'warning',
							target: 'newNotificationToast'
						});						
					}					
				} else {
					addNotification({
						msg: res.message,
						type: 'warning',
						target: 'newNotificationToast'
					});						
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;		
			}
		}
	};

	const actionAsistenciaModule = async (eModuloURL) => {
		//console.log(eModulo.url);

		const dataSession = JSON.parse(browserGet('dataSession'));
		const connectionToken = dataSession['connectionToken'];
		//(window.location.href = eModulo.url_page);
		window.location.href = `${connectionToken}&ret=/${eModuloURL}`;

		return;
	};
	
	/*const openCalendario = async (component) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		aDataModal = { mensaje: 'Hola mundo' };
		modalContent = component;
		mOpenModal = !mOpenModal;
		mTitleModal = 'Calendario de matriculación';

		loading.setLoading(false, 'Cargando, espere por favor...');
	};*/

	const changeItinerarioVisible = (iti) => {
		itinerario = iti;
		//console.log(itinerario_aux);
	};

	const actionSearchKeyPress = (e) => {
		let levels = [];
		let valueYesSearchs = document.getElementsByClassName('valueYesSearch');		
		[].forEach.call(valueYesSearchs, (element) => {
			if (
				converToAscii(element.textContent.toLowerCase()).indexOf(
					converToAscii(search.toLowerCase())
				) === -1
			){
				element.style.display = 'none'; // hide
				//element.classList.remove('valueYesSearch');
			} else {
				element.style.display = ''; // show
				//element.classList.toggle('valueYesSearch'); 

				levels.push(element.querySelector('.card-level-academic').textContent);
			}
		});
		[].forEach.call(document.getElementsByClassName('hr_nivel_malla'), (element) => {
			if (levels.indexOf(converToAscii(element.textContent.toLowerCase())) === -1) {
				element.style.display = 'none'; // hide
			} else {
				element.style.display = ''; // show
			}
		});
	};

	const loadAjax = async (data, url) =>
		new Promise(async (resolve, reject) => {
			const [res, errors] = await apiPOST(fetch, 'alumno/matricula/posgrado', data);
			//console.log(errorsCertificates);						
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

	const changeMatricularse = () => {
		puede_matricularse = false;
		if (eMaterias.length > 0) {
			puede_matricularse = true;
		}
	};

	const changeItinerario = () => {
		const itinerario_inscripcion = eInscripcion.itinerario ? eInscripcion.itinerario : 0;
		if (itinerario_inscripcion > 0) {
			listItinerarios.forEach(function (iti, index) {
				if (iti != itinerario_inscripcion) {
					[].forEach.call(
						document.querySelectorAll(`[itinerario='itinerario_${iti}']`),
						(element) => {
							element.style.display = 'none'; // hide
						}
					);
				}
			});
			itinerario = itinerario_inscripcion;
			changeItinerarioVisible(itinerario_inscripcion);
		} else {
			let utilizaItinerario = false;
			let itinerario = 0;
			eMaterias.forEach(function (_materia, index) {
				if (_materia.itinerario > 0) {
					itinerario = _materia.itinerario;
					utilizaItinerario = true;
					return false;
				}
			});
			if (utilizaItinerario) {
				listItinerarios.forEach(function (iti, index) {
					if (iti != itinerario) {
						[].forEach.call(
							document.querySelectorAll(`[itinerario='itinerario_${iti}']`),
							(element) => {
								element.style.display = 'none'; // hide
							}
						);
					}
				});
			} else {
				itinerario = 0;
				listItinerarios.forEach(function (iti, index) {
					[].forEach.call(
						document.querySelectorAll(`[itinerario='itinerario_${iti}']`),
						(element) => {
							element.style.display = ''; //show
						}
					);
				});
			}
			changeItinerarioVisible(itinerario);
		}
	};

	const countSelectSubjectLevel = () => {
		total_asignaturas_aperturadas_seleccionada = 0;
		eMaterias.forEach(function (_materia, index) {
			if (_materia.nivelmalla_id == nivelmalla_matricula_id) {
				total_asignaturas_aperturadas_seleccionada += 1;
			}
		});
	};

	const countSubjectsApproved = () => {
		let _total_asignaturas_aprobadas = 0;
		asignaturasmalla.forEach(function (_asignatura, index) {
			//console.log(asignatura.nivelmalla_id);
			//console.log(self.nivelmalla_matricula_id);
			if (_asignatura.nivelmalla_id == nivelmalla_matricula_id && _asignatura.materias.length > 0) {
				_total_asignaturas_aprobadas += 1;
			}
		});
	};

	const countSubjectsOpen = () => {
		total_asignaturas_aperturadas = 0;		
		asignaturasmalla.forEach(function (_asignatura, index) {			
			if (_asignatura.nivelmalla_id == nivelmalla_matricula_id && _asignatura.puede_ver_horario) {
				total_asignaturas_aperturadas += 1;
			}
		});
	};

	const sumHoursTeacherContacts = () => {		
		let t_h_c_d = 0;
		asignaturasmalla.forEach(function (_am, index) {
			if (eMaterias.find((_materia) => _materia.asignatura_id === _am.id))
				t_h_c_d += _am.horas_contacto_docente;
				console.log(t_h_c_d);
		});
		return t_h_c_d;
	};

	const sumWeeklyHours = () => {
		let t_h_s = 0;
		asignaturasmalla.forEach(function (_am, index) {
			if (eMaterias.find((_materia) => _materia.asignatura_id === _am.id))
				t_h_s += _am.horas_semanal;
		});
		return t_h_s;
	};

	const changeNivelMatricula = () =>
		new Promise((resolve, reject) => {
			let mismaterias = [];
			eMaterias.forEach(function (_materia, index) {
				mismaterias.push(_materia.id);
			});
			if (eMaterias.length > 0) {
				//loading.setLoading(true, 'Cargando, espere por favor...');
				console.log('ejecuta changeNivelMatricula');
				loadAjax(
					{
						action: 'locateEnrollmentLevel',
						mismaterias: JSON.stringify(mismaterias)
					},
					'alumno/matricula/posgrado'
				)
					.then((response) => {
						if (response.value.isSuccess) {
							//console.log(response.value.data);
							nivelmalla_matricula_id = response.value.data.id;
							nivelmalla_matricula = response.value.data.nombre;
							countSubjectsApproved();
							countSelectSubjectLevel();
							countSubjectsOpen();
							resolve({
								error: false,
								value: true
							});
							//loading.setLoading(false, 'Cargando, espere por favor...');
						} else {
							//loading.setLoading(false, 'Cargando, espere por favor...');
							//addToast({ type: 'error', header: 'Ocurrio un error', body: response.value.message });
							//addNotification({ msg: response.value.message, type: 'error' });
							reject({
								error: true,
								message: response.value.message
							});
						}
					})
					.catch((error) => {
						//loading.setLoading(false, 'Cargando, espere por favor...');
						//addToast({ type: 'error', header: 'Ocurrio un error', body: error.message });
						//addNotification({ msg: error.message, type: 'error' });
						reject({
							error: true,
							message: error.message
						});
					});
			} else {
				nivelmalla_matricula_id = 0;
				nivelmalla_matricula = '';
				countSubjectsApproved();
				countSelectSubjectLevel();
				countSubjectsOpen();
				resolve({
					error: false,
					value: true
				});
			}
		});

	const removeAsignatura = (_asignatura) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		let ids_asignaturas = eMaterias.map((ele) => ele.asignatura_id);
		//console.log(_asignatura);
		let is_last_enroll = false;
		let _count_libre = 0;
		let _count_max_last_roll = 0;
		let _count_repet_subject = 0;
		asignaturasmalla.forEach(function (_am, index) {
			if (_asignatura.id === _am.id && _am.va_num_matricula >= ePeriodoMatricula.num_matriculas) {
				is_last_enroll = true;
			}
			if (
				ids_asignaturas.indexOf(_am.id) !== -1 &&
				_am.va_num_matricula < ePeriodoMatricula.num_matriculas
			) {
				_count_libre += 1;
			}
			if (
				ids_asignaturas.indexOf(_am.id) !== -1 &&
				_am.va_num_matricula >= ePeriodoMatricula.num_matriculas
			) {
				_count_max_last_roll += 1;
			}
			if (_am.id === _asignatura.id && _am.va_num_matricula > 1) {
				_count_repet_subject += 1;
			}
		});
		/*if (is_last_enroll && _count_libre > 0 && _count_max_last_roll <= count_max_last_roll) {
			addNotification({
				msg: `Debe dar prioridad a las materias de ${
					ePeriodoMatricula.num_matriculas == 3
						? 'tercera'
						: ePeriodoMatricula.num_matriculas == 4
						? 'cuarta'
						: ePeriodoMatricula.num_matriculas == 5
						? 'quinta'
						: ePeriodoMatricula.num_matriculas
				} matrícula`,
				type: 'warning',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return true;
		}*/

		let _eM = {};
		eMaterias.forEach(function (_materia, index) {
			if (_asignatura.id == _materia.asignatura_id) {
				_eM = _materia;
				eMaterias.splice(index, 1); // 1 es la cantidad de elemento a eliminar
			}
		});

		changeMatricularse();
		changeItinerario();

		const t_h_c_d = sumHoursTeacherContacts();
		const t_h_s = sumWeeklyHours();
		changeNivelMatricula()
			.then(() => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				document.getElementById(`btn_aplicar_${_asignatura.id}`).style.display = ''; // hide
				document.getElementById(`btn_remover_${_asignatura.id}`).style.display = 'none'; // show
				//eMaterias.splice(index, 1); // 1 es la cantidad de elemento a eliminar
				total_eMaterias = eMaterias.length;
				total_horas_contanto_docente = t_h_c_d;
				total_horas_semanales = t_h_s;
				count_repet_subject += _count_repet_subject;
				if (
					_asignatura.va_num_matricula >= ePeriodoMatricula.num_materias_maxima_ultima_matricula
				) {
					count_select_last_roll -= 1;
				}
				/*
				if (aData.tienePreMatricula) {
					if (
						ePreMatriculaAsignaturas
							.map((ele) => ele.asignatura.id_display)
							.indexOf(_asignatura.asignatura_id) !== -1
					) {
						count_select_pre_matricula -= 1;
						document.getElementById(`identificador_prematricula_${_asignatura.id}`).style.display =
							''; // show
					}
				}*/
				//calcula_gratuidad();
			})
			.catch((error) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				addNotification({ msg: error.message, type: 'error' });
				eMaterias.push(_eM);
				total_eMaterias = eMaterias.length;
				document.getElementById(`btn_aplicar_${_asignatura.id}`).style.display = 'none'; // hide
				document.getElementById(`btn_remover_${_asignatura.id}`).style.display = ''; // show
			});
	};

	const closeAsignatura = () => {
		mOpenAsignatura = false;
	};

	const closeAsignaturaPractica = () => {
		mOpenAsignaturaPractica = false;
	};

	const closeConfirmarMatricula = () => {
		//$('[name="acept_t"]', self.$modalConfirmarMatricula).prop('checked', false);
		mOpenConfirmarMatricula = false;
	};

	const getLastNivelMalla = () => {
		return eNivelesMalla[eNivelesMalla.length - 1];
	};

	const openAsignatura = (asignatura) => {
		if (asignatura.validarequisitograduacion) {
			loading.setLoading(true, 'Cargando, espere por favor...');
			let contadorCumple = 0;
			const ultimoNivel = getLastNivelMalla();
			let contadorMateriaSeleccionadaUltimoNivel = 0;
			let contadorMateriaOfertadaUltimoNivel = 0;
			let eRequisitos = asignatura.requisitos;
			eRequisitos.forEach(function (requisito, index) {
				if (requisito.enlineamatriculacion) {
					//contadorValidaEnLineaMatriculacion += 1;
					eMaterias.forEach(function (_materia, index) {						
						if (
							_materia.nivelmalla_id === ultimoNivel.idm &&
							_materia.validarequisitograduacion === false
						) {
							if (itinerario === 0) {
								contadorMateriaSeleccionadaUltimoNivel += 1;
							} else if (itinerario > 0) {
								if (_materia.itinerario === itinerario) {
									contadorMateriaSeleccionadaUltimoNivel += 1;
								}
							}
						}
					});
					
					asignaturasmalla.forEach(function (_asignaturamalla, index) {
						if (
							_asignaturamalla.nivelmalla_id === ultimoNivel.idm &&
							_asignaturamalla.puede_ver_horario === 1 &&
							_asignaturamalla.validarequisitograduacion === false
						) {
							if (itinerario === 0) {
								contadorMateriaOfertadaUltimoNivel += 1;
							} else if (itinerario > 0) {
								if (_asignaturamalla.itinerario === itinerario) {
									contadorMateriaOfertadaUltimoNivel += 1;
								}
							}
						}
					});
					const cumple =
						contadorMateriaOfertadaUltimoNivel === contadorMateriaSeleccionadaUltimoNivel;
					//console.log('cumple:', cumple);
					eRequisitos[index]['cumple'] = cumple;
					if (cumple) {
						contadorCumple += 1;
					}
				} else {
					//contadorValidaMatriculacion += 1;
					if (requisito.cumple) {
						contadorCumple += 1;
					}
				}
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (eRequisitos.length != contadorCumple) {
				addNotification({
					msg: `No cumple con los requisitos de ingreso a la asignatura ${asignatura.asignatura}`,
					type: 'warning',
					target: 'newNotificationToast'
				});
				aDataModal = { eRequisitos: eRequisitos };
				modalContent = ComponentRequisitosTitulacion;
				mOpenModal = !mOpenModal;
				mTitleModal = 'Requisitos de Ingreso a la Unidad de Integración Curricular';
				return true;
			}
		}
		loading.setLoading(true, 'Cargando, espere por favor...');
		if (ePeriodoMatricula.valida_materias_maxima && eMaterias.length + 1 > num_materias_maxima) {
			addNotification({
				msg: `Número de materias: Ha superado la cantidad (${num_materias_maxima}) asignaturas permitidas a seleccionar`,
				type: 'warning',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return true;
		}
		/*
		const _total_horas_contanto_docente =
			total_horas_contanto_docente + asignatura.horas_contacto_docente;
		const _total_horas_semanales = total_horas_semanales + asignatura.horas_semanal;
		
		if (
			_total_horas_contanto_docente > maxhoras_contactodocente_matricula ||
			_total_horas_semanales > maxhoras_semanal_matricula
		) {
			addNotification({
				msg: `Solo puede elegir materias que sumen hasta ${maxhoras_contactodocente_matricula} horas de contacto docente o ${maxhoras_semanal_matricula} horas totales a la semana`,
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return true;
		}*/

		/*if (
			aData.vaUltimaMatricula &&
			count_select_last_roll < count_max_last_roll &&
			asignatura.va_num_matricula != ePeriodoMatricula.num_matriculas
		) {
			addNotification({
				msg: `Debe dar prioridad a las materias de ${
					ePeriodoMatricula.num_matriculas == 3
						? 'tercera'
						: ePeriodoMatricula.num_matriculas == 4
						? 'cuarta'
						: ePeriodoMatricula.num_matriculas == 5
						? 'quinta'
						: ePeriodoMatricula.num_matriculas
				} matrícula`,
				type: 'warning',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return true;
		}*/

		if (eMaterias.length == 0 || vaUltimaMatricula) {
			eAsignatura = asignatura;
		} else {
			if (asignatura.itinerario == 0) {
				let _paralelo_id = 0;
				eMaterias.forEach(function (_materia, index) {					
					if (_materia.nivelmalla_id == asignatura.nivelmalla_id) {
						_paralelo_id = _materia.paralelo_id;
						return false;
					}
				});				
				
				if (_paralelo_id > 0) {
					let _aux_asignatura = {};
					//console.log(asignatura);
					for (const [key, value] of Object.entries(asignatura)) {
						if (key != 'materias') {
							_aux_asignatura[key] = value;
						}
					}
					/*asignatura.forEach((value, key, map) => {
						if (key != 'materias') {
							_aux_asignatura[key] = value;
						}
					});*/
					let _materias = [];
					asignatura.materias.forEach(function (_materia, index) {
						if (_paralelo_id == _materia.paralelo_id) {
							_materias.push(_materia);
						}
					});
					_aux_asignatura['materias'] = _materias;
					eAsignatura = _aux_asignatura;
				} else {
					eAsignatura = asignatura;
				}
			} else {
				eAsignatura = asignatura;
			}
		}
		
		let fnModal = function () {
			mOpenAsignatura = true;
		};
		if (ePeriodoMatricula.valida_cupo_materia) {
			loadAjax(
				{
					action: 'loadCupoMateria',
					asignatura: JSON.stringify(eAsignatura)
				},
				'alumno/matricula/posgrado'
			)
				.then((response) => {
					if (response.value.isSuccess) {
						loading.setLoading(false, 'Cargando, espere por favor...');
						eAsignatura = response.value.data;
						fnModal();
					} else {
						loading.setLoading(false, 'Cargando, espere por favor...');
						//addToast({ type: 'error', header: 'Ocurrio un error', body: response.value.message });
						addNotification({ msg: response.value.message, type: 'error' });
					}
				})
				.catch((error) => {
					loading.setLoading(false, 'Cargando, espere por favor...');
					//addToast({ type: 'error', header: 'Ocurrio un error', body: error.message });
					addNotification({ msg: error.message, type: 'error' });
				});
		} else {
			if (fnModal) {
				fnModal();
			} else {
				addNotification({ msg: `Ocurrio un error al cargar los datos`, type: 'error' });
			}
			loading.setLoading(false, 'Cargando, espere por favor...');
		}
	};

	const selectSubject = (_materia) => {
		//console.log(_materia);

		let fnSelect = function () {
			loading.setLoading(true, 'Cargando, espere por favor...');
			if (_materia.teoriapractica == 0) {
				eMaterias.push({
					id: _materia.id,
					asignatura_id: eAsignatura.id,
					itinerario: eAsignatura.itinerario,
					nivelmalla_id: _materia.nivelmalla_id,
					paralelo_id: _materia.paralelo_id,
					practica: {},
					horarios: _materia.horarios,
					validarequisitograduacion: eAsignatura.validarequisitograduacion
				});

				closeAsignatura();
				changeMatricularse();
				changeItinerario();
				const t_h_c_d = sumHoursTeacherContacts();
				const t_h_s = sumWeeklyHours();
				changeNivelMatricula()
					.then(() => {
						//calcula_gratuidad();

						asignaturasmalla.forEach(function (asignatura, index) {
							if (asignatura.id == eAsignatura.id) {
								document.getElementById(`btn_aplicar_${eAsignatura.id}`).style.display = 'none'; // hide
								document.getElementById(`btn_remover_${eAsignatura.id}`).style.display = ''; // show
							}
						});
						total_eMaterias = eMaterias.length;
						total_horas_contanto_docente = t_h_c_d;
						total_horas_semanales = t_h_s;
						if (eAsignatura.va_num_matricula > 1) {
							count_repet_subject += 1;
						}

						if (
							eAsignatura.va_num_matricula >= ePeriodoMatricula.num_materias_maxima_ultima_matricula
						) {
							count_select_last_roll += 1;
						}
						/*if (aData.tienePreMatricula) {
							if (
								ePreMatriculaAsignaturas
									.map((ele) => ele.asignatura.id_display)
									.indexOf(eAsignatura.asignatura_id) !== -1
							) {
								count_select_pre_matricula += 1;
								document.getElementById(
									`identificador_prematricula_${eAsignatura.id}`
								).style.display = 'none'; // hide
							}
						}*/
						//console.log("correcto");
						//console.log(eMaterias);
						loading.setLoading(false, 'Cargando, espere por favor...');
					})
					.catch((error) => {
						loading.setLoading(false, 'Cargando, espere por favor...');

						eMaterias.forEach(function (_materia, index) {
							if (_materia.id == _materia.id) {
								eMaterias.splice(index, 1); // 1 es la cantidad de elemento a eliminar
							}
						});
						total_eMaterias = eMaterias.length;
						addNotification({ msg: error.message, type: 'error' });
						//console.log("incorrecto");
						//console.log(eMaterias);
					});
			} else {
				openPractica(_materia);
				loading.setLoading(false, 'Cargando, espere por favor...');
			}
		};
		loading.setLoading(true, 'Cargando, espere por favor...');
		if (
			ePeriodoMatricula.valida_conflicto_horario &&
			eMaterias.length > 0 &&
			eInscripcion.modalidad_id != 3
		) {
			//console.log(eMaterias);
			if (eMaterias.length > 0) {
				let materia_aux = {
					id: _materia.id,
					asignatura_id: eAsignatura.id,
					itinerario: eAsignatura.itinerario,
					nivelmalla_id: _materia.nivelmalla_id,
					paralelo_id: _materia.paralelo_id,
					practica: {},
					horarios: _materia.horarios,
					validarequisitograduacion: eAsignatura.validarequisitograduacion
				};

				loadAjax(
					{
						action: 'validConflictoHorario',
						materias: JSON.stringify(eMaterias),
						materia: JSON.stringify(materia_aux)
					},
					'alumno/matricula/posgrado'
				)
					.then((response) => {
						if (response.value.isSuccess) {
							//console.log(response.value.data);
							if (response.value.data.conflicto) {
								/*const mensaje = {
									toast: true,
									position: 'top-end',
									type: 'warning',
									title: response.value.data.mensaje,
									showConfirmButton: false,
									timer: 6000
								};
								Swal.fire(mensaje);*/
								addNotification({
									msg: response.value.data.mensaje,
									type: 'warning',
									target: 'newNotificationToast'
								});
							} else {
								fnSelect();
							}
							loading.setLoading(false, 'Cargando, espere por favor...');
						} else {
							loading.setLoading(false, 'Cargando, espere por favor...');
							//addToast({ type: 'error', header: 'Ocurrio un error', body: response.value.message });
							addNotification({ msg: response.value.message, type: 'error' });
						}
					})
					.catch((error) => {
						loading.setLoading(false, 'Cargando, espere por favor...');
						//addToast({ type: 'error', header: 'Ocurrio un error', body: error.message });
						addNotification({ msg: error.message, type: 'error' });
					});
			} else {
				if (fnSelect) {
					fnSelect();
				} else {
					loading.setLoading(false, 'Cargando, espere por favor...');
					/*addToast({
						type: 'error',
						header: 'Ocurrio un error',
						body: 'No se pudieron cargar los datos'
					});*/
					addNotification({
						msg: 'Ocurrio un error: No se pudieron cargar los datos',
						type: 'error'
					});
				}
			}
		} else {
			if (fnSelect) {
				fnSelect();
			} else {
				loading.setLoading(false, 'Cargando, espere por favor...');
				/*addToast({
					type: 'error',
					header: 'Ocurrio un error',
					body: 'No se pudieron cargar los datos'
				});*/
				addNotification({
					msg: 'Ocurrio un error: No se pudieron cargar los datos',
					type: 'error'
				});
			}
		}
	};

	const openPractica = (_materia) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		eMateria = _materia;

		let fnModal = function () {
			mOpenAsignaturaPractica = true;
			loading.setLoading(false, 'Cargando, espere por favor...');
		};
		if (ePeriodoMatricula.valida_cupo_materia) {
			loadAjax(
				{
					action: 'loadCupoPractica',
					materia: JSON.stringify(eMateria)
				},
				'alumno/matricula/posgrado'
			)
				.then((response) => {
					//console.log(response);
					if (response.value.isSuccess) {
						eMateria = response.value.data.materia;
						fnModal();
						loading.setLoading(false, 'Cargando, espere por favor...');
					} else {
						loading.setLoading(false, 'Cargando, espere por favor...');
						/*addToast({
							type: 'error',
							header: 'Ocurrio un error',
							body: response.value.message
						});*/
						addNotification({ msg: response.value.message, type: 'error' });
					}
				})
				.catch((error) => {
					loading.setLoading(false, 'Cargando, espere por favor...');
					/*addToast({
						type: 'error',
						header: 'Ocurrio un error',
						body: error.message
					});*/
					addNotification({ msg: error.message, type: 'error' });
				});
		} else {
			if (fnModal) {
				fnModal();
			} else {
				loading.setLoading(false, 'Cargando, espere por favor...');
				/*addToast({
					type: 'error',
					header: 'Ocurrio un error',
					body: 'All cargar los datos'
				});*/
				addNotification({ msg: 'Ocurrio un error: No se pudo cargar los datos', type: 'error' });
			}
		}
	};

	const selectSubjectPractice = (_materia, _practica) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		console.log('se ejecuta el selectSubjectPractice ')
		let fnSelect = function () {
			const _eMaterias = eMaterias;
			eMaterias.push({
				id: _materia.id,
				asignatura_id: eAsignatura.id,
				itinerario: eAsignatura.itinerario,
				nivelmalla_id: _materia.nivelmalla_id,
				paralelo_id: _materia.paralelo_id,
				practica: _practica,
				horarios: _materia.horarios,
				validarequisitograduacion: eAsignatura.validarequisitograduacion
			});

			closeAsignaturaPractica();
			closeAsignatura();
			changeMatricularse();
			changeItinerario();
			const t_h_c_d = sumHoursTeacherContacts();
			const t_h_s = sumWeeklyHours();
			changeNivelMatricula()
				.then(() => {
					//calcula_gratuidad();

					asignaturasmalla.forEach(function (_asignatura, index) {
						if (_asignatura.id == eAsignatura.id) {
							document.getElementById(`btn_aplicar_${eAsignatura.id}`).style.display = 'none'; // hide
							document.getElementById(`btn_remover_${eAsignatura.id}`).style.display = ''; // show
						}
					});
					total_eMaterias = eMaterias.length;
					total_horas_contanto_docente = t_h_c_d;
					total_horas_semanales = t_h_s;
					if (eAsignatura.va_num_matricula > 1) {
						count_repet_subject += 1;
					}
					if (
						eAsignatura.va_num_matricula >= ePeriodoMatricula.num_materias_maxima_ultima_matricula
					) {
						count_select_last_roll += 1;
					}
					/*if (aData.tienePreMatricula) {
						if (
							ePreMatriculaAsignaturas
								.map((ele) => ele.asignatura.id_display)
								.indexOf(eAsignatura.asignatura_id) !== -1
						) {
							count_select_pre_matricula += 1;
							document.getElementById(
								`identificador_prematricula_${eAsignatura.id}`
							).style.display = 'none'; // hide
						}
					}*/
					//console.log("correcto");
					//console.log(eMaterias);
					loading.setLoading(false, 'Cargando, espere por favor...');
				})
				.catch((error) => {
					loading.setLoading(false, 'Cargando, espere por favor...');
					addNotification({ msg: error.message, type: 'error' });
					eMaterias = _eMaterias;

					eMaterias.forEach(function (_ma, index) {
						if (_ma.id == _materia.id) {
							eMaterias.splice(index, 1); // 1 es la cantidad de elemento a eliminar
						}
					});
					/*//console.log('incorrecto');
					//console.log(eMaterias);*/
					total_eMaterias = eMaterias.length;
				});
		};
		if (
			ePeriodoMatricula.valida_conflicto_horario &&
			eMaterias.length > 0 &&
			eInscripcion.modalidad_id != 3
		) {
			if (eMaterias.length > 0) {
				let materia_aux = {
					id: _materia.id,
					asignatura_id: eAsignatura.id,
					itinerario: eAsignatura.itinerario,
					nivelmalla_id: _materia.nivelmalla_id,
					paralelo_id: _materia.paralelo_id,
					practica: _practica,
					horarios: _materia.horarios
				};
				loadAjax(
					{
						action: 'validConflictoHorario',
						materias: JSON.stringify(eMaterias),
						materia: JSON.stringify(materia_aux)
					},
					'alumno/matricula/posgrado'
				)
					.then((response) => {
						if (response.value.isSuccess) {
							if ((eMateria = response.value.data.conflicto)) {
								/*const mensaje = {
									toast: true,
									position: 'top-end',
									type: 'warning',
									title: response.value.data.mensaje,
									showConfirmButton: false,
									timer: 6000
								};
								Swal.fire(mensaje);*/
								addNotification({
									msg: response.value.data.mensaje,
									type: 'warning',
									target: 'newNotificationToast'
								});
							} else {
								fnSelect();
							}
							loading.setLoading(false, 'Cargando, espere por favor...');
						} else {
							loading.setLoading(false, 'Cargando, espere por favor...');
							/*addToast({
								type: 'error',
								header: 'Ocurrio un error',
								body: response.value.message
							});*/
							addNotification({ msg: response.value.message, type: 'error' });
						}
					})
					.catch((error) => {
						loading.setLoading(false, 'Cargando, espere por favor...');
						/*addToast({
							type: 'error',
							header: 'Ocurrio un error',
							body: error.message
						});*/
						addNotification({ msg: error.message, type: 'error' });
					});
			} else {
				if (fnSelect) {
					fnSelect();
				} else {
					loading.setLoading(false, 'Cargando, espere por favor...');
					/*addToast({
						type: 'error',
						header: 'Ocurrio un error',
						body: 'Al cargar los datos'
					});*/
					addNotification({ msg: 'Ocurrio un error: No se pudo cargar los datos', type: 'error' });
				}
			}
		} else {
			if (fnSelect) {
				fnSelect();
			} else {
				loading.setLoading(false, 'Cargando, espere por favor...');
				/*addToast({
					type: 'error',
					header: 'Ocurrio un error',
					body: 'Al cargar los datos'
				});*/
				addNotification({ msg: 'Ocurrio un error: No se pudo cargar los datos', type: 'error' });
			}
		}
	};

	const actionSearchLevel = (event, value) => {
		let levels = [];
		const classname = document.getElementsByClassName('actionSearchLevel');		
		for (let i = 0; i < classname.length; i++) {
			classname[i].classList.remove('active');			
		}		
		event.target.classList.toggle('active');		
		let cards = document.getElementsByClassName('cardSubjects');
		[].forEach.call(cards, (element) => {
			if (value.toLowerCase() === 'all') {
				search = '';
				element.style.display = ''; // show
				//element.classList.toggle('valueYesSearch');
			} else {
				if (
					converToAscii(element.textContent.toLowerCase()).indexOf(
						converToAscii(value.toLowerCase())
					) === -1
				) {
					element.style.display = 'none'; // hide
					//element.classList.remove('valueYesSearch');
				} else {
					element.style.display = ''; // show
					//element.classList.toggle('valueYesSearch');

					levels.push(element.querySelector('.card-level-academic').textContent);
				}
			}
		});
		[].forEach.call(document.getElementsByClassName('hr_nivel_malla'), (element) => {
			if (value.toLowerCase() == 'all') {
				element.style.display = ''; //show
			} else {
				if (levels.indexOf(converToAscii(element.textContent.toLowerCase())) === -1) {
					element.style.display = 'none'; // hide
				} else {
					element.style.display = ''; // show
				}
			}
		});
	};

	/*const calcula_gratuidad = () => {
		//var materias_nivel = $("#id_materias_nivel_aperturadas").html();
		//var materias_nivel_seleccionadas = $("#id_materias_seleccionadas_nivel_aperturadas").html();

		cobro = 0;
		let porcentaje_seleccionadas = 0;
		perdida_gratuidad = false;
		mensaje_gratuidad = '';

		const porciento_perdida_parcial_gratuidad =
			ePeriodoMatricula.porcentaje_perdidad_parcial_gratuidad
				? ePeriodoMatricula.porcentaje_perdidad_parcial_gratuidad
				: 0;
		const porciento_perdida_total_gratuidad = ePeriodoMatricula.porcentaje_perdidad_total_gratuidad
			? ePeriodoMatricula.porcentaje_perdidad_total_gratuidad
			: 0;
		if (ePeriodoMatricula.valida_gratuidad && eMaterias.length > 0) {
			porcentaje_seleccionadas = Math.round(
				(total_asignaturas_aperturadas * porciento_perdida_parcial_gratuidad) / 100,
				0
			);			

			if (ePersona.tiene_otro_titulo) {
				cobro = 3;
				perdida_gratuidad = true;
				mensaje_gratuidad =
					"<p class='alert alert-danger' style='text-align: justify'>Con base al Art.11 del Reglamento para garantizar el cumplimiento de la gratuidad emitido por el Concejo de Educación Superior (CES) y en relación al Art.11 del Reglamento interno para garantizar el ejercicio del derecho a la gratuidad en la Universidad Estatal de Milagro. Usted supera el 30% de las asignaturas reprobadas correspondientes al plan de estudios  como indica la Ley. Su estado es PÉRDIDA DEFINITIVA DE LA GRATUIDAD. A partir de este momento todas las asignaturas, cursos o sus equivalentes hasta la culminación de su carrera, cancelará; los valores respectivos a matrículas y aranceles.</p>";
			} else {
				if (
					eInscripcion.estado_gratuidad == 2 ||
					eInscripcion.estado_gratuidad == 3 ||
					eInscripcion.estado_gratuidad == 1 ||
					count_repet_subject > 1
				) {
					if (total_asignaturas_aperturadas_seleccionada < porcentaje_seleccionadas) {
						cobro = 1;
						perdida_gratuidad = true;
						mensaje_gratuidad = `<p class='alert alert-danger' style='text-align: justify'>Con base en el Art.7 del Reglamento para garantizar el cumplimiento de la gratuidad, emitido por el Consejo de Educación Superior (CES) y en relación al Art.5 del Reglamento Interno para garantizar el ejercicio del derecho a la gratuidad en la Universidad Estatal de Milagro, informamos que usted se ha matriculado en menos del ${porciento_perdida_parcial_gratuidad}% de las asignaturas correspondientes a su nivel del plan de estudios; por lo tanto, no cumple con los requisitos necesarios para considerarse como ESTUDIANTE REGULAR, motivo por el cual deberá cancelar los valores correspondientes a matrícula y arancel.</p>`;
					} else if (eInscripcion.estado_gratuidad == 3) {
						cobro = 3;
						perdida_gratuidad = true;
						mensaje_gratuidad =
							"<p class='alert alert-danger' style='text-align: justify'>Con base al Art.11 del Reglamento para garantizar el cumplimiento de la gratuidad emitido por el Concejo de Educación Superior (CES) y en relación al Art.11 del Reglamento interno para garantizar el ejercicio del derecho a la gratuidad en la Universidad Estatal de Milagro. Usted supera el 30% de las asignaturas reprobadas correspondientes al plan de estudios  como indica la Ley. Su estado es PÉRDIDA DEFINITIVA DE LA GRATUIDAD. A partir de este momento todas las asignaturas, cursos o sus equivalentes hasta la culminación de su carrera, cancelará; los valores respectivos a matrículas y aranceles.</p>";
					} else if (eInscripcion.estado_gratuidad == 2) {
						cobro = 2;
						perdida_gratuidad = true;
						mensaje_gratuidad =
							"<p class='alert alert-danger' style='text-align: justify'>Con base al Art.5 del Reglamento para garantizar el cumplimiento de la gratuidad emitido por el Concejo de Educación Superior (CES) y en relación a los Arts. 6, 7 y 12 del Reglamento interno para garantizar el ejercicio del derecho a la gratuidad en la Universidad Estatal de Milagro. Su estado es PÉRDIDA PARCIAL DE LA GRATUIDAD y tendrá; que cancelar el valor correspondiente entre matrícula y arancel.</p>";
					} else if (count_repet_subject > 1) {
						cobro = 2;
						perdida_gratuidad = true;
						mensaje_gratuidad =
							"<p class='alert alert-danger' style='text-align: justify'>Con base al Art.5 del Reglamento para garantizar el cumplimiento de la gratuidad emitido por el Concejo de Educación Superior (CES) y en relación a los Arts. 6, 7 y 12 del Reglamento interno para garantizar el ejercicio del derecho a la gratuidad en la Universidad Estatal de Milagro. Su estado es PÉRDIDA PARCIAL DE LA GRATUIDAD y tendrá; que cancelar el valor correspondiente entre matrícula y arancel.</p>";
					} else {
						cobro = 0;
						perdida_gratuidad = false;
						mensaje_gratuidad =
							"<p class='alert alert-success' style='text-align: justify'>Ha seleccionado correctamente las asignatura de su nivel.</p>";
					}
				}
			}

			if (
				total_asignaturas_aperturadas_seleccionada < porcentaje_seleccionadas ||
				count_repet_subject > 1
			) {
				tipo_matricula = 2;
			} else {
				tipo_matricula = 1;
			}
		}
		//console.log('perdida_gratuidad: ', perdida_gratuidad);
		//console.log('cobro: ', cobro);
	};*/

	const actionEnroll = () => {
		if (eMaterias.length == 0) {
			addNotification({
				msg: `Acción no permitida: Tiene (${eMaterias.length}) asignaturas seleccionadas`,
				type: 'error',
				target: 'newNotificationToast'
			});
			return false;
		} else {
			//console.log('count_select_last_roll: ', count_select_last_roll);
			//console.log('count_max_last_roll: ', count_max_last_roll);
			/*if (aData.vaUltimaMatricula && count_select_last_roll > count_max_last_roll) {
				addNotification({
					msg: `Debe dar prioridad a las materias de ${
						ePeriodoMatricula.num_matriculas == 3
							? 'tercera'
							: ePeriodoMatricula.num_matriculas == 4
							? 'cuarta'
							: ePeriodoMatricula.num_matriculas == 5
							? 'quinta'
							: ePeriodoMatricula.num_matriculas
					} matrícula`,
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return true;
			}*/
			if (eMaterias.length > num_materias_maxima) {
				addNotification({
					msg: `No puede seleccionar más de ${num_materias_maxima} asignaturas`,
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return true;
			}
			/*
			if (
				total_horas_contanto_docente > maxhoras_contactodocente_matricula ||
				total_horas_semanales > maxhoras_semanal_matricula
			) {
				addNotification({
					msg: `Solo puede elegir materias que sumen hasta ${maxhoras_contactodocente_matricula} horas de contacto docente o ${maxhoras_semanal_matricula} horas totales a la semana`,
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return true;
			}*/

			openConfirmarMatricula();
			acept_t = false;

			/*if (aData.tienePreMatricula && ePreMatriculaAsignaturas.length > count_select_pre_matricula) {
				const mensaje = {
					title: `¡Advertencia!`,
					html: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
						ePersona.nombre_completo
					}, le informamos que tiene asignaturas pendientes (${
						ePreMatriculaAsignaturas.length - count_select_pre_matricula
					}) por asignar horario que eligió en Prematrícula. <br>Si desea continuar presione "ACEPTAR", pero recuerde que se perderan las asignaturas que eligió en Prematrícula y se asignaran las que esta eligiendo ahora en la Matriculación; en caso contrario desea asignar horario favor presione "CANCELAR"`,
					type: 'warning',
					icon: 'warning',
					showCancelButton: true,
					allowOutsideClick: false,
					confirmButtonColor: '#3085d6',
					cancelButtonColor: '#d33',
					confirmButtonText: 'Aceptar',
					cancelButtonText: 'Cancelar'
				};
				Swal.fire(mensaje)
					.then((result) => {
						if (result.value) {
							if (ePeriodoMatricula.valida_configuracion_ultima_matricula && vaUltimaMatricula) {
								openConfirmarCaso();
								acept_t = false;
							} else {
								openConfirmarMatricula();
								acept_t = false;
							}
						} else {
							loading.setLoading(false, 'Cargando, espere por favor...');
							addNotification({
								msg: 'Se ha cancelado, puede seguir eligiendo o asignando horario a sus asignaturas',
								type: 'info'
							});
							acept_t = false;
						}
					})
					.catch((error) => {
						addNotification({ msg: error.message, type: 'error' });
						acept_t = false;
					});
			} else {
				if (ePeriodoMatricula.valida_configuracion_ultima_matricula && vaUltimaMatricula) {
					openConfirmarCaso();
					acept_t = false;
				} else {
					openConfirmarMatricula();
					acept_t = false;
				}
			}*/
		}
	};

	const openConfirmarMatricula = () => {
		//calcula_gratuidad();
		loading.setLoading(false, 'Cargando, espere por favor...');
		if (ePeriodoMatricula.valida_terminos) {
			if (perdida_gratuidad) {
				mSizeConfirmarMatricula = 'xl';
			} else {
				mSizeConfirmarMatricula = 'xl';
			}
		} else {
			mSizeConfirmarMatricula = 'sm';
		}
		mOpenConfirmarMatricula = true;
	};

	const confirmarMatricula = () => {
		const fnIniti = function () {
			//mensajeConfirmarDiferido = '';			
			const acepto_terminos = acept_t;
			if (ePeriodoMatricula.valida_terminos){
				if (!acepto_terminos) {
					addNotification({
						msg: `Para continuar, favor acepte los términos y condiciones`,
						type: 'warning',
						target: 'newNotificationToast'
					});
					return false;
				}		
			}									
			const _acept_t = acepto_terminos ? 1 : 0;

			loading.setLoading(true, 'Cargando, espere por favor...');
			loadAjax(
				{
					action: 'enroll',
					materias: JSON.stringify(eMaterias),
					nivel_id: eNivel.id,
					cobro: cobro,
					tipo_matricula: tipo_matricula,
					acept_t: _acept_t,
					caso: casoSelected === undefined ? 0 : casoSelected
				},
				'alumno/matricula/posgrado'
			)
				.then((response) => {
					if (response.value.isSuccess) {
						loading.setLoading(false, 'Cargando, espere por favor...');
						matricula_id = response.value.data.phase;
						/*if (
							ePeriodoMatricula.valida_cuotas_rubro &&
							ePeriodoMatricula.num_cuotas_rubro &&
							response.value.data.valorarancel > 0
						) {
							openConfirmarDiferir(response.value.data);
							closeConfirmarMatricula();
						} else {}*/
						if (response.value.data.valorpagar > 0) {
							const mensaje = {
								title: `NOTIFICACIÓN`,
								text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
									ePersona.nombre_completo
								}, le informamos que el proceso de matriculación ha finalizado y cuenta rubros pendientes por cancelar. Consulte los valores en el Módulo "Mis Finanzas"`,
								type: 'warning',
								icon: 'warning',
								showCancelButton: false,
								allowOutsideClick: false,
								confirmButtonColor: '#3085d6',
								cancelButtonColor: '#d33',
								confirmButtonText: 'Aceptar',
								cancelButtonText: 'Cancelar'
							};
							Swal.fire(mensaje)
								.then((result) => {
									if (result.value) {
										loading.setLoading(true, 'Cargando, espere por favor...');
										if (ePeriodoMatricula.valida_login) {
											logOutUser();
										} else {
											changeProfile(
												'token/change/academic_period',
												{ periodo_id: response.value.data.periodo_id },
												1
											);
										}
									} else {
										loading.setLoading(true, 'Cargando, espere por favor...');
										if (ePeriodoMatricula.valida_login) {
											logOutUser();
										} else {
											changeProfile(
												'token/change/academic_period',
												{ periodo_id: response.value.data.periodo_id },
												1
											);
										}
									}
								})
								.catch((error) => {
									loading.setLoading(false, 'Cargando, espere por favor...');
									/*addToast({
									type: 'error',
									header: 'Ocurrio un error',
									body: error.message
								});*/
									addNotification({ msg: error.message, type: 'error' });
								});
						} else {
							const mensaje = {
								title: `NOTIFICACIÓN`,
								text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
									ePersona.nombre_completo
								}, se informa que el proceso de matriculación ha finalizado.`,
								type: 'success',
								icon: 'success',
								showCancelButton: false,
								allowOutsideClick: false,
								confirmButtonColor: '#3085d6',
								cancelButtonColor: '#d33',
								confirmButtonText: 'Aceptar',
								cancelButtonText: 'Cancelar'
							};
							Swal.fire(mensaje)
								.then((result) => {
									if (result.value) {
										loading.setLoading(true, 'Cargando, espere por favor...');
										if (ePeriodoMatricula.valida_login) {
											logOutUser();
										} else {
											changeProfile(
												'token/change/academic_period',
												{ periodo_id: response.value.data.periodo_id },
												1
											);
										}
									} else {
										loading.setLoading(true, 'Cargando, espere por favor...');
										if (ePeriodoMatricula.valida_login) {
											logOutUser();
										} else {
											changeProfile(
												'token/change/academic_period',
												{ periodo_id: response.value.data.periodo_id },
												1
											);
										}
									}
								})
								.catch((error) => {
									loading.setLoading(false, 'Cargando, espere por favor...');
									/*addToast({
									type: 'error',
									header: 'Ocurrio un error',
									body: error.message
								});*/
									addNotification({ msg: error.message, type: 'error' });
								});
						}
						
					} else {
						loading.setLoading(false, 'Cargando, espere por favor...');
						/*addToast({
						type: 'error',
						header: 'Ocurrio un error',
						body: response.value.message
					});*/
						addNotification({ msg: response.value.message, type: 'error' });
					}
				})
				.catch((error) => {
					loading.setLoading(false, 'Cargando, espere por favor...');
					/*addToast({
					type: 'error',
					header: 'Ocurrio un error',
					body: error.message
				});*/
					addNotification({ msg: error.message, type: 'error' });
				});
		};
		fnIniti();
	};

	/*const closeConfirmarCaso = () => {
		mOpenConfirmarCaso = false;
		if (eCasoUltimaMatricula) {
			casoSelected = eCasoUltimaMatricula.id;
		} else {
			casoSelected = undefined;
		}
	};*/

	/*const openConfirmarCaso = () => {
		loading.setLoading(false, 'Cargando, espere por favor...');
		if (eCasoUltimaMatricula) {
			casoSelected = eCasoUltimaMatricula.id;
			openConfirmarMatricula();
		} else {
			casoSelected = undefined;
			mOpenConfirmarCaso = true;
		}
	};*/

	/*const closeConfirmarDiferir = () => {
		mOpenConfirmarDiferido = false;
		const mensaje = {
			title: `NOTIFICACIÓN`,
			text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
				ePersona.nombre_completo
			}, se informa que el proceso ha finalizado y registra valores por concepto de matricula. Consulte los valores en Módulo "Mis Finanzas"`,
			type: 'warning',
			icon: 'warning',
			showCancelButton: false,
			allowOutsideClick: false,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: 'Aceptar',
			cancelButtonText: 'Cancelar'
		};
		Swal.fire(mensaje)
			.then((result) => {
				if (result.value) {
					loading.setLoading(true, 'Cargando, espere por favor...');

					if (ePeriodoMatricula.valida_login) {
						logOutUser();
					} else {
						changeProfile('token/change/academic_period', { periodo_id: periodo_id_aux }, 1);
					}
				} else {
					loading.setLoading(true, 'Cargando, espere por favor...');
					if (ePeriodoMatricula.valida_login) {
						logOutUser();
					} else {
						changeProfile('token/change/academic_period', { periodo_id: periodo_id_aux }, 1);
					}
				}
			})
			.catch((error) => {
				loading.setLoading(false, 'Cargando, espere por favor...');				
				addNotification({ msg: error.message, type: 'error' });
			});
	};

	const openConfirmarDiferir = (data) => {
		loading.setLoading(false, 'Cargando, espere por favor...');
		periodo_id_aux = data.periodo_id;
		mOpenConfirmarDiferido = true;
		mensajeConfirmarDiferido = `<p style="font-size:15px !important">${
			ePersona.es_mujer ? 'Estimada' : 'Estimado'
		} ${ePersona.nombre_completo}, ¿desea diferir el valor de <strong>$ ${
			data.valorarancel
		}</strong> del rubro <strong>${data.descripcionarancel}</strong> a <strong>${
			ePeriodoMatricula.num_cuotas_rubro
		}</strong> ${ePeriodoMatricula.num_cuotas_rubro > 1 ? 'meses' : 'mes'}?</p>`;		
	};
	const confirmarDiferir = () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		loadAjax(
			{
				action: 'to_differ',
				idm: matricula_id
			},
			'alumno/matricula/posgrado'
		)
			.then((response) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				if (response.value.isSuccess) {
					const mensaje = {
						title: `NOTIFICACIÓN`,
						text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
							ePersona.nombre_completo
						}, le informamos que se procedió a diferir los rubros generados. El proceso de matriculación ha finalizado. Consulte los valores en Módulo "Mis Finanzas"`,
						type: 'success',
						icon: 'success',
						showCancelButton: false,
						allowOutsideClick: false,
						confirmButtonColor: '#3085d6',
						cancelButtonColor: '#d33',
						confirmButtonText: 'Aceptar',
						cancelButtonText: 'Cancelar'
					};
					Swal.fire(mensaje)
						.then((result) => {
							if (result.value) {
								loading.setLoading(true, 'Cargando, espere por favor...');
								if (ePeriodoMatricula.valida_login) {
									logOutUser();
								} else {
									changeProfile('token/change/academic_period', { periodo_id: periodo_id_aux }, 1);
								}
							} else {
								loading.setLoading(true, 'Cargando, espere por favor...');
								if (ePeriodoMatricula.valida_login) {
									logOutUser();
								} else {
									changeProfile('token/change/academic_period', { periodo_id: periodo_id_aux }, 1);
								}
							}
						})
						.catch((error) => {
							addNotification({ msg: error.message, type: 'error' });
						});
				} else {
					addNotification({ msg: response.value.message, type: 'error' });
				}
			})
			.catch((error) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				addNotification({ msg: error.message, type: 'error' });
			});
	};*/

	/*const confirmarCaso = () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		if (casoSelected === undefined) {
			loading.setLoading(false, 'Cargando, espere por favor...');
			addNotification({
				msg: `Para continuar, favor seleccione un caso`,
				type: 'warning',
				target: 'newNotificationToast'
			});
			return false;
		}
		loading.setLoading(false, 'Cargando, espere por favor...');
		mOpenConfirmarCaso = false;
		openConfirmarMatricula();
	};*/

	/*const filtrarAsignaturasPreMatricula = () => {*/
		/*ePreMatriculaAsignaturas;
		id = 'identificador_prematricula_{am.id}';*/
		//console.log("sal");
	/*	let levels = [];
		let cards = document.getElementsByClassName('cardSubjects');
		[].forEach.call(cards, (element) => {
			let band = false;
			ePreMatriculaAsignaturas.forEach((pre) => {
				if (
					converToAscii(element.textContent.toLowerCase()).indexOf(
						converToAscii(pre.asignatura.nombre.toLowerCase())
					) !== -1
				) {
					band = true;
				}
			});

			if (!band) {
				element.style.display = 'none'; // hide
				element.classList.remove('valueYesSearch');
			} else {
				element.style.display = ''; // show
				element.classList.toggle('valueYesSearch');

				levels.push(element.querySelector('.card-level-academic').textContent);
			}
		});
		[].forEach.call(document.getElementsByClassName('hr_nivel_malla'), (element) => {
			element.style.display = 'none'; // hide
			if (levels.indexOf(converToAscii(element.textContent.toLowerCase())) === -1) {
				element.style.display = 'none'; // hide
			} else {
				element.style.display = ''; // show
			}
		});
	};*/

	/*$: {
		if (!load) {
			//console.log("entro");
			if (aData.tienePreMatricula) {
				//console.log("entro 2");
				filtrarAsignaturasPreMatricula();
			}
		}
	}*/
</script>

<svelte:head>
	<title>{Title}</title>
</svelte:head>

{#if !load}
	<BreadCrumb title={Title} items={itemsBreadCrumb} back={backBreadCrumb} />

	<div class="row align-items-center">
		<div class="col-xl-8 col-lg-8 col-md-12 col-12">
			<!--<div
				class="pt-16 rounded-top-md"
				style="background: url({variables.BASE_API_STATIC}/images/aok/banner-tarjeta3.png) no-repeat; background-size: cover;"
			/>-->
			<div
				class="d-flex align-items-end justify-content-between bg-white px-4 pt-4 pb-4 rounded-none rounded-bottom-md shadow-sm"
			>
				<div class="d-flex align-items-center">
					<div
						class="me-4 position-relative d-flex justify-content-end align-items-end mt-n5 d-none d-sm-block d-sm-none d-md-block"
					>
						<img
							src={ePersona.foto_perfil}
							onerror="this.onerror=null;this.src='./image.png'"
							class="avatar-xxl rounded-circle border border-4 border-white"
						/>
						<a
							href="#"
							class="position-absolute mt-2 ms-n3"
							data-bs-toggle="tooltip"
							data-placement="top"
							title="Verifed"
						>
							<img src="./assets/images/svg/checked-mark.svg" alt="" height="35" width="35" />
						</a>
					</div>
					<div class="lh-1">
						<h2 class="mb-2">{ePersona.nombre_completo}</h2>
						<p class="mb-2 d-block lh-lg">
							<b>Documento:</b>
							{DEBUG ? '0999999999' : ePersona.documento}
							{#if ePersona.emailinst !== ePersona.email}
								{#if ePersona.emailinst}
									<b>Correo Institucional:</b> {DEBUG ? 'unemi@unemi.edu.ec' : ePersona.emailinst}
								{/if}
								{#if ePersona.email}
									<b>Correo Personal:</b> {DEBUG ? 'unemi@unemi.edu.ec' : ePersona.email}
								{/if}
							{:else}
								<b>Correo Institucional:</b> {DEBUG ? 'unemi@unemi.edu.ec' : ePersona.emailinst}
							{/if}
						</p>
						<p class="mb-2 d-block lh-lg">
							<b>Telf.:</b>
							{DEBUG ? '0920991910' : ePersona.telefono}
							<b>Ciudad:</b>
							{DEBUG ? 'MILAGRO' : ePersona.ciudad} <b>Dirección:</b>
							{DEBUG ? 'cdla. Universitaria Romulo Minchala' : ePersona.direccion}
						</p>
						<p class="mb-2 d-block lh-lg">
							<b>Carrera:</b>
							{eCarrera.display} <b>Malla:</b>
							{eMalla.display}
						</p>
						<p class="mb-2 d-block lh-lg">
							<b>Periodo:</b>
							{ePeriodo.display} <b>Nivel malla:</b>
							{eNivelMalla.nombre}
						</p>
						<p class="mb-2 d-block lh-lg">							
							{#if itinerario > 0}
								<b> <Icon name="gear" /> Itinerario {itinerario}: </b>
								{#if itinerario == 1}
								<span class="badge bg-primary smaller">DERECHO PROCESAL CONSTITUCIONAL</span>
								{/if}
								{#if itinerario == 2}
								<span class="badge bg-primary smaller">DERECHO PROCESAL PENAL</span>
								{/if}
							{/if}
							<b> <Icon name="gear" /> Jornada: </b>
							<span class="badge bg-black smaller">{eInscripcion.sesion.nombre}</span>
						</p>
					</div>
				</div>
			</div>
		</div>
		<div class="col-xl-4 col-lg-4 col-md-12 col-12">
			<!--<div class="d-grid gap-2 m-2">
				<button class="btn btn-info" type="button" on:click={() => openCalendario(ComponentCalendario)}
					>CALENDARIO DE MATRICULACIÓN</button
				>
			</div>
			<hr />-->
			<div class="card h-100">
				<div class="card-header">
					<h6 class="mb-0 fs-6 fw-bolder"><Icon name="building" /> {eNivel.display}</h6>
				</div>
				<table class="table   mb-0">
					<tbody>
						<tr>
							<td class="border-top-0 fs-6 fw-bolder">
								<span class="align-middle"><Icon name="hdd-network" /> Nivel de matrícula:</span>
							</td>
							<td class="text-end border-top-0 fs-6">{nivelmalla_matricula}</td>
						</tr>
						<tr>
							<td class="border-top-0 fs-6 fw-bolder">
								<span class="align-middle"
									><Icon name="bookmarks" /> Asignaturas aperturadas en el nivel:</span
								>
							</td>
							<td class="text-end border-top-0 fs-6">{total_asignaturas_aperturadas}</td>
						</tr>
						<tr>
							<td class="border-top-0 fs-6 fw-bolder">
								<span class="align-middle"
									><Icon name="bookmark-plus" /> Asignaturas seleccionadas del nivel aperturado:</span
								>
							</td>
							<td class="text-end border-top-0 fs-6"
								>{total_asignaturas_aperturadas_seleccionada}</td
							>
						</tr>
						<tr>
							<td class="border-top-0 fs-6 fw-bolder">
								<span class="align-middle"
									><Icon name="bookmark-check" /> Total de asignaturas seleccionadas:</span
								>
							</td>
							<td class="text-end border-top-0 fs-6">{total_eMaterias}</td>
						</tr>
						<!--<tr>
							<td class="border-top-0 fs-6 fw-bolder">
								<span class="align-middle"
									><Icon name="clock" /> Total de Horas Contacto Docente:</span
								>
							</td>
							<td class="text-end border-top-0 fs-6">{total_horas_contanto_docente}</td>
						</tr>
						<tr>
							<td class="border-top-0 fs-6 fw-bolder">
								<span class="align-middle"
									><Icon name="clock-history" /> Total de Horas Semanales:</span
								>
							</td>
							<td class="text-end border-top-0 fs-6">{total_horas_semanales}</td>
						</tr>-->
						{#if num_materias_maxima && vaUltimaMatricula}
							<tr>
								<td class="border-top-0 fs-6 fw-bolder">
									<span class="align-middle"
										><Icon name="suit-club-fill" /> Máximo de asignaturas a seleccionar:</span
									>
								</td>
								<td class="text-end border-top-0 fs-6">{num_materias_maxima}</td>
							</tr>
						{/if}
						<!--{#if aData.tienePreMatricula}
							<tr>
								<td class="border-top-0 fs-6 fw-bolder">
									<span class="align-middle"
										><Icon name="list-ul" /> Total de Asignatura de Prematrícula:</span
									>
								</td>
								<td class="text-end border-top-0 fs-6">{ePreMatriculaAsignaturas.length}</td>
							</tr>
						{/if}-->
					</tbody>
				</table>
			</div>
		</div>
	</div>
	{#if !aData.NoTienePago}
		<div class="row mt-2">
			<div class="col-12">				
				<div class="pt-2">
					<div class="alert alert-danger" style="margin-top: 10px;">						
						{ePersona.es_mujer ? 'Estimada' : 'Estimado'}, aún <b>NO HA REALIZADO NINGÚN PAGO</b>, para <b>HABILITAR</b> su matriculación a la maestría.
					</div>
					
				</div>						
			</div>
		</div>
	{/if}
	{#if aData.tienePreMatricula || vaUltimaMatricula || (ePeriodoMatricula.valida_deuda && tiene_valores_pendientes)}
		<div class="row mt-2">
			<div class="col-12">
				{#if ePeriodoMatricula.valida_deuda && tiene_valores_pendientes}
					<div class="pt-2">{@html msg_valores_pendientes}</div>
				{/if}
				<!--{#if vaUltimaMatricula}
					<div class="pt-2">
						<div class="alert alert-danger">
							<h4 class="alert-heading">
								Usted tiene asignatura(s) de {ePeriodoMatricula.num_matriculas == 3
									? 'tercera'
									: ePeriodoMatricula.num_matriculas == 4
									? 'cuarta'
									: ePeriodoMatricula.num_matriculas == 5
									? 'quinta'
									: ePeriodoMatricula.num_matriculas} matrícula:
							</h4>
							Durante el proceso, primero deberá elegir la(s) materia(s) que debe matricularse {ePeriodoMatricula.num_matriculas ==
							3
								? 'tercera'
								: ePeriodoMatricula.num_matriculas == 4
								? 'cuarta'
								: ePeriodoMatricula.num_matriculas == 5
								? 'quinta'
								: ePeriodoMatricula.num_matriculas} vez. Soló podrá seleccionar hasta tres asignaturas
							en este periodo.
						</div>
					</div>
				{/if}
				{#if aData.tienePreMatricula}
					<div class="pt-2">
						<div class="alert alert-info">
							<h4 class="alert-heading"><Icon name="info-circle-fill" /> Información</h4>
							Usted tiene asignaturas de Prematrícula generada el {ePreMatricula.fecha} a las {ePreMatricula.hora}
							<button
								type="button"
								class="btn btn-info btn-sm p-1"
								on:click={() => filtrarAsignaturasPreMatricula()}>Ver</button
							>
						</div>
					</div>
				{/if}-->
			</div>
		</div>
	{/if}
	<div class="row align-items-center mt-6 align-items-center">
		<div class="col-xl-12 col-lg-12 col-md-12 col-12">
			<h2 class="display-6">Asignaturas de mi malla</h2>

			{#if puede_matricularse}
				<a href="javascript:;" class="btn-flotante" on:click|preventDefault={() => actionEnroll()}
					><Icon name="plus-circle" /> Matricularse</a
				>
			{/if}
		</div>
	</div>

	<div class="row mt-2">
		<div class="col-xl-3 col-lg-3 col-md-3 col-12">
			<div class="card">
				<div class="card-header">
					<h5>Filtrar asignaturas</h5>
					<form class="">
						<div class="d-grid gap-2 mt-2">
							<button
								class="btn btn-danger btn-sm fs-6"
								type="button"
								on:click|preventDefault={(event) => actionSearchLevel(event, 'all')}
								>LIMPIAR BUSQUEDA</button
							>
						</div>
					</form>
				</div>
				<nav class="navbar navbar-expand  p-4 navbar-mail">
					<div class="collapse navbar-collapse" id="navbarNav">
						<ul class="navbar-nav flex-column in w-100" id="sidebarnav">
							<li class="navbar-header">
								<h5 class="heading">Estado</h5>
							</li>
							<li class="nav-item">
								<a
									href="javascript:;"
									class="nav-link actionSearchLevel"
									on:click|preventDefault={(event) => actionSearchLevel(event, 'pendiente')}
									><Icon class="icon" name="circle" /> Pendientes</a
								>
							</li>
							<li class="nav-item">
								<a
									href="javascript:;"
									class="nav-link actionSearchLevel"
									on:click|preventDefault={(event) => actionSearchLevel(event, 'aprobada')}
									><Icon class="icon" name="circle" /> Aprobadas</a
								>
							</li>
							<li class="nav-item">
								<a
									href="javascript:;"
									class="nav-link actionSearchLevel"
									on:click|preventDefault={(event) => actionSearchLevel(event, 'reprobada')}
									><Icon class="icon" name="circle" /> Reprobadas</a
								>
							</li>
							<li>
								<div class="navbar-border" />
							</li>
							<li class="navbar-header mt-0">
								<h5 class="heading">Niveles</h5>
							</li>
							{#each eNivelesMalla as nm}
								<li class="nav-item">
									<a
										href="javascript:;"
										class="nav-link actionSearchLevel"
										on:click|preventDefault={(event) => actionSearchLevel(event, nm.nombre)}
										><Icon class="icon" name="circle" /> {nm.nombre}</a
									>
								</li>
							{/each}
							{#if isItinerarios}
								<li>
									<div class="navbar-border" />
								</li>
								<li class="navbar-header mt-0">
									<h5 class="heading">Itinerario</h5>
								</li>
								{#each listItinerarios as iti}
									<li class="nav-item">
										<a
											href="javascript:;"
											class="nav-link actionSearchLevel"
											on:click|preventDefault={(event) =>
												actionSearchLevel(event, `ITINERARIO ${iti}`)}
											><Icon class="icon" name="circle" /> ITINERARIO {iti}</a
										>
									</li>
								{/each}
							{/if}
							<!--{#if aData.tienePreMatricula}
								<li>
									<div class="navbar-border" />
								</li>
								<li class="navbar-header mt-0">
									<h5 class="heading">
										Prematrícula <button
											type="button"
											class="btn btn-info btn-sm p-0"
											on:click={() => filtrarAsignaturasPreMatricula()}>Ver</button
										>
									</h5>
								</li>
								{#each ePreMatriculaAsignaturas as _am}
									<li class="nav-item">
										<a
											href="javascript:;"
											class="nav-link actionSearchLevel"
											on:click|preventDefault={(event) =>
												actionSearchLevel(event, `${_am.asignatura.nombre}`)}
											><Icon name="circle" /> {_am.asignatura.nombre}</a
										>
									</li>
								{/each}
							{/if}-->
						</ul>
					</div>
				</nav>
			</div>
		</div>
		<div class="col-xl-9 col-lg-9 col-md-9 col-12">
			<form class="mb-4">
				<input
					class="form-control me-2"
					type="search"
					aria-label="Search"
					bind:value={search}
					on:keyup={actionSearchKeyPress}
					id="searchSubjects"
					placeholder="Buscar ..."
				/>
			</form>
			{#each eNivelesMalla as eNM}
				<div class="row align-items-center">
					<div class="col-xl-12 col-lg-12 col-md-12 col-12">
						<h4
							class="hr_nivel_malla mb-6"
							style="width:100%; text-align:left; border-bottom: 1px solid #198754; line-height:0.1em; margin:10px 0 20px;"
						>
							<span
								style="padding:0 10px; background: #198754; padding: 5px 10px; color: #FFFFFF; border-radius: 5px"
								>{eNM.nombre}</span
							>
						</h4>
						{#if asignaturasmalla.length > 0}
							<div
								class="row row-cols-1 row-cols-sm-2 row-cols-md-2 row-cols-lg-2 row-cols-xl-2 row-cols-xxl-3 mb-3 text-center"
							>
								{#each asignaturasmalla as am}
									{#if eNM.idm == am.nivelmalla_id}
										<div class="col mb-4 cardSubjects valueYesSearch ida_{am.asignatura_id}">
											<div class="card rounded-3 shadow-sm h-100 card-hover">
												{#if am.va_num_matricula === ePeriodoMatricula.num_matriculas && am.estado === 2}
													<span class="position-absolute top-0 end-0 badge rounded-pill bg-danger">
														<span id={`Tooltip_va_num_matricula_${am.id}`}
															>{am.va_num_matricula} MAT.</span
														>
														<Tooltip target={`Tooltip_va_num_matricula_${am.id}`} placement="top"
															>Va a su {am.va_num_matricula == 3
																? 'tercera'
																: am.va_num_matricula == 4
																? 'cuarta'
																: am.va_num_matricula == 5
																? 'quinta'
																: am.va_num_matricula} matrícula</Tooltip
														>
													</span>
												{/if}
												
												<!--{#if aData.tienePreMatricula}
													{#if ePreMatriculaAsignaturas
														.map((ele) => ele.asignatura.id_display)
														.indexOf(am.asignatura_id) !== -1}
														<div
															id="identificador_prematricula_{am.id}"
															class="position-absolute top-0 start-0 translate-middle blinkimg"
														>
															<Icon
																name="bell-fill"
																style="font-size: 1.5rem;"
																class="text-warning"
															/>
														</div>
													{/if}
												{/if}-->
												<div
													class="card-header py-1"
													style="height: 5.5rem; font-size: 13px; font-weight: bold; overflow: hidden; display: flex; text-overflow: ellipsis; width: 100%; align-items: center; justify-content: center;"
												>
													<div class="my-0 text-truncate-line-2 text-inherit">
														{am.asignatura}
													</div>
												</div>
												<div class="card-body">
													<h6 class="card-title pricing-card-title card-level-academic">
														{am.nivelmalla}
													</h6>
													<h6 class="card-title pricing-card-title">
														<small class="text-muted fw-light">{am.ejeformativo}</small>
													</h6>
													{#if am.estado === 1}
														<span class="badge rounded-pill bg-success">APROBADA</span>
													{:else if am.estado === 2}
														<span class="badge rounded-pill bg-danger"> REPROBADA </span>
														/
														<span class="badge rounded-pill bg-warning">
															<span id={`Tooltip_num_matricula_${am.id}`}
																>{am.totalrecordasignatura} MAT.</span
															>
															<Tooltip target={`Tooltip_num_matricula_${am.id}`} placement="top"
																>Tiene {am.totalrecordasignatura == 3
																	? 'tres'
																	: am.totalrecordasignatura == 4
																	? 'cuatro'
																	: am.totalrecordasignatura == 5
																	? 'cinco'
																	: am.totalrecordasignatura == 2
																	? 'dos'
																	: am.totalrecordasignatura == 1
																	? 'una'
																	: am.totalrecordasignatura} matrículas reprobadas</Tooltip
															>
														</span>
													{:else if am.estado === 3}
														<span class="badge rounded-pill bg-warning text-dark">PENDIENTE</span>
													{:else if am.estado === 0}
														<span class="badge rounded-pill bg-info text-dark">NO APLICA</span>
													{/if}
													{#if am.itinerario > 0}
														/ <span class="badge rounded-pill bg-info text-dark"
															>{am.itinerario_verbose}</span
														>
													{/if}
													<div
														class="border-top row mt-3 border-bottom mb-3 g-0 align-items-center"
													>
														<!--{am.id}-->
														<div class="col">
															<div class="pe-1 ps-2 py-3">
																<h5 class="mb-0">{converToDecimal(am.creditos)}</h5>
																<span class="fs-6 text-muted">Créditos</span>
															</div>
														</div>
														<div class="col border-start">
															<div class="pe-1 pt-2 pb-2 ps-2 py-1">
																<h5 class="mb-0 fs-6 text-muted">Horas</h5>
															</div>
															<div
																class="justify-content-between border-bottom pe-1 ps-2 py-1"
															>
																<span class="fs-6 text-muted">Total asignatura</span>
																<span class="fs-6">
																	<h6 class="mb-0">{am.horas}</h6>
																</span>
															</div>
															<!--
															<div
																class="d-flex justify-content-between border-bottom pe-1 ps-2 py-1"
															>
																<span class="fs-6 text-muted">Semanales</span>
																<span class="fs-6">
																	<h6 class="mb-0">{am.horas_semanal}</h6>
																</span>
															</div>
															<div
																class="d-flex justify-content-between border-bottom pe-1 ps-2 py-1"
															>
																<span class="fs-6 text-muted">Contacto docente</span>
																<span class="fs-6">
																	<h6 class="mb-0">{am.horas_contacto_docente}</h6>
																</span>
															</div>
															-->
														</div>
													</div>																										
													<p class="fs-6 text-muted">Precedencias</p>
													<ul class="list-group list-group-flush">
														{#if am.predecesoras.length > 0}
															{#each am.predecesoras as predecesora}
																<li class="list-group-item fs-6 text-muted">{predecesora}</li>
															{/each}
														{:else}
															<li class="list-group-item fs-6 text-muted">
																No registra ninguna precedencia
															</li>															
														{/if}																												
													</ul>																										
													{#if !am.matriculado_materia && am.estado != 1}	 
														{#if !am.disponible_fechas_matricular || am.pendiente_evaluaciondocente}	
														<div class="border-top row mt-3 g-0 align-items-center">
															<p class="fs-6 text-muted"><br>Alertas</p>
															<ul class="list-group list-group-flush">																																									
																<li class="list-group-item fs-6 text-danger">
																	{#if !am.disponible_fechas_matricular}		
																		Sin fechas de matriculación <br>
																	{/if}
																	{#if am.disponible_fechas_matricular && am.pendiente_evaluaciondocente}
																		Pendiente Evaluación Docente <br>																	
																		<a
																			href=""
																			on:click|preventDefault={() =>
																				actionAsistenciaModule('pro_aluevaluacion')}
																			class="btn btn-info btn-sm"
																			target="_blank"
																		> <i class="bi bi-bell" /> Evaluar Docente
																		</a>
																	{/if}
																</li>																																																																																																				
															</ul>
														</div>
														{/if}
													{/if}
												</div>
												<div class="card-footer">
													<div class="row align-items-center g-0">														
														{#if am.puede_ver_horario == 1 && !am.matricula_bloqueda && am.disponible_fechas_matricular && !am.matriculado_materia && !am.pendiente_evaluaciondocente  }															
															<button
																type="button"
																itinerario="itinerario_{am.itinerario}"
																id="btn_aplicar_{am.id}"
																class="w-100 btn btn-lg btn-info"
																on:click={openAsignatura(am)}><Icon name="plus" /> HORARIO</button
															>
															<button
																style="display: none"
																type="button"
																id="btn_remover_{am.id}"
																class="w-100 btn btn-lg btn-danger"
																on:click={() => {
																	removeAsignatura(am);
																}}><Icon name="eraser" /> REMOVER</button
															>
														{:else}														
															{#if am.matriculado_materia }
																<p class="text-success w-100">MATRICULADO</p>													
															{:else}	
																{#if am.matricula_bloqueda }
																	<span class="badge bg-danger text-white">
																		MATRICULACIÓN BLOQUEADA POR FALTA DE PAGO
																	</span>																		
																{:else}
																	<p class="text-info w-100">UNEMI</p>																																		
																{/if}																														
															{/if}
														{/if}
													</div>
												</div>
											</div>
										</div>
									{/if}
								{/each}
							</div>
						{/if}
					</div>
				</div>
			{/each}
		</div>
	</div>
	<Modal
		isOpen={mOpenAsignatura}
		toggle={mToggleAsignatura}
		size="xl"
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
		backdrop="static"
	>
		<ModalHeader toggle={mToggleAsignatura}>
			<h4>
				<span>HORARIOS DE CLASES DE </span>
				{eAsignatura.asignatura} [{eAsignatura.nivelmalla}]
			</h4>
		</ModalHeader>
		<ModalBody>
			<div
				class="row row-cols-1 row-cols-sm-1 row-cols-md-2 row-cols-lg-2 row-cols-xl-2 row-cols-xxl-3 text-center"
			>
				{#if eAsignatura.materias && eAsignatura.materias.length === 0}
					<div class="alert alert-warning">
						<h4 class="alert-heading">Importante!</h4>
						<p class="alert-body">MATERIA NO ESTÁ ABIERTA,CONTACTAR A SU DIRECTOR/A DE CARRERA</p>
					</div>
				{:else}
					{#each eAsignatura.materias as m}
						<div class="col mb-4">
							<div class="card rounded-3 shadow-sm h-100 card-hover text-center">
								<div class="card-header">
									<div class="text-muted fs-6">
										{#if m.coordinacion_alias}
											<span id={`Tooltip_alias_facultad_${m.id}`}>{m.coordinacion_alias}</span> /
											&nbsp;
											<Tooltip target={`Tooltip_alias_facultad_${m.id}`} placement="top"
												>{m.coordinacion}</Tooltip
											>
										{:else if m.coordinacion}
											{m.coordinacion} /&nbsp;
										{/if}
										{m.carrera}
										
									</div>
									<span class="badge rounded-pill bg-dark" id={`Tooltip_paralelo_${m.id}`}
										>{m.paralelo}</span
									>
									<Tooltip target={`Tooltip_paralelo_${m.id}`} placement="top">Paralelo</Tooltip>
									{#if m.tipomateria === 1}
										&nbsp;/ <span class="badge rounded-pill bg-info bg-info"
											>{m.tipomateria_display}</span
										>
									{:else if m.tipomateria === 2}
										&nbsp;/ <span class="badge rounded-pill bg-secondary"
											>{m.tipomateria_display}</span
										>
									{:else}
										&nbsp;/ <span class="badge rounded-pill bg-light text-dark"
											>{m.tipomateria_display}</span
										>
									{/if}
									{#if m.teoriapractica === 1}
										&nbsp;/ <span class="badge rounded-pill bg-warning" id={`Tooltip_tp_${m.id}`}
											>TP</span
										>
										<Tooltip target={`Tooltip_tp_${m.id}`} placement="top"
											>Teórica y Práctica</Tooltip
										>
									{:else if m.teoriapractica === 0}
										&nbsp;/ <span class="badge rounded-pill bg-warning" id={`Tooltip_t_${m.id}`}
											>T</span
										>
										<Tooltip target={`Tooltip_t_${m.id}`} placement="top">Teórica</Tooltip>
									{/if}
								</div>
								<div class="card-body">
									{#if m.iniciomatriculacion && m.finmatriculacion }
									<div class="text-center">
										<h5 class="card-title mb-0 fs-6 text-info">FECHA DE MATRICULACIÓN</h5>
										<p class="card-text mb-0 fs-6 text-muted">Inicio: {m.iniciomatriculacion} - Fin: {m.finmatriculacion}</p>																														
									</div>
									{:else}
									<div class="text-center">
										<h5 class="card-title mb-0 fs-6 text-muted">SIN FECHAS DE MATRICULACIÓN</h5>								
									</div>
									{/if}
									<div class="text-center">
										<h5 class="card-title mb-0 fs-6">{m.session}</h5>
										<p class="card-text mb-0 fs-6 text-muted">{m.inicio} - {m.fin}</p>																				
										
									</div>									
									{#if ePeriodoMatricula.ver_profesor_materia}
										{#if m.profesor}
											<div class="d-flex justify-content-between border-bottom py-1 mt-1 fs-6">
												<span>{m.genero_profesor}</span>
												<span class="text-dark">{m.profesor}</span>
											</div>																					
										{/if}											
									{/if}
									{#if ePeriodoMatricula.ver_cupo_materia}
										<div class="d-flex justify-content-between border-bottom py-1 mt-1 fs-6">
											<span>Cupo</span>
											<span class="text-dark">{m.cupos}</span>
										</div>
										<div class="d-flex justify-content-between border-bottom py-1 mt-1 fs-6">
											<span>Disponibles</span>
											<span class="text-dark">{m.disponibles}</span>
										</div>
									{/if}									
									{#if ePeriodoMatricula.ver_horario_materia}
										<h4 class="fw-bold mt-4 mb-4">Horario de clases:</h4>
										<ul class="list-unstyled mb-0">
											{#if m.horarios_verbose_aux.length > 0}
												{#each m.horarios_verbose_aux as h}
													<li class="mb-1 fs-6">
														<span class="text-success me-1"><Icon name="calendar-event" /></span>
														{h.dia_verbose}
														<span class="fw-bold text-dark">{h.comienza} - {h.termina}</span>
														<span class="fw-bold text-muted" id={`Tooltip_aula_${h.id}`}>
															<Icon name="geo-alt-fill" />{h.aula}
															<Tooltip target={`Tooltip_aula_${h.id}`} placement="top">AULA</Tooltip
															>
														</span>
														<span class="text-info me-1"
															><Icon name="info" id={`Tooltip_horario_${h.id}`} />
															<Tooltip target={`Tooltip_horario_${h.id}`} placement="top"
																>{h.inicio} - {h.fin}</Tooltip
															></span
														>
													</li>
												{/each}
											{:else}
												<li class="mb-1">
													<span class="text-success me-1"><Icon name="stopwatch" /></span>
													<span>No existe registro de horario</span>
												</li>
											{/if}
										</ul>
									{/if}
								</div>
								<div class="card-footer">
									{#if m.puede_agregar}
										{#if ePeriodoMatricula.valida_horario_materia}
											{#if m.horarios.length > 0}
												{#if ePeriodoMatricula.valida_cupo_materia}
													{#if m.disponibles > 0}
														<button
															type="button"
															class="w-100 btn btn-lg btn-success"
															on:click={selectSubject(m)}>SELECCIONAR</button
														>
													{:else}
														<p class="text-info w-100">SIN CUPOS DISPONIBLES</p>
													{/if}
												{:else}
													<button
														type="button"
														class="w-100 btn btn-lg btn-success"
														on:click={selectSubject(m)}>SELECCIONAR</button
													>
												{/if}
											{:else}
												<p class="text-info w-100">UNEMI</p>
											{/if}
										{:else if ePeriodoMatricula.valida_cupo_materia}
											{#if m.disponibles > 0}
												<button
													type="button"
													class="w-100 btn btn-lg btn-success"
													on:click={selectSubject(m)}>SELECCIONAR</button
												>
											{:else}
												<p class="text-info w-100">SIN CUPOS DISPONIBLES</p>
											{/if}
										{:else}
											<button
												type="button"
												class="w-100 btn btn-lg btn-success"
												on:click={selectSubject(m)}>SELECCIONAR</button
											>
										{/if}
									{:else}
										<p class="text-info w-100">UNEMI</p>
									{/if}
								</div>
							</div>
						</div>
					{/each}
				{/if}
			</div>
		</ModalBody>
		<ModalFooter>
			<Button color="primary" on:click={mToggleAsignatura}>Cerrar</Button>
		</ModalFooter>
	</Modal>
	<Modal
		isOpen={mOpenAsignaturaPractica}
		toggle={mToggleAsignaturaPractica}
		size="lg"
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
		backdrop="static"
		fade={false}
	>
		<ModalHeader toggle={mToggleAsignaturaPractica}>
			<h4>
				<span>HORARIOS DE CLASES DE ASIGNATURA PRÁCTICA DE </span>
				{eAsignatura.asignatura} [{eAsignatura.nivelmalla}]
			</h4>
		</ModalHeader>
		<ModalBody>
			{#if eMateria.mispracticas && eMateria.mispracticas.length === 0}
				<div class="alert alert-warning">
					<h4 class="alert-heading">Importante!</h4>
					<p class="alert-body">NO EXISTEN PRÁCTICAS PROGRAMADAS</p>
				</div>
			{:else}
				<div
					class="row row-cols-1 row-cols-sm-1 row-cols-md-1 row-cols-lg-2 row-cols-xl-2 row-cols-xxl-2 text-center"
				>
					{#each eMateria.mispracticas as p}
						<div class="col mb-4">
							<div class="card rounded-3 shadow-sm h-100 card-hover text-center">
								<div class="card-header">
									<div class="text-muted">
										{p.paralelo}
									</div>
								</div>
								<div class="card-body">
									{#if ePeriodoMatricula.ver_cupo_materia}
										<div class="d-flex justify-content-between border-bottom py-1 mt-1 fs-6">
											<span>Cupo</span>
											<span class="text-dark">{p.cupos}</span>
										</div>
										<div class="d-flex justify-content-between border-bottom py-1 mt-1 fs-6">
											<span>Disponibles</span>
											<span class="text-dark">{p.disponibles}</span>
										</div>
									{/if}
									{#if ePeriodoMatricula.ver_horario_materia}
										<h4 class="fw-bold mt-4 mb-4">Horario de prácticas:</h4>
										<ul class="list-unstyled mb-0">
											{#if p.horarios.length > 0}
												{#each p.horarios as h}
													<li class="mb-1 fs-6">
														<span class="text-success me-1"><Icon name="calendar-event" /></span>
														{h.dia_verbose}
														<span class="fw-bold text-dark">{h.comienza} - {h.termina}</span>
														<span class="fw-bold text-muted" id={`Tooltip_aula_${h.id}`}>
															<Icon name="geo-alt-fill" />{h.aula}
															<Tooltip target={`Tooltip_aula_${h.id}`} placement="top">AULA</Tooltip
															>
														</span>
														<span class="text-info me-1"
															><Icon name="info" id={`Tooltip_horario_${h.id}`} />
															<Tooltip target={`Tooltip_horario_${h.id}`} placement="top"
																>{h.inicio} - {h.fin}</Tooltip
															></span
														>
													</li>
												{/each}
											{:else}
												<li class="mb-1">
													<span class="text-success me-1"><Icon name="stopwatch" /></span>
													<span>No existe registro de horario</span>
												</li>
											{/if}
										</ul>
									{/if}
								</div>
								<div class="card-footer">
									{#if ePeriodoMatricula.valida_horario_materia}
										{#if p.horarios.length > 0}
											{#if ePeriodoMatricula.valida_cupo_materia}
												{#if p.cupos > 0 && p.disponibles <= p.cupos}
													<button
														type="button"
														class="w-100 btn btn-lg btn-success"
														on:click={selectSubjectPractice(eMateria, p)}>SELECCIONAR</button
													>
												{:else}
													<p class="text-info w-100">UNEMI</p>
												{/if}
											{:else}
												<button
													type="button"
													class="w-100 btn btn-lg btn-success"
													on:click={selectSubjectPractice(eMateria, p)}>SELECCIONAR</button
												>
											{/if}
										{:else}
											<p class="text-info w-100">UNEMI</p>
										{/if}
									{:else if ePeriodoMatricula.valida_cupo_materia}
										{#if p.cupos > 0 && p.disponibles <= p.cupos}
											<button
												type="button"
												class="w-100 btn btn-lg btn-success"
												on:click={selectSubjectPractice(eMateria, p)}>SELECCIONAR</button
											>
										{:else}
											<p class="text-info w-100">UNEMI</p>
										{/if}
									{:else}
										<button
											type="button"
											class="w-100 btn btn-lg btn-success"
											on:click={selectSubjectPractice(eMateria, p)}>SELECCIONAR</button
										>
									{/if}
								</div>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</ModalBody>
		<ModalFooter>
			<Button color="primary" on:click={mToggleAsignaturaPractica}>Cerrar</Button>
		</ModalFooter>
	</Modal>

	<Modal
		isOpen={mOpenConfirmarMatricula}
		toggle={mToggleConfirmarMatricula}
		size={mSizeConfirmarMatricula}
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
		backdrop="static"
		fade={false}
	>
		<ModalHeader toggle={mToggleConfirmarMatricula}>
			<h4>Confirmar matrícula</h4>
		</ModalHeader>
		<ModalBody>
			{#if perdida_gratuidad === true}
				<div class="alert alert-danger" role="alert">
					<p>{@html mensaje_gratuidad}</p>
					<hr />
					<p class="mb-0">
						Una vez confirmada la matriculación, podrá consultar los rubros a pagar a través del
						módulo "Mis Finanzas".
					</p>
				</div>
			{:else}
				<div>
					<p>{@html mensaje_gratuidad}</p>
				</div>
			{/if}
			{#if ePeriodoMatricula.valida_configuracion_ultima_matricula && vaUltimaMatricula && eCasoUltimaMatricula && casoSelected}
				<p>{@html eCasoUltimaMatricula.articulo.descripcion}</p>
				<div class="border p-4 rounded-3 mb-3">
					<div class="form-check">
						<input
							class="form-check-input"
							type="radio"
							name="casoRadio"
							id="caso_id_{eCasoUltimaMatricula.id}"
							value={eCasoUltimaMatricula.id}
							bind:group={casoSelected}
						/>
						<label class="form-check-label" for="caso_id_{eCasoUltimaMatricula.id}">
							<b>Caso {eCasoUltimaMatricula.orden}:</b>
							{eCasoUltimaMatricula.descripcion}
						</label>
					</div>
				</div>
			{/if}
			{#if ePeriodoMatricula.valida_terminos}
				<table class="table table-bordered table-striped">
					<thead>
						<tr>
							<th colspan="2"
								><h4 style="color: red; padding-left: 15px; padding-right: 15px">
									<strong>TÉRMINOS Y CONDICIONES</strong>
								</h4></th
							>
						</tr>
					</thead>
					<tbody style="text-align: justify-all">
						<tr>
							<td style="text-align: center !important; vertical-align: middle; ">
								<!--<input name="acept_t" type="checkbox" bind:checked={acept_t} />-->
								<div class="form-check form-switch">
									<input
										name="acept_t"
										class="form-check-input"
										type="checkbox"
										bind:checked={acept_t}
									/>
									{#if !acept_t}
										<label class="form-check-label text-muted fs-6 fw-bold" for="acept_t"
											>Aceptar</label
										>
									{/if}
								</div>
							</td>
							<td style=" vertical-align: middle;">
								<div class="terminos">
									{@html ePeriodoMatricula.terminos}
								</div>
							</td>
						</tr>
					</tbody>
				</table>
			{/if}
			<p>
				{ePersona.es_mujer ? 'Estimada' : 'Estimado'}
				{ePersona.nombre_completo}, al confirmar usted se estaría matriculando en (<b
					>{eMaterias.length}</b
				>) {eMaterias.length > 1 ? 'materias' : 'materia'}.
				<b class="fs-5">¿Está {ePersona.es_mujer ? 'segura' : 'seguro'} de matricularse?</b>
			</p>
		</ModalBody>
		<ModalFooter>
			<Button color="success" on:click={() => confirmarMatricula()}>Confirmar</Button>
			<Button color="primary" on:click={mToggleConfirmarMatricula}>Cerrar</Button>
		</ModalFooter>
	</Modal>

	<!--<Modal
		isOpen={mOpenConfirmarDiferido}
		toggle={mToggleConfirmarDiferido}
		size="md"
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
		backdrop="static"
		fade={false}
	>
		<ModalHeader toggle={() => closeConfirmarDiferir()}>
			<h4>Confirmar diferido</h4>
		</ModalHeader>
		<ModalBody>
			{@html mensajeConfirmarDiferido}
		</ModalBody>
		<ModalFooter>
			<Button color="success" on:click={() => confirmarDiferir()}>Diferir</Button>
			<Button color="primary" on:click={() => closeConfirmarDiferir()}>No Diferir</Button>
		</ModalFooter>
	</Modal>-->

	<!--<Modal
		isOpen={mOpenConfirmarCaso}
		toggle={mToggleConfirmarCaso}
		size="xl"
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
		backdrop="static"
		fade={false}
	>
		<ModalHeader toggle={() => closeConfirmarCaso()}>
			<h4>
				Confirmar casos por {ePeriodoMatricula.num_matriculas == 2
					? 'segunda'
					: ePeriodoMatricula.num_matriculas == 3
					? 'tercera'
					: ePeriodoMatricula.num_matriculas == 4
					? 'cuarta'
					: ePeriodoMatricula.num_matriculas == 5
					? 'quinta'
					: ePeriodoMatricula.num_matriculas} matrícula
			</h4>
		</ModalHeader>
		<ModalBody>
			<div class="row mt-1">
				<div class="col-12">
					<h3>Seleccione el caso con el que se identifica:</h3>
					<p>{@html ePeriodoMatricula.configuracion_ultima_matricula.articulo.descripcion}</p>
					{#each ePeriodoMatricula.configuracion_ultima_matricula.caso as caso}
						{#if caso.validar === false}
							<div class="border p-4 rounded-3 mb-3">
								<div class="form-check">
									<input
										class="form-check-input"
										type="radio"
										name="casoRadio"
										id="caso_id_{caso.id}"
										value={caso.id}
										bind:group={casoSelected}
									/>
									<label class="form-check-label" for="caso_id_{caso.id}">
										<b>Caso {caso.orden}:</b>
										{caso.descripcion}
									</label>
								</div>
							</div>
						{/if}
					{/each}
				</div>
			</div>
		</ModalBody>
		<ModalFooter>
			<Button color="success" on:click={() => confirmarCaso()}>Confirmar</Button>
			<Button color="primary" on:click={() => closeConfirmarCaso()}>Cerrar</Button>
		</ModalFooter>
	</Modal>-->
	{#if mOpenModal}
		<ModalGenerico
			mToggle={mToggleModal}
			mOpen={mOpenModal}
			{modalContent}
			title={mTitleModal}
			aData={aDataModal}
			size="xl"
			on:actionRun={actionRun}
		/>
	{/if}
{:else}
	<div
		class="m-0 vh-100 row justify-content-center align-items-centser"
		style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 1000; display: flex; flex-direction: column; align-items: center; justify-content: center;"
	>
		<div class="col-auto text-center">
			<Spinner color="dark" type="border" style="width: 3rem; height: 3rem;" />
			<h3>Verificando la información, espere por favor...</h3>
		</div>
	</div>
{/if}

<style>
	@keyframes blink {
		0% {
			opacity: 1;
		}
		50% {
			opacity: 0;
		}
		100% {
			opacity: 1;
		}
	}

	.blinkimg {
		animation: blink 1s;
		animation-iteration-count: infinite;
	}
	.navbar-nav .navbar-border {
		border-bottom: 1px solid #ecebf1;
		margin: 1.25rem 0;
	}
	.card-header {
		padding: 0.5rem 1rem;
	}
	.list-group-item {
		padding: 0px !important;
	}	

	.btn-flotante {
		font-size: 16px; /* Cambiar el tamaño de la tipografia */
		text-transform: uppercase; /* Texto en mayusculas */
		font-weight: bold; /* Fuente en negrita o bold */
		color: #ffffff; /* Color del texto */
		border-radius: 5px; /* Borde del boton */
		letter-spacing: 2px; /* Espacio entre letras */
		background: rgb(25, 135, 84) none repeat scroll 0% 0%; /* Color de fondo */
		padding: 0.5rem 0.875rem; /* Relleno del boton */
		position: fixed;
		bottom: 60px;
		right: 70px;
		transition: all 300ms ease 0ms;
		box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.1);
		z-index: 99;
	}
	.btn-flotante:hover {
		background-color: #2c2fa5; /* Color de fondo al pasar el cursor */
		box-shadow: 0px 15px 20px rgba(0, 0, 0, 0.3);
		transform: translateY(-7px);
	}
	@media only screen and (max-width: 600px) {
		.btn-flotante {
			font-size: 14px;
			padding: 12px 20px;
			bottom: 70px;
			right: 70px;
		}
		.btn-flotante:hover {
			background-color: #2c2fa5; /* Color de fondo al pasar el cursor */
			box-shadow: 0px 15px 20px rgba(0, 0, 0, 0.3);
			transform: translateY(-7px);
		}
	}
	@media only screen and (max-width: 360px) {
		.btn-flotante {
			font-size: 14px;
			padding: 12px 20px;
			bottom: 100px;
			right: 70px;
		}
		.btn-flotante:hover {
			background-color: #2c2fa5; /* Color de fondo al pasar el cursor */
			box-shadow: 0px 15px 20px rgba(0, 0, 0, 0.3);
			transform: translateY(-7px);
		}
	}
</style>
