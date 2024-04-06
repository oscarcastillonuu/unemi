<script context="module" lang="ts">
	import type { Load } from '@sveltejs/kit';

	export const load: ({ fetch }: { fetch: any }) => Promise<
		| { redirect: string; status: number }
		| { redirect: string; status: number }
		| string
		| { redirect: string; status: number }
		| { redirect: string; status: number }
		| {
				props: {
					eBecaSolicitudPendienteDocumentacion: any[];
					tieneValoresPendientes: boolean;
					mensajeValoresRubros: string;
					ePeriodoEventoDisponibleSinConfirmar: {};
					eBecaSolicitudPendiente: any[];
					aDataActualizarDato: {};
					eNews: any[];
					ids_modulesFavorite: any[];
					tieneValoresVencidos: boolean;
					actualizar_sedes: boolean;
					aDataSedeElectoral: {};
					actualiza_datos_pregrado: boolean;
					eQuizzes_answered: any[];
					eQuizzes_answered_sil: any[];
					eDataMessages: any[];
					eFiles: any[];
					ePersona: {};
					eInscripcion: {};
					eCoordinacion: {};
					eNewsBanner: any[];
					eModules: any[];
					eModulesFavorite: any[];
					eTemplateBaseSetting: {};
					eDataInsignias: any[];
					eQuizzes_to_answer: any[];
					eQuizzes_to_answer_sil: any[];
				};
		  }
	> = async ({ fetch }) => {
		let eModules = [];
		let eModulesFavorite = [];
		let ids_modulesFavorite = [];
		let eNews = [];
		let eNewsBanner = [];
		let eFiles = [];
		let eQuizzes_to_answer = [];
		let eQuizzes_to_answer_sil = [];
		let eQuizzes_answered = [];
		let eQuizzes_answered_sil = [];
		let tieneValoresPendientes = false;
		let tieneValoresVencidos = false;
		let mensajeValoresRubros = '';
		let eDataMessages = [];
		let ePersona = {};
		let eInscripcion = {};
		let eCoordinacion = {};
		let aDataActualizarDato = {};
		let aDataSedeElectoral = {};
		let eTemplateBaseSetting = {};
		let eDataInsignias = [];
		let eBecaSolicitudPendiente = [];
		let eBecaSolicitudPendienteDocumentacion = [];
		let ePeriodoEventoDisponibleSinConfirmar = {};
		let actualiza_datos_pregrado = false;
		let actualizar_sedes = false;

		if (browserGet('refreshToken')) {
			const response = await getCurrentRefresh(fetch, `${variables.BASE_API_URI}/token/refresh`);
			if (response.status >= 400) {
				//window.localStorage.clear();
				//addToast({ type: 'error', header: 'Ocurrio un error', body: 'Usuario no identificado' });
				return {
					status: 302,
					redirect: '/lock-screen'
				};
			}
			if (response.ok == true) {
				const json = decodeToken(await response.json());
				browserSet('refreshToken', json.tokens.refresh);
				browserSet('accessToken', json.tokens.access);
				browserSet('dataSession', JSON.stringify(json));
				userData.set(json);
			}
		} else {
			//window.localStorage.clear();
			//addToast({ type: 'error', header: 'Ocurrio un error', body: 'Usuario no identificado' });

			return {
				status: 302,
				redirect: '/login'
			};
		}

		const ds = browserGet('dataSession');
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			ePersona = dataSession['persona'];
			eInscripcion = dataSession['inscripcion'];
			eTemplateBaseSetting = dataSession['templatebasesetting'];
			eCoordinacion = dataSession['coordinacion'];
			const [resPanel, errorsPanel] = await apiPOST(fetch, 'alumno/panel', {});
			if (errorsPanel.length > 0) {
				errorsPanel.forEach((element) => {
					addToast({ type: 'error', header: 'Ocurrio un error', body: element.error });
				});
			} else {
				if (!resPanel.isSuccess) {
					//addToast({ type: 'error', header: 'Ocurrio un error', body: resPanel.message });
					if (!resPanel.module_access) {
						if (resPanel.redirect) {
							if (resPanel.token) {
								return (window.location.href = `${connectionToken}&ret=/${resPanel.redirect}`);
							} else {
								if (resPanel.message) {
									addToast({ type: 'warning', header: 'Advertencia', body: resPanel.message });
								}
								return {
									status: 302,
									redirect: `/${resPanel.redirect}`
								};
							}
						} else {
							if (resPanel.message) {
								addToast({ type: 'warning', header: 'Advertencia', body: resPanel.message });
							}
							return {
								status: 302,
								redirect: '/'
							};
						}
					} else {
						if (resPanel.message) {
							addToast({ type: 'warning', header: 'Advertencia', body: resPanel.message });
						}
					}
				} else {
					eModules = resPanel.data.eModules;
					eNews = resPanel.data.eNews;
					eNewsBanner = resPanel.data.eNewsBanner;
					tieneValoresPendientes = resPanel.data.tieneValoresPendientes;
					tieneValoresVencidos = resPanel.data.tieneValoresVencidos;
					mensajeValoresRubros = resPanel.data.mensajeValoresRubros;
					eDataMessages = resPanel.data.eDataMessages;
				}
			}
			/*const [resBeca, errorsBeca] = await apiPOST(fetch, 'alumno/becas', {});
			if (errorsBeca.length > 0) {
				errorsBeca.forEach((element) => {
					addToast({ type: 'error', header: 'Ocurrio un error', body: element.error });
				});
			} else {
				if (!resBeca.isSuccess) {
					addToast({ type: 'error', header: 'Ocurrio un error', body: resBeca.message });
				} else {
					// console.log(resBeca.data);
					eBecaSolicitudPendiente = resBeca.data.eBecaSolicitudPendiente; // Mensajes de Advertencia Actualizar Hoja de vida
					eBecaSolicitudPendienteDocumentacion = resBeca.data.eBecaSolicitudPendienteDocumentacion; // Mensajes de Advertencia Actualizar Hoja de vida
				}
			}*/
			/*const [resQuizzes, errorsQuizzes] = await apiPOST(fetch, 'alumno/panel/get/quizzes', {});
			if (errorsQuizzes.length > 0) {
				errorsQuizzes.forEach((element) => {
					addToast({ type: 'error', header: 'Ocurrio un error', body: element.error });
				});
			} else {
				if (!resQuizzes.isSuccess) {
					addToast({ type: 'error', header: 'Ocurrio un error', body: resQuizzes.message });
				} else {
					eQuizzes_to_answer = resQuizzes.data.eQuizzes_to_answer; // encuestas por contestar
					eQuizzes_answered = resQuizzes.data.eQuizzes_answered; // encuestas contestadas
				}
			}

			const [resQuizzesSil, errorsQuizzesSil] = await apiGET(fetch, 'alumno/materias/get/quizzes', {action:'traerEncuesta'});
			if (errorsQuizzesSil.length > 0) {
				errorsQuizzesSil.forEach((element) => {
					addToast({ type: 'error', header: 'Ocurrio un error', body: element.error });
				});
			} else {
				if (!resQuizzesSil.isSuccess) {
					addToast({ type: 'error', header: 'Ocurrio un error', body: resQuizzesSil.message });
				} else {
					eQuizzes_to_answer_sil = resQuizzesSil.data.eQuizzes_to_answer_sil; // encuestas por contestar
					eQuizzes_answered_sil = resQuizzesSil.data.eQuizzes_answered_sil; // encuestas contestadas
				}
			}

			const [resBeca, errorsBeca] = await apiPOST(fetch, 'alumno/becas', {});
			if (errorsBeca.length > 0) {
				errorsBeca.forEach((element) => {
					addToast({ type: 'error', header: 'Ocurrio un error', body: element.error });
				});
			} else {
				if (!resBeca.isSuccess) {
					addToast({ type: 'error', header: 'Ocurrio un error', body: resBeca.message });
				} else {
					// console.log(resBeca.data);
					eBecaSolicitudPendiente = resBeca.data.eBecaSolicitudPendiente; // Mensajes de Advertencia Actualizar Hoja de vida
					eBecaSolicitudPendienteDocumentacion = resBeca.data.eBecaSolicitudPendienteDocumentacion; // Mensajes de Advertencia Actualizar Hoja de vida
				}
			}*/

			/*const [resActualizaDatos, errorsActualizaDatos] = await apiPOST(
				fetch,
				'alumno/actualizadatosdomicilio',
				{}
			);
			if (errorsActualizaDatos.length > 0) {
				errorsActualizaDatos.forEach((element) => {
					addToast({ type: 'error', header: 'Ocurrio un error', body: element.error });
				});
			} else {
				if (!resActualizaDatos.isSuccess) {
					addToast({ type: 'error', header: 'Ocurrio un error', body: resActualizaDatos.message });
				} else {
					actualiza_datos_pregrado = resActualizaDatos.data['ver_modal'];
					aDataActualizarDato = resActualizaDatos.data['ePersona'];
				}
			}

			const [resSedeElectoral, errorsSedeElectoral] = await apiPOST(
				fetch,
				'alumno/sedeelectoral',
				{}
			);
			if (errorsSedeElectoral.length > 0) {
				errorsSedeElectoral.forEach((element) => {
					addToast({ type: 'error', header: 'Ocurrio un error', body: element.error });
				});
			} else {
				if (!resSedeElectoral.isSuccess) {
					addToast({ type: 'error', header: 'Ocurrio un error', body: resSedeElectoral.message });
				} else {
					actualizar_sedes = resSedeElectoral.data['ver_modal'];
					aDataSedeElectoral = resSedeElectoral.data;
				}
			}*/

			/*const [resFiles, errorsFiles] = await apiPOST(fetch, 'alumno/panel/get/files', {});
			if (errorsFiles.length > 0) {
				errorsFiles.forEach((element) => {
					addToast({ type: 'error', header: 'Ocurrio un error', body: element.error });
				});
			} else {
				if (!resFiles.isSuccess) {
					addToast({ type: 'error', header: 'Ocurrio un error', body: resNews.message });
				} else {
					eFiles = resFiles.data.eFiles;
				}
			}*/

			/*

			const [resInsignia, errorsInsignia] = await apiPOST(fetch, 'alumno/insignias', {});
			if (errorsInsignia.length > 0) {
				errorsInsignia.forEach((element) => {
					addToast({ type: 'error', header: 'Ocurrio un error', body: element.error });
				});
			} else {
				if (!resInsignia.isSuccess) {
					addToast({ type: 'error', header: 'Ocurrio un error', body: resInsignia.message });
				} else {
					// console.log(resInsignia.data.eInsignia);
					eDataInsignias = resInsignia.data; // Mensajes de Advertencia Actualizar Hoja de vida
				}
			}

			
			const [resEvento, errorsEvento] = await apiPOST(fetch, 'alumno/panel/get/evento',{});
			if (errorsEvento.length > 0) {
				errorsEvento.forEach((element) => {
					addToast({ type: 'error', header: 'Ocurrio un error', body: element.error });
				});
			} else {
				if (!resEvento.isSuccess) {
					addToast({ type: 'error', header: 'Ocurrio un error', body: resEvento.message });
				} else {
					// console.log(resBeca.data);
					ePeriodoEventoDisponibleSinConfirmar = resEvento.data.ePeriodoEventoDisponibleSinConfirmar; // Mensajes de Advertencia Actualizar Hoja de vida
				}
			}*/
		}

		return {
			props: {
				ePersona,
				eInscripcion,
				eCoordinacion,
				eModules,
				eModulesFavorite,
				ids_modulesFavorite,
				eTemplateBaseSetting,
				eNews,
				eNewsBanner,
				tieneValoresPendientes,
				tieneValoresVencidos,
				mensajeValoresRubros,
				eFiles,
				eQuizzes_to_answer,
				eQuizzes_to_answer_sil,
				eQuizzes_answered,
				eQuizzes_answered_sil,
				eDataMessages,
				eDataInsignias,
				eBecaSolicitudPendiente,
				eBecaSolicitudPendienteDocumentacion,
				ePeriodoEventoDisponibleSinConfirmar,
				actualiza_datos_pregrado,
				actualizar_sedes,
				aDataActualizarDato,
				aDataSedeElectoral
			}
		};
	};
