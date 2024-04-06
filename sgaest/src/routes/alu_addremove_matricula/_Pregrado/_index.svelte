<script lang="ts">
	import { apiPOST, browserGet, logOutUser } from '$lib/utils/requestUtils';
	import { variables } from '$lib/utils/constants';
	import { addToast } from '$lib/store/toastStore';
	import { onMount } from 'svelte';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import DetalleValores from '$components/Alumno/Matricula/DetalleValores.svelte';
	import ComponentRequisitosTitulacion from '$components/Alumno/Matricula/DetalleRequisitosTitulacion.svelte';
	import {
		Button,
		Icon,
		Modal,
		ModalBody,
		ModalFooter,
		ModalHeader,
		Spinner,
		Tooltip
	} from 'sveltestrap';
	import type { Matricula } from '$lib/interfaces/user.interface';
	import type { CustomError } from '$lib/interfaces/error.interface';
	import { goto } from '$app/navigation';
	import { addNotification } from '$lib/store/notificationStore';
	import { converToAscii } from '$lib/formats/formatString';
	import { loading } from '$lib/store/loadingStore';
	import { converToDecimal } from '$lib/formats/formatDecimal';
	import Swal from 'sweetalert2';
	const DEBUG = import.meta.env.DEV;
	let itemsBreadCrumb = [
		{
			text: 'Adicionar y Retirar - Matriculación Online',
			active: true,
			href: undefined
		}
	];
	let backBreadCrumb = {
		href: '/',
		text: 'Atrás'
	};
	let Title = '';
	let search = '';
	let load = true;
	let aData = undefined;
	let ePersona = undefined;
	let eInscripcion = undefined;
	let eCarrera = undefined;
	let eMalla = undefined;
	let ePeriodoMatricula = undefined;
	let ePeriodo = undefined;
	let eNivelMalla = undefined;
	let eNivelesMalla = [];
	let eNivelesMallaOfertada = [];
	let FichaSocioEconomicaINEC = undefined;
	let eAsignaturasMalla = [];
	let eAsignaturaMalla = {};
	let eNivel = undefined;
	let isItinerarios = false;
	let listItinerarios = [];
	let itinerario = 0;
	let itinerario_aux = 0;
	let eMatricula = undefined;
	let eMateriasAsignadas = [];
	let eMateria = {};
	let vaUltimaMatricula = false;
	let num_materias_maxima = 0;
	let count_max_last_roll = 0;
	let count_select_last_roll = 0;
	let maxhoras_contactodocente_matricula = 0;
	let maxhoras_semanal_matricula = 0;
	let confirm_digit_remove_enrollment_1 = '';
	let confirm_digit_remove_enrollment_2 = '';
	let confirm_digit_remove_enrollment_3 = '';
	let confirm_digit_remove_enrollment_4 = '';
	let confirm_digit_remove_enrollment_5 = '';
	let confirm_digit_remove_enrollment_6 = '';
	let confirm_digit_remove_course_1 = '';
	let confirm_digit_remove_course_2 = '';
	let confirm_digit_remove_course_3 = '';
	let confirm_digit_remove_course_4 = '';
	let confirm_digit_remove_course_5 = '';
	let confirm_digit_remove_course_6 = '';
	let eMateriaAsignadaRemove = {};
	let aDataModal = {};
	let modalTitle = '';
	let mOpenAsignatura = false;
	let mOpenEliminarConfirmarMatricula = false;
	let mOpenEliminarConfirmarMateria = false;
	let mOpenAsignaturaPractica = false;
	let showModalGenerico = false;
	let modalGenericoContent;
	const mToggleAsignatura = () => (mOpenAsignatura = !mOpenAsignatura);
	const mToggleAsignaturaPractica = () => (mOpenAsignaturaPractica = !mOpenAsignaturaPractica);
	const mToggleEliminarConfirmarMatricula = () =>
		(mOpenEliminarConfirmarMatricula = !mOpenEliminarConfirmarMatricula);
	const mToggleEliminarConfirmarMateria = () =>
		(mOpenEliminarConfirmarMateria = !mOpenEliminarConfirmarMateria);
	const mToggleModalGenerico = () => (showModalGenerico = !showModalGenerico);
	export let data;

	onMount(async () => {
		if (data) {
			aData = data.aData;
			Title = aData.Title;
			ePersona = aData.ePersona;
			eInscripcion = aData.eInscripcion;
			itinerario = aData.itinerario;
			eCarrera = aData.eCarrera;
			eMalla = aData.eMalla;
			ePeriodoMatricula = aData.ePeriodoMatricula;
			ePeriodo = aData.ePeriodoMatricula.periodo;
			eNivelMalla = aData.eNivelMalla;
			FichaSocioEconomicaINEC = aData.FichaSocioEconomicaINEC;
			eNivel = aData.eNivel;
			eNivelesMalla = aData.eNivelesMalla;
			isItinerarios = aData.isItinerarios;
			listItinerarios = aData.listItinerarios;
			vaUltimaMatricula = aData.vaUltimaMatricula;
			maxhoras_contactodocente_matricula = eMalla.maxhoras_contactodocente_matricula;
			maxhoras_semanal_matricula = eMalla.maxhoras_semanal_matricula;
			if (vaUltimaMatricula) {
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

			const initial = await loadInitial()
				.then((response) => {
					//console.log(response);
					addNotification({ msg: 'La información se ha cargado puede continuar.', type: 'info' });
				})
				.catch((error) => {
					//console.log(error);
					addToast({
						type: 'error',
						header: 'Ocurrio un error',
						body: error.message
					});
					goto('/');
				});
		}
		load = false;
	});

	// pass in component as parameter and toggle modal state
	const toggleModalDetalleValores = async (component) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/general/data', {
			action: 'detail_enroll_items_invoice',
			id: eMatricula.id
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
				modalTitle = 'Detalle de los valores generados en la matriculación';
				aDataModal = res.data;
				modalGenericoContent = component;
				showModalGenerico = !showModalGenerico;
			}
		}
	};

	const actionSearchKeyPress = (e) => {
		let levels = [];
		let valueYesSearchs = document.getElementsByClassName('valueYesSearch');
		[].forEach.call(valueYesSearchs, (element) => {
			if (
				converToAscii(element.textContent.toLowerCase()).indexOf(
					converToAscii(search.toLowerCase())
				) === -1
			) {
				element.style.display = 'none'; // hide
			} else {
				element.style.display = ''; // show
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
				element.classList.toggle('valueYesSearch');
			} else {
				if (
					converToAscii(element.textContent.toLowerCase()).indexOf(
						converToAscii(value.toLowerCase())
					) === -1
				) {
					element.style.display = 'none'; // hide
					element.classList.remove('valueYesSearch');
				} else {
					element.style.display = ''; // show
					element.classList.toggle('valueYesSearch');

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

	const changeItinerarioVisible = (iti) => {
		itinerario = iti;
		//console.log(itinerario_aux);
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
			eMateriasAsignadas.forEach(function (_materiaasignada, index) {
				if (_materiaasignada.materia.asignaturamalla.itinerario > 0) {
					itinerario = _materiaasignada.materia.asignaturamalla.itinerario;
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

	const closeAsignatura = () => {
		mOpenAsignatura = false;
		eMateria = {};
	};

	const closeAsignaturaPractica = () => {
		mOpenAsignaturaPractica = false;
	};

	const closeConfirmarEliminarMatricula = () => {
		mOpenEliminarConfirmarMatricula = false;
		confirm_digit_remove_enrollment_1 = '';
		confirm_digit_remove_enrollment_2 = '';
		confirm_digit_remove_enrollment_3 = '';
		confirm_digit_remove_enrollment_4 = '';
		confirm_digit_remove_enrollment_5 = '';
		confirm_digit_remove_enrollment_6 = '';
	};

	const closeConfirmarEliminarMateria = () => {
		mOpenEliminarConfirmarMateria = false;
		eMateriaAsignadaRemove = {};
		confirm_digit_remove_course_1 = '';
		confirm_digit_remove_course_2 = '';
		confirm_digit_remove_course_3 = '';
		confirm_digit_remove_course_4 = '';
		confirm_digit_remove_course_5 = '';
		confirm_digit_remove_course_6 = '';
	};

	const loadAjax = async (data, url) =>
		new Promise(async (resolve, reject) => {
			const [res, errors] = await apiPOST(fetch, url, data);
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

	const loadInitial = () =>
		new Promise((resolve, reject) => {
			const ds = browserGet('dataSession');
			const dataSession = JSON.parse(ds);
			const matricula = <Matricula>dataSession['matricula'];
			eAsignaturasMalla = [];
			eNivelesMallaOfertada = [];
			loadAjax(
				{
					action: 'loadInitialData',
					idm: matricula.id
				},
				'alumno/matricula/add_remove/pregrado'
			)
				.then((response) => {
					if (response.value.isSuccess) {
						eMatricula = response.value.data.eMatricula;
						eInscripcion = eMatricula.inscripcion;
						eMateriasAsignadas = response.value.data.eMateriasAsignadas;
						changeItinerario();
						eAsignaturasMalla = response.value.data.eAsignaturasMalla;
						eAsignaturasMalla.forEach(function (_eAsignaturaMalla, index) {
							if (_eAsignaturaMalla.puede_ver_horario) {
								//eNivelesMallaOfertada.push(_eAsignaturaMalla.nivelmalla);
								let isExit = false;
								for (let i in eNivelesMallaOfertada) {
									if (eNivelesMallaOfertada[i]['id'] == _eAsignaturaMalla.nivelmalla.id) {
										isExit = true;
										return false;
									}
								}
								if (!isExit) {
									eNivelesMallaOfertada.push(_eAsignaturaMalla.nivelmalla);
								}
							}
						});

						eMateriasAsignadas.forEach(function (_materiaasignada, index) {
							if (
								_materiaasignada.va_num_matricula >=
								ePeriodoMatricula.num_materias_maxima_ultima_matricula
							) {
								count_select_last_roll += 1;
							}
						});

						resolve({
							error: false,
							value: true
						});
					} else {
						reject({
							error: true,
							message: response.value.message
						});
					}
				})
				.catch((error) => {
					reject({
						error: true,
						message: error.message
					});
				});
		});

	const deleteMatricula = () => {
		//console.log("entro");
		const mensaje = {
			title: `NOTIFICACIÓN`,
			html: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
				ePersona.nombre_completo
			}, al realizar esta acción usted estará liberando cupo. </br> <b>¿Está ${
				ePersona.es_mujer ? 'segura' : 'seguro'
			} de eliminar la matrícula.?</b>`,
			type: 'warning',
			icon: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: `Sí, estoy ${ePersona.es_mujer ? 'segura' : 'seguro'}`,
			cancelButtonText: 'No, cancelar'
		};
		Swal.fire(mensaje)
			.then((result) => {
				if (result.value) {
					loading.setLoading(true, 'Cargando, espere por favor...');
					if (ePeriodoMatricula.seguridad_remove_materia) {
						loadAjax(
							{
								action: 'generateCodeEliminarMatricula',
								id: eMatricula.id
							},
							'alumno/matricula/add_remove/pregrado'
						)
							.then((response) => {
								if (response.value.isSuccess) {
									let lista_emails_envio = ePersona.lista_emails;
									loading.setLoading(false, 'Cargando, espere por favor...');
									const mensaje = {
										title: `NOTIFICACIÓN`,
										text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
											ePersona.nombre_completo
										}, se informa que se ha enviado un correo electrónico (${lista_emails_envio.join(
											', '
										)}) para continuar con el proceso de eliminar matrícula`,
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
											/*if (result.value) {
												loadInitial();
											} else {
												loadInitial();
											}*/
											loading.setLoading(true, 'Cargando, espere por favor...');
											loadInitial()
												.then((response) => {
													loading.setLoading(false, 'Cargando, espere por favor...');
												})
												.catch((error) => {
													loading.setLoading(false, 'Cargando, espere por favor...');
													addToast({
														type: 'error',
														header: 'Ocurrio un error',
														body: error.message
													});
													goto('/');
												});
										})
										.catch((error) => {
											loading.setLoading(false, 'Cargando, espere por favor...');
											addNotification({
												msg: error.message,
												type: 'error'
											});
										});
								} else {
									loading.setLoading(false, 'Cargando, espere por favor...');
									addNotification({
										msg: response.value.message,
										type: 'error'
									});
								}
							})
							.catch((error) => {
								loading.setLoading(false, 'Cargando, espere por favor...');
								addNotification({
									msg: error.message,
									type: 'error'
								});
							});
					} else {
						loadAjax(
							{
								action: 'deleteMatricula',
								id: eMatricula.id,
								utilizaSeguridad: ePeriodoMatricula.seguridad_remove_materia ? 1 : 0
							},
							'alumno/matricula/add_remove/pregrado'
						)
							.then((response) => {
								if (response.value.isSuccess) {
									loading.setLoading(false, 'Cargando, espere por favor...');
									const mensaje = {
										title: `NOTIFICACIÓN`,
										text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
											ePersona.nombre_completo
										}, se informa que la matricula ha sido eliminada correctamente.`,
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
												logOutUser();
											} else {
												logOutUser();
											}
										})
										.catch((error) => {
											loading.setLoading(false, 'Cargando, espere por favor...');
											addNotification({
												msg: error.message,
												type: 'error'
											});
										});
								} else {
									loading.setLoading(false, 'Cargando, espere por favor...');
									addNotification({
										msg: response.value.message,
										type: 'error'
									});
								}
							})
							.catch((error) => {
								loading.setLoading(false, 'Cargando, espere por favor...');
								addNotification({
									msg: error.message,
									type: 'error'
								});
							});
					}
				} else {
					loading.setLoading(false, 'Cargando, espere por favor...');
					addNotification({
						msg: 'Enhorabuena el registro esta salvado.!',
						type: 'info'
					});
				}
			})
			.catch((error) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				addNotification({
					msg: error.message,
					type: 'error'
				});
			});eMatricula
	};

	const reenviarDeleteMatricula = () => {
		if (eMatricula.contador_reenviar_email_token >= 6) {
			addNotification({
				msg: 'Número de reenvio de correos electrónicos.',
				type: 'warning'
			});

			return false;
		}
		let lista_emails_envio = ePersona.lista_emails;
		const mensaje = {
			title: `NOTIFICACIÓN`,
			text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
				ePersona.nombre_completo
			}, se procedera a reenviar código de confirmación a las siguientes direcciones electrónicas ${lista_emails_envio.join(
				', '
			)} para la eliminación de la matrícula.`,
			type: 'warning',
			icon: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: 'Si, reenviar',
			cancelButtonText: 'No, cancelar'
		};
		Swal.fire(mensaje)
			.then((result) => {
				if (result.value) {
					loading.setLoading(true, 'Cargando, espere por favor...');
					loadAjax(
						{
							action: 'reenviarEliminarMatricula',
							id: eMatricula.id
						},
						'alumno/matricula/add_remove/pregrado'
					)
						.then((response) => {
							if (response.value.isSuccess) {
								loading.setLoading(false, 'Cargando, espere por favor...');
								const mensaje = {
									title: `NOTIFICACIÓN`,
									text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
										ePersona.nombre_completo
									}, se informa que se ha reenviado el correo electrónico correctamente.`,
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
											eMatricula.contador_reenviar_email_token = response.value.data.contador;
											eMatricula.puede_reenviar_token =
												response.value.data.contador >= 6 ? false : true;
											loading.setLoading(false, 'Cargando, espere por favor...');
										}
									})
									.catch((error) => {
										loading.setLoading(false, 'Cargando, espere por favor...');
										addNotification({
											msg: error.message,
											type: 'error'
										});
									});
							} else {
								loading.setLoading(false, 'Cargando, espere por favor...');
								addNotification({
									msg: response.value.message,
									type: 'error'
								});
							}
						})
						.catch((error) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							addNotification({
								msg: error.message,
								type: 'error'
							});
						});
				} else {
					loading.setLoading(false, 'Cargando, espere por favor...');
					addNotification({
						msg: 'Enhorabuena no se ha reenviado correo electrónico!',
						type: 'info'
					});
				}
			})
			.catch((error) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				addNotification({
					msg: error.message,
					type: 'error'
				});
			});
	};

	const confirmarEliminarMatricula = () => {
		let code = `${confirm_digit_remove_enrollment_1}${confirm_digit_remove_enrollment_2}${confirm_digit_remove_enrollment_3}${confirm_digit_remove_enrollment_4}${confirm_digit_remove_enrollment_5}${confirm_digit_remove_enrollment_6}`;
		if (
			confirm_digit_remove_enrollment_1 === '' ||
			confirm_digit_remove_enrollment_2 === '' ||
			confirm_digit_remove_enrollment_3 === '' ||
			confirm_digit_remove_enrollment_4 === '' ||
			confirm_digit_remove_enrollment_5 === '' ||
			confirm_digit_remove_enrollment_6 === ''
		) {
			addNotification({
				msg: 'Favor ingrese el código de confirmación',
				type: 'error'
			});
			document.getElementById('confirm_digit_remove_enrollment_1').focus();
			document.getElementById('confirm_digit_remove_enrollment_2').focus();
			document.getElementById('confirm_digit_remove_enrollment_3').focus();
			document.getElementById('confirm_digit_remove_enrollment_4').focus();
			document.getElementById('confirm_digit_remove_enrollment_5').focus();
			document.getElementById('confirm_digit_remove_enrollment_6').focus();
			return false;
		}

		loading.setLoading(true, 'Cargando, espere por favor...');
		loadAjax(
			{
				action: 'deleteMatricula',
				id: eMatricula.id,
				utilizaSeguridad: ePeriodoMatricula.seguridad_remove_materia ? 1 : 0,
				code: code
			},
			'alumno/matricula/add_remove/pregrado'
		)
			.then((response) => {
				if (response.value.isSuccess) {
					loading.setLoading(false, 'Cargando, espere por favor...');
					const mensaje = {
						title: `NOTIFICACIÓN`,
						text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
							ePersona.nombre_completo
						}, se informa que la matricula ha sido eliminada.`,
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
								logOutUser();
							} else {
								logOutUser();
							}
						})
						.catch((error) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							addNotification({
								msg: error.message,
								type: 'error'
							});
						});
				} else {
					loading.setLoading(false, 'Cargando, espere por favor...');
					addNotification({
						msg: response.value.message,
						type: 'error'
					});
				}
			})
			.catch((error) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				addNotification({
					msg: error.message,
					type: 'error'
				});
			});
	};

	const cancelarEliminarMatricula = () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		loadAjax(
			{
				action: 'cancelarEliminarMatricula',
				id: eMatricula.id
			},
			'alumno/matricula/add_remove/pregrado'
		)
			.then((response) => {
				if (response.value.isSuccess) {
					loading.setLoading(false, 'Cargando, espere por favor...');
					const mensaje = {
						title: `NOTIFICACIÓN`,
						text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
							ePersona.nombre_completo
						}, se informa que la matrícula se mantiene.`,
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
							loading.setLoading(true, 'Cargando, espere por favor...');
							closeConfirmarEliminarMatricula();
							loadInitial()
								.then((response) => {
									loading.setLoading(false, 'Cargando, espere por favor...');
								})
								.catch((error) => {
									loading.setLoading(false, 'Cargando, espere por favor...');
									addToast({
										type: 'error',
										header: 'Ocurrio un error',
										body: error.message
									});
									goto('/');
								});
						})
						.catch((error) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							addNotification({
								msg: error.message,
								type: 'error'
							});
						});
				} else {
					loading.setLoading(false, 'Cargando, espere por favor...');
					addNotification({
						msg: response.value.message,
						type: 'error'
					});
				}
			})
			.catch((error) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				addNotification({
					msg: error.message,
					type: 'error'
				});
			});
	};

	const openConfirmarEliminarMatricula = () => {
		mOpenEliminarConfirmarMatricula = true;
		confirm_digit_remove_enrollment_1 = '';
		confirm_digit_remove_enrollment_2 = '';
		confirm_digit_remove_enrollment_3 = '';
		confirm_digit_remove_enrollment_4 = '';
		confirm_digit_remove_enrollment_5 = '';
		confirm_digit_remove_enrollment_6 = '';
	};

	const removeMateria = (MateriaAsignada) => {
		if (eMateriasAsignadas.length === 1) {
			loading.setLoading(true, 'Cargando, espere por favor...');
			addNotification({
				msg: `Número mínimo de materias: No se permite eliminar última materia asignada a su matrícula.`,
				type: 'warning',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return true;
		}
		const mensaje = {
			title: `NOTIFICACIÓN`,
			html: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${ePersona.nombre_completo}, <b>¿Está ${
				ePersona.es_mujer ? 'segura' : 'seguro'
			} de remover/quitar la materia.?</b>`,
			type: 'warning',
			icon: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: `SÍ, estoy ${ePersona.es_mujer ? 'segura' : 'seguro'}`,
			cancelButtonText: 'No, cancelar'
		};
		Swal.fire(mensaje)
			.then((result) => {
				if (result.value) {
					loading.setLoading(true, 'Cargando, espere por favor...');
					if (ePeriodoMatricula.seguridad_remove_materia) {
						loadAjax(
							{
								action: 'generateRetiroMateria',
								id: MateriaAsignada.id
							},
							'alumno/matricula/add_remove/pregrado'
						)
							.then((response) => {
								if (response.value.isSuccess) {
									let lista_emails_envio = ePersona.lista_emails;
									loading.setLoading(false, 'Cargando, espere por favor...');
									const mensaje = {
										title: `NOTIFICACIÓN`,
										text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
											ePersona.nombre_completo
										}, se informa que se ha enviado un correo electrónico (${lista_emails_envio.join(
											', '
										)}) para continuar con el proceso de retiro.`,
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
											loading.setLoading(true, 'Cargando, espere por favor...');
											loadInitial()
												.then((response) => {
													loading.setLoading(false, 'Cargando, espere por favor...');
												})
												.catch((error) => {
													loading.setLoading(false, 'Cargando, espere por favor...');
													addToast({
														type: 'error',
														header: 'Ocurrio un error',
														body: error.message
													});
													goto('/');
												});
										})
										.catch((error) => {
											loading.setLoading(false, 'Cargando, espere por favor...');
											addNotification({
												msg: error.message,
												type: 'error'
											});
										});
								} else {
									loading.setLoading(false, 'Cargando, espere por favor...');

									addNotification({
										msg: response.value.message,
										type: 'error'
									});
								}
							})
							.catch((error) => {
								loading.setLoading(false, 'Cargando, espere por favor...');

								addNotification({
									msg: error.message,
									type: 'error'
								});
							});
					} else {
						loadAjax(
							{
								action: 'deleteMateria',
								id: MateriaAsignada.id,
								utilizaSeguridad: ePeriodoMatricula.seguridad_remove_materia ? 1 : 0
							},
							'alumno/matricula/add_remove/pregrado'
						)
							.then((response) => {
								if (response.value.isSuccess) {
									loading.setLoading(false, 'Cargando, espere por favor...');
									const mensaje = {
										title: `NOTIFICACIÓN`,
										text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
											ePersona.nombre_completo
										}, se informa que la materia ha sido removido/quitado correctamente.`,
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
											loading.setLoading(true, 'Cargando, espere por favor...');
											loadInitial()
												.then((response) => {
													loading.setLoading(false, 'Cargando, espere por favor...');
												})
												.catch((error) => {
													loading.setLoading(false, 'Cargando, espere por favor...');
													addToast({
														type: 'error',
														header: 'Ocurrio un error',
														body: error.message
													});
													goto('/');
												});
										})
										.catch((error) => {
											loading.setLoading(false, 'Cargando, espere por favor...');
											addNotification({
												msg: error.message,
												type: 'error'
											});
										});
								} else {
									loading.setLoading(false, 'Cargando, espere por favor...');

									addNotification({
										msg: response.value.message,
										type: 'error'
									});
								}
							})
							.catch((error) => {
								loading.setLoading(false, 'Cargando, espere por favor...');
								addNotification({
									msg: error.message,
									type: 'error'
								});
							});
					}
				} else {
					loading.setLoading(false, 'Cargando, espere por favor...');
					addNotification({
						msg: 'Enhorabuena el registro esta salvado.!',
						type: 'info'
					});
				}
			})
			.catch((error) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				addNotification({
					msg: error.message,
					type: 'error'
				});
			});
	};

	const reenviarRemoveMateria = (MateriaAsignada) => {
		if (MateriaAsignada.contador_reenviar_email_token >= 6) {
			addNotification({
				msg: 'Número de reenvio de correos electrónicos.',
				type: 'warning'
			});

			return false;
		}
		let lista_emails_envio = ePersona.lista_emails;
		const mensaje = {
			title: `NOTIFICACIÓN`,
			text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
				ePersona.nombre_completo
			}, se procedera a reenviar código de confirmación a las siguientes direcciones electrónicas ${lista_emails_envio.join(
				', '
			)} para el retiro de la materia (${MateriaAsignada.materia.asignatura.nombre}).`,
			type: 'warning',
			icon: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: 'Si, reenviar',
			cancelButtonText: 'No, cancelar'
		};

		Swal.fire(mensaje)
			.then((result) => {
				if (result.value) {
					loading.setLoading(true, 'Cargando, espere por favor...');
					loadAjax(
						{
							action: 'reenviarRetiroMateria',
							id: MateriaAsignada.id
						},
						'alumno/matricula/add_remove/pregrado'
					)
						.then((response) => {
							if (response.value.isSuccess) {
								loading.setLoading(false, 'Cargando, espere por favor...');
								const mensaje = {
									title: `NOTIFICACIÓN`,
									text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
										ePersona.nombre_completo
									}, se informa que se ha reenviado el correo electrónico correctamente.`,
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
											eMateriasAsignadas.forEach(function (_ma, index) {
												if (_ma.id == MateriaAsignada.id) {
													eMateriasAsignadas[index].contador_reenviar_email_token =
														response.value.data.contador;
													eMateriasAsignadas[index].puede_reenviar_token =
														response.value.data.contador >= 6 ? false : true;
												}
											});
											loading.setLoading(false, 'Cargando, espere por favor...');
										}
									})
									.catch((error) => {
										loading.setLoading(false, 'Cargando, espere por favor...');
										addNotification({
											msg: error.message,
											type: 'error'
										});
									});
							} else {
								loading.setLoading(false, 'Cargando, espere por favor...');
								addNotification({
									msg: response.value.message,
									type: 'error'
								});
							}
						})
						.catch((error) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							addNotification({
								msg: error.message,
								type: 'error'
							});
						});
				} else {
					loading.setLoading(false, 'Cargando, espere por favor...');
					addNotification({
						msg: 'Enhorabuena no se ha reenviado correo electrónico!',
						type: 'error'
					});
				}
			})
			.catch((error) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				addNotification({
					msg: error.message,
					type: 'error'
				});
			});
	};

	const cancelarRemoveMateria = () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		loadAjax(
			{
				action: 'cancelarRetiroMateria',
				id: eMateriaAsignadaRemove.id
			},
			'alumno/matricula/add_remove/pregrado'
		)
			.then((response) => {
				if (response.value.isSuccess) {
					loading.setLoading(false, 'Cargando, espere por favor...');
					const mensaje = {
						title: `NOTIFICACIÓN`,
						text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
							ePersona.nombre_completo
						}, se informa que la materia ${
							eMateriaAsignadaRemove.materia.asignatura.nombre
						} se mantiene en su matrícula.`,
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
							closeConfirmarEliminarMateria();
							loading.setLoading(true, 'Cargando, espere por favor...');
							loadInitial()
								.then((response) => {
									loading.setLoading(false, 'Cargando, espere por favor...');
								})
								.catch((error) => {
									loading.setLoading(false, 'Cargando, espere por favor...');
									addToast({
										type: 'error',
										header: 'Ocurrio un error',
										body: error.message
									});
									goto('/');
								});
						})
						.catch((error) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							addNotification({
								msg: error.message,
								type: 'error'
							});
						});
				} else {
					loading.setLoading(false, 'Cargando, espere por favor...');
					addNotification({
						msg: response.value.message,
						type: 'error'
					});
				}
			})
			.catch((error) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				addNotification({
					msg: error.message,
					type: 'error'
				});
			});
	};

	const confirmarRemoveMateria = () => {
		let code = `${confirm_digit_remove_course_1}${confirm_digit_remove_course_2}${confirm_digit_remove_course_3}${confirm_digit_remove_course_4}${confirm_digit_remove_course_5}${confirm_digit_remove_course_6}`;
		if (
			confirm_digit_remove_course_1 === '' ||
			confirm_digit_remove_course_2 === '' ||
			confirm_digit_remove_course_3 === '' ||
			confirm_digit_remove_course_4 === '' ||
			confirm_digit_remove_course_5 === '' ||
			confirm_digit_remove_course_6 === ''
		) {
			addNotification({
				msg: 'Favor ingrese el código de confirmación',
				type: 'error'
			});
			document.getElementById('confirm_digit_remove_course_1').focus();
			document.getElementById('confirm_digit_remove_course_2').focus();
			document.getElementById('confirm_digit_remove_course_3').focus();
			document.getElementById('confirm_digit_remove_course_4').focus();
			document.getElementById('confirm_digit_remove_course_5').focus();
			document.getElementById('confirm_digit_remove_course_6').focus();
			return false;
		}

		loading.setLoading(true, 'Cargando, espere por favor...');

		loadAjax(
			{
				action: 'deleteMateria',
				id: eMateriaAsignadaRemove.id,
				utilizaSeguridad: ePeriodoMatricula.seguridad_remove_materia ? 1 : 0,
				code: code
			},
			'alumno/matricula/add_remove/pregrado'
		)
			.then((response) => {
				if (response.value.isSuccess) {
					loading.setLoading(false, 'Cargando, espere por favor...');
					const mensaje = {
						title: `NOTIFICACIÓN`,
						text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
							ePersona.nombre_completo
						}, se informa que la materia ${
							eMateriaAsignadaRemove.materia.asignatura.nombre
						} ha sido removido/quitado correctamente.`,
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
							closeConfirmarEliminarMateria();
							loading.setLoading(true, 'Cargando, espere por favor...');
							loadInitial()
								.then((response) => {
									loading.setLoading(false, 'Cargando, espere por favor...');
								})
								.catch((error) => {
									loading.setLoading(false, 'Cargando, espere por favor...');
									addToast({
										type: 'error',
										header: 'Ocurrio un error',
										body: error.message
									});
									goto('/');
								});
						})
						.catch((error) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							addNotification({
								msg: error.message,
								type: 'error'
							});
						});
				} else {
					loading.setLoading(false, 'Cargando, espere por favor...');
					addNotification({
						msg: response.value.message,
						type: 'error'
					});
				}
			})
			.catch((error) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				addNotification({
					msg: error.message,
					type: 'error'
				});
			});
	};

	const openConfirmarRemoveMateria = (eMateriaAsignada) => {
		eMateriaAsignadaRemove = eMateriaAsignada;
		mOpenEliminarConfirmarMateria = true;
		confirm_digit_remove_course_1 = '';
		confirm_digit_remove_course_2 = '';
		confirm_digit_remove_course_3 = '';
		confirm_digit_remove_course_4 = '';
		confirm_digit_remove_course_5 = '';
		confirm_digit_remove_course_6 = '';
	};
	const getLastNivelMalla = () => {
		return eNivelesMalla[eNivelesMalla.length - 1];
	};
	const openAsignatura = (_asignaturamalla) => {
		if (_asignaturamalla.validarequisitograduacion) {
			loading.setLoading(true, 'Cargando, espere por favor...');
			let contadorCumple = 0;
			let eRequisitos = _asignaturamalla.aRequisitos;
			eRequisitos.forEach(function (requisito, index) {
				if (requisito.cumple) {
					contadorCumple += 1;
				}
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (eRequisitos.length != contadorCumple) {
				addNotification({
					msg: `No cumple con los requisitos de ingreso a la asignatura ${_asignaturamalla.asignatura.nombre}`,
					type: 'warning',
					target: 'newNotificationToast'
				});
				aDataModal = { eRequisitos: eRequisitos };
				modalGenericoContent = ComponentRequisitosTitulacion;
				showModalGenerico = !showModalGenerico;
				modalTitle = 'Requisitos de Ingreso a la Unidad de Integración Curricular';
				return true;
			}
		}
		loading.setLoading(true, 'Cargando, espere por favor...');
		if (
			ePeriodoMatricula.valida_materias_maxima &&
			eMateriasAsignadas.length + 1 > num_materias_maxima
		) {
			addNotification({
				msg: `Número de materias: Ha superado la cantidad (${num_materias_maxima}) asignaturas permitidas a seleccionar`,
				type: 'warning',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return true;
		}
		let _total_horas_contacto_docente = 0;
		let _total_horas_semanales = 0;
		eMateriasAsignadas.forEach((element) => {
			_total_horas_contacto_docente += element.materia.asignaturamalla.horasacdsemanal;
			_total_horas_semanales += element.materia.asignaturamalla.horas_semanal;
		});
		_total_horas_contacto_docente += _asignaturamalla.horasacdsemanal;
		_total_horas_semanales += _asignaturamalla.horas_semanal;
		/*const _total_horas_contacto_docente =
			eMatricula.total_horas_contacto_docente + _asignaturamalla.horasacdtotal;
		const _total_horas_semanales =
			eMatricula.total_horas_semanales + _asignaturamalla.horas_semanal;
		//console.log('_total_horas_contacto_docente: ', _total_horas_contacto_docente);
		//console.log('_total_horas_semanales: ', _total_horas_semanales);*/
		if (
			_total_horas_contacto_docente > maxhoras_contactodocente_matricula ||
			_total_horas_semanales > maxhoras_semanal_matricula
		) {
			addNotification({
				msg: `Solo puede elegir materias que sumen hasta ${maxhoras_contactodocente_matricula} horas de contacto docente o ${maxhoras_semanal_matricula} horas totales a la semana`,
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return true;
		}
		/*//console.log("count_select_last_roll: ", count_select_last_roll);
		//console.log("count_max_last_roll: ", count_max_last_roll);*/
		if (
			aData.vaUltimaMatricula &&
			count_select_last_roll < count_max_last_roll &&
			_asignaturamalla.va_num_matricula != ePeriodoMatricula.num_matriculas
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
		}
		let _paralelo_id = 0;
		if (eMateriasAsignadas.length == 0 || vaUltimaMatricula) {
			eAsignaturaMalla = _asignaturamalla;
		} else {
			if (_asignaturamalla.itinerario == 0) {
				eMateriasAsignadas.forEach(function (_materiaasignada, index) {
					if (
						_materiaasignada.materia.asignaturamalla.nivelmalla.id == _asignaturamalla.nivelmalla.id
					) {
						_paralelo_id = _materiaasignada.materia.paralelomateria.idm;
						return false;
					}
				});
				if (_paralelo_id > 0) {
					let _aux_asignatura = {};
					//console.log(asignatura);
					for (const [key, value] of Object.entries(_asignaturamalla)) {
						if (key != 'eMaterias') {
							_aux_asignatura[key] = value;
						}
					}

					/*asignatura.forEach((value, key, map) => {
						if (key != 'materias') {
							_aux_asignatura[key] = value;
						}
					});*/
					let _eMaterias = [];
					_asignaturamalla.eMaterias.forEach(function (_materia, index) {
						if (_paralelo_id == _materia.paralelomateria.idm) {
							_eMaterias.push(_materia);
						}
					});

					_aux_asignatura['eMaterias'] = _eMaterias;
					//console.log("_aux_asignatura: ", _aux_asignatura);
					eAsignaturaMalla = _aux_asignatura;
				} else {
					eAsignaturaMalla = _asignaturamalla;
				}
			} else {
				eAsignaturaMalla = _asignaturamalla;
			}
		}
		//console.log('eAsignaturaMalla: ', eAsignaturaMalla);
		let fnModal = function () {
			mOpenAsignatura = true;
		};
		if (ePeriodoMatricula.valida_cupo_materia) {
			loadAjax(
				{
					action: 'loadCupoMateria',
					aData: JSON.stringify(eAsignaturaMalla),
					idn: eNivel.id,
					idp: _paralelo_id
				},
				'alumno/matricula/add_remove/pregrado'
			)
				.then((response) => {
					if (response.value.isSuccess) {
						loading.setLoading(false, 'Cargando, espere por favor...');
						eAsignaturaMalla = response.value.data.aData;
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
				loading.setLoading(false, 'Cargando, espere por favor...');
				addNotification({ msg: `Ocurrio un error al cargar los datos`, type: 'error' });
			}
			loading.setLoading(false, 'Cargando, espere por favor...');
		}
		if (_asignaturamalla.asignaturapracticas){
			const mensaje = {
					title: ``,
					html: `<b> ACTA DE COMPROMISO Y RESPONSABILIDAD PARA MATRICULACIÓN EN ASIGNATURAS DE PRÁCTICAS PREPROFESIONALES (Prácticas Laborales y/o Prácticas de Servicio Comunitario).</b>

							<p style="text-align: justify; font-size: 16px; margin-top: 15px">Al matricularse en la asignatura ${_asignaturamalla.asignatura.nombre} que incluye prácticas preprofesionales se
							compromete a cumplir con todas las obligaciones, responsabilidad y actividades planificadas en
							el marco de la materia, además de tener en cuenta lo siguiente:</p>

        <ol style="padding-left: 20px;font-size: 14px!important;">
                <li style="text-align: justify">La Universidad Estatal de Milagro gestionará la asignación de cupos para prácticas preprofesionales,
                    al momento de asignar un cupo para las prácticas preprofesionales, el estudiante deberá firmar la carta
                    de aceptación la cual se encuentra en el SGA. Una vez que legalice el acta, obligatoriamente el estudiante
                    deberá cumplir con el proceso de prácticas correspondiente.  Si el estudiante obtiene por gestión propia una
                    institución que le brinde una plaza para realizar sus prácticas preprofesionales acorde a su perfil, deberá
                    notificar al departamento de vinculación, adjuntando la carta de aceptación por parte de la institución o
                    empresa dentro del plazo determinado, el cual es antes de la asignación de cupos que realiza la institución.
                </li>
                <li style="text-align: justify">El estudiante que cumpla las actividades de la asignatura de manera satisfactoria,
                    pero no haya cumplido con las prácticas preprofesionales reprobará automáticamente la materia.
                </li>
                <li style="text-align: justify">El estudiante que cumpla satisfactoriamente con las actividades de prácticas preprofesionales,
                    pero no cumpla con las actividades de la asignatura reprobará automáticamente las de prácticas
                    preprofesionales.
                </li>
                <li style="text-align: justify">
                    Si el estudiante no presenta las actividades relacionadas a prácticas preprofesionales dentro de los componentes
                    de gestión que corresponda reprobará automáticamente la asignatura.
                </li>
                <li style="text-align: justify">
                   Los estudiantes que mantengan rubros pendientes deberán cancelar
				   dentro de la tercera y cuarta semana, de lo contrario reprobarán las asignaturas.
                </li>
                <li style="text-align: justify">
                    Los pagos realizados en asignaturas que contiene prácticas preprofesionales no serán reembolsables,
                    con el fin de evitar los inconvenientes causados al retirarse y dejar a otros estudiantes sin cupo.
                </li>
                <li style="text-align: justify">
                    El estudiante se compromete a cumplir con todas las políticas y procedimientos establecidos por la institución
                    o empresa donde realice sus prácticas preprofesionales.
                </li>
                <li style="text-align: justify">
                    La UNEMI se reserva el derecho de cancelar o interrumpir las prácticas preprofesionales en caso de incumplimiento grave por parte del estudiante.
                </li>
            </ol>
        </p><p style="text-align: justify; font-size: 16px">
							<b>Nota:</b> Al hacer clic en el botón "Aceptar", estará confirmando su matrícula en la materia seleccionada.
							De forma automática, se generará un acta de compromiso que contendrá sus datos de aceptación misma que podrá visualizar en el
							móduo "Mis materias"</p>`,
					type: 'warning',
					icon: 'warning',
					width: '1150px',
					showCancelButton: false,
					allowOutsideClick: false,
					confirmButtonColor: '#FA7E23',
					cancelButtonColor: '#d33',
					confirmButtonText: 'Aceptar',
				};
			Swal.fire(mensaje)
		}
	};

	const openPractica = (_materia) => {
		//console.log(_materia);
		eMateria = _materia;
		let fnModal = function () {
			mOpenAsignaturaPractica = true;
		};
		if (ePeriodoMatricula.valida_cupo_materia) {
			loadAjax(
				{
					action: 'loadCupoPractica',
					aData: JSON.stringify(_materia)
				},
				'alumno/matricula/add_remove/pregrado'
			)
				.then((response) => {
					if (response.value.isSuccess) {
						loading.setLoading(false, 'Cargando, espere por favor...');
						eMateria = response.value.data.aData;
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
				loading.setLoading(false, 'Cargando, espere por favor...');
				addNotification({ msg: `Ocurrio un error al cargar los datos`, type: 'error' });
			}
			loading.setLoading(false, 'Cargando, espere por favor...');
		}
	};

	const selectSubject = (_materia) => {
		//console.log("inicio _materia:", _materia);
		//eMateria = _materia;
		const _mispracticas = _materia['mispracticas'];
		//console.log("inicio _mispracticas:", _mispracticas);
		let fnSelect = function () {
			if (!_materia.asignaturamalla.practicas) {
				loading.setLoading(true, 'Cargando, espere por favor...');
				let _materias = [];
				eMateriasAsignadas.forEach((element) => {
					/*let __materia = element.materia;
					__materia['mispracticas'] = {};*/
					_materias.push(element.materia);
				});
				let __materia = _materia;
				__materia['mispracticas'] = {};
				_materias.push(__materia);

				loadAjax(
					{
						action: 'setMateria',
						id: eMatricula.id,
						materia: JSON.stringify(__materia),
						materias: JSON.stringify(_materias)
					},
					'alumno/matricula/add_remove/pregrado'
				)
					.then((response) => {
						loading.setLoading(false, 'Cargando, espere por favor...');
						if (response.value.isSuccess) {
							const mensaje = {
								title: `NOTIFICACIÓN`,
								text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
									ePersona.nombre_completo
								}, se informa que la materia ha sido guardada correctamente`,
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
									closeAsignatura();
									loading.setLoading(true, 'Cargando, espere por favor...');
									loadInitial()
										.then((response) => {
											loading.setLoading(false, 'Cargando, espere por favor...');
										})
										.catch((error) => {
											loading.setLoading(false, 'Cargando, espere por favor...');
											addToast({
												type: 'error',
												header: 'Ocurrio un error',
												body: error.message
											});
											goto('/');
										});
								})
								.catch((error) => {
									loading.setLoading(false, 'Cargando, espere por favor...');
									addNotification({
										msg: error.message,
										type: 'error'
									});
								});
						} else {
							//closeAsignatura();
							loading.setLoading(false, 'Cargando, espere por favor...');
							addNotification({
								msg: response.value.message,
								type: 'error'
							});
						}
					})
					.catch((error) => {
						loading.setLoading(false, 'Cargando, espere por favor...');
						addNotification({
							msg: error.message,
							type: 'error'
						});
					});
			} else {
				loading.setLoading(false, 'Cargando, espere por favor...');
				//console.log("_mispracticas: ", _mispracticas);
				let _eMateria = _materia;
				_eMateria['mispracticas'] = _mispracticas;
				//console.log("_eMateria: ", _eMateria);
				openPractica(_eMateria);
			}
		};
		/**/
		if (
			ePeriodoMatricula.valida_conflicto_horario &&
			eMateriasAsignadas.length > 0 &&
			_materia.tipomateria != 3 && !_materia.validaconflictohorarioalu
		) {
			if (eMateriasAsignadas.length > 0) {
				loading.setLoading(true, 'Cargando, espere por favor...');
				let materias_aux = [];
				eMateriasAsignadas.forEach(function (_ma, index) {
					materias_aux.push(_ma.materia);
				});
				let materia_aux = _materia;
				materia_aux['mispracticas'] = {};
				loadAjax(
					{
						action: 'validConflictoHorario',
						materias: JSON.stringify(materias_aux),
						materia: JSON.stringify(materia_aux)
					},
					'alumno/matricula/add_remove/pregrado'
				)
					.then((response) => {
						if (response.value.isSuccess) {
							loading.setLoading(false, 'Cargando, espere por favor...');

							if (response.value.data.conflicto) {
								addNotification({
									msg: response.value.data.mensaje,
									type: 'warning',
									target: 'newNotificationToast'
								});
							} else {
								if (!_materia.asignaturamalla.practicas) {
									const mensaje = {
										title: `NOTIFICACIÓN`,
										html: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
											ePersona.nombre_completo
										}, <br> <b>¿Está ${
											ePersona.es_mujer ? 'segura' : 'seguro'
										} de adicionar la materia?</b>`,
										type: 'warning',
										icon: 'warning',
										showCancelButton: true,
										allowOutsideClick: false,
										confirmButtonColor: '#3085d6',
										cancelButtonColor: '#d33',
										confirmButtonText: `Sí, estoy ${ePersona.es_mujer ? 'segura' : 'seguro'}`,
										cancelButtonText: 'No, cancelar'
									};
									//console.log(mensaje);
									Swal.fire(mensaje)
										.then((result) => {
											if (result.value) {
												fnSelect();
											}
										})
										.catch((error) => {
											addNotification({
												msg: error.message,
												type: 'error'
											});
										});
								} else {
									fnSelect();
								}
							}
						} else {
							loading.setLoading(false, 'Cargando, espere por favor...');
							addNotification({
								msg: response.value.message,
								type: 'error'
							});
						}
					})
					.catch((error) => {
						loading.setLoading(false, 'Cargando, espere por favor...');
						addNotification({
							msg: error.message,
							type: 'error'
						});
					});
			} else {
				fnSelect();
			}
		} else {
			fnSelect();
		}
	};

	const selectSubjectPractice = (materia, practica) => {
		//console.log(materia);
		//console.log(practica);
		let fnSelect = function () {
			loading.setLoading(true, 'Cargando, espere por favor...');
			let _materias = [];
			eMateriasAsignadas.forEach((element) => {
				_materias.push(element.materia);
			});
			let _materia = materia;
			_materia['mispracticas'] = practica;
			_materias.push(_materia);

			loadAjax(
				{
					action: 'setMateria',
					id: eMatricula.id,
					materia: JSON.stringify(_materia),
					materias: JSON.stringify(_materias)
				},
				'alumno/matricula/add_remove/pregrado'
			)
				.then((response) => {
					loading.setLoading(false, 'Cargando, espere por favor...');
					if (response.value.isSuccess) {
						closeAsignatura();
						closeAsignaturaPractica();
						const mensaje = {
							title: `NOTIFICACIÓN`,
							text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
								ePersona.nombre_completo
							}, se informa que la materia ha sido guardada correctamente`,
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
								loading.setLoading(true, 'Cargando, espere por favor...');
								loadInitial()
									.then((response) => {
										loading.setLoading(false, 'Cargando, espere por favor...');
									})
									.catch((error) => {
										loading.setLoading(false, 'Cargando, espere por favor...');
										addToast({
											type: 'error',
											header: 'Ocurrio un error',
											body: error.message
										});
										goto('/');
									});
							})
							.catch((error) => {
								loading.setLoading(false, 'Cargando, espere por favor...');
								addNotification({
									msg: error.message,
									type: 'error'
								});
							});
					} else {
						//closeAsignatura();
						loading.setLoading(false, 'Cargando, espere por favor...');
						addNotification({
							msg: response.value.message,
							type: 'error'
						});
					}
				})
				.catch((error) => {
					loading.setLoading(false, 'Cargando, espere por favor...');
					addNotification({
						msg: error.message,
						type: 'error'
					});
				});
		};

		if (ePeriodoMatricula.valida_conflicto_horario && eMateriasAsignadas.length > 0) {
			if (eMateriasAsignadas.length > 0) {
				loading.setLoading(true, 'Cargando, espere por favor...');
				let materias_aux = [];
				eMateriasAsignadas.forEach(function (_ma, index) {
					materias_aux.push(_ma.materia);
				});
				let materia_aux = materia;
				materia_aux['mispracticas'] = practica;
				loadAjax(
					{
						action: 'validConflictoHorario',
						materias: JSON.stringify(materias_aux),
						materia: JSON.stringify(materia_aux)
					},
					'alumno/matricula/add_remove/pregrado'
				)
					.then((response) => {
						if (response.value.isSuccess) {
							loading.setLoading(false, 'Cargando, espere por favor...');

							if (response.value.data.conflicto) {
								addNotification({
									msg: response.value.data.mensaje,
									type: 'warning',
									target: 'newNotificationToast'
								});
							} else {
								const mensaje = {
									title: `NOTIFICACIÓN`,
									html: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
										ePersona.nombre_completo
									}, <br> <b>¿Está ${
										ePersona.es_mujer ? 'segura' : 'seguro'
									} de adicionar la materia</b>?`,
									type: 'warning',
									icon: 'warning',
									showCancelButton: true,
									allowOutsideClick: false,
									confirmButtonColor: '#3085d6',
									cancelButtonColor: '#d33',
									confirmButtonText: `Sí, estoy ${ePersona.es_mujer ? 'segura' : 'seguro'}`,
									cancelButtonText: 'No, cancelar'
								};
								//console.log(mensaje);
								Swal.fire(mensaje)
									.then((result) => {
										if (result.value) {
											fnSelect();
										}
									})
									.catch((error) => {
										addNotification({
											msg: error.message,
											type: 'error'
										});
									});
							}
						} else {
							loading.setLoading(false, 'Cargando, espere por favor...');
							addNotification({
								msg: response.value.message,
								type: 'error'
							});
						}
					})
					.catch((error) => {
						loading.setLoading(false, 'Cargando, espere por favor...');
						addNotification({
							msg: error.message,
							type: 'error'
						});
					});
			} else {
				fnSelect();
			}
		} else {
			fnSelect();
		}
	};

	$: {
		//	console.log(aData);
	}
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
							<b>Grupo Socioeconómico:</b>
							<span class="badge bg-info text-white" style="width: 6rem;"
								>{FichaSocioEconomicaINEC}</span
							>
							{#if itinerario > 0}
								<b> <Icon name="gear" /> Itinerario: </b>
								<span class="badge bg-primary smaller">ITINERARIO {itinerario}</span>
							{/if}
							<b> <Icon name="gear" /> Jornada: </b>
							<span class="badge bg-black smaller">{eInscripcion.sesion.nombre}</span>
						</p>
					</div>
				</div>
			</div>

			{#if vaUltimaMatricula}
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
		</div>
		<div class="col-xl-4 col-lg-4 col-md-12 col-12">
			<!--<div class="d-grid gap-2 mt-4">
				<button class="btn btn-info" type="button">CALENDARIO DE MATRICULACIÓN</button>
			</div>-->
			{#if eMatricula.puede_quitar}
				{#if eMatricula.tiene_token}
					<div class="d-grid gap-2 mt-4">
						<button
							class="btn btn-warning"
							type="button"
							on:click|preventDefault={() => openConfirmarEliminarMatricula()}
							><Icon name="code-slash" /> INGRESAR CÓDIGO DE CONFIRMACIÓN</button
						>
					</div>
				{:else}
					<div class="d-grid gap-2 mt-4">
						<button
							class="btn btn-danger"
							type="button"
							on:click|preventDefault={() => deleteMatricula()}
							><Icon name="trash" /> ELIMINAR MATRICULA</button
						>
					</div>
				{/if}
				{#if eMatricula.puede_reenviar_token}
					<div class="d-grid gap-2 mt-4">
						<button
							class="btn btn-success"
							type="button"
							on:click|preventDefault={() => reenviarDeleteMatricula()}
							><Icon name="mailbox" /> REENVIAR ({eMatricula.contador_reenviar_email_token}/6)</button
						>
					</div>
				{/if}
			{/if}
			{#if ePeriodoMatricula.valida_materias_maxima && eMateriasAsignadas.length > num_materias_maxima}
				<div class="pt-2">
					<div class="alert alert-danger">
						<h4 class="alert-heading">
							Máximo de materias {num_materias_maxima}
						</h4>
						{ePersona.es_mujer ? 'Estimada' : 'Estimado'}
						{ePersona.nombre_completo}, ha llegado al máximo de materias seleccionadas por
						matrícula.
					</div>
				</div>
			{/if}
			{#if eMatricula.total_pagado_rubro > 0}
				<div class="p-0 mt-4 text-center">
					<div class="alert alert-success">
						<h4 class="alert-heading m-0">
							<i class="fa fa-warning" /> Tiene rubros pagados: $ {converToDecimal(
								eMatricula.total_pagado_rubro
							)}
						</h4>
					</div>
				</div>
			{/if}
			{#if eMatricula.total_saldo_rubro > 0}
				<div class="p-0 mt-4 text-center">
					<div class="alert alert-danger">
						<h4 class="alert-heading m-0">
							<i class="fa fa-warning" /> Tiene rubros pendientes: $ {converToDecimal(
								eMatricula.total_saldo_rubro
							)}
						</h4>
					</div>
				</div>
			{/if}
			{#if eMatricula.total_pagado_rubro > 0 || eMatricula.total_saldo_rubro > 0}
				<div class="d-grid gap-2 mt-4 ">
					<button
						class="btn btn-warning"
						type="button"
						on:click={() => toggleModalDetalleValores(DetalleValores)}
						>Detalle de los valores generados en la matriculación</button
					>
				</div>
			{/if}
		</div>
	</div>
	<div class="row align-items-center mt-2 align-items-center">
		<div class="col-xl-12 col-lg-12 col-md-12 col-12">
			<div class="card">
				<!-- card header  -->
				<div class="card-header">
					<h4 class="mb-1">Asignaturas de su matrícula</h4>
					<!--<p class="mb-0">Add <code class="highlighter-rouge">.table-sm</code> to make tables more compact by cutting cell padding in half.</p>-->
				</div>
				<!-- table  -->
				<div class="table-responsive">
					<table class="table table-bordered table-sm text-nowrap mb-0">
						<thead>
							<tr>
								<th />
								<th class="text-center">Asignatura</th>
								<th class="text-center">Paralelo</th>
								<th class="text-center">Asignada</th>
								<th class="text-center">Inicio</th>
								<th class="text-center">Fin</th>
								<th class="text-center">Horas</th>
								<th class="text-center">Créditos</th>
								<!--<th class="text-center">Nota</th>
								<th class="text-center">Asistencia</th>-->
							</tr>
						</thead>
						<tbody>
							{#each eMateriasAsignadas as eMateriaAsignada}
								<tr>
									<td class="align-middle text-center fs-6 text-muted">
										{#if eMatricula}
											{#if eMatricula.tiene_token}
												<span class="badge rounded-pill bg-warning text-dark"
													>Pendiente de eliminar matrícula</span
												>
											{:else if eMateriaAsignada.puede_quitar}
												{#if !eMateriaAsignada.tiene_token}
													<button
														type="button"
														class="btn btn-danger btn-sm"
														on:click|preventDefault={() => removeMateria(eMateriaAsignada)}
														><Icon name="trash2" /> REMOVER</button
													>
												{:else}
													<button
														type="button"
														class="btn btn-warning btn-sm"
														on:click|preventDefault={() =>
															openConfirmarRemoveMateria(eMateriaAsignada)}
														><Icon name="code-slash" /> INGRESAR CÓDIGO</button
													>
												{/if}
												{#if eMateriaAsignada.puede_reenviar_token}
													<button
														type="button"
														class="btn btn-success btn-sm"
														on:click|preventDefault={() => reenviarRemoveMateria(eMateriaAsignada)}
														><Icon name="mailbox" /> REENVIAR ({eMateriaAsignada.contador_reenviar_email_token}/6)</button
													>
												{/if}
											{/if}
										{/if}
									</td>
									<td class="align-middle fs-6 text-muted text-break">
										<div class="d-flex align-items-center">
											<div>
												<span class="badge bg-light text-success"
													>{eMateriaAsignada.materia.asignaturamalla.nivelmalla.display}</span
												>
											</div>
											<div class="ms-3 lh-1">
												<h6 class="mb-1">
													{eMateriaAsignada.materia.asignaturamalla.asignatura.display}
												</h6>
											</div>
										</div>
										<div class="">
											{#if eMateriaAsignada.materia.asignaturamalla.itinerario}
												<span class="badge bg-warning me-2"
													>ITINERARIO {eMateriaAsignada.materia.asignaturamalla.itinerario}</span
												>
											{/if}
											{#if eMateriaAsignada.retirado}
												<span
													id={`Tooltip_retirado_${eMateriaAsignada.id}`}
													class="badge bg-warning me-2">RETIRADO</span
												>
												<Tooltip target={`Tooltip_retirado_${eMateriaAsignada.id}`} placement="top"
													>SE RETIRO DE LA MATERIA</Tooltip
												>
											{/if}
											{#if eMateriaAsignada.convalidada || eMateriaAsignada.homologada}
												<span class="badge bg-success me-2">HOMOLOGADA</span>
											{/if}
											{#if !eMateriaAsignada.existe_en_malla}
												<span class="badge bg-dark me-2">NO CONSTA EN MALLA</span>
											{/if}
											{#if eMateriaAsignada.valida_pararecord}
												<span
													id={`Tooltip_valida_pararecord_${eMateriaAsignada.id}`}
													class="badge bg-info me-2">VALIDA</span
												>
												<Tooltip
													target={`Tooltip_valida_pararecord_${eMateriaAsignada.id}`}
													placement="top">PASA AL RECORD ACADÉMICO</Tooltip
												>
											{:else}
												<span
													id={`Tooltip_no_valida_pararecord_${eMateriaAsignada.id}`}
													class="badge bg-danger me-2">NO VALIDA</span
												>
												<Tooltip
													target={`Tooltip_no_valida_pararecord_${eMateriaAsignada.id}`}
													placement="top">NO PASA AL RECORD ACADÉMICO</Tooltip
												>
											{/if}
											{#if eMateriaAsignada.aprobada}
												<span class="badge bg-success me-2">{eMateriaAsignada.estado.nombre}</span>
											{:else}
												<span class="badge bg-secondary me-2">{eMateriaAsignada.estado.nombre}</span
												>
											{/if}
											{#if eMateriaAsignada.evaluar}
												<span
													id={`Tooltip_evaluar_${eMateriaAsignada.id}`}
													class="badge bg-warning me-2">AE</span
												>
												<Tooltip target={`Tooltip_evaluar_${eMateriaAsignada.id}`} placement="top"
													>Autorizado a evaluar</Tooltip
												>
											{/if}
											<!--{#if eMateriaAsignada.evaluada}
												<span
													id={`Tooltip_evaluada_${eMateriaAsignada.id}`}
													class="badge bg-warning me-2">EVALUÓ</span
												>
												<Tooltip target={`Tooltip_evaluada_${eMateriaAsignada.id}`} placement="top"
													>Realizo la evaluación</Tooltip
												>
											{/if}-->
											{#if !eMateriaAsignada.pertenece_malla}
												<span
													id={`Tooltip_pertenece_malla_${eMateriaAsignada.id}`}
													class="badge bg-danger me-2">FUERA DE MALLA</span
												>
												<Tooltip
													target={`Tooltip_pertenece_malla_${eMateriaAsignada.id}`}
													placement="top">Esta materia no pertenece a su malla</Tooltip
												>
											{/if}
											{#if eMateriaAsignada.materia.cerrado}
												<span class="badge bg-danger me-2"
													>CERRADA {eMateriaAsignada.fechacierre}</span
												>
											{/if}
											{#if eMateriaAsignada.practica}
												<span class="badge bg-info text-dark me-2">{eMateriaAsignada.practica}</span
												>
											{/if}
											{#if eMateriaAsignada.sinasistencia}
												<span
													id={`Tooltip_sinasistencia_${eMateriaAsignada.id}`}
													class="badge bg-primary me-2">SA</span
												>
												<Tooltip
													target={`Tooltip_sinasistencia_${eMateriaAsignada.id}`}
													placement="top">SIN ASISTENCIA</Tooltip
												>
											{:else}
												<span
													id={`Tooltip_sinasistencia_${eMateriaAsignada.id}`}
													class="badge bg-primary me-2">CA</span
												>
												<Tooltip
													target={`Tooltip_sinasistencia_${eMateriaAsignada.id}`}
													placement="top">CON ASISTENCIA</Tooltip
												>
											{/if}
											{#if eMateriaAsignada.totalrecordasignatura >= 2}
												<span
													id={`Tooltip_totalrecordasignatura_${eMateriaAsignada.id}`}
													class="badge bg-warning me-2"
													>{eMateriaAsignada.totalrecordasignatura + 1} MAT.</span
												>
												<Tooltip
													target={`Tooltip_totalrecordasignatura_${eMateriaAsignada.id}`}
													placement="top"
													>{eMateriaAsignada.totalrecordasignatura + 1 == 2
														? 'Segunda'
														: eMateriaAsignada.totalrecordasignatura + 1 == 3
														? 'Tercera'
														: eMateriaAsignada.totalrecordasignatura + 1 == 4
														? 'Cuarta'
														: eMateriaAsignada.totalrecordasignatura + 1 == 5
														? 'Quinta'
														: eMateriaAsignada.totalrecordasignatura + 1} matrícula</Tooltip
												>
											{/if}
										</div>
									</td>
									<td class="align-middle text-center fs-6 text-muted"
										>{eMateriaAsignada.materia.paralelomateria.nombre}</td
									>
									<td class="align-middle text-center fs-6 text-muted"
										>{eMateriaAsignada.fechaasignacion}</td
									>
									<td class="align-middle text-center fs-6 text-muted"
										>{eMateriaAsignada.materia.inicio}</td
									>
									<td class="align-middle text-center fs-6 text-muted"
										>{eMateriaAsignada.materia.fin}</td
									>
									<td class="align-middle text-center fs-6 text-muted">
										<ul class="list-group list-group-flush">
											<li class="list-group-item px-0 pb-3 pt-0">
												<div class="d-flex justify-content-between">
													<div class="d-flex">Total asignatura</div>
													<div class="">{eMateriaAsignada.materia.asignaturamalla.horas}</div>
												</div>
											</li>
											<li class="list-group-item px-0 pb-3 pt-0">
												<div class="d-flex justify-content-between">
													<div class="d-flex">Semanales</div>
													<div class="">
														{eMateriaAsignada.materia.asignaturamalla.horas_semanal}
													</div>
												</div>
											</li>
											<li class="list-group-item px-0 pb-3 pt-0">
												<div class="d-flex justify-content-between">
													<div class="d-flex">Contacto docente</div>
													<div class="">
														{converToDecimal(
															eMateriaAsignada.materia.asignaturamalla.horasacdsemanal
														)}
													</div>
												</div>
											</li>
										</ul>
									</td>
									<td class="align-middle text-center fs-6 text-muted"
										>{converToDecimal(eMateriaAsignada.materia.creditos)}</td
									>
									<!--<td class="align-middle text-center fs-6 text-muted">
										{#if !eMateriaAsignada.convalidada && !eMateriaAsignada.homologada}
											{converToDecimal(eMateriaAsignada.notafinal)}
										{/if}
									</td>
									<td class="align-middle text-center fs-6 text-muted">
										{#if !eMateriaAsignada.convalidada && !eMateriaAsignada.homologada}
											{eMateriaAsignada.asistenciafinal}%
										{/if}
									</td>-->
								</tr>
							{/each}
						</tbody>
						<tfoot>
							<tr>
								<td colspan="6" />
								<td class="align-middle text-center fs-6 text-muted">
									<ul class="list-group list-group-flush">
										<li class="list-group-item px-0 pb-3 pt-0">
											<div class="d-flex justify-content-between">
												<div class="d-flex">Total asignatura</div>
												<div class="">{eMatricula.totalhoras}</div>
											</div>
										</li>
										<li class="list-group-item px-0 pb-3 pt-0">
											<div class="d-flex justify-content-between">
												<div class="d-flex">Semanales</div>
												<div class="">{eMatricula.total_horas_semanales}</div>
											</div>
										</li>
										<li class="list-group-item px-0 pb-3 pt-0">
											<div class="d-flex justify-content-between">
												<div class="d-flex">Contacto docente</div>
												<div class="">{eMatricula.total_horas_contacto_docente}</div>
											</div>
										</li>
									</ul>
								</td>
								<td class="align-middle text-center fs-6 text-muted">{eMatricula.totalcreditos}</td>
								<!--<td class="align-middle text-center fs-6 text-muted">{eMatricula.promedionotas}</td>
								<td class="align-middle text-center fs-6 text-muted"
									>{eMatricula.promedioasistencias}%</td
								>-->
							</tr>
						</tfoot>
					</table>
				</div>
			</div>
		</div>
	</div>
	{#if eMatricula.puede_agregar}
		<div class="row align-items-center mt-6 align-items-center">
			<div class="col-xl-12 col-lg-12 col-md-12 col-12">
				<h2 class="display-6">Materias de malla (pendientes y reprobadas)</h2>
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
										href={'#'}
										class="nav-link actionSearchLevel"
										on:click|preventDefault={(event) => actionSearchLevel(event, 'pendiente')}
										><Icon name="circle" /> Pendientes</a
									>
								</li>
								<li class="nav-item">
									<a
										href={'#'}
										class="nav-link actionSearchLevel"
										on:click|preventDefault={(event) => actionSearchLevel(event, 'aprobada')}
										><Icon name="circle" /> Aprobadas</a
									>
								</li>
								<li class="nav-item">
									<a
										href={'#'}
										class="nav-link actionSearchLevel"
										on:click|preventDefault={(event) => actionSearchLevel(event, 'reprobada')}
										><Icon name="circle" /> Reprobadas</a
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
											href={'#'}
											class="nav-link actionSearchLevel"
											on:click|preventDefault={(event) => actionSearchLevel(event, nm.nombre)}
											><Icon name="circle" /> {nm.nombre}</a
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
												href={'#'}
												class="nav-link actionSearchLevel"
												on:click|preventDefault={(event) =>
													actionSearchLevel(event, `ITINERARIO ${iti}`)}
												><Icon name="circle" /> ITINERARIO {iti}</a
											>
										</li>
									{/each}
								{/if}
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
						id="searchSubjects"
						bind:value={search}
						on:keyup={actionSearchKeyPress}
						placeholder="Buscar ..."
					/>
				</form>
				{#if eAsignaturasMalla.length > 0}
					{#each eNivelesMallaOfertada as eNiveleMallaOfertada}
						<!--eNiveleMallaOfertada_ID: {eNiveleMallaOfertada.idm}-->
						<div class="row align-items-center">
							<div class="col-xl-12 col-lg-12 col-md-12 col-12">
								<h4
									class="hr_nivel_malla mb-6"
									style="width:100%; text-align:left; border-bottom: 1px solid #198754; line-height:0.1em; margin:10px 0 20px;"
								>
									<span
										style="padding:0 10px; background: #198754; padding: 5px 10px; color: #FFFFFF; border-radius: 5px"
										>{eNiveleMallaOfertada.nombre}</span
									>
								</h4>
								<div
									class="row row-cols-1 row-cols-sm-2 row-cols-md-2 row-cols-lg-2 row-cols-xl-2 row-cols-xxl-3 mb-3 text-center"
								>
									{#each eAsignaturasMalla as am}
										<!--AsignaturaMalla_NivelMalla_ID:{am.nivelmalla.idm}-->
										{#if eNiveleMallaOfertada.idm == am.nivelmalla.idm && am.puede_ver_horario}
											<div class="col mb-4 cardSubjects valueYesSearch">
												<div class="card rounded-3 shadow-sm h-100 card-hover">
													{#if am.va_num_matricula === ePeriodoMatricula.num_matriculas && am.estado === 2}
														<span
															class="position-absolute top-0 end-0 badge rounded-pill bg-danger"
														>
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
													<div
														class="card-header py-1"
														style="height: 5.5rem; font-size: 13px; font-weight: bold; overflow: hidden; display: flex; text-overflow: ellipsis; width: 100%; align-items: center; justify-content: center;"
													>
														<div class="my-0 text-truncate-line-2 text-inherit">
															{am.asignatura.nombre}
														</div>
													</div>
													<div class="card-body">
														<h6 class="card-title pricing-card-title card-level-academic">
															{am.nivelmalla.nombre}
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
																>ITINERARIO {am.itinerario}</span
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
																	class="d-flex justify-content-between border-bottom pe-1 ps-2 py-1"
																>
																	<span class="fs-6 text-muted">Total asignatura</span>
																	<span class="fs-6">
																		<h6 class="mb-0">{am.horas}</h6>
																	</span>
																</div>
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
																		<h6 class="mb-0">{am.horasacdsemanal}</h6>
																	</span>
																</div>
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
																<!--<div class="pe-1 pt-2 pb-2 ps-2 py-1">
																<h5 class="mb-0 fs-6 text-muted">
																	No registra ninguna precedencia
																</h5>
															</div>-->
															{/if}
														</ul>
													</div>
													<div class="card-footer">
														<div class="row align-items-center g-0">
															{#if !eMatricula.tiene_token && am.puede_ver_horario == 1}
																<button
																	type="button"
																	itinerario="itinerario_{am.itinerario}"
																	id="btn_aplicar_{am.id}"
																	class="w-100 btn btn-lg btn-info"
																	on:click={openAsignatura(am)}><Icon name="plus" /> ASIGNAR</button
																>
															{:else}
																<p class="text-info w-100">UNEMI</p>
															{/if}
														</div>
													</div>
												</div>
											</div>
										{/if}
									{/each}
								</div>
							</div>
						</div>
					{/each}
				{:else}
					<div class="pt-2">
						<div class="alert alert-warning">
							<h4 class="alert-heading m-0">
								NO HAY DISPONIBLE ASIGNATURAS PENDIENTES O REPROBADAS
							</h4>
						</div>
					</div>
				{/if}
			</div>
		</div>
	{/if}
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
				{eAsignaturaMalla.asignatura.nombre} [{eAsignaturaMalla.nivelmalla.nombre}]
			</h4>
		</ModalHeader>
		<ModalBody>
			{#if eAsignaturaMalla.eMaterias && eAsignaturaMalla.eMaterias.length === 0}
				<div class="row">
					<div class="col-12 text-center">
						<div class="alert alert-warning">
							<h4 class="alert-heading">Importante!</h4>
							<p class="alert-body">
								MATERIA NO ESTÁ ABIERTA, CONTACTAR Al BALCÓN DE SERVICIOS
							</p>
						</div>
					</div>
				</div>
			{:else}
				<div class="row">
					<div class="col-12 text-left">
						<div class="alert alert-warning">
							<h3 class="alert-heading">Importante!</h3>
							<p class="alert-body fs-4">
								{ePersona.es_mujer ? 'Estimada' : 'Estimado'} estudiante recuerde que debe seleccionar
								el mismo paralelo para garantizar la disponiblidad de cupo.
							</p>
						</div>
					</div>
				</div>
				<div
					class="row row-cols-1 row-cols-sm-1 row-cols-md-2 row-cols-lg-2 row-cols-xl-2 row-cols-xxl-3 text-center"
				>
					{#each eAsignaturaMalla.eMaterias as eM}
						<div class="col mb-4">
							<div
								class="card rounded-3 h-100 border border-2 shadow-none card-dashed-hover text-center"
							>
								<div class="card-header">
									<div class="text-muted fs-6">
										{#if eM.coordinacion.alias}
											<span id={`Tooltip_alias_facultad_${eM.id}`}>{eM.coordinacion.alias}</span>
											/ &nbsp;
											<Tooltip target={`Tooltip_alias_facultad_${eM.id}`} placement="top"
												>{eM.coordinacion.nombre}</Tooltip
											>
										{:else if eM.coordinacion}
											{eM.coordinacion.nombre} /&nbsp;
										{/if}
										{eM.asignaturamalla.malla.carrera.nombre}
									</div>
									<div class="text-muted fs-6">
										{#if eM.tipomateria === 1}
											<span class="badge rounded-pill bg-info bg-info" id={`Tooltip_tipomateria_${eM.id}`}>{eM.tipomateria_display}</span>
											<Tooltip target={`Tooltip_tipomateria_${eM.id}`} placement="top">Tipo de impartición de clase</Tooltip>
										{:else if eM.tipomateria === 2}
											<span class="badge rounded-pill bg-secondary" id={`Tooltip_tipomateria_${eM.id}`}>{eM.tipomateria_display}</span>
											<Tooltip target={`Tooltip_tipomateria_${eM.id}`} placement="top">Tipo de impartición de clase</Tooltip>
										{:else if eM.tipomateria === 3}
											<span class="badge rounded-pill bg-success" id={`Tooltip_tipomateria_${eM.id}`}>{eM.tipomateria_display}</span>
											<Tooltip target={`Tooltip_tipomateria_${eM.id}`} placement="top">Tipo de impartición de clase</Tooltip>
										{:else}
											<span class="badge rounded-pill bg-light text-dark" id={`Tooltip_tipomateria_${eM.id}`}>{eM.tipomateria_display}</span>
											<Tooltip target={`Tooltip_tipomateria_${eM.id}`} placement="top">Tipo de impartición de clase</Tooltip>
										{/if}
										{#if eM.asignaturamalla.practicas}
											&nbsp;/ <span class="badge rounded-pill bg-warning" id={`Tooltip_tp_${eM.id}`}
												>TP</span
											>
											<Tooltip target={`Tooltip_tp_${eM.id}`} placement="top"
												>Teórica y Práctica</Tooltip
											>
										{:else if !eM.asignaturamalla.practicas}
											&nbsp;/ <span class="badge rounded-pill bg-warning" id={`Tooltip_t_${eM.id}`}
												>T</span
											>
											<Tooltip target={`Tooltip_t_${eM.id}`} placement="top">Teórica</Tooltip>
										{/if}
									</div>
								</div>
								<div class="card-body">
									<div class="text-center">
										<span
											class="badge rounded-pill fs-3 bg-primary"
											id={`Tooltip_paralelo_${eM.id}`}>{eM.paralelomateria.nombre}</span
										>
										<Tooltip target={`Tooltip_paralelo_${eM.id}`} placement="top">Paralelo</Tooltip>
										{#if eM.tipomateria != 3}
											<h5 class="card-title mb-0 mt-2 fs-6">{eM.session}</h5>
										{/if}
										<p class="card-text mb-0 fs-6 text-muted">{eM.inicio} - {eM.fin}</p>
									</div>
									{#if ePeriodoMatricula.ver_cupo_materia}
										<div class="d-flex justify-content-between border-bottom py-1 mt-1 fs-6">
											<span>Cupo</span>
											<span class="text-dark">{eM.cupo}</span>
										</div>
										<div class="d-flex justify-content-between border-bottom py-1 mt-1 fs-6">
											<span>Disponibles</span>
											<span class="text-dark">{eM.disponibles}</span>
										</div>
									{/if}
									{#if ePeriodoMatricula.ver_horario_materia && eM.tipomateria != 3}
										<h4 class="fw-bold mt-4 mb-4">Horario de clases:</h4>
										<ul class="list-unstyled mb-0">
											{#if eM.horarios.length > 0}
												{#each eM.horarios as h}
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
									{#if eM.puede_agregar}
										{#if eM.tipomateria === 3}
											{#if ePeriodoMatricula.valida_cupo_materia}
												{#if eM.disponibles > 0}
													<button
														type="button"
														class="w-100 btn btn-lg btn-success"
														on:click|preventDefault={() => selectSubject(eM)}
														><Icon name="check-all" /> SELECCIONAR</button
													>
												{:else}
													<p class="text-info w-100">NO EXISTE DISPONIBILIDAD DE CUPO</p>
												{/if}
											{:else}
												<button
													type="button"
													class="w-100 btn btn-lg btn-success"
													on:click|preventDefault={() => selectSubject(eM)}
													><Icon name="check-all" /> SELECCIONAR</button
												>
											{/if}
										{:else if ePeriodoMatricula.valida_horario_materia}
											{#if eM.horarios.length > 0}
												{#if ePeriodoMatricula.valida_cupo_materia}
													{#if eM.disponibles > 0}
														<button
															type="button"
															class="w-100 btn btn-lg btn-success"
															on:click|preventDefault={() => selectSubject(eM)}
															><Icon name="check-all" /> SELECCIONAR</button
														>
													{:else}
														<p class="text-info w-100">NO EXISTE DISPONIBILIDAD DE CUPO</p>
													{/if}
												{:else}
													<button
														type="button"
														class="w-100 btn btn-lg btn-success"
														on:click|preventDefault={() => selectSubject(eM)}
														><Icon name="check-all" /> SELECCIONAR</button
													>
												{/if}
											{:else}
												<p class="text-info w-100">UNEMI</p>
											{/if}
										{:else if ePeriodoMatricula.valida_cupo_materia}
											{#if eM.disponibles > 0}
												<button
													type="button"
													class="w-100 btn btn-lg btn-success"
													on:click|preventDefault={() => selectSubject(eM)}
													><Icon name="check-all" /> SELECCIONAR</button
												>
											{:else}
												<p class="text-info w-100">NO EXISTE DISPONIBILIDAD DE CUPO</p>
											{/if}
										{:else}
											<button
												type="button"
												class="w-100 btn btn-lg btn-success"
												on:click|preventDefault={() => selectSubject(eM)}
												><Icon name="check-all" /> SELECCIONAR</button
											>
										{/if}
									{:else}
										<p class="text-info w-100">UNEMI</p>
									{/if}
								</div>
							</div>
						</div>
					{/each}
				</div>
			{/if}
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
				{eAsignaturaMalla.asignatura.nombre} [{eAsignaturaMalla.nivelmalla.nombre}]
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
				class="row row-cols-1 row-cols-sm-1 row-cols-md-1 row-cols-lg-2 row-cols-xl-2 row-cols-xxl-3 text-center"
			>
					{#each eMateria.mispracticas as p}
						<div class="col mb-4">
							<div
								class="card rounded-3 h-100 border border-2 shadow-none card-dashed-hover text-center"
							>
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
														on:click|preventDefault={() => selectSubjectPractice(eMateria, p)}
														>SELECCIONAR</button
													>
												{:else}
													<p class="text-info w-100">NO EXISTE DISPONIBILIDAD DE CUPO</p>
												{/if}
											{:else}
												<button
													type="button"
													class="w-100 btn btn-lg btn-success"
													on:click|preventDefault={() => selectSubjectPractice(eMateria, p)}
													>SELECCIONAR</button
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
												on:click|preventDefault={() => selectSubjectPractice(eMateria, p)}
												>SELECCIONAR</button
											>
										{:else}
											<p class="text-info w-100">NO EXISTE DISPONIBILIDAD DE CUPO</p>
										{/if}
									{:else}
										<button
											type="button"
											class="w-100 btn btn-lg btn-success"
											on:click|preventDefault={() => selectSubjectPractice(eMateria, p)}
											>SELECCIONAR</button
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
		isOpen={mOpenEliminarConfirmarMatricula}
		toggle={mToggleEliminarConfirmarMatricula}
		size="md"
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
		backdrop="static"
	>
		<ModalHeader toggle={mToggleEliminarConfirmarMatricula}>
			<h4>
				<span>Confirmación - Eliminación de matrícula </span>
			</h4>
		</ModalHeader>
		<ModalBody>
			<div class="card  mb-3 mb-lg-0">
				<!-- Card Header -->
				<div class="card-header">
					<h3 class="mb-0">Código de confirmación</h3>
				</div>
				<!-- Card Body -->
				<div class="card-body">
					<div class="d-inline-flex ">
						<!-- Form -->
						<form class="row " id="cardpayment">
							<div class="mb-3 col-md-2">
								<input
									type="text"
									class="cc-inputmask form-control"
									style="padding: .75rem .75rem; text-align: center;"
									name="confirm_digit_remove_enrollment_1"
									id="confirm_digit_remove_enrollment_1"
									placeholder="X"
									maxlength="1"
									bind:value={confirm_digit_remove_enrollment_1}
								/>
							</div>
							<div class="mb-3 col-md-2">
								<input
									type="text"
									class="cc-inputmask form-control"
									style="padding: .75rem .75rem; text-align: center;"
									name="confirm_digit_remove_enrollment_2"
									id="confirm_digit_remove_enrollment_2"
									placeholder="X"
									maxlength="1"
									bind:value={confirm_digit_remove_enrollment_2}
								/>
							</div>
							<div class="mb-3 col-md-2">
								<input
									type="text"
									class="cc-inputmask form-control"
									style="padding: .75rem .75rem; text-align: center;"
									name="confirm_digit_remove_enrollment_3"
									id="confirm_digit_remove_enrollment_3"
									placeholder="X"
									maxlength="1"
									bind:value={confirm_digit_remove_enrollment_3}
								/>
							</div>
							<div class="mb-3 col-md-2">
								<input
									type="text"
									class="cc-inputmask form-control"
									style="padding: .75rem .75rem; text-align: center;"
									name="confirm_digit_remove_enrollment_4"
									id="confirm_digit_remove_enrollment_4"
									placeholder="X"
									maxlength="1"
									bind:value={confirm_digit_remove_enrollment_4}
								/>
							</div>
							<div class="mb-3 col-md-2">
								<input
									type="text"
									class="cc-inputmask form-control"
									style="padding: .75rem .75rem; text-align: center;"
									name="confirm_digit_remove_enrollment_5"
									id="confirm_digit_remove_enrollment_5"
									placeholder="X"
									maxlength="1"
									bind:value={confirm_digit_remove_enrollment_5}
								/>
							</div>
							<div class="mb-3 col-md-2">
								<input
									type="text"
									class="cc-inputmask form-control"
									style="padding: .75rem .75rem; text-align: center;"
									name="confirm_digit_remove_enrollment_6"
									id="confirm_digit_remove_enrollment_6"
									placeholder="X"
									maxlength="1"
									bind:value={confirm_digit_remove_enrollment_6}
								/>
							</div>
						</form>
					</div>
				</div>
			</div>
			<div class="row mt-4">
				<div class="col-12">
					<p>
						{ePersona.es_mujer ? 'Estimada' : 'Estimado'}
						{ePersona.nombre_completo}, al confirmar usted estaría eliminando su matrícula.
					</p>
					<h4 class="text-center">
						¿Está {ePersona.es_mujer ? 'segura' : 'seguro'} de eliminar matrícula?
					</h4>
				</div>
			</div>
			<div class="row">
				<div class="col-12 text-center">
					<button
						class="btn btn-warning"
						on:click|preventDefault={() => confirmarEliminarMatricula()}
						>Si, estoy {ePersona.es_mujer ? 'segura' : 'seguro'}</button
					>
					<button
						class="btn btn-success"
						on:click|preventDefault={() => cancelarEliminarMatricula()}
						>No, conversar matrícula</button
					>
				</div>
			</div>
		</ModalBody>
		<ModalFooter>
			<Button color="primary" on:click={mToggleEliminarConfirmarMatricula}>Cerrar</Button>
		</ModalFooter>
	</Modal>

	<Modal
		isOpen={mOpenEliminarConfirmarMateria}
		toggle={mToggleEliminarConfirmarMateria}
		size="md"
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
		backdrop="static"
	>
		<ModalHeader toggle={mToggleEliminarConfirmarMatricula}>
			<h4>
				<span>Confirmación - Quitar/Remover materia </span>
			</h4>
		</ModalHeader>
		<ModalBody>
			<div class="card  mb-3 mb-lg-0">
				<!-- Card Header -->
				<div class="card-header">
					<h3 class="mb-0">Código de confirmación</h3>
					<h6 class="text-muted">{eMateriaAsignadaRemove.materia.asignatura.nombre}</h6>
				</div>
				<!-- Card Body -->
				<div class="card-body">
					<div class="d-inline-flex ">
						<!-- Form -->
						<form class="row " id="cardpayment">
							<div class="mb-3 col-md-2">
								<input
									type="text"
									class="cc-inputmask form-control"
									style="padding: .75rem .75rem; text-align: center;"
									name="confirm_digit_remove_course_1"
									id="confirm_digit_remove_course_1"
									placeholder="X"
									maxlength="1"
									bind:value={confirm_digit_remove_course_1}
								/>
							</div>
							<div class="mb-3 col-md-2">
								<input
									type="text"
									class="cc-inputmask form-control"
									style="padding: .75rem .75rem; text-align: center;"
									name="confirm_digit_remove_course_2"
									id="confirm_digit_remove_course_2"
									placeholder="X"
									maxlength="1"
									bind:value={confirm_digit_remove_course_2}
								/>
							</div>
							<div class="mb-3 col-md-2">
								<input
									type="text"
									class="cc-inputmask form-control"
									style="padding: .75rem .75rem; text-align: center;"
									name="confirm_digit_remove_course_3"
									id="confirm_digit_remove_course_3"
									placeholder="X"
									maxlength="1"
									bind:value={confirm_digit_remove_course_3}
								/>
							</div>
							<div class="mb-3 col-md-2">
								<input
									type="text"
									class="cc-inputmask form-control"
									style="padding: .75rem .75rem; text-align: center;"
									name="confirm_digit_remove_course_4"
									id="confirm_digit_remove_course_4"
									placeholder="X"
									maxlength="1"
									bind:value={confirm_digit_remove_course_4}
								/>
							</div>
							<div class="mb-3 col-md-2">
								<input
									type="text"
									class="cc-inputmask form-control"
									style="padding: .75rem .75rem; text-align: center;"
									name="confirm_digit_remove_course_5"
									id="confirm_digit_remove_course_5"
									placeholder="X"
									maxlength="1"
									bind:value={confirm_digit_remove_course_5}
								/>
							</div>
							<div class="mb-3 col-md-2">
								<input
									type="text"
									class="cc-inputmask form-control"
									style="padding: .75rem .75rem; text-align: center;"
									name="confirm_digit_remove_course_6"
									id="confirm_digit_remove_course_6"
									placeholder="X"
									maxlength="1"
									bind:value={confirm_digit_remove_course_6}
								/>
							</div>
						</form>
					</div>
				</div>
			</div>
			<div class="row mt-4">
				<div class="col-12">
					<p>
						{ePersona.es_mujer ? 'Estimada' : 'Estimado'}
						{ePersona.nombre_completo}, al confirmar usted estaría quitando/removiendo la asignatura
						<strong>{eMateriaAsignadaRemove.materia.asignatura.nombre}</strong> de su matrícula.
					</p>
					<h4 class="text-center">
						¿Está {ePersona.es_mujer ? 'segura' : 'seguro'} quitar/remover la asignatura?
					</h4>
				</div>
			</div>
			<div class="row">
				<div class="col-12 text-center">
					<button class="btn btn-warning" on:click|preventDefault={() => confirmarRemoveMateria()}
						>Si, estoy {ePersona.es_mujer ? 'segura' : 'seguro'}</button
					>
					<button class="btn btn-success" on:click|preventDefault={() => cancelarRemoveMateria()}
						>No, conversar materia</button
					>
				</div>
			</div>
		</ModalBody>
		<ModalFooter>
			<Button color="primary" on:click={mToggleEliminarConfirmarMateria}>Cerrar</Button>
		</ModalFooter>
	</Modal>
	{#if showModalGenerico}
		<ModalGenerico
			mToggle={mToggleModalGenerico}
			mOpen={showModalGenerico}
			modalContent={modalGenericoContent}
			title={modalTitle}
			aData={aDataModal}
			size="xl"
		/>
	{/if}
{:else}
	<div
		class="m-0 vh-100 row justify-content-center align-items-center"
		style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 1000; display: flex; flex-direction: column; align-items: center; justify-content: center;"
	>
		<div class="col-auto text-center">
			<Spinner color="primary" type="border" style="width: 3rem; height: 3rem;" />
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
		font-size: 16px;
		/* Cambiar el tamaño de la tipografia */
		text-transform: uppercase;
		/* Texto en mayusculas */
		font-weight: bold;
		/* Fuente en negrita o bold */
		color: #ffffff;
		/* Color del texto */
		border-radius: 5px;
		/* Borde del boton */
		letter-spacing: 2px;
		/* Espacio entre letras */
		background: rgb(25, 135, 84) none repeat scroll 0% 0%;
		/* Color de fondo */
		padding: 0.5rem 0.875rem;
		/* Relleno del boton */
		position: fixed;
		bottom: 60px;
		right: 70px;
		transition: all 300ms ease 0ms;
		box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.1);
		z-index: 99;
	}

	.btn-flotante:hover {
		background-color: #2c2fa5;
		/* Color de fondo al pasar el cursor */
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
			background-color: #2c2fa5;
			/* Color de fondo al pasar el cursor */
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
			background-color: #2c2fa5;
			/* Color de fondo al pasar el cursor */
			box-shadow: 0px 15px 20px rgba(0, 0, 0, 0.3);
			transform: translateY(-7px);
		}
	}
</style>