</script>

<script lang="ts">
	import { goto } from '$app/navigation';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader } from 'sveltestrap';
	import { addToast } from '$lib/store/toastStore';
	import { userData } from '$lib/store/userStore';
	import {
		browserGet,
		apiPOST,
		getCurrentRefresh,
		browserSet,
		logOutUser,
		apiGET
	} from '$lib/utils/requestUtils';
	import { onMount } from 'svelte';
	import { converToAscii, action_print_ireport } from '$lib/helpers/baseHelper';
	import { fly } from 'svelte/transition';
	import { loading } from '$lib/store/loadingStore';
	import { variables } from '$lib/utils/constants';
	import { decodeToken } from '$lib/utils/decodetoken';
	import { navigating } from '$app/stores';
	// import pkg from '@fancyapps/ui';
	// const { Fancybox } = pkg
	// import { Fancybox, Carousel, Panzoom } from '@fancyapps/ui';
	// import '@fancyapps/ui/dist/fancybox.css';
	// import { Card } from 'sveltestrap';
	import { addNotification } from '$lib/store/notificationStore';
	import EncuentaGeneral from '$components/Alumno/Encuesta/General.svelte';
	import ActualizaDatoGeneral from '$components/Alumno/ActualizaDato/General.svelte';
	import ActualizaSede from '$components/Alumno/sedeelectoral/General.svelte';
	import { Tooltip, Carousel, CarouselControl, CarouselItem } from 'sveltestrap';
	import ModalInsigniaGeneral from '$components/Alumno/Insignia/Insignia.svelte';
	import ModalEvento from '$components/Alumno/Evento/Modal.svelte';
	import ModalEncuestaSilabo from '$components/Alumno/Evento/ModalEncuestaSilabo.svelte';
	import contentInfo from './_contentinfo.svelte';
	import Swal from 'sweetalert2';
	// Fancybox.bind('[data-fancybox]', {});
	let active = false;
	let activeIndex = 0;

	export let ePersona;
	export let eInscripcion;
	export let eCoordinacion;
	export let aDataActualizarDato;
	export let aDataSedeElectoral;
	export let eModules;
	export let eModulesFavorite;
	export let ids_modulesFavorite;
	export let eTemplateBaseSetting;
	export let eNews = [];
	export let eNewsBanner = [];
	export let eFiles = [];
	export let eQuizzes_to_answer = [];
	export let eQuizzes_to_answer_sil = [];
	export let eQuizzes_answered = [];
	export let eQuizzes_answered_sil = [];
	export let tieneValoresPendientes;
	export let tieneValoresVencidos;
	export let mensajeValoresRubros;
	export let eDataMessages = [];
	export let eDataInsignias;
	export let eBecaSolicitudPendiente;
	export let eBecaSolicitudPendienteDocumentacion;
	export let ePeriodoEventoDisponibleSinConfirmar;
	export let actualiza_datos_pregrado;
	export let actualizar_sedes;

	let mOpenModal = false;
	let mOpenModalActualizaDato = actualiza_datos_pregrado;
	let mOpenModalSedeElectoral = actualizar_sedes;
	let aDataModal = {};
	const mToggleModal = () => (mOpenModal = !mOpenModal);
	const mToggleModalActualizaDato = () => (mOpenModalActualizaDato = !mOpenModalActualizaDato);
	const mToggleModalSedeElectoral = () => (mOpenModalSedeElectoral = !mOpenModalSedeElectoral);

	let mOpenModalSeccion = false;
	const mToggleModalSeccion = () => (mOpenModalSeccion = !mOpenModalSeccion);

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		// console.log(eDataInsignias.activo)
		if (eDataInsignias.activo) {
			toggleModalInfo();
		}
		if (tieneValoresPendientes) {
			addNotification({
				msg: `${mensajeValoresRubros}`,
				type: 'error',
				target: 'newNotificationToast',
				duration: 10000,
				pausable: true,
				intro: { y: 192 }
			});
		} else if (tieneValoresVencidos) {
			/*addNotification({
				msg: `${mensajeValoresRubros}`,
				type: 'error',
				target: 'newNotificationToast',
				duration: 10000,
				pausable: true,
				intro: { y: 192 }
			});*/
			const mensaje = {
				title: `<p style='color:#FE9900;'><b>Cuenta suspendida</b></p>`,
				html: `<p style='color:#ACAEAF;'>Su cuenta se encuentra suspendida temporalmente por una deuda vencida</p>
			${mensajeValoresRubros}`,
				//icon:'warning',
				iconHtml: `<img src='${variables.BASE_API}/static/images/icons/icon_stop.svg' style='height: 150%;'>`,
				customClass: { icon: 'no-border', cancelButton: 'swalBtnP' },
				showCancelButton: false,
				showConfirmButton: true,
				confirmButtonColor: '#FE9900',
				allowOutsideClick: false,
				allowEscapeKey: false,
				confirmButtonText: 'Consultar deuda',
				cancelButtonText: 'Cerrar'
			};
			Swal.fire(mensaje)
				.then(async (result) => {
					console.log(result);
					if (result.isConfirmed) {
						goto('alu_finanzas');
					}
				})
				.catch((error) => {
					loading.setLoading(false, 'Cargando, espere por favor...');
					addNotification({
						msg: error.message,
						type: 'error'
					});
				});
			let noborder = document.getElementsByClassName('no-border')[0];
			noborder.style.border = 0;
		} else if (eInscripcion) {
			if (
				!eInscripcion.isGraduado &&
				!eInscripcion.isEgresado &&
				eCoordinacion.clasificacion == 1
			) {
				if (eInscripcion.seccion) {
					//console.log(eInscripcion.seccion.nombre);
					mOpenModalSeccion = true;
				}
			}
		}
		if (eCoordinacion.clasificacion == 1) {
			if (Object.keys(eBecaSolicitudPendiente).length > 0) {
				const mensajeBeca = {
					title: `<p style='color:#FE9900;'><b>Beca aprobada</b></p>`,
					html: `
				<p style='color:#ACAEAF;'>Felicitaciones, tienes una beca aprobada por ${eBecaSolicitudPendiente.becatipo.display}</p>
				<p style='color:#ACAEAF;'>Para acceder a esta beca, debes aceptar los  <a target='_blan' href='${eBecaSolicitudPendiente.url_acta}'>términos y condiciones </a>.</p>
				`,
					//icon:'warning',
					// icon: `info`,
					showCancelButton: true,
					showConfirmButton: true,
					confirmButtonColor: '#FE9900',
					allowOutsideClick: false,
					allowEscapeKey: false,
					confirmButtonText: 'Aceptar',
					cancelButtonText: 'Rechazar'
				};
				Swal.fire(mensajeBeca)
					.then(async (result) => {
						console.log(result);
						if (result.isConfirmed) {
							loading.setLoading(true, 'Cargando, espere por favor...');
							const [resBeca, errorsBeca] = await apiPOST(fetch, 'alumno/becas', {
								action: 'aceptarrechazarbeca',
								id: eBecaSolicitudPendiente.id,
								acepto: 1
							});
							if (errorsBeca.length > 0) {
								errorsBeca.forEach((element) => {
									addToast({ type: 'error', header: 'Ocurrio un error', body: element.error });
								});
							} else {
								if (!resBeca.isSuccess) {
									addToast({ type: 'error', header: 'Ocurrio un error', body: resBeca.message });
								} else {
									// console.log(resBeca.data);
									//eDataBecaSolicitud = resBeca.data; // Mensajes de Advertencia Actualizar Hoja de vida
									loading.setLoading(false, 'Cargando, espere por favor...');
									const dataSession = JSON.parse(browserGet('dataSession'));
									const connectionToken = dataSession['connectionToken'];
									window.location.href = `${connectionToken}&ret=/alu_becas&periodo_id=${eBecaSolicitudPendiente.periodo_idenc}`;
								}
							}
						}
						if (result.isDismissed) {
							Swal.fire({
								title: "<p style='color:#FE9900;'><b>¿Está seguro de rechazar su beca?</b></p>",
								html: `<p style='color:#ACAEAF;'>Recuerde que al momento de rechazar la beca, esta será asignada a otro estudiante.</p>`,
								//icon: 'warning',
								showCancelButton: true,
								confirmButtonColor: '#FE9900',
								//cancelButtonColor: '#d33',
								confirmButtonText: 'Si',
								cancelButtonText: 'No'
							}).then(async (result) => {
								if (result.isConfirmed) {
									loading.setLoading(true, 'Cargando, espere por favor...');
									const [resBeca, errorsBeca] = await apiPOST(fetch, 'alumno/becas', {
										action: 'aceptarrechazarbeca',
										id: eBecaSolicitudPendiente.id,
										acepto: 0
									});
									if (errorsBeca.length > 0) {
										errorsBeca.forEach((element) => {
											addToast({ type: 'error', header: 'Ocurrio un error', body: element.error });
										});
									} else {
										if (!resBeca.isSuccess) {
											addToast({
												type: 'error',
												header: 'Ocurrio un error',
												body: resBeca.message
											});
										} else {
											// console.log(resBeca.data);
											//eDataBecaSolicitud = resBeca.data; // Mensajes de Advertencia Actualizar Hoja de vida
											window.location.href = '.';
										}
									}
								} else {
									loading.setLoading(true, 'Cargando, espere por favor...');
									window.location.href = '.';
								}
							});
						}
						return;
					})
					.catch((error) => {
						loading.setLoading(false, 'Cargando, espere por favor...');
						addNotification({
							msg: error.message,
							type: 'error'
						});
					});
			}
			if (
				Object.keys(eBecaSolicitudPendiente).length == 0 &&
				Object.keys(eBecaSolicitudPendienteDocumentacion).length > 0
			) {
				if (eBecaSolicitudPendienteDocumentacion.tiene_documentacion_pendiente) {
					const mensajedocumentacionBeca = {
						title: `<p style='color:#FE9900;'><b>Carga de documentos</b></p>`,
						html: `
					<p style='color:#ACAEAF; text-align: justify;' >Estimado estudiante, Usted aceptó una solicitud beca  con tipo <span class="badge bg-info">${eBecaSolicitudPendienteDocumentacion.becatipo.display}</span>. </p>
					<p style='color:#ACAEAF;'><b>por favor subir los documentos pendientes</b>.</p>
					`,
						//icon:'warning',
						// icon: `info`,
						showCancelButton: true,
						showConfirmButton: true,
						confirmButtonColor: '#FE9900',
						allowOutsideClick: false,
						allowEscapeKey: false,
						confirmButtonText: 'Subir Documentación',
						cancelButtonText: 'Cerrar'
					};
					Swal.fire(mensajedocumentacionBeca)
						.then(async (result) => {
							console.log(result);
							if (result.isConfirmed) {
								loading.setLoading(false, 'Cargando, espere por favor...');
								const dataSession = JSON.parse(browserGet('dataSession'));
								const connectionToken = dataSession['connectionToken'];
								//(window.location.href = eModulo.url_page);
								window.location.href = `${connectionToken}&ret=/alu_becas?action=actualizardatos`;
							}
							if (result.isDismissed) {
							}

							return;
						})
						.catch((error) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							addNotification({
								msg: error.message,
								type: 'error'
							});
						});
				}
			}
		}
		if (Object.keys(ePeriodoEventoDisponibleSinConfirmar).length > 0) {
			loadModalEvento(ePeriodoEventoDisponibleSinConfirmar);
		}

		if (eQuizzes_to_answer.length > 0) {
			await loadModalEncuestaGeneral();
		}

		// if (eQuizzes_to_answer_sil.length > 0) {
		// 	await loadAlertaEncuestaSilabo();
		// }
	});

	const actionRunSeccion = (event) => {};

	//const botones = document.querySelectorAll(".botones");

	const loadAlertaEncuestaSilabo = async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		mOpenModalEncuestaSilaboRespondida = !mOpenModalEncuestaSilaboRespondida;
		loading.setLoading(false, 'Cargando, espere por favor...');
	};

	const actionGotoModule = async (event, eModulo) => {
		//sconsole.log('currentTarget', event.currentTarget);
		//let childElementClicked = false;
		/*for (const child of event.currentTarget.childNodes) {
			if (child.classList){
				console.log("classList", child.classList);
				const iconfavorite = child.classList.contains('iconfavorite');
				if (iconfavorite) {
					childElementClicked = true;
				}
				console.log("iconfavorite", iconfavorite);
			}
			
		}*/
		//if (childElementClicked != true) {
		if (eModulo.api) {
			return goto(eModulo.url);
		} else {
			const dataSession = JSON.parse(browserGet('dataSession'));
			const connectionToken = dataSession['connectionToken'];
			//(window.location.href = eModulo.url_page);
			window.location.href = `${connectionToken}&ret=/${eModulo.url}`;

			return;
		}
		//}
	};

	const searchModules = (e) => {
		//console.log(e);

		const BodyModules = document.querySelectorAll('.menuPanelCard > div');
		for (let i = 0; i < BodyModules.length; i++) {
			const BModule = BodyModules[i];
			const nombre_modules = BModule.querySelector('.tituloicon');
			if (
				converToAscii(nombre_modules.innerText.toLowerCase()).indexOf(
					converToAscii(e.toLowerCase())
				) === -1
			) {
				BModule.style.display = 'none';
			} else {
				BModule.style.display = '';
			}
		}
	};

	const clickSearchPanel = () => {
		var x = document.getElementById('myDIV');
		if (x.style.display === 'none') {
			x.style.display = 'block';
			x.focus();
		} else {
			x.style.display = 'none';
		}
	};

	const clickOutside = () => {
		var x = document.getElementById('myDIV');
		x.style.display = 'none';
	};

	const loadModalEncuestaGeneral = async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const eQuiz = eQuizzes_to_answer[0];
		aDataModal = eQuiz;
		mOpenModal = !mOpenModal;
		loading.setLoading(false, 'Cargando, espere por favor...');
	};

	const calcularTiempoEstimado = (total) => {
		const segundos_x_pregunta = 60;
		let tiempo_total = total * segundos_x_pregunta;
		if (tiempo_total / 60 > 59) {
			if (tiempo_total / 60 == 60) {
				return `1 Hora`;
			} else {
				return `${tiempo_total / 60} Horas`;
			}
		} else {
			if (tiempo_total / 60 == 1) {
				return `${tiempo_total / 60} Minuto`;
			} else {
				return `${tiempo_total / 60} Minutos`;
			}
		}
	};

	const eliminarEncuesta = (eQuiz) => {
		const mensaje = {
			title: `Estás por eliminar este registro:\n ${eQuiz.descripcion}`,
			html: `Esta acción es irreversible`,
			type: 'warning',
			icon: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: `Si, deseo hacerlo!`,
			cancelButtonText: 'No, cancelar'
		};
		Swal.fire(mensaje)
			.then(async (result) => {
				if (result.value) {
					loading.setLoading(true, 'Cargando, espere por favor...');
					const [res, errors] = await apiPOST(fetch, 'alumno/panel/delete/quizzes', {
						id: eQuiz.id
					});
					if (errors.length > 0) {
						errors.forEach((element) => {
							addToast({ type: 'error', header: 'Ocurrio un error', body: element.error });
						});
					} else {
						if (!res.isSuccess) {
							addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
						} else {
							addToast({
								type: 'success',
								header: 'Exitoso!',
								body: 'Se elimino correctamente la encuesta'
							});
							eQuizzes_to_answer = res.data.eQuizzes_to_answer; // encuestas por contestar
							eQuizzes_answered = res.data.eQuizzes_answered; // encuestas contestadas

							if (eQuizzes_to_answer.length > 0) {
								loadModalEncuestaGeneral();
							}
						}
					}
					loading.setLoading(false, 'Cargando, espere por favor...');
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

	const actionFavoriteModule = (eModule, action) => {};

	let aDataModal2 = {};
	let modalTitle2 = '';
	let modalDetalleContent2 = contentInfo;
	let mOpenModalGenerico2 = false;
	const mToggleModalGenerico2 = () => (mOpenModalGenerico2 = !mOpenModalGenerico2);
	const actionRun2 = (event) => {
		//mOpenModalGenerico2 = false;
		//loading.setLoading(false, 'Cargando, espere por favor...');
		//action_init_load();
	};
	const toggleModalInfo = (ocultar = false) => {
		aDataModal2.ocultar = ocultar;
		aDataModal2.insignia = eDataInsignias.eInsignia;
		modalDetalleContent2 = contentInfo;
		mOpenModalGenerico2 = !mOpenModalGenerico2;
		modalTitle2 = 'Nueva Solicitud';
	};

	const saveInsignia = async (insigniaS) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/insignias', {
			action: 'insigniavisto',
			id: insigniaS
		});
		if (errors.length > 0) {
			errors.forEach((element) => {
				addToast({ type: 'error', header: 'Ocurrio un error', body: element.error });
			});
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
			} else {
				mToggleModalGenerico2();
				const dataSession = JSON.parse(browserGet('dataSession'));
				const connectionToken = dataSession['connectionToken'];
				//(window.location.href = eModulo.url_page);
				window.location.href = `${connectionToken}&ret=/insignia`;
			}
		}
	};

	let mOpenModal3 = false;
	let aDataModal3 = {};
	let mOpenModalGenerico3 = false;
	let mOpenModalEncuestaSilaboRespondida = false;
	const mToggleModalGenerico3 = () =>
		(mOpenModalEncuestaSilaboRespondida = !mOpenModalEncuestaSilaboRespondida);
	const mToggleModalEncuestaSilaboRespondida = () =>
		(mOpenModalEncuestaSilaboRespondida = !mOpenModalEncuestaSilaboRespondida);
	const actionRun3 = (event) => {
		//mOpenModalGenerico2 = false;
		//loading.setLoading(false, 'Cargando, espere por favor...');
	};
	const actionRun4 = (event) => {
		//mOpenModalGenerico2 = false;
		//loading.setLoading(false, 'Cargando, espere por favor...');
	};
	const saveEvento = async (eEvento) => {
		//loading.setLoading(true, 'Cargando, espere por favor...');
		console.log('Hola');
	};
	const loadModalEvento = async (eEvento) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		aDataModal3 = eEvento;
		mToggleModalGenerico3();
		loading.setLoading(false, 'Cargando, espere por favor...');
	};

	//$: console.log(eModules);
	const inscribirseAsistenciaEvento = (eEvento, tipo) => {
		let texto = tipo == 1 ? `confirmar` : `declinar`;
		texto = `Está a punto de ${texto} su asistencia al evento.\n¿Desea continuar?`;
		const mensaje = {
			html: `<b>${texto}</b>`,
			//html: `Esta acción es irreversible`,}
			customClass: {
				cancelButton: 'btn-mini',
				confirmButton: 'btn-confirm'
			},
			type: 'warning',
			icon: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonColor: '#FE9900',
			//cancelButtonColor: '#d33',
			confirmButtonText: `Si, deseo hacerlo!`,
			cancelButtonText: 'No, cancelar'
		};
		Swal.fire(mensaje).then(async (result) => {
			if (result.value) {
				loading.setLoading(true, 'Cargando, espere por favor...');
				const [res, errors] = await apiPOST(fetch, 'alumno/evento', {
					action: 'confirmAssistance',
					id: eEvento.inscrito.id,
					tipo: tipo
				});
				if (errors.length > 0) {
					errors.forEach((element) => {
						addToast({ type: 'error', header: 'Ocurrio un error', body: element.error });
					});
				} else {
					if (!res.isSuccess) {
						addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
					} else {
						addToast({
							type: 'success',
							header: 'Exitoso!',
							body: res.data.msg
						});
						goto(`alu_eventos/${eEvento.id}`);
					}
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
			}
		});
	};
</script>

<svelte:head>
	<title>Panel | SGAEstudiante</title>
</svelte:head>
<!-- color scheme -->
<div class="row pt-0 pb-2 px-1">
	<div class="col-lg-12 col-md-12 col-12 mb-2">
		<div class="border-bottom pb-1 mb-1 d-md-flex align-items-center justify-content-between">
			<div class="mb-3 mb-md-0">
				{#if ePersona}
					{#if ePersona.nombre_minus}
						<h4 class="mb-0" style="color: #012E46;margin-left: 5px;">
							¡<b>Hola {ePersona.nombre_minus}</b>, {ePersona.sexo_id == 1
								? 'bienvenida'
								: 'bienvenido'} al Sistema de Gestión Académica!
						</h4>
					{/if}
				{/if}
				<!--<nav aria-label="breadcrumb">
					<ol class="breadcrumb">
						<li class="breadcrumb-item">
							<a href="/">Inicio</a>
						</li>
					</ol>
				</nav>-->
			</div>
			<div
				class="bg-primary rounded-pill p-1 d-grid gap-2 d-md-flex justify-content-md-end d-none d-sm-none d-md-block"
			>
				<input
					id="myDIV"
					class="form-control rounded-pill"
					placeholder="Buscar"
					style="max-width: 350px !important; display:none;"
					on:blur={() => clickOutside()}
					on:keyup={({ target: { value } }) => searchModules(value)}
				/>

				<button class="btn btn-primary rounded-pill search-icon" on:click={() => clickSearchPanel()}
					><i class="bi bi-search" /></button
				>
			</div>
		</div>
	</div>
</div>
{#if eDataMessages.length > 0}
	<div class="row">
		{#each eDataMessages as eMessage}
			<div class="col-12">
				<div class="alert alert-{eMessage.type} d-flex align-items-center" role="alert">
					{@html eMessage.icon}
					<div>
						<h2>{eMessage.title}</h2>
						<p>{eMessage.body}</p>
					</div>
				</div>
			</div>
		{/each}
	</div>
{/if}
<div class="row">
	{#if eNewsBanner.length > 0 || eQuizzes_answered.length > 0}
		<div class="col-xl-8 col-lg-8 col-md-8 col-12 mb-4">
			{#each eNews as eNew}
				<div class="row">
					<div class="col-12">
						<div class="alert alert-info">
							<!-- svelte-ignore a11y-invalid-attribute -->
							<a href={'#'} class="close" data-dismiss="alert">×</a>
							<h4 class="alert-heading">{eNew.titular}</h4>
							{@html eNew.cuerpo}
						</div>
					</div>
				</div>
			{/each}

			{#if eModulesFavorite.length > 0 && eTemplateBaseSetting.use_menu_favorite_module}
				<h4 class="mb-2" style="color: #012E46;">
					<b>&nbsp;<i class="fe fe-bookmark" /> Mis Favoritos</b>
				</h4>
				<div class="containerMenuFavoritos">
					<ul class="menuPanelFavoritos ">
						{#each eModulesFavorite as eModule, i}
							<li
								class="action-menu-entry modFavorito"
								on:click|preventDefault={(event) => actionGotoModule(event, eModule)}
								style="height: 200px;"
							>
								<div class="iconfavorite">
									<div style="padding: 5px 15px 0px; width: 100%">
										<a
											href="javascript:;"
											class="action-menu-favorite tr"
											title="Quitar de favorito"
											on:click|preventDefault={() => actionFavoriteModule(eModule, 'delete')}
											id={`Tooltip_favorito_${eModule.id}`}
											style="float:left; margin-bottom: 50px; font-size:13px"
											><i class="fe fe-star text-warning" /></a
										>
										<Tooltip target={`Tooltip_favorito_${eModule.id}`} placement="left"
											>Quitar de favorito</Tooltip
										>
									</div>
								</div>
								<div class="iconimage">
									<div class="pd">
										<img src={eModule.icono} border="0" />
									</div>
								</div>
								<div class="iconname">
									<div class="pd">
										<div class="tituloicon">{eModule.nombre}</div>
										<span class="icondesc">{eModule.descripcion}</span>
									</div>
								</div>
							</li>
						{/each}
					</ul>
				</div>
			{/if}
			<h4 class="mb-2" style="color: #012E46;">
				<b>&nbsp;<i class="fe fe-layers" /> Mis Módulos</b>
			</h4>
			<div class="containerMenu" id="mybuscador">
				<div class="menuPanelCard">
					<!-- MODULOS -->
					{#each eModules as eModule, i}
						<div
							data-nombre={eModule.nombre}
							on:click|preventDefault={(event) => actionGotoModule(event, eModule)}
							class="carbon-example flex-wrapper action-menu-entry"
						>
							<img src={eModule.icono} border="0" class="avatar-md iconosga" />
							<div class="inner-wrapper">
								<h4 class="mb-1" style="font-size: 14px;">
									<div class="tituloicon" data-inicial={eModule.nombre}>{eModule.nombre}</div>
								</h4>
								<span class="icondesc">{eModule.descripcion}</span>
							</div>
						</div>
					{/each}
				</div>
			</div>
		</div>
		<div class="col-xl-4 col-lg-4 col-md-4 col-12 mb-4">
			{#if eQuizzes_answered.length > 0}
				<div class="card">
					<div class="card-header d-flex align-items-center justify-content-between">
						<div class="">
							<h3 class="mb-0">Gestionar mis encuestas</h3>
						</div>
					</div>
					<div class="card-body">
						<ul class="list-group list-group-flush">
							{#each eQuizzes_answered as eQuiz}
								<li class="list-group-item px-0 pt-0">
									<div class="row">
										<!-- Col -->
										<div class="col-auto ">
											<div class="text-end pe-0 align-middle pt-0">
												<!--<a href="#" class="text-inherit"><i class="fe fe-settings" /></a>-->
												<a
													href="#"
													on:click={() => eliminarEncuesta(eQuiz)}
													class="ms-2 link-danger"><i class="fe fe-trash-2" /></a
												>
											</div>
										</div>
										<!-- Col -->
										<div class="col ps-0">
											<a href="#">
												<h5 class="text-primary-hover">{eQuiz.descripcion}</h5>
											</a>
											<div class="d-flex align-items-center">
												<span
													><span class="me-2 align-middle"><i class="fe fe-list" /></span>{eQuiz
														.preguntas.length > 1
														? `${eQuiz.preguntas.length} Preguntas`
														: `${eQuiz.preguntas.length} Pregunta`}
												</span>
												<span class="ms-2"
													><span class="me-2 align-middle"><i class="fe fe-clock" /></span>
													{calcularTiempoEstimado(eQuiz.preguntas.length)}</span
												>
												<!--<a href="instructor-quiz-result.html" class="ms-2 text-body"
												><span class="me-2 align-middle"><i class="fe fe-file-text" /></span
												>Result</a
											>-->
											</div>
										</div>
									</div>
								</li>
							{/each}
						</ul>
					</div>
				</div>
			{/if}
			{#if eNewsBanner.length > 0}
				<Carousel dark items={eNewsBanner} bind:activeIndex>
					<div class="carousel-inner">
						{#each eNewsBanner as item, index}
							{#if item.imagen}
								<CarouselItem bind:activeIndex itemIndex={index}>
									<div class="card card-hover mb-lg-4 m-4">
										<a class="" href={item.imagen} target="_blank">
											<img src={item.imagen} alt="" class="img-fluid w-100 rounded-top-md" />
										</a>

										<div class="card-body pb-0 pl-5 pr-5 pt-0">
											<h3 class="h3">
												<a href="#1" class="text-inherit">{item.titular}</a>
											</h3>
											{@html item.cuerpo}
										</div>
									</div>
								</CarouselItem>
							{:else}
								<CarouselItem bind:activeIndex itemIndex={index}>
									<div class="card card-hover mb-lg-4 m-4">
										<div class="card-body pb-0 pl-5 pr-5 pt-3">
											<h3 class="h3">
												<a href="#1" class="text-inherit">{item.titular}</a>
											</h3>
											{@html item.cuerpo}
										</div>
									</div>
								</CarouselItem>
							{/if}
						{/each}
					</div>

					<CarouselControl
						style="color:black;maring:-25px!important;"
						direction="prev"
						bind:activeIndex
						items={eNewsBanner}
					/>
					<CarouselControl direction="next" bind:activeIndex items={eNewsBanner} />
				</Carousel>
			{/if}
		</div>
	{:else}
		{#each eNews as eNew}
			<div class="col-12 mb-4">
				<div class="alert alert-info">
					<!-- svelte-ignore a11y-invalid-attribute -->
					<a href={'#'} class="close" data-dismiss="alert">×</a>
					<h4 class="alert-heading">{eNew.titular}</h4>
					{@html eNew.cuerpo}
				</div>
			</div>
		{/each}
		<div class="col-12 mb-4">
			{#if eModulesFavorite.length > 0 && eTemplateBaseSetting.use_menu_favorite_module}
				<h4 class="mb-2" style="color: #012E46;">
					<b>&nbsp;<i class="fe fe-bookmark" /> Mis Favoritos</b>
				</h4>
			{/if}
			<h4 class="mb-2" style="color: #012E46;">
				<b>&nbsp;<i class="fe fe-layers" /> Mis Módulos</b>
			</h4>
			<div class="containerMenu" id="mybuscador">
				<div class="menuPanelCard">
					{#each eModules as eModule, i}
						<div
							data-nombre={eModule.nombre}
							on:click|preventDefault={(event) => actionGotoModule(event, eModule)}
							class="carbon-example flex-wrapper action-menu-entry"
						>
							<img src={eModule.icono} border="0" class="avatar-md iconosga" />
							<div class="inner-wrapper">
								<h4 class="mb-1" style="font-size: 14px;">
									<div class="tituloicon" data-inicial={eModule.nombre}>{eModule.nombre}</div>
								</h4>
								<span class="icondesc">{eModule.descripcion}</span>
							</div>
						</div>
					{/each}
				</div>
			</div>
		</div>
	{/if}
</div>
{#if eFiles.length > 0}
	<hr />
	<h3 class="m-2">Archivo Generales</h3>
	<div class="row">
		<div class="col-12 mb-4">
			<div class="containerFile">
				<ul class="menuFile">
					{#each eFiles as eFile}
						<li class="action-menu-entry" style="height: auto;">
							<a data-fancybox data-type="iframe" data-preload="false" href={eFile.archivo}>
								<div class="iconimage">
									<div class="pd">
										<!-- svelte-ignore a11y-missing-attribute -->
										<img src={eFile.icono} border="0" />
									</div>
								</div>
								<div class="iconname">
									<div class="pd">
										<!--<div class="tituloicon">{eFile.nombre}</div>-->
										<span class="icondesc">{eFile.nombre}</span>
									</div>
								</div>
							</a>
						</li>
					{/each}
				</ul>
			</div>
		</div>
	</div>
{/if}
{#if mOpenModal}
	<EncuentaGeneral mToggle={mToggleModal} mOpen={mOpenModal} aData={aDataModal} size="xl" />
{/if}

{#if actualiza_datos_pregrado}
	<ActualizaDatoGeneral
		mToggle={mToggleModalActualizaDato}
		mOpen={mOpenModalActualizaDato}
		aData={aDataActualizarDato}
		size="xl"
	/>
{/if}

{#if actualizar_sedes}
	<ActualizaSede
		mToggle={mToggleModalSedeElectoral}
		mOpen={mOpenModalSedeElectoral}
		aData={aDataSedeElectoral}
		size="xl"
	/>
{/if}

{#if mOpenModalGenerico2}
	<ModalInsigniaGeneral
		mToggle={mToggleModalGenerico2}
		mOpen={mOpenModalGenerico2}
		modalContent={modalDetalleContent2}
		{saveInsignia}
		title={modalTitle2}
		aData={aDataModal2}
		size="md"
		on:actionRun={actionRun2}
	/>
{/if}
{#if mOpenModalGenerico3}
	<ModalEvento
		mToggle={mToggleModalGenerico3}
		mOpen={mOpenModalGenerico3}
		size="md"
		on:actionRun={actionRun3}
	>
		<h4 slot="modal-content-header"><i class="mdi mdi-bullhorn" /> Evento disponible</h4>
		<div slot="modal-content-body">
			<img
				src={ePeriodoEventoDisponibleSinConfirmar.imagen}
				class="img-thumbnail"
				style="width: 100%;"
			/>

			{#if Object.keys(ePeriodoEventoDisponibleSinConfirmar.inscrito).length > 0}
				<div class="text-center mt-2">
					<h4 style="margin-bottom: 12px">¿Asistirás?</h4>
					<a
						class="btn btn-sm btn-mini transition-3d-hover"
						on:click={() => {
							inscribirseAsistenciaEvento(ePeriodoEventoDisponibleSinConfirmar, 1);
						}}
						style="color:white;background-color: #faa732; width: 40%;  border-radius: 3.2rem; font-size: 15px"
					>
						<i class="mdi mdi-check" /> Si
					</a>
					<a
						class="btn  btn-outline-secondary btn-sm btn-mini transition-3d-hover"
						on:click={() => {
							inscribirseAsistenciaEvento(ePeriodoEventoDisponibleSinConfirmar, 2);
						}}
						style="width: 40%;  border-radius: 3.2rem; font-size: 15px"
					>
						<i class="mdi mdi-close" /> No
					</a>
				</div>
			{:else}
				<div class="text-center">
					<a href="/alu_eventos/{ePeriodoEventoDisponibleSinConfirmar.id}" class="btn btn-primary"
						><i class="bi bi-plus" /> Ver más</a
					>
				</div>
			{/if}
		</div>
	</ModalEvento>
{/if}

{#if mOpenModalEncuestaSilaboRespondida}
	<ModalEncuestaSilabo
		mToggle={mToggleModalEncuestaSilaboRespondida}
		mOpen={mOpenModalEncuestaSilaboRespondida}
		size="md"
		on:actionRun={actionRun4}
	>
		<div slot="modal-content-body">
			<p class="text-center">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					width="130.000"
					height="130.000"
					viewBox="0 0 150.829 137.786"
				>
					<g id="Grupo_1" data-name="Grupo 1" transform="translate(-189.374 -334.373)">
						<path
							id="Trazado_1"
							data-name="Trazado 1"
							d="M340.2,447.413c-.9,3.086-1.374,6.376-2.763,9.222-5,10.254-13.444,15.434-24.835,15.479-21.237.085-42.474.024-63.711.024q-15.964,0-31.929,0c-8.58-.015-15.884-3.038-21.249-9.818-6.786-8.577-8.369-18.221-3.567-28.1,4.016-8.266,8.971-16.078,13.569-24.056q17.723-30.755,35.49-61.485c4.306-7.478,10.508-12.192,19.062-13.863,9.7-1.895,21.137,2.531,26.335,10.915,5.574,8.99,10.753,18.226,16.053,27.385,10.9,18.827,21.728,37.692,32.66,56.5A35.983,35.983,0,0,1,340.2,443ZM264.6,459.99q23.829,0,47.658.006c4.516,0,8.5-1.279,11.648-4.649,4.707-5.039,5.393-11.823,1.8-18.047q-19.016-32.965-38.058-65.916C284.095,365.236,280.674,359,276.886,353c-3.058-4.844-7.8-6.862-13.494-6.334-5.306.491-8.99,3.4-11.612,7.957q-18.735,32.534-37.548,65.023c-3.7,6.4-7.528,12.74-10.989,19.27-2.588,4.884-2.069,9.887.947,14.514,3.052,4.681,7.579,6.568,13.042,6.564Q240.915,459.976,264.6,459.99Z"
							transform="translate(0 0)"
							fill="#fc7e00"
						/>
						<path
							id="Trazado_2"
							data-name="Trazado 2"
							d="M379.2,452.114c-.632,10.865-1.232,21.182-1.83,31.5a39.271,39.271,0,0,1-.253,4.242,5.648,5.648,0,0,1-5.724,4.709,5.42,5.42,0,0,1-5.5-4.738c-.434-3.839-.572-7.712-.812-11.572-.49-7.87-.933-15.744-1.452-23.612-.434-6.589,5.436-11.191,11.076-8.63C377.847,445.444,379.333,448.313,379.2,452.114Z"
							transform="translate(-106.642 -66.67)"
							fill="#1c3247"
						/>
						<path
							id="Trazado_3"
							data-name="Trazado 3"
							d="M364.133,591.748a7.763,7.763,0,0,1,7.77-7.714,7.711,7.711,0,0,1-.152,15.419A7.728,7.728,0,0,1,364.133,591.748Z"
							transform="translate(-106.969 -152.816)"
							fill="#1c3247"
						/>
					</g>
				</svg>
			</p>
			<p class="text-center info px-4" style="font-size: 16px">
				Responde las encuestas de <b style="color:#182F44">CADA UNA</b> de tus materias, en el
				módulo <b style="color:#182F44">MIS MATERIAS</b>, para estar al tanto de tus calificaciones
				previo a los exámenes finales.
			</p>
			<p class="text-center info px-4 mt-2">
				<a
					class="btn btn-sm btn-mini transition-3d-hover"
					on:click={() => {
						goto('/alu_materias');
					}}
					style="color:white;background-color: #faa732; width: 40%;  border-radius: 3.2rem; font-size: 15px"
				>
					Responder
				</a>
			</p>
		</div>
	</ModalEncuestaSilabo>
{/if}

{#if mOpenModalSeccion && eInscripcion.seccion}
	<Modal
		isOpen={mOpenModalSeccion}
		toggle={mToggleModalSeccion}
		size="sm"
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable"
		backdrop="static"
	>
		<ModalBody>
			<div class="text-center">
				{#if eInscripcion.modalidad}
					<h3 class="texto-blue">
						<span class="border border-2 border-left me-2 border-warning" />Modalidad {eInscripcion
							.modalidad.nombre}
					</h3>
				{/if}
				<img src={eInscripcion.seccion.imagen} width="139px" height="110px" />
				<p class="text-muted">
					¡<b class="text-primary" style="color: #18113c !important">Hola {ePersona.nombre_minus}</b
					>, usted se encuentra en la sección
					<b class="text-primary" style="color: #18113c !important">{eInscripcion.seccion.nombre}</b
					>!
				</p>
				<button
					class="btn btn-warning btn-sm mt-2 rounded-pill px-6 text-white"
					on:click={() => {
						mOpenModalSeccion = !mOpenModalSeccion;
					}}>Cerrar</button
				>
			</div>
		</ModalBody>
	</Modal>
{/if}

<style>
	.btn-mini {
		padding-top: 3px;
		padding-bottom: 3px;
		padding-left: 3px;
		padding-right: 3px;
		font-size: 10.5px;
		-webkit-border-radius: 3px;
		-moz-border-radius: 3px;
		border-radius: 3px;
	}

	.no-border {
		border: 0 !important;
	}

	body {
		-webkit-tap-highlight-color: rgba(0, 0, 0, 0);
	}
	/*MENU PRINCIPAL PANEL*/
	.pd {
		padding: 5px 15px 15px 15px;
	}
	.menuPanelCard {
		list-style: none;
		margin: 0em !important;
		padding: 0px !important;
		padding-left: 10px !important;
		padding-right: 10px !important;
		display: grid;
		grid-gap: 6px;
		grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
		/*grid-template-columns: 1fr 1fr 1fr 1fr 1fr;*/
		font-size: 12px;
	}

	.menuPanelCard .carbon-example {
		border: 1px solid #e3e3e3;
	}

	.menuPanelCard > .carbon-example:hover {
		background: #eff7ff;
		cursor: pointer;
		box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
	}

	.menuPanel {
		list-style: none;
		margin: 0em !important;
		padding: 0px !important;
		padding-left: 10px !important;
		padding-right: 10px !important;
		display: grid;
		grid-gap: 15px;
		grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
	}

	.menuPanel > li {
		/*border: 1px solid #ffe066;*/
		border-radius: 5px;
		display: flex;
		flex-direction: column;
		background: #fff;
		border: 1px solid #e3e3e3;
		border-radius: 15px 15px;
		vertical-align: middle;
		text-align: center;
	}

	.menuPanel > li:hover {
		background: #eff7ff;
		cursor: pointer;
		box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
	}

	/*.menuPanel > li:hover .pd > img {*/
	/*    filter: brightness(0) invert(1);*/
	/*}*/

	/*.menuPanel > li:hover .tituloicon {*/
	/*    color: #FE9900;*/
	/*}*/

	/*.menuPanel > li:hover .icondesc {*/
	/*    color: white;*/
	/*}*/

	.menuPanel .iconimage {
		width: 100%;
		text-align: center;
		padding-top: 10px;
	}

	.menuPanel .iconimage img {
		height: 80px;
	}

	.menuPanel .iconname {
		font-weight: bold;
		width: 100%;
		/*position: absolute;*/
		bottom: 0;
		text-align: center;
		font-size: 14px;
		line-height: 10px;
	}

	.menuPanel .tituloicon {
		font-size: 15px;
		margin: 0;
		font-family: inherit;
		font-weight: bold !important;
		line-height: 20px;
		color: inherit;
		text-rendering: optimizelegibility;
	}

	.menuPanel .icondesc {
		font-weight: normal;
		font-size: 10px;
		line-height: 5px;
	}

	.menuPanelFavoritos {
		list-style: none;
		margin: 0em !important;
		padding: 0px !important;
		padding-left: 10px !important;
		padding-right: 10px !important;
		display: grid;
		grid-gap: 15px;
		grid-template-columns: repeat(auto-fill, minmax(165px, 1fr));
	}

	.menuPanelFavoritos > li {
		display: flex;
		flex-direction: column;
		background: #fff;
		border: 1px solid #e3e3e3;
		border-radius: 15px 15px;
		vertical-align: middle;
		text-align: center;
	}

	.menuPanelFavoritos .iconimage {
		width: 100%;
		text-align: center;
		padding-top: 10px;
	}

	.menuPanelFavoritos .iconimage img {
		height: 65px;
	}

	.menuPanelFavoritos .iconname {
		font-weight: bold;
		width: 100%;
		/*position: absolute;*/
		bottom: 0;
		text-align: center;
		font-size: 14px;
		line-height: 10px;
	}

	.menuPanelFavoritos .tituloicon {
		font-size: 15px;
		margin: 0;
		font-family: inherit;
		font-weight: bold !important;
		line-height: 20px;
		color: inherit;
		text-rendering: optimizelegibility;
	}

	.menuPanelFavoritos .icondesc {
		font-weight: normal;
		font-size: 10px;
		line-height: 5px;
	}

	.menuPanelFavoritos > li:hover {
		background: #eff7ff;
		cursor: pointer;
		box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
	}
	.containerFile {
		display: grid;
		grid-template-columns: repeat(12, [col-start] 1fr);
		grid-gap: 20px;
	}

	.containerFile > * {
		grid-column: col-start / span 12;
	}

	.menuFile {
		list-style: none;
		margin: 0em !important;
		padding: 0px !important;
		padding-left: 10px !important;
		padding-right: 10px !important;
		display: grid;
		grid-gap: 15px;
		grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
	}

	.menuFile > li {
		/*border: 1px solid #ffe066;*/
		/*border-radius: 5px;*/
		display: flex;
		flex-direction: column;
		background: #fff;
		border: 1px solid #e3e3e3;
		border-radius: 15px 15px;
		vertical-align: middle;
		text-align: center;
	}

	.menuFile > li:hover {
		/*background: #999;*/
		/*background: #9cb539;*/
		/*background: #13c2c2;*/
		/*background: #00cfdd;*/
		background: rgba(90, 141, 238, 0.15);
		color: white;
		/*color: #5a8dee;*/
		cursor: pointer;

		box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
		/*border: 2.5px solid #859a2f;*/
		/*background-image: linear-gradient(to bottom, #038fde , #20C997);*/
	}

	.menuFile .iconimage {
		width: 100%;
		text-align: center;
		padding-top: 10px;
	}

	.menuFile .iconimage img {
		height: 80px;
	}

	.menuFile .iconname {
		font-weight: bold;
		width: 100%;
		/*position: absolute;*/
		bottom: 0;
		text-align: center;
		font-size: 14px;
		line-height: 10px;
	}

	.menuFile .icondesc {
		font-weight: normal;
		font-size: 10px;
		line-height: 5px;
	}

	.carbon-example {
		padding: 8px;
		background-color: #fff;
		/*width: 295px;*/
		/*width: 215px;*/
		height: 90px;
		box-sizing: border-box;
		border-radius: 6px;
		-webkit-box-align: start;
		-ms-flex-align: start;
		-webkit-align-items: flex-start;
		-moz-align-items: flex-start;
		align-items: flex-start;
		position: relative;
		z-index: 5;
		/*box-shadow: 0 2px 20px 0 rgba(0, 0, 0, 0.1);*/
		margin-top: 6px;
		border: 1px solid #e3e3e3;
	}

	.carbon-example img {
		margin-right: 9px;
		border-right: 1.5px solid #e3e3e3;
		max-width: 125px;
		padding-right: 8px;
		width: 51px;
	}

	.carbon-example .inner-wrapper {
		text-align: left;
	}

	.carbon-example .inner-wrapper p {
		font-size: 12px;
		line-height: 1.33;
		margin: 8px 0;
	}

	.carbon-example .inner-wrapper p.fine-print {
		font-size: 8px;
		color: #c5cdd0;
		line-height: 1.25;
		text-transform: uppercase;
		font-weight: 500;
	}

	.flex-wrapper {
		display: -webkit-box;
		display: -webkit-flex;
		display: -moz-flex;
		display: -ms-flexbox;
		display: flex;
		-webkit-box-align: center;
		-ms-flex-align: center;
		-webkit-align-items: center;
		-moz-align-items: center;
		align-items: center;
		/*-webkit-box-pack: justify;*/
		/*-ms-flex-pack: justify;*/
		/*-webkit-justify-content: space-between;*/
		/*-moz-justify-content: space-between;*/
		/*justify-content: space-between;*/
	}

	@media screen and (max-width: 991px) {
		.flex-wrapper.two-col {
			display: block;
			text-align: center;
		}
	}

	.flex-wrapper.two-col > * {
		width: 50%;
	}

	.flex-wrapper.two-col > *:first-of-type {
		padding-right: 130px;
	}

	@media screen and (max-width: 991px) {
		.flex-wrapper.two-col > * {
			width: 100%;
		}

		.flex-wrapper.two-col > *:first-of-type {
			padding-right: 0;
		}
	}

	.flex-wrapper.two-col.reversed > *:first-of-type {
		order: 2;
		padding-right: 0;
	}

	@media screen and (min-width: 992px) {
		.flex-wrapper.two-col.reversed > *:first-of-type {
			padding-left: 130px;
		}
	}

	.flex-wrapper.three-col {
		text-align: left;
		-webkit-box-align: start;
		-ms-flex-align: start;
		-webkit-align-items: flex-start;
		-moz-align-items: flex-start;
		align-items: flex-start;
		margin-top: 40px;
	}

	@media screen and (max-width: 767px) {
		.flex-wrapper.three-col {
			-webkit-flex-wrap: wrap;
			-moz-flex-wrap: wrap;
			-ms-flex-wrap: wrap;
			flex-wrap: wrap;
		}
	}

	.flex-wrapper.three-col > * {
		width: 33.3%;
	}

	@media screen and (max-width: 767px) {
		.flex-wrapper.three-col > * {
			width: 100%;
		}
	}

	@media screen and (min-width: 768px) {
		.flex-wrapper.three-col li {
			padding-left: 20px;
			padding-right: 20px;
		}

		.flex-wrapper.three-col li:first-child {
			padding-left: 0;
		}

		.flex-wrapper.three-col li:last-child {
			padding-right: 0;
		}
	}

	.flex-wrapper.three-col .flex-wrapper {
		-webkit-box-align: start;
		-ms-flex-align: start;
		-webkit-align-items: flex-start;
		-moz-align-items: flex-start;
		align-items: flex-start;
		margin-top: 0;
	}

	@media screen and (max-width: 767px) {
		.flex-wrapper.three-col .flex-wrapper {
			-webkit-box-pack: center;
			-ms-flex-pack: center;
			-webkit-justify-content: center;
			-moz-justify-content: center;
			justify-content: center;
		}

		.flex-wrapper.three-col .flex-wrapper:not(:first-of-type) {
			margin-top: 40px;
		}
	}

	.flex-wrapper.three-col .flex-wrapper .icon {
		top: 0;
		transform: none;
	}
	.search-icon:hover {
		transform: rotate(360deg) scale(0.8);
	}
</style>
