<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET,apiPOSTFormData } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';
	import ModuleError from './_Errors.svelte';
	import FilePond, { registerPlugin, supported } from 'svelte-filepond';
	export const load: ({fetch}: { fetch: any }) => Promise<{ redirect: string; status: number } | string | { redirect: string; status: number } | { redirect: string; status: number } | { props: { habilitar_adicionar_propuesta: boolean; mensajesmaterias: string; grupo_seleccionado: any[]; lista_tutorias_individuales: any[]; message_error: any; grupo: any[]; detallecalificacion: any[]; puede_solicitar_prorroga: boolean; solicitudes_prorroga: any[]; puede_subir_correccion_revision_tribunal: boolean; solicitudingreso: any[]; es_en_pareja: boolean; historial_firma: any[]; cronograma: any[]; hoy: any; tematitulacionposgradomatricula_serializers: any[]; ePersona: any[]; lista_tutorias_pareja: any[]; mensaje3: string; is_error: boolean; mensaje1: string; disponible: boolean; mensaje2: string; puede: boolean; mostrar_aviso: boolean; disponible_elejirTutor: boolean; profesores_disponibles: any[]; revisiones_serializer: any[]; propuestas_ensayo: any[]; puede2: boolean; configuracion_programa_etapa: any[]; prorroga_activa: boolean; matricula: any[]; tiene_notas_complexivo: boolean; tematitulacionposgradomatriculacabecera_serializers: any[] } }> = async ({ fetch }) => {
		let ePersona = [];
		let tematitulacionposgradomatricula_serializers = [];
		let es_en_pareja = false;
		let tiene_notas_complexivo = false;
		let historial_firma = [];
		let tematitulacionposgradomatriculacabecera_serializers = [];
		let lista_tutorias_individuales = [];
		let lista_tutorias_pareja = [];
		let cronograma = [];
		let grupo = [];
		let solicitudingreso = [];
		let matricula = [];
		let detallecalificacion = [];
		let configuracion_programa_etapa = [];
		let profesores_disponibles = [];
		let propuestas_ensayo = [];
		let grupo_seleccionado = [];
		let puede = false;
		let puede2 = false;
		let disponible_elejirTutor = false;
		let disponible = false;
		let prorroga_activa = false;
		let puede_solicitar_prorroga = false;
		let mensaje1 = '';
		let mensaje2 = '';
		let mensaje3 = '';
		let mensajesmaterias = '';
		let mostrar_aviso = false;
		let habilitar_adicionar_propuesta = false;
		let solicitudes_prorroga = [];
		let revisiones_serializer = [];
		let puede_subir_correccion_revision_tribunal = false;
		let hoy = null;
		let is_error = false;
		let message_error = undefined;
		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {});
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (errors.length > 0) {
				addToast({
					type: 'error',
					header: 'Ocurrio un error',
					body: errors[0].error
				});
				return {
					status: 302,
					redirect: '/'
				};
			} else {
				if (!res.isSuccess) {
					message_error = res.message ;
					is_error = true;
					if (!res.module_access) {
						if (res.redirect) {
							if (res.token) {
								return (window.location.href = `${connectionToken}&ret=/${res.redirect}`);
							} else {

								addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
								return {
									status: 302,
									redirect: `${res.redirect}`
								};
							}
						} else {
							addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
							return {
								status: 302,
								redirect: '/'
							};
						}
					}
				} else {

					ePersona = res.data['ePersona'];
					tematitulacionposgradomatricula_serializers =
						res.data['tematitulacionposgradomatricula_serializers'];
					tematitulacionposgradomatriculacabecera_serializers =
						res.data['tematitulacionposgradomatriculacabecera_serializers'];
					configuracion_programa_etapa = res.data['configuracion_programa_etapa'];
					historial_firma = res.data['historial_firma'];
					lista_tutorias_individuales = res.data['lista_tutorias_individuales'];
					lista_tutorias_pareja = res.data['lista_tutorias_pareja'];
					cronograma = res.data['cronograma'];
					matricula = res.data['matricula'];
					profesores_disponibles = res.data['profesores_disponibles'];
					grupo = res.data['grupo'];
					solicitudingreso = res.data['solicitudingreso'];
					disponible_elejirTutor = res.data['disponible_elejirTutor'];
					disponible = res.data['disponible'];
					prorroga_activa = res.data['prorroga_activa'];
					puede_solicitar_prorroga = res.data['puede_solicitar_prorroga'];
					habilitar_adicionar_propuesta = res.data['habilitar_adicionar_propuesta'];
					es_en_pareja = res.data['es_en_pareja'];
					detallecalificacion = res.data['detallecalificacion'];
					tiene_notas_complexivo = res.data['tiene_notas_complexivo'];
					puede = res.data['puede'];
					puede2 = res.data['puede2'];
					mensaje1 = res.data['mensaje1'];
					mensaje2 = res.data['mensaje2'];
					mensaje3 = res.data['mensaje3'];
					mensajesmaterias = res.data['mensajesmaterias'];
					mostrar_aviso = res.data['mostrar_aviso'];
					propuestas_ensayo = res.data['propuestas_ensayo'];
					grupo_seleccionado = res.data['grupo_seleccionado'];
					solicitudes_prorroga = res.data['solicitudes_prorroga'];
					revisiones_serializer = res.data['revisiones_serializer'];
					hoy = res.data['hoy'];
					puede_subir_correccion_revision_tribunal =
						res.data['puede_subir_correccion_revision_tribunal'];
				}

				if (!res.isSuccess) {
					message_error = res.message;
					is_error = true;
				} else {
					message_error = '';
					is_error = false;
				}
			}
		}
		return {
			props: {
				ePersona,
				tematitulacionposgradomatricula_serializers,
				tematitulacionposgradomatriculacabecera_serializers,
				lista_tutorias_individuales,
				lista_tutorias_pareja,
				cronograma,
				matricula,
				profesores_disponibles,
				configuracion_programa_etapa,
				grupo,
				solicitudingreso,
				detallecalificacion,
				historial_firma,
				es_en_pareja,
				tiene_notas_complexivo,
				disponible_elejirTutor,
				disponible,
				habilitar_adicionar_propuesta,
				puede,
				puede2,
				mensaje1,
				mensaje2,
				mensaje3,
				mensajesmaterias,
				mostrar_aviso,
				propuestas_ensayo,
				grupo_seleccionado,
				solicitudes_prorroga,
				puede_solicitar_prorroga,
				prorroga_activa,
				revisiones_serializer,
				puede_subir_correccion_revision_tribunal,
				hoy,
				message_error,
				is_error
			}
		};
	};
</script>

<script lang="ts">
	import { onMount } from 'svelte';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { navigating } from '$app/stores';
	import Swal from 'sweetalert2';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import OffCanvasGenerico from '$components/Alumno/OffCanvasModal.svelte';
	import seleccionarTutor from './_selecciontutor.svelte';
	import detalleTutor from './_instrucciónFormalModal.svelte';
	import HistorialAprobacion from './_historial.svelte';
	import HistorialAprobacionTutor from './_historialAprobacionTutor.svelte';
	import DetalleRevisionTribunal from './_detallerevisiontribunal.svelte';
	import FormAgregarPropuestaTitulacion from './_formagregartema.svelte';
	import { addNotification } from '$lib/store/notificationStore';
	import { converToDecimal } from '$lib/formats/formatDecimal';
	import { encodeQueryString } from '$lib/helpers/baseHelper';
	import {
		Button,
		Icon,
		Modal,
		ModalBody,
		ModalFooter,
		ModalHeader,
		Tooltip,
		Alert,
		Badge,
		ButtonDropdown,
		DropdownItem,
		DropdownMenu,
		DropdownToggle,
		Form,
		FormGroup,
		Input,
		Label,
		FormText,
		Offcanvas
	} from 'sveltestrap';
	import { each, element, group_outros, is_empty } from 'svelte/internal';
	import { variables } from '$lib/utils/constants';
	import { stringify } from 'postcss';
	import Formagregardocensayo from './_formagregardocensayo.svelte';
	import FormAgregarArchivoFinal from './_formaddarchivofinal.svelte';
	import Formeditardocensayo from './_formeditardocensayo.svelte';
	import FormSeleccionarGrupoExaComplexivo from './_formaddexagrupocomplexivo.svelte';
	import FormAddActaFirmada from './_formaddactafirmadacomplexivo.svelte';
	import FormAddAvanceTutoriaPosgrado from './_formaddavancetutoriaposgrado.svelte';
	import FormAddCorreccionRevisionTribunalDoc from './_formaddcorrecciontribunal.svelte';
	import FormEditCorreccionRevisionTribunalDoc from './_formeditDocCorrecciontribunal.svelte';
	import FormSolicitudIngresoTitulacion from './_formSolicitudIngresoTitulacion.svelte';
	import FormSolicitudIngresoTitulacionSubirDoc from './_form_subir_doc_ingreso_titulacion.svelte';
	import FormSolicitudIngresoTitulacionToken from './_formSolicitudIngresoTitulacionToken.svelte';
	import FormAddDocFinalTitulacion from './_formadddocfinaltitulacionposgrado.svelte';
	import FormAddDocumentoFinalTitulacion from './_formadddocumentofinaltitulacionposgrado.svelte';
	import DetalleTutoriaPosgrado from './_detalletutoriaposgrado.svelte';
	import HistorialSolicitudProrrogaPropuestaTitulacion from './_historiasolicitudprorrogapropuestatitulacion.svelte';
	import FormSolicitudProrrogapropuestatitulacion from './_formsolicitudprorrogatitulacion.svelte';

	let valor = false;
	export let tematitulacionposgradomatricula_serializers;
	export let tematitulacionposgradomatriculacabecera_serializers;
	export let cronograma;
	export let lista_tutorias_individuales;
	export let lista_tutorias_pareja;
	export let configuracion_programa_etapa;
	export let grupo;
	export let solicitudingreso;
	export let profesores_disponibles;
	export let matricula;
	export let historial_firma;
	export let es_en_pareja;
	export let tiene_notas_complexivo;
	export let disponible_elejirTutor;
	export let disponible;
	export let habilitar_adicionar_propuesta;
	export let puede;
	export let puede2;
	export let mensaje1;
	export let mensaje2;
	export let mensaje3;
	export let mensajesmaterias;
	export let mostrar_aviso;
	export let detallecalificacion;
	export let propuestas_ensayo;
	export let grupo_seleccionado;
	export let ePersona;
	export let solicitudes_prorroga;
	export let puede_solicitar_prorroga;
	export let prorroga_activa;
	export let revisiones_serializer;
	export let puede_subir_correccion_revision_tribunal;
	export let hoy;
	export let is_error;
	export let message_error;
	let aDataModal = {};
	let aplacement = '';
	let modalDetalleOffCanvasContent;
	let modalDetalleContent;
	let mOpenModalGenerico = false;
	let mOpenOffCanvasGenerico = false;
	let modalTitle = '';

	//Formulario firma solicitud
	let mSizeFirmaSolicitud = 'lg';
	let mOpenFirmaSolicitud = false;
	const mToggleFirmaSolicitud = () => (mOpenFirmaSolicitud = !mOpenFirmaSolicitud);
	let titleFirmaSolicitud;
	let pondFirmaSolicitud;
	let nameFirmaSolicitud = 'fileFirmaSolicitud';
	let ePassword = '';

	let titleFirmaSolicitudSign;
	let pondFirmaSolicitudSign;
	let nameFirmaSolicitudSign = 'fileFirmaSolicitudSign';


	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);
	const mToggleOffCanvasGenerico = () => (mOpenOffCanvasGenerico = !mOpenOffCanvasGenerico);
	let itemsBreadCrumb = [
		{
			text: 'Titulación Posgrado',
			active: true,
			href: undefined
		}
	];
	let backBreadCrumb = {
		href: '/',
		text: 'Atrás'
	};
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {
		ocultar_acordion();
	});

	const loadAjax = async (data, url, method = undefined) =>
		new Promise(async (resolve, reject) => {
			if (method === undefined) {
				const [res, errors] = await apiPOST(fetch, url, data);
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
			} else {
				const [res, errors] = await apiGET(fetch, url, data);
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
			}
		});

	const loadInitial = () =>
		new Promise((resolve, reject) => {
			loading.setLoading(true, 'Cargando, espere por favor...');
			loadAjax({}, 'alumno/tematitulacion_posgrado', 'GET')
				.then((response) => {
					if (response.value.isSuccess) {
						ePersona = response.value.data['ePersona'];
						tematitulacionposgradomatricula_serializers = response.value.data['tematitulacionposgradomatricula_serializers'];
						tematitulacionposgradomatriculacabecera_serializers = response.value.data['tematitulacionposgradomatriculacabecera_serializers'];
						cronograma = response.value.data['cronograma'];
						lista_tutorias_individuales = response.value.data['lista_tutorias_individuales'];
						lista_tutorias_pareja = response.value.data['lista_tutorias_pareja'];
						configuracion_programa_etapa = response.value.data['configuracion_programa_etapa'];
						matricula = response.value.data['matricula'];
						profesores_disponibles = response.value.data['profesores_disponibles'];
						grupo = response.value.data['grupo'];
						solicitudingreso = response.value.data['solicitudingreso'];
						historial_firma = response.value.data['historial_firma'];
						es_en_pareja = response.value.data['es_en_pareja'];
						detallecalificacion = response.value.data['detallecalificacion'];
						tiene_notas_complexivo = response.value.data['tiene_notas_complexivo'];
						disponible_elejirTutor = response.value.data['disponible_elejirTutor'];
						disponible = response.value.data['disponible'];
						habilitar_adicionar_propuesta = response.value.data['habilitar_adicionar_propuesta'];
						puede = response.value.data['puede'];
						puede2 = response.value.data['puede2'];
						mensaje1 = response.value.data['mensaje1'];
						mensaje2 = response.value.data['mensaje2'];
						mensaje3 = response.value.data['mensaje3'];
						mensajesmaterias = response.value.data['mensajesmaterias'];
						mostrar_aviso = response.value.data['mostrar_aviso'];
						propuestas_ensayo = response.value.data['propuestas_ensayo'];
						grupo_seleccionado = response.value.data['grupo_seleccionado'];
						solicitudes_prorroga = response.value.data['solicitudes_prorroga'];
						puede_solicitar_prorroga = response.value.data['puede_solicitar_prorroga'];
						prorroga_activa = response.value.data['prorroga_activa'];
						revisiones_serializer = response.value.data['revisiones_serializer'];
						hoy = response.value.data['hoy'];
						puede_subir_correccion_revision_tribunal = response.value.data['puede_subir_correccion_revision_tribunal'];
						resolve({
							error: false,
							value: true
						});
					} else {
						is_error = true;
						message_error = response.value.message
						reject({
							error: true,
							message: response.value.message
						});
					}
				})
				.catch((error) => {
					is_error = true;
					message_error = error.message
					reject({
						error: true,
						message: error.message
					});
				});
			loading.setLoading(false, 'Cargando, espere por favor...');
		});

	const toggleModalLoadFormAgregarPropuestaTitulacion = async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'addPropuestaTitulacion'
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
				aDataModal = res.data;
				modalDetalleContent = FormAgregarPropuestaTitulacion;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'AGREGAR PROPUESTA DE TITULACIÓN';
			}
		}
	};

	const toggleModalLoadFormAgregarDocFinalPosgrado = async (id_tutoria, id_tema) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'adddocfinaltitulacionposgrado',
			id_tutoria: id_tutoria,
			id: id_tema
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
				aDataModal = res.data;
				modalDetalleContent = FormAddDocFinalTitulacion;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'AGREGAR DOCUMENTO FINAL DE TITULACIÓN POSGRADO';
			}
		}
	};

	const toggleModalLoadFormAgregarDocumentoFinalPosgrado = async (id_tutoria, id_tema) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'adddocumentofinaltitulacionpormecanismo',
			id_tutoria: id_tutoria,
			id: id_tema
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
				aDataModal = res.data;
				modalDetalleContent = FormAddDocumentoFinalTitulacion;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'AGREGAR DOCUMENTOS FINAL DE TITULACIÓN POSGRADO';
			}
		}
	};

	const toggleModalLoadFormSolicitarProrrogaTitulacion = async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'addsolicitudprorrogaregistropropuestatitulacion'
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
				aDataModal = res.data;
				modalDetalleContent = FormSolicitudProrrogapropuestatitulacion;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'SOLICITUD DE PRÓRROGA DE REGISTRO DE PROPUESTA DE TITULACIÓN';
			}
		}
	};

	const EditarSolicitarProrrogaTitulacion = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'editsolicitudprorrogaregistropropuestatitulacion',
			id: id
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
				aDataModal = res.data;
				modalDetalleContent = FormSolicitudProrrogapropuestatitulacion;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'EDITAR SOLICITUD DE PRÓRROGA DE REGISTRO DE PROPUESTA DE TITULACIÓN';
			}
		}
	};

	const EliminarSolicitarProrrogaTitulacion = async (id) => {
		const mensaje = {
			title: `NOTIFICACIÓN`,
			text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
				ePersona.nombre_completo
			}, con esta acción usted eliminará su solicitud de prórroga de propuesta de titulación. ¿Está ${
				ePersona.es_mujer ? 'segura' : 'seguro'
			} de eliminar su solicitud?`,
			type: 'warning',
			icon: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonText: 'Si, seguro',
			cancelButtonText: 'No, cancelar'
		};
		Swal.fire(mensaje)
			.then(async (result) => {
				if (result.value) {
					loading.setLoading(true, 'Eliminando, espere por favor...');
					const [res, errors] = await apiPOST(fetch, 'alumno/tematitulacion_posgrado', {
						action: 'deletesolicitudprorrogapropuestatitulacion',
						id: id
					});
					loading.setLoading(false, 'Eliminando, espere por favor...');
					if (errors.length > 0) {
						addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
						goto('/');
					} else {
						if (!res.isSuccess) {
							addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
						} else {
							addToast({
								type: 'success',
								header: 'Exitoso',
								body: 'Se elimino correctamente la solicitud'
							});
							loadInitial();
						}
					}
				} else {
					addToast({
						type: 'info',
						header: 'Enhorabuena',
						body: 'Has cancelado la acción de eliminar la solicitud de prórroga de propuesta de titulación'
					});
				}
			})
			.catch((error) => {
				addToast({ type: 'error', header: 'Ocurrio un error', body: error });
			});
	};

	const toggleModalLoadFormAgregarAvanceTutoriaPosgrado = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'addavancetutoriaposgrado',
			id: id
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
				aDataModal = res.data;
				modalDetalleContent = FormAddAvanceTutoriaPosgrado;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'AGREGAR AVANCE TUTORÍA POSGRADO';
			}
		}
	};

	const toggleModalLoadFormAgregarCorreccionRevisionTribunal = async (id, es_pareja) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'addcorreccionrevisiontribunal',
			id: id,
			es_pareja: es_pareja
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
				aDataModal = res.data;
				modalDetalleContent = FormAddCorreccionRevisionTribunalDoc;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'AGREGAR CORRECCIÓN TRABAJO FINAL DE TITULACIÓN ';
			}
		}
	};

	const toggleModalLoadFormEditarCorreccionRevisionTribunal = async (id, es_pareja) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'editdoccorreccionrevisiontribunal',
			id: id,
			es_pareja: es_pareja
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
				aDataModal = res.data;
				modalDetalleContent = FormEditCorreccionRevisionTribunalDoc;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'EDITAR DOCUMENTO CORRECCIÓN TRABAJO FINAL DE TITULACIÓN ';
			}
		}
	};

	const toggleModalLoadFormSolicitudIngresoTitulacionElectronica = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'solicitudIngresoTitulacion',
			id: id,
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
				aDataModal = res.data;
				modalDetalleContent = FormSolicitudIngresoTitulacion;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'SOLICITUD INGRESO TITULACIÓN - FIRMA ';
			}
		}
	};

	const generar_pdf_solicitud_ingreso_titulacion = async (id) =>{
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'solicitudIngresoTitulacionToken',
			id: id,
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
				aDataModal = res.data;
				modalDetalleContent = FormSolicitudIngresoTitulacionToken;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'GENERAR SOLICITUD DE INGRESO A LA UNIDAD DE TITULACIÓN';
			}
		}
	};

	const toggleModalLoadFormEditarPropuestaTitulacion = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'editPropuestaTitulacion',
			id: id
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
				aDataModal = res.data;
				modalDetalleContent = FormAgregarPropuestaTitulacion;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'EDITAR PROPUESTA DE TITULACIÓN';
			}
		}
	};

	const toggleModalAddComponentePractico = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'adddocensayo',
			id: id
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
				aDataModal = res.data;
				modalDetalleContent = Formagregardocensayo;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'AGREGAR DOCUMENTO DEL COMPONENTE PRÁCTICO';
			}
		}
	};

	const toggleModalAddCorreccionTrabajoFinalPryTribunal = async (id, en_pareja) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'addarchivofinaltitulacion',
			id: id,
			en_pareja: en_pareja
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
				aDataModal = res.data;
				modalDetalleContent = FormAgregarArchivoFinal;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'ACTUALIZAR DOCUMENTO DE TITULACIÓN - FINAL';
			}
		}
	};

	const toggleModalAddActaFirmada = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'subir_acta_firmada',
			id: id
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
				aDataModal = res.data;
				modalDetalleContent = FormAddActaFirmada;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'SUBIR ACTA DE APROBACIÓN DE EXAMEN COMPLEXIVO FIRMADA ';
			}
		}
	};

	const toggleModalAddSolicitudIngresoTitulacion = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'subir_solicitud_ingreso_firmada',
			id: id
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
				aDataModal = res.data;
				modalDetalleContent = FormSolicitudIngresoTitulacionSubirDoc;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'SUBIR SOLICITUD DE INGRESO DE TITULACIÓN ';
			}
		}
	};

	const toggleModalSeleccionarGrupoExamenComplexivo = async (id_tema, id_configuracion) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'asignar_grupo_complexivo',
			id_tema: id_tema,
			id_configuracion: id_configuracion
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
				aDataModal = res.data;
				modalDetalleContent = FormSeleccionarGrupoExaComplexivo;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'SELECCIONAR GRUPO PARA RENDIR EXAMEN COMPLEXIVO';
			}
		}
	};

	const toggleModalEditDocFinalTitulacion = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'editdocfinaltitulacionposgrado',
			id: id
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
				aDataModal = res.data;
				modalDetalleContent = Formeditardocensayo;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'EDITAR DOCUMENTO FINAL DE TITULACIÓN';
			}
		}
	};

	const toggleModalEditDocComponentePractico = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'editdocensayo',
			id: id
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
				aDataModal = res.data;
				modalDetalleContent = Formeditardocensayo;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'EDITAR DOCUMENTO DEL COMPONENTE PRÁCTICO';
			}
		}
	};

	const toggleModalDetalleTutoriaPosgrado = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'detalletutoriaposgrado',
			id: id
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
				aDataModal = res.data;
				modalDetalleContent = DetalleTutoriaPosgrado;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'INFORMACIÓN DE LA TUTORÍA';
			}
		}
	};

	const toggleModalHistorialProrrogaPropuestaTitulacion = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'listarhistorialsolicitudprorrogapropuestatitulacion',
			id: id
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
				aDataModal = res.data;
				modalDetalleContent = HistorialSolicitudProrrogaPropuestaTitulacion;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'HISTORIAL DE SOLICITUD DE PRÓRROGA DE PROPUESTA DE TITULACIÓN';
			}
		}
	};

	const toggleModalHistorial = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'listarhistorial',
			id: id
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
				aDataModal = res.data;
				modalDetalleContent = HistorialAprobacion;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'Historial de aprobación de la propuesta de titulación';
			}
		}
	};

	const toggleModalHistorialAprobacionTutor = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'historialAprobacionTutor',
			id: id
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
				aDataModal = res.data;
				modalDetalleContent = HistorialAprobacionTutor;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'Historial de aprobación del tutor';
			}
		}
	};

	const toggleModalRevisionDetalle = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'detalle_revision_tribunal',
			id: id
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
				aDataModal = res.data;
				modalDetalleContent = DetalleRevisionTribunal;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'Revisión Tribunal';
			}
		}
	};

	const toggleDetalleTutor = async (id) => {
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'instruccionformaldocente',
			id: id
		});

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
				aDataModal = res.data;
				modalDetalleContent = detalleTutor;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'MÁS INFORMACIÓN DEL DOCENTE';
			}
		}
	};

	const toggleOffCanvasSeleccionarTutor = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'aprobar_rechazar_tutor_titulacion',
			id: id
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
				aDataModal = res.data;
				modalDetalleOffCanvasContent = seleccionarTutor;
				mOpenOffCanvasGenerico = !mOpenOffCanvasGenerico;
				aplacement = 'end';
				modalTitle = 'APROBAR / RECHAZAR TUTOR';
			}
		}
	};

	const eliminarPropuestaTema = async (id) => {
		const mensaje = {
			title: `NOTIFICACIÓN`,
			text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
				ePersona.nombre_completo
			}, con esta acción usted eliminará su propuesta de titulación. ¿Está ${
				ePersona.es_mujer ? 'segura' : 'seguro'
			} de eliminar su propuesta?`,
			type: 'warning',
			icon: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonText: 'Si, seguro',
			cancelButtonText: 'No, cancelar'
		};
		Swal.fire(mensaje)
			.then(async (result) => {
				if (result.value) {
					loading.setLoading(true, 'Eliminando, espere por favor...');
					const [res, errors] = await apiPOST(fetch, 'alumno/tematitulacion_posgrado', {
						action: 'deletepropuestatematitulacion',
						id: id
					});
					loading.setLoading(false, 'Eliminando, espere por favor...');
					if (errors.length > 0) {
						addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
						goto('/');
					} else {
						if (!res.isSuccess) {
							addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
						} else {
							addToast({
								type: 'success',
								header: 'Exitoso',
								body: 'Se elimino correctamente la propuesta de titulación'
							});
							loadInitial();
						}
					}
				} else {
					addToast({
						type: 'info',
						header: 'Enhorabuena',
						body: 'Has cancelado la acción de eliminar la propuesta de titulación'
					});
				}
			})
			.catch((error) => {
				addToast({ type: 'error', header: 'Ocurrio un error', body: error });
			});
	};

	const nextProccess = (value) => {
		if (value == 1) {
			loadInitial();
		}
	};

	const descargar_pdf_complexivo = async (id,variable) =>{
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'pdfactaaprobacionexamencomplexivo',
			id: id
		});

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

				let a = "https://sga.unemi.edu.ec"
				window.open(a+res.data.file_url, '_blank');

			}
		}
	};


	const actionRun = (event) => {
		mOpenModalGenerico = false;
		mOpenOffCanvasGenerico = false;
		const detail = event.detail;
		const action = detail.action;
		const value = detail.value;
		if (action == 'nextProccess') {
			loading.setLoading(false, 'Cargando, espere por favor...');
			nextProccess(value);
		}
	};

	function ocultar_acordion() {
		let obtener_elemento = document.querySelectorAll('.collapse');
		obtener_elemento.forEach((element) => {
			element.classList.remove('show');
		});
		let obtener_elemento2 = document.querySelectorAll('.accordion-button');
		obtener_elemento2.forEach((element) => {
			element.classList.add('collapsed');
		});
	}

	const downloadsoli = async (eSolicitud) => {
		//		let archivo =  variables.BASE_API + eSolicitud;
		//		console.log(archivo);
		console.log(eSolicitud);
		window.open(eSolicitud, '_blank');
	};


	const changetypeval2 = async (event) => {
		valor = event.target.checked;
		//		let inputElement1 = document.getElementById("id_firmararchivo");
		let inputfirma = document.getElementById('id_div_password');
		let inputsolicitud = document.getElementById('id_div_solicitud');
		let inputsolicitudsign = document.getElementById('id_div_solicitudsign');
		if (valor == true) {
			inputfirma.style.display = 'none';
			inputsolicitud.style.display = 'none';
			inputsolicitudsign.style.display = '';
		} else {
			inputfirma.style.display = '';
			inputsolicitud.style.display = '';
			inputsolicitudsign.style.display = 'none';
		}
	};


	const handleInit = () => {
		console.log('FilePond has initialised');
	};
	const handleAddFileFirmaSolicitud = (err, fileItem) => {
		console.log(pondFirmaSolicitud.getFiles());
		console.log('A file has been added', fileItem);
	};
	const handleAddFileFirmaSolicitudSign = (err, fileItem) => {
		console.log(pondFirmaSolicitudSign.getFiles());
		console.log('A file has been added', fileItem);
	};
	const closeFirmaSolicitudForm = () => {
		mOpenFirmaSolicitud = false;
	};
	const limpiarcampos = () => {
		pondFirmaSolicitud;
		pondFirmaSolicitudSign;
		ePassword = '';
	};
	const openFirmaSolicitud = async (id) => {
		let mensaje = ''
		limpiarcampos();
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'verificar_turno_firmar',
			id:id
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
				if (res.data.puede) {
							loading.setLoading(true, 'Cargando, espere por favor...');
							loading.setLoading(false, 'Cargando, espere por favor...');
							mSizeFirmaSolicitud = 'lg';
							mOpenFirmaSolicitud = true;
							titleFirmaSolicitud = 'Firma de solicitud de homologación';
				} else {
					const mensajeOtro = {
						title: `NOTIFICACIÓN`,
						html: res.data.mensaje,
						type: 'info',
						icon: 'info',
						showCancelButton: false,
						allowOutsideClick: false,
						confirmButtonColor: 'rgb(255, 154, 1)',
						confirmButtonText: `Aceptar`
					};
					Swal.fire(mensajeOtro)

			}
		}


		}
	};
	const saveFirmaSolicitud = async (id = null) => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmFirmaSolicitud = document.querySelector('#frmFirmaSolicitud');
		const formData = new FormData($frmFirmaSolicitud);

		let inputsolicitudcheck = document.getElementById('id_firmararchivo');

		if (inputsolicitudcheck.checked == true) {
			formData.append('action', 'subirarchivotoken');
		} else {
			formData.append('action', 'firmarelectronica');
		}

		formData.append('id', id);

		let password = document.getElementById('ePassword');

		if (inputsolicitudcheck.checked == true) {
			let fileDocumentoSign = pondFirmaSolicitudSign.getFiles();
			if (fileDocumentoSign.length == 0) {
				addNotification({
					msg: 'Debe subir el archivo de solicitud firmado con firma electrónica',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			if (fileDocumentoSign.length > 1) {
				addNotification({
					msg: 'Archivo de documento debe ser único',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			let eFileDocumentoSign = undefined;
			if (pondFirmaSolicitudSign && pondFirmaSolicitudSign.getFiles().length > 0) {
				eFileDocumentoSign = pondFirmaSolicitudSign.getFiles()[0];
			}
			formData.append('eFileSolicitudSignForm', eFileDocumentoSign.file);
		} else {
			if (password.value === null || password.value === undefined || password.value === '') {
				addNotification({
					msg: 'Llene el campo contraseña',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}

			let fileDocumento = pondFirmaSolicitud.getFiles();
			if (fileDocumento.length == 0) {
				addNotification({
					msg: 'Debe subir el archivo de su firma electrónica',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			if (fileDocumento.length > 1) {
				addNotification({
					msg: 'Archivo de documento debe ser único',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			let eFileDocumento = undefined;
			if (pondFirmaSolicitud && pondFirmaSolicitud.getFiles().length > 0) {
				eFileDocumento = pondFirmaSolicitud.getFiles()[0];
			}
			formData.append('eFileSolicitudForm', eFileDocumento.file);
		}

		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/tematitulacion_posgrado', formData);
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			if (!res.isSuccess) {
				//				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				const mensajeOtro1 = {
					title: `NOTIFICACIÓN`,
					html: `${res.message}`,
					type: 'error',
					icon: 'error',
					showCancelButton: false,
					allowOutsideClick: false,
					confirmButtonColor: 'rgb(255, 154, 1)',
					confirmButtonText: `Aceptar`
				};
				Swal.fire(mensajeOtro1).then(async (result) => {
					if (result.value) {
						mOpenFirmaSolicitud = true;
					}
				});
				if (!res.module_access) {
					goto('/');
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				loading.setLoading(false, 'Cargando, espere por favor...');
				mOpenFirmaSolicitud = false;
				limpiarcampos();
				const mensajeOtro = {
					title: `NOTIFICACIÓN`,
					html: `${res.message}`,
					type: 'info',
					icon: 'info',
					showCancelButton: false,
					allowOutsideClick: false,
					confirmButtonColor: 'rgb(255, 154, 1)',
				};
				goto('/alu_tematitulacionposgrado');

			}
		}
	};

</script>

<!-- mis componentes -->

<svelte:head>
	<title>Titulación Posgrado</title>
</svelte:head>
{#if !is_error}
<BreadCrumb title="TITULACIÓN POSGRADO" items={itemsBreadCrumb} back={backBreadCrumb} />
<div class="row-fluid ">
	{#if !puede}
		<!-- Dismissing alert -->
		<Alert color="info" dismissible>
			<strong>Aviso importante!</strong> <br />
			{mensaje1}{#if mensaje1 != ''}<br /> {/if}
			{mensaje2}{#if mensaje2 != ''}<br /> {/if}
			{mensaje3}{#if mensaje3 != ''}<br /> {/if}
			<!--{#if mostrar_aviso}-->
			<!--	{mensajesmaterias}-->
			<!--{/if}-->
		</Alert>
	<!--{:else if mensaje1.length > 0 || mensajesmaterias.length > 0}-->
	<!--	&lt;!&ndash; content here &ndash;&gt;-->
	<!--	<Alert color="danger" dismissible>-->
	<!--		<strong>Aviso importante!</strong> <br />-->
	<!--		{mensaje1}{#if mensaje1 != ''}<br /> {/if}-->
	<!--		&lt;!&ndash;{#if mostrar_aviso}&ndash;&gt;-->
	<!--		&lt;!&ndash;	{mensajesmaterias}&ndash;&gt;-->
	<!--		&lt;!&ndash;{/if}&ndash;&gt;-->
	<!--	</Alert>-->
	{:else if habilitar_adicionar_propuesta}
		<!-- content here -->
		<Alert color="info" dismissible>
			<strong>Aviso importante!</strong> <br />
			A continuación registre su propuesta de titulación, en la sección de
			<b>Registro propuesta de titulación.</b>
		</Alert>
	{:else if prorroga_activa}
		<!-- content here -->
		<Alert color="info" dismissible>
			<strong>Aviso importante!</strong> <br />
			A continuación registre su propuesta de titulación, en la sección de
			<b>Registro propuesta de titulación.</b>
		</Alert>
	{:else}
		<!-- content here -->
		<Alert color="warning" dismissible>
			<strong>Aviso importante!</strong> <br />
			El cronograma de registro de solicitud de propuesta de titulación, ha finalizado. <br />
			<small
				>Puede realizar una solicitud de prórroga de registro de propuesta de titulación en la
				sección de <b>Solicitud Prórroga propuesta de titulación.</b></small
			>
		</Alert>
	{/if}
</div>
<nav class="bs-stepper">
	<div class="nav nav-tabs bs-stepper-header shadow-sm" id="nav-tab" role="tablist">
		<button
			class="nav-link { solicitudingreso.status || tematitulacionposgradomatricula_serializers.status ? '' : 'active'}  step-trigger"
			id="nav-solic-tab"
			data-bs-toggle="tab"
			data-bs-target="#nav-solic"
			type="button"
			role="tab"
			aria-controls="nav-solic"
			aria-selected="true"
		>
			<span class="bs-stepper-circle">1</span>
			<span class="bs-stepper-label">Solicitud de ingreso </span>
		</button>
		<!-- else content here -->
				<div class="bs-stepper-line" />
		{#if matricula.tiene_propuesta_engrupo_y_no_tiene_solicitud }
			<button
				class="nav-link { solicitudingreso.status  ? 'active' : ''}  step-trigger"
				id="nav-propu-tab"
				data-bs-toggle="tab"
				data-bs-target="#nav-propu"
				type="button"
				role="tab"
				aria-controls="nav-home"
				aria-selected="true"
			>
				<span class="bs-stepper-circle">2</span>
				<span class="bs-stepper-label">Propuesta titulación</span>
			</button>


			<div class="bs-stepper-line" />
			{#if tematitulacionposgradomatricula_serializers.idmecanismotitulacion == 15 || tematitulacionposgradomatricula_serializers.idmecanismotitulacion == 21}
				{#if tematitulacionposgradomatricula_serializers.estadoaprobacion == 2}
					<!-- content here -->
					<button
						class="nav-link step-trigger"
						id="nav-complexivo-tab"
						data-bs-toggle="tab"
						data-bs-target="#nav-complexivo"
						type="button"
						role="tab"
						aria-controls="nav-complexivo"
						aria-selected="false"
					>
						<span class="bs-stepper-circle">3</span>
						<span class="bs-stepper-label">Complexivo</span>
					</button>
					<div class="bs-stepper-line" />
					<button
						class="nav-link step-trigger"
						id="nav-calificaciones-tab"
						data-bs-toggle="tab"
						data-bs-target="#nav-calificaciones"
						type="button"
						role="tab"
						aria-controls="nav-calificaciones"
						aria-selected="false"
					>
						<span class="bs-stepper-circle">4</span>
						<span class="bs-stepper-label">Calificaciones</span>
					</button>
				{/if}
			{:else if tematitulacionposgradomatricula_serializers.estadoaprobacion == 2}
				<!-- else content here -->
				<button
					class="nav-link step-trigger"
					id="nav-seguimiento_tutoria-tab"
					data-bs-toggle="tab"
					data-bs-target="#nav-seguimiento_tutoria"
					type="button"
					role="tab"
					aria-controls="nav-seguimiento_tutoria"
					aria-selected="false"
				>
					<span class="bs-stepper-circle">3</span>
					<span class="bs-stepper-label">Tutorias</span>
				</button>

				{#if es_en_pareja}
					<!-- content here -->
					{#if tematitulacionposgradomatriculacabecera_serializers.tutor}
						<!-- content here -->
						<div class="bs-stepper-line" />
						<button
							class="nav-link step-trigger"
							id="nav-tribunal-rev-tab"
							data-bs-toggle="tab"
							data-bs-target="#nav-tribunal-rev"
							type="button"
							role="tab"
							aria-controls="nav-tribunal-rev"
							aria-selected="false"
						>
							<span class="bs-stepper-circle">4</span>
							<span class="bs-stepper-label">Revisión tribunal</span>
						</button>

						<!-- else content here -->
						<div class="bs-stepper-line" />
						<button
							class="nav-link step-trigger"
							id="nav-sustentacion-tab"
							data-bs-toggle="tab"
							data-bs-target="#nav-sustentacion"
							type="button"
							role="tab"
							aria-controls="nav-sustentacion"
							aria-selected="false"
						>
							<span class="bs-stepper-circle">5</span>
							<span class="bs-stepper-label">Sustentación</span>
						</button>
					{/if}
				{:else if tematitulacionposgradomatricula_serializers.tutor}
					<!-- content here -->
					<div class="bs-stepper-line" />
					<button
						class="nav-link step-trigger"
						id="nav-tribunal-rev-tab"
						data-bs-toggle="tab"
						data-bs-target="#nav-tribunal-rev"
						type="button"
						role="tab"
						aria-controls="nav-tribunal-rev"
						aria-selected="false"
					>
						<span class="bs-stepper-circle">4</span>
						<span class="bs-stepper-label">Revisión tribunal</span>
					</button>

					<!-- else content here -->
					<div class="bs-stepper-line" />
					<button
						class="nav-link step-trigger"
						id="nav-sustentacion-tab"
						data-bs-toggle="tab"
						data-bs-target="#nav-sustentacion"
						type="button"
						role="tab"
						aria-controls="nav-sustentacion"
						aria-selected="false"
					>
						<span class="bs-stepper-circle">5</span>
						<span class="bs-stepper-label">Sustentación</span>
					</button>
				{/if}
			{/if}
		{/if}
	</div>
</nav>

<div class="container-fluid">
	<div class="tab-content bs-stepper-content mt-5" id="nav-tabContent">
		<div
			class="row tab-pane fade bs-stepper-pane  show { matricula.tiene_propuesta_engrupo_y_no_tiene_solicitud ? '' : 'active'} "
			id="nav-solic"
			role="tabpanel"
			aria-labelledby="nav-solic-tab"
		>
			<div class="card">
				<!-- Card -->
				<div class=" mb-5">
					<div class="container">
						<div class="row mt-5">
						<Alert color="info" dismissible>
							<strong>Información:</strong> <br/>
							 <p>Para el ingreso a la unidad de titulación primero registre su solicitud de ingreso con su firma electrónica.
								 <br><b>El mecanismo de titulación de la solicitud de ingreso y del registro de la propuesta de titulación deben coincidir.</b>
								 <br><b>Si realiza en pareja o en grupo su titulación verifique que hayan seleccionado el mismo mecanismo.</b></p>
							 <p>Puede generar la solicitud de ingreso a la unidad de titulación de dos formas:</p>
							 <p>1.- Generar la solicitud y firma electrónica por archivo.</p>
							 <p>2.- Generar el documento, descargar el archivo, firma electrónica por token  y subir el documento firmado. Previamente generado desde el sistema.</p>
						</Alert>
					</div>
					</div>
					{#if solicitudingreso.status}

						<div class="container">

							<div class="row mt-5">
								<div class="col">
									<!-- card -->
									<div class="card border shadow-none">
										<!-- card body -->
										<div class="card-body p-5">
											<!-- para -->
											<p class="lead text-dark font-italic fw-medium mb-0">Actualizar solicitud y firma manual por token</p>
										</div>
										<!-- card footer -->
										<div class="card-footer px-5 py-4">
											<div class="d-flex align-items-center">
												<div class="ms-3">
													<a href="Javascript:void(0);"
													   on:click={() => generar_pdf_solicitud_ingreso_titulacion()}
													   class="btn btn-secondary">Generar documento</a>
													<a href="Javascript:void(0);"
													   on:click={() => toggleModalAddSolicitudIngresoTitulacion()}
													   class="btn btn-warning">Subir documento firmado</a>

												</div>
											</div>

										</div>
									</div>
								</div>
								<div class="col">
									<div class="card border shadow-none">
										<!-- card body -->
										<div class="card-body p-5">
											<!-- para -->
											<p class="lead text-dark font-italic fw-medium mb-0">Actualizar solicitud y firma electrónica</p>
										</div>
										<!-- card footer -->
										<div class="card-footer px-5 py-4">
											<div class="d-flex align-items-center">
												<div class="ms-3">
													<a href="Javascript:void(0);"
													   on:click={() => toggleModalLoadFormSolicitudIngresoTitulacionElectronica()}
													   class="btn btn-success">Actualizar solicitud y firmar Electrònica</a>

												</div>
											</div>

										</div>
									</div>
								</div>
							</div>

							  <div class="card-body text-center" style="height: 50vh">
                                <span class="text-danger d-none text-left" id="helptext_error_acta"></span>
                                <iframe id="id_archivoacta" src="{variables.BASE_API}{solicitudingreso.archivo}" width="100%" style="height:50vh" frameborder="0"></iframe>
                            </div>

						</div>
					{:else}
						<div class="container">
							<div class="row mt-5">
								<div class="col">
									<!-- card -->
									<div class="card border shadow-none">
										<!-- card body -->
										<div class="card-body p-5">
											<!-- para -->
											<p class="lead text-dark font-italic fw-medium mb-0">Generación y firma
												manual por token</p>
										</div>
										<!-- card footer -->
										<div class="card-footer px-5 py-4">
											<div class="d-flex align-items-center">
												<div class="ms-3">
													<a href="Javascript:void(0);"
													   on:click={() => generar_pdf_solicitud_ingreso_titulacion()}
													   class="btn btn-secondary">Generar documento</a>
													<a href="Javascript:void(0);"
													   on:click={() => toggleModalAddSolicitudIngresoTitulacion()}
													   class="btn btn-warning">Subir documento firmado</a>

												</div>
											</div>

										</div>
									</div>
								</div>
								<div class="col">
									<div class="card border shadow-none">
										<!-- card body -->
										<div class="card-body p-5">
											<!-- para -->
											<p class="lead text-dark font-italic fw-medium mb-0">Generación y firma Electrónica</p>
										</div>
										<!-- card footer -->
										<div class="card-footer px-5 py-4">
											<div class="d-flex align-items-center">
												<div class="ms-3">
													<a href="Javascript:void(0);"
													   on:click={() => toggleModalLoadFormSolicitudIngresoTitulacionElectronica()}
													   class="btn btn-success">Generar solicitud y firmar</a>

												</div>
											</div>

										</div>
									</div>
								</div>
							</div>

						</div>
					{/if}


				</div>
				<!-- Card -->
			</div>
		</div>

		<div
			class="row tab-pane fade bs-stepper-pane  show  { matricula.tiene_propuesta_engrupo_y_no_tiene_solicitud ? 'active' : ''}  "
			id="nav-propu"
			role="tabpanel"
			aria-labelledby="nav-propu-tab"
		>
			<div class="card">
				<!-- Card -->
				<div class=" mb-5">
					<div class="row mt-5 ml-5">
						<div class="col-md-12">
							<h5 class="mb-0">
								[{cronograma.obtenerid}] - {cronograma.display}
							</h5>
							<div class="d-flex justify-content-between border-bottom py-2">
								<span>Fecha inicio</span>
								<span>{cronograma.fechainimaestrante} </span>
							</div>
							<div class="d-flex justify-content-between pt-2">
								<span>Fecha fin:</span>
								<span class="text-dark"> {cronograma.fechafinmaestrante} </span>
							</div>


						</div>
					</div>

					<div class="accordion-item mt-4 ">
						<h2 class="accordion-header" id="headingTwo_registro_titulacion">
							<button
								class="accordion-button"
								type="button"
								data-bs-toggle="collapse"
								data-bs-target="#collapseTwo_registro_titulacion"
								aria-expanded="true"
								aria-controls="collapseTwo_registro_titulacion"
							>
								Registro propuesta de titulación.
							</button>
						</h2>
						<div
							id="collapseTwo_registro_titulacion"
							class="accordion-collapse show "
							aria-labelledby="headingTwo_registro_titulacion"
							data-bs-parent="#accordionExample"
						>
							<div class="accordion-body">
								<!-- content here -->
								<div class="row-fluid">
									<div class="container">
										<h4 class="accordion-header"/>
										<!-- Card -->
									</div>
								</div>
								<div class="">
									<!-- Card -->
									<div class="mb-5">
										<!-- Card header -->

										{#if habilitar_adicionar_propuesta}
											<!-- content here -->
											{#if  puede && puede2}
												<div
													class="card-header d-flex align-items-center  justify-content-between card-header-height"
												>
													<a
														href="javascript:void(0)"
														class="btn btn-outline-white btn-sm"
														on:click={() => toggleModalLoadFormAgregarPropuestaTitulacion()}
														><i class="bi bi-plus-lg" /> Adicionar</a
													>
												</div>
											{/if}
										{:else if prorroga_activa}
											{#if tematitulacionposgradomatricula_serializers == null || tematitulacionposgradomatricula_serializers.length == 0}
												<div
													class="card-header d-flex align-items-center  justify-content-between card-header-height"
												>
													<a
														href="javascript:void(0)"
														class="btn btn-outline-white btn-sm"
														on:click={() => toggleModalLoadFormAgregarPropuestaTitulacion()}
														><i class="bi bi-plus-lg" /> Adicionar</a
													>
												</div>
											{:else}
												<!-- else content here -->
												{#if tematitulacionposgradomatricula_serializers.estadoaprobacion == 3}
													<a
														href="javascript:void(0)"
														class="btn btn-outline-white btn-sm"
														on:click={() => toggleModalLoadFormAgregarPropuestaTitulacion()}
														><i class="bi bi-plus-lg" /> Adicionar</a
													>
												{/if}
											{/if}
										{/if}

										<!-- Card body -->
										<div class="card-body">
											<!-- List group -->
											<ul class="list-group list-group-flush">
												<li class="list-group-item px-0 pt-0 ">
													<div class="row">
														<div class="col-auto">
															<div class="table-responsive">
																<!--border-0 table-invoice-->
																<table
																	class="table mb-0 text-nowrap table-hover table-bordered align-middle"
																>
																	<thead class="table-light">
																		<tr>
																			<th
																				scope="col"
																				class="border-top-0 text-center align-middle "
																				style="width: 400rem;">Tema</th
																			>
																			{#if tematitulacionposgradomatricula_serializers.sublinea !== null}
																				<th
																				scope="col"
																				class="border-top-0 text-center align-middle "
																				style="width: 200rem;"
																				>Linea/SubLinea
																			</th>
																			{/if}

																			<th
																				scope="col"
																				class="border-top-0 text-center align-middle "
																				style="width: 22rem;">Mecanismo Titulación</th
																			>
																			<th
																				scope="col"
																				class="border-top-0 text-center align-middle "
																				style="width: 22rem;">Estado</th
																			>
																			<th
																				scope="col"
																				class="border-top-0 text-center align-middle "
																				style="width: 22rem;">Historial de Aprobación</th
																			>
																			<th
																				scope="col"
																				class="border-top-0 text-center align-middle "
																				style="width: 22rem;"
																				>Archivo <i class="bi bi-download" /></th
																			>
																			<th
																				scope="col"
																				class="border-top-0 text-center align-middle "
																				style="width: 22rem;">Acciones</th
																			>
																		</tr>
																	</thead>

																	<tbody>
																		{#if tematitulacionposgradomatricula_serializers.length != 'undefined' && tematitulacionposgradomatricula_serializers.length != 0}
																			<tr>
																				<td
																					class="fs-6 align-middle border-top-0 text-justify text-wrap"
																				>
																					{tematitulacionposgradomatricula_serializers.propuestatema}
																				</td>
																				{#if tematitulacionposgradomatricula_serializers.sublinea !== null}
																				<td
																					class="fs-6 align-middle border-top-0 text-justify text-wrap"
																				>

																						<b>Linea: </b>{tematitulacionposgradomatricula_serializers.sublinea.linea['nombre']}
																						<br/>
																						<b
																						>Sub Linea:
																						</b>{tematitulacionposgradomatricula_serializers.sublinea['nombre']}
																						<br>
																						<b>
																							[{tematitulacionposgradomatricula_serializers.convocatoria.obtenerid}]
																							Convocatorias:</b> {tematitulacionposgradomatricula_serializers.convocatoria.display}


																				</td>
																					{/if}
																				<td
																					class="fs-6 align-middle border-top-0 text-justify text-wrap"
																				>
																					{tematitulacionposgradomatricula_serializers.mecanismotitulacionposgrado['display']}
																				</td>

																				<td class="fs-6 align-middle border-top-0 text-center">
																					<div>
																						{#if tematitulacionposgradomatricula_serializers.estadoaprobacion == 1}
																							<span class="badge bg-warning">SOLICITADO</span>
																						{:else if tematitulacionposgradomatricula_serializers.estadoaprobacion == 2}
																							<span class="badge bg-success">APROBADO</span>
																						{:else}
																							<span class="badge bg-danger">RECHAZADO</span>
																						{/if}
																					</div>
																				</td>
																				<td class="fs-6 align-middle border-top-0 text-center">
																					<button
																						class="btn btn-info  btn-xs"
																						id="id_historial"
																						title="Historial"
																						on:click={() =>
																							toggleModalHistorial(
																								tematitulacionposgradomatricula_serializers.id
																							)}
																					>
																						<i class="bi bi-list-task" />
																					</button>
																					<Tooltip target="id_historial" placement="top"
																						>Historial</Tooltip
																					>
																				</td>
																				<td class="fs-6 align-middle border-top-0 text-center">
																					{#if tematitulacionposgradomatricula_serializers.archivo}
																						<a
																							id="evidencia_doc"
																							class="btn btn-info btn-xs "
																							target="_blank"
																							href="{variables.BASE_API}{tematitulacionposgradomatricula_serializers.archivo}"
																							title="Evidencia"
																						>
																							<i class="bi bi-download" />
																						</a>
																						<Tooltip target="evidencia_doc" placement="top"
																							>Evidencia</Tooltip
																						>
																					{/if}
																				</td>
																				<td class="fs-6 align-middle border-top-0 text-center">
																					{#if tematitulacionposgradomatricula_serializers.estadoaprobacion == 1 || tematitulacionposgradomatricula_serializers.estadoaprobacion == 3}
																						<div>
																							<span class="dropdown dropstart">
																								<button
																									class="btn-icon btn btn-ghost btn-sm rounded-circle"
																									role="button"
																									id="paymentDropdown"
																									data-bs-toggle="dropdown"
																									data-bs-offset="-20,20"
																									aria-expanded="false"
																								>
																									<i class="fe fe-more-vertical" />
																								</button>
																								<span
																									class="dropdown-menu"
																									aria-labelledby="paymentDropdown"
																								>
																									<span class="dropdown-header">Acciones </span>

																									<!-- content here -->
																									<button
																										class="dropdown-item"
																										on:click={() =>
																											toggleModalLoadFormEditarPropuestaTitulacion(
																												tematitulacionposgradomatricula_serializers.id
																											)}
																										><i
																											class="fe fe-edit dropdown-item-icon"
																										/>Editar</button
																									>
																									<button
																										class="dropdown-item"
																										on:click={() =>
																											eliminarPropuestaTema(
																												tematitulacionposgradomatricula_serializers.id
																											)}
																										><i
																											class="fe fe-trash dropdown-item-icon"
																										/>Eliminar</button
																									>
																								</span>
																							</span>
																						</div>
																					{/if}
																				</td>
																			</tr>
																		{:else}
																			<tr>
																				<td colspan="7"> No existen registros </td>
																			</tr>
																		{/if}
																	</tbody>
																</table>
															</div>
														</div>
													</div>
												</li>
											</ul>
										</div>
									</div>
									<!-- Card -->
								</div>
							</div>
						</div>
					</div>

					{#if habilitar_adicionar_propuesta == false}
						<div class="accordion-item  mb-2">
							<h2 class="accordion-header" id="headingTwo_registro_solicitud_titulacion">
								<button
									class="accordion-button "
									type="button"
									data-bs-toggle="collapse"
									data-bs-target="#collapseTwo_registro_solicitud_titulacion"
									aria-expanded="true"
									aria-controls="collapseTwo_registro_solicitud_titulacion"
								>
									Solicitud Prórroga propuesta de titulación.
								</button>
							</h2>
							<div
								id="collapseTwo_registro_solicitud_titulacion"
								class="accordion-collapse  show"
								aria-labelledby="headingTwo_registro_solicitud_titulacion"
								data-bs-parent="#accordionExample"
							>
								<div class="accordion-body">
									<!-- content here -->
									<div class="row-fluid">
										<div class="row">
											<Alert color="info" dismissible>
												<strong>Aviso importante!</strong> <br />
												Puede solicitar prórroga para el registro de la propuesta de titulación si las
												tutorias no han empezado y un máximo dos veces.
											</Alert>
										</div>
									</div>
									<div class="">
										<!-- Card -->
										{#if puede_solicitar_prorroga == true && !(prorroga_activa == true)}
											<!-- Card header -->
											<div
												class="card-header d-flex align-items-center   justify-content-between card-header-height"
											>
												<a
													href="javascript:void(0)"
													class="btn btn-outline-white btn-sm"
													on:click={() => toggleModalLoadFormSolicitarProrrogaTitulacion()}
													><i class="bi bi-plus-lg" /> Solicitar</a
												>
											</div>
										{/if}
										<!-- Card body -->
										<div class="card-body">
											<!-- List group -->
											<ul class="list-group list-group-flush">
												<li class="list-group-item px-0 pt-0 ">
													<div class="row">
														<div class="col-auto">
															<div class="table-responsive">
																<table
																	class="table mb-0 text-nowrap table-hover table-bordered align-middle"
																>
																	<thead class="table-light">
																		<tr>
																			<th
																				scope="col"
																				class="border-top-0 text-center align-middle "
																				style="width: 400rem;">N°</th
																			>
																			<th
																				scope="col"
																				class="border-top-0 text-center align-middle "
																				style="width: 400rem;">Fecha inicio Prórroga</th
																			>
																			<th
																				scope="col"
																				class="border-top-0 text-center align-middle "
																				style="width: 400rem;">Fecha fin Prórroga</th
																			>
																			<th
																				scope="col"
																				class="border-top-0 text-center align-middle "
																				style="width: 400rem;">Observación</th
																			>

																			<th
																				scope="col"
																				class="border-top-0 text-center align-middle "
																				style="width: 22rem;">Estado</th
																			>
																			<th
																				scope="col"
																				class="border-top-0 text-center align-middle "
																				style="width: 22rem;">Historial de Aprobación</th
																			>

																			<th
																				scope="col"
																				class="border-top-0 text-center align-middle "
																				style="width: 22rem;">Acciones</th
																			>
																		</tr>
																	</thead>

																	<tbody>
																		{#each solicitudes_prorroga as solicitud, index}
																			<tr>
																				<td
																					class="fs-6 align-middle border-top-0 text-justify text-wrap"
																				>
																					{index + 1}
																				</td>
																				<td
																					class="fs-6 align-middle border-top-0 text-justify text-wrap"
																				>
																					{#if solicitud.fechainicioprorroga == null}
																						S/N
																					{:else}
																						{solicitud.fechainicioprorroga}
																					{/if}
																				</td>

																				<td
																					class="fs-6 align-middle border-top-0 text-justify text-wrap"
																				>
																					{#if solicitud.fechafinprorroga == null}
																						S/N
																					{:else}
																						{solicitud.fechafinprorroga}
																					{/if}
																				</td>

																				<td
																					class="fs-6 align-middle border-top-0 text-justify text-wrap"
																				>
																					{solicitud.observacion}
																				</td>

																				<td class="fs-6 align-middle border-top-0 text-center">
																					{#if solicitud.estado == 1}
																						<span class="badge bg-warning">
																							{solicitud.estado_display}</span
																						>
																					{:else if solicitud.estado == 2}
																						<span class="badge bg-success">
																							{solicitud.estado_display}</span
																						>
																					{:else}
																						<span class="badge bg-danger">
																							{solicitud.estado_display}</span
																						>
																					{/if}
																				</td>
																				<td class="fs-6 align-middle border-top-0 text-center">
																					<button
																						class="btn btn-info  btn-xs"
																						id="id_historial"
																						title="Historial"
																						on:click={() =>
																							toggleModalHistorialProrrogaPropuestaTitulacion(
																								solicitud.id
																							)}
																					>
																						<i class="bi bi-list-task" />
																					</button>
																					<Tooltip target="id_historial" placement="top"
																						>Historial</Tooltip
																					>
																				</td>

																				<td class="fs-6 align-middle border-top-0 text-center">
																					{#if solicitud.estado == 1}
																						<div>
																							<span class="dropdown dropstart">
																								<button
																									class="btn-icon btn btn-ghost btn-sm rounded-circle"
																									role="button"
																									id="paymentDropdown"
																									data-bs-toggle="dropdown"
																									data-bs-offset="-20,20"
																									aria-expanded="false"
																								>
																									<i class="fe fe-more-vertical" />
																								</button>
																								<span
																									class="dropdown-menu"
																									aria-labelledby="paymentDropdown"
																								>
																									<span class="dropdown-header">Acciones </span>

																									<!-- content here -->
																									<button
																										class="dropdown-item"
																										on:click={() =>
																											EditarSolicitarProrrogaTitulacion(
																												solicitud.id
																											)}
																										><i
																											class="fe fe-edit dropdown-item-icon"
																										/>Editar</button
																									>
																									<button
																										class="dropdown-item"
																										on:click={() =>
																											EliminarSolicitarProrrogaTitulacion(
																												solicitud.id
																											)}
																										><i
																											class="fe fe-trash dropdown-item-icon"
																										/>Eliminar</button
																									>
																								</span>
																							</span>
																						</div>
																					{/if}
																				</td>
																			</tr>
																		{:else}
																			<tr>
																				<td colspan="5"> No existen solicitudes </td>
																			</tr>
																		{/each}
																	</tbody>
																</table>
															</div>
														</div>
													</div>
												</li>
											</ul>
										</div>
										<!-- Card -->
									</div>
								</div>
							</div>
						</div>
					{/if}
				</div>
				<!-- Card -->
			</div>
		</div>

		{#if tematitulacionposgradomatricula_serializers.estadoaprobacion == 2}
			<!-- nav-seguimiento_tutoria-tab -->
			<div
				class="row tab-pane fade bs-stepper-pane  show "
				id="nav-seguimiento_tutoria"
				role="tabpanel"
				aria-labelledby="nav-seguimiento_tutoria-tab"
			>
				<!-- Card -->
				<div class="card mb-3 ">
					<div class="card-header border-bottom px-4 py-3">
						<h4 class="mb-0">Tutorias</h4>
					</div>

					<div class="row">
						{#if es_en_pareja}
							<!-- content here -->
							{#if tematitulacionposgradomatriculacabecera_serializers.tutor}
								<!-- content here -->

								<!-- Card -->
								<div class="card mb-4">
									<!-- Card header -->
									<div
										class="card-header d-flex align-items-center
									  justify-content-between card-header-height"
									>
										<h5 class="mb-0">TUTOR DE TITULACIÓN</h5>
									</div>

									<!-- Card body -->
									<div class="card-body">
										<div class="row">
											<div class="text-center">
												{#if tematitulacionposgradomatriculacabecera_serializers.tutor.persona.obtenerfoto}
													<!-- content here -->
													<img
														src="{variables.BASE_API}{tematitulacionposgradomatriculacabecera_serializers
															.tutor.persona.obtenerfoto.foto}"
														class="rounded-circle avatar-xl mb-3"
														alt=""
													/>
												{:else if tematitulacionposgradomatriculacabecera_serializers.tutor.persona.sexo == 1}
													<!-- content here -->
													<img
														src="{variables.BASE_API_STATIC}/images/iconos/mujer.png"
														class="rounded-circle avatar-xl mb-3"
														alt=""
													/>
												{:else}
													<!-- else content here -->
													<img
														src="{variables.BASE_API_STATIC}/images/iconos/hombre.png"
														class="rounded-circle avatar-xl mb-3"
														alt=""
													/>
												{/if}

												<h4 class="mb-0">
													{tematitulacionposgradomatriculacabecera_serializers.tutor.display}
												</h4>
												<p class="mb-0">
													{tematitulacionposgradomatriculacabecera_serializers.tutor.persona.email}
												</p>
											</div>
										</div>
									</div>
								</div>
							{/if}
						{:else}
							<!-- else content here -->
							{#if grupo.tutor}
								<!-- content here -->

								<!-- Card -->
								<div class="card mb-4">
									<!-- Card header -->
									<div
										class="card-header d-flex align-items-center
										  justify-content-between card-header-height"
									>
										<h5 class="mb-0">TUTOR DE TITULACIÓN</h5>
									</div>

									<!-- Card body -->
									<div class="card-body">
										<div class="text-center">
											{#if grupo.tutor.persona.obtenerfoto}
												<!-- content here -->
												<img
													src="{variables.BASE_API}{grupo.tutor.persona.obtenerfoto.foto}"
													class="rounded-circle avatar-xl mb-3"
													alt=""
												/>
											{:else if grupo.tutor.persona.sexo == 1}
												<!-- content here -->
												<img
													src="{variables.BASE_API_STATIC}/images/iconos/mujer.png"
													class="rounded-circle avatar-xl mb-3"
													alt=""
												/>
											{:else}
												<!-- else content here -->
												<img
													src="{variables.BASE_API_STATIC}/images/iconos/hombre.png"
													class="rounded-circle avatar-xl mb-3"
													alt=""
												/>
											{/if}

											<h4 class="mb-0">{grupo.tutor.display}</h4>
											<p class="mb-0">{grupo.tutor.persona.email}</p>
										</div>
									</div>
								</div>
							{/if}
							<div class="row">
								<!-- Card -->
								<div class="card mb-4">
									<!-- Card body -->
									<div class="card-body">
										<h5 class="mb-0">
											CRONOGRAMA DE TUTORIAS DE TRABAJO DE TITULACIÓN
										</h5>

										<div class="d-flex justify-content-between border-bottom py-2">
											<span>Fecha inicio tutoria:</span>
											<span>{cronograma.fechainiciotutoria} </span>
										</div>
										<div class="d-flex justify-content-between pt-2">
											<span>Fecha fin tutoria:</span>
											<span class="text-dark"> {cronograma.fechafintutoria} </span>
										</div>
									</div>
								</div>
							</div>
						{/if}
					</div>

					<!-- Card body -->
					<div class="card-body">
						<div class="row">
							<div class="col-md-12">
								{#if es_en_pareja}
									<div class="accordion mt-2 " id="accordionExample">
										<div class="accordion-item ">
											<h2 class="accordion-header" id="headingOne">
												<button
													class="accordion-button"
													type="button"
													data-bs-toggle="collapse"
													data-bs-target="#collapseOne"
													aria-expanded="true"
													aria-controls="collapseOne"
												>
													<strong>Selección de tutor</strong>
												</button>
											</h2>
											<div
												id="collapseOne"
												class="accordion-collapse collapse show "
												aria-labelledby="headingOne"
												data-bs-parent="#accordionExample"
											>
												<div class="accordion-body">
													<div class="row-fluid">
														{#if disponible_elejirTutor}
															<!-- content here -->
															<!-- content here -->
															<Alert color="info" dismissible>
																<strong>Selección de tutor!</strong> <br />
																A continuación puede <strong>seleccionar</strong> a su tutor
																acompañante en el proceso de titulación.
																<br />
																Una vez seleccionado su tutor, tiene la opción de cambiar de tutor; siempre
																y cuando las tutorias no hayan empezado y la fecha de selección este
																dentro del cronograma.
															</Alert>
														{:else}
															<!-- else content here -->
															<!-- content here -->
															<Alert color="warning" dismissible>
																<strong>Selección tutor!</strong> <br />
																La opción de seleccionar tutor no está disponible, las tutorías ya empezaron.
															</Alert>
														{/if}
														<!-- Card -->
														<div class="card h-100">
															<!-- Card body -->
															<div class="card-body">
																<!-- List group -->
																{#if profesores_disponibles.length > 0}
																	<!-- content here -->
																	<ul class="list-group list-group-flush">
																		{#each profesores_disponibles as docente}
																			<!-- content here -->

																			<li class="list-group-item px-0 pt-0 mt-3">
																				<div class="row">
																					<div class="col-auto">
																						<div
																							class="avatar avatar-md avatar-indicators avatar-offline"
																						>
																							{#if docente.profesor.persona.obtenerfoto}
																								<!-- content here -->
																								<img
																									src="{variables.BASE_API}{docente.profesor.persona
																										.obtenerfoto.foto}"
																									class="rounded-circle avatar-xl mb-3"
																									alt=""
																								/>
																							{:else if docente.profesor.persona.sexo == 1}
																								<!-- content here -->
																								<img
																									src="{variables.BASE_API_STATIC}/images/iconos/mujer.png"
																									class="rounded-circle avatar-xl mb-3"
																									alt=""
																								/>
																							{:else}
																								<!-- else content here -->
																								<img
																									src="{variables.BASE_API_STATIC}/images/iconos/hombre.png"
																									class="rounded-circle avatar-xl mb-3"
																									alt=""
																								/>
																							{/if}
																						</div>
																					</div>
																					<div class="col ms-n3">
																						<h4 class="mb-0 h5">
																							<a
																								id="id_docente_dispo_tutor"
																								href="javascript:void(0)"
																								on:click={() =>
																									toggleDetalleTutor(docente.profesor.id)}
																								>{docente.profesor.display}</a
																							>
																							<Tooltip
																								target="id_docente_dispo_tutor"
																								placement="top">Ver información del docente</Tooltip
																							>
																						</h4>

																						<span class="fs-6">
																							<span class="text-dark  me-1 fw-semi-bold"
																								>{docente.profesor.persona.email}</span
																							>
																						</span>
																					</div>

																					<div class="col-auto ">
																						{#if docente.estado_estudiante == 1}
																							<Badge color="warning"
																								>{docente.obtener_estado_seleccion_estudiante}</Badge
																							>
																						{/if}
																						{#if docente.estado_estudiante == 2}
																							<Badge color="success"
																								>{docente.obtener_estado_seleccion_estudiante}</Badge
																							>
																						{/if}

																						{#if docente.estado_estudiante == 3}
																							<Badge color="danger"
																								>{docente.obtener_estado_seleccion_estudiante}</Badge
																							>
																						{/if}
																					</div>
																					<div class="col-auto">
																						<button
																							class="btn btn-info  btn-xs"
																							id="id_historial"
																							title="Historial"
																							on:click={() =>
																								toggleModalHistorialAprobacionTutor(docente.id)}
																						>
																							<i class="bi bi-list-task" />
																						</button>
																						<Tooltip target="id_historial" placement="top"
																							>Historial de aprobación</Tooltip
																						>
																					</div>

																					<div class="col-auto ">
																						{#if disponible_elejirTutor}
																							<!-- content here -->
																							<button
																								class="btn btn-outline-white btn-sm"
																								on:click={() =>
																									toggleOffCanvasSeleccionarTutor(docente.id)}
																								>Aprobar / rechazar</button
																							>
																						{/if}
																					</div>
																				</div>
																			</li>
																		{/each}
																	</ul>
																{:else}
																	<!-- else content here -->
																	No existen docentes aptos para seleccionar.
																{/if}
															</div>
														</div>
													</div>
												</div>
											</div>
										</div>
										{#if disponible_elejirTutor == false && tematitulacionposgradomatriculacabecera_serializers.tutor != null}
											<div class="accordion-item ">
												<h2 class="accordion-header" id="headingTwo">
													<button
														class="accordion-button collapsed"
														type="button"
														data-bs-toggle="collapse"
														data-bs-target="#collapseTwo"
														aria-expanded="true"
														aria-controls="collapseTwo"
													>
														<strong>Seguimiento de tutorias</strong>
													</button>
												</h2>
												<div
													id="collapseTwo"
													class="accordion-collapse collapse"
													aria-labelledby="headingTwo"
													data-bs-parent="#accordionExample"
												>
													<div class="accordion-body">
														<!-- content here -->
														<div class="row-fluid">
															<div class="container">
																<h4 class="accordion-header">
																	{#if tematitulacionposgradomatriculacabecera_serializers.tema_correcto}
																		<!-- content here -->
																		<Alert color="warning">
																			<strong>TEMA:</strong><br />
																			{tematitulacionposgradomatriculacabecera_serializers.tema_correcto}
																		</Alert>
																	{:else}
																		<!-- else content here -->
																		<Alert color="info" dismissible
																			><strong>Aviso importante!</strong> No se ha definido el tema
																			final de su propuesta de titulación, favor comunicar a su
																			tutor.
																			<br />
																		</Alert>
																	{/if}
																</h4>
															</div>
														</div>
														<div class="container">
															<div class="row mt-4 pb-5">
																{#each configuracion_programa_etapa as programa_etapa}
																	<!-- card -->
																	<div class=" shadow-none rounded-3  me-4 align-top  task-card">
																		<!-- card body -->
																		<div class="card-body p-3">
																			<!-- task list -->

																			<div
																				class="accordion"
																				id="configuracion_programa_etapa_{programa_etapa
																					.etapatutoria.id}"
																			>
																				<div class="accordion-item">
																					<div
																						class="accordion-header"
																						id="panelsStayOpen-headingOne_{programa_etapa
																							.etapatutoria.id}"
																					>
																						<button
																							class="accordion-button"
																							type="button"
																							data-bs-toggle="collapse"
																							data-bs-target="#panelsStayOpen-collapseOne_{programa_etapa
																								.etapatutoria.id}"
																							aria-expanded="true"
																							aria-controls="panelsStayOpen-collapseOne"
																						>
																							{programa_etapa.etapatutoria.display}
																						</button>
																					</div>
																					<div
																						id="panelsStayOpen-collapseOne_{programa_etapa
																							.etapatutoria.id}"
																						class="accordion-collapse collapse show"
																						aria-labelledby="panelsStayOpen-headingOne_{programa_etapa
																							.etapatutoria.id}"
																					>
																						<div class="accordion-body">
																							{#each lista_tutorias_pareja as tutoria}
																								{#if tutoria.programaetapatutoria != null}
																									{#if tutoria.programaetapatutoria.etapatutoria.obtener_id == programa_etapa.etapatutoria.obtener_id}
																										<div class="table-responsive">
																											<table
																												class="table table-bordered table-striped "
																											>
																												<tr class="bg-light mb-5 ">
																													<td>
																														<div
																															class="d-flex justify-content-between  align-items-center "
																														>
																															<div>
																																<!-- heading -->
																																<h4 class="mb-0 ">
																																	{tutoria.observacion} :
																																	{tutoria.fecharegistro}
																																	de {tutoria.horainicio} a {tutoria.horafin}
																																</h4>
																															</div>
																															<div
																																class="d-flex align-items-center"
																															>
																																<!--  dropdown -->
																																<div class="dropdown dropstart">
																																	<button
																																		class="btn-icon btn btn-ghost btn-sm rounded-circle"
																																		data-bs-toggle="dropdown"
																																		data-offset="-140"
																																		aria-haspopup="true"
																																		aria-expanded="false"
																																		><i
																																			class="bi bi-three-dots-vertical"
																																		/></button
																																	>
																																	<ul
																																		class="dropdown-menu pull-right"
																																	>
																																		<li class="dropdown-item">
																																			<a
																																				href="javascript:void(0)"
																																				on:click={() =>
																																					toggleModalDetalleTutoriaPosgrado(
																																						tutoria.id
																																					)}
																																				><i class="bi bi-eye" /> Ver</a
																																			>
																																		</li>
																																		{#if tutoria.programaetapatutoria.etapatutoria.obtener_id == 8}
																																			{#if disponible}
																																				{#if  tematitulacionposgradomatricula_serializers.tiene_documentos_tutoria_configurado}
																																					<li class="dropdown-item">
																																						<a
																																							href="javascript:void(0)"
																																							on:click={() =>
																																								toggleModalLoadFormAgregarDocumentoFinalPosgrado(
																																									tutoria.id,
																																									tematitulacionposgradomatricula_serializers.id
																																								)}
																																						>
																																							<i
																																								class="bi bi-file-plus-fill"
																																							/>Subir documentos</a
																																						>
																																					</li>

																																				{:else}
																																					<li class="dropdown-item">
																																						<a
																																							href="javascript:void(0)"
																																							on:click={() =>
																																								toggleModalLoadFormAgregarDocFinalPosgrado(
																																									tutoria.id,
																																									tematitulacionposgradomatricula_serializers.id
																																								)}
																																						>
																																							<i
																																								class="bi bi-file-plus-fill"
																																							/>Subir doc. Final</a
																																						>
																																					</li>
																																				{/if}

																																			{/if}
																																		{:else}
																																			<li class="dropdown-item">
																																				<a
																																					href="javascript:void(0)"
																																					on:click={() =>
																																						toggleModalLoadFormAgregarAvanceTutoriaPosgrado(
																																							tutoria.id
																																						)}
																																				>
																																					<i
																																						class="bi bi-plus-circle-dotted"
																																					/>
																																					Adicionar avance</a
																																				>
																																			</li>
																																		{/if}
																																	</ul>
																																</div>
																															</div>
																														</div>
																													</td>
																												</tr>
																												<tr>
																													<td>
																														<div
																															class="table-responsive overflow-y-hidden"
																														>
																															{#if tutoria.programaetapatutoria.etapatutoria.obtener_id == 8}
																																<table
																																	class="table mb-0 text-nowrap mb-5"
																																>
																																	<thead class="table-active">
																																		<tr>
																																			<th
																																				scope="col"
																																				class=" border-top-0"
																																			>
																																				%
																																			</th>
																																			<th
																																				scope="col"
																																				class=" border-top-0"
																																			>
																																				Observaciones
																																			</th>
																																			<th
																																				scope="col"
																																				class=" border-top-0"
																																			>
																																				Estado
																																			</th>
																																			<th
																																				scope="col"
																																				class=" border-top-0"
																																			>
																																				Acciones
																																			</th>
																																		</tr>
																																	</thead>
																																	<tbody>
																																		{#each tutoria.revisiones_tutoria as revision, index}
																																			<tr>
																																				<td class="align-middle">
																																					<p class="text-wrap">
																																						{#if revision.porcentajeurkund}
																																							{converToDecimal(
																																								revision.porcentajeurkund
																																							)}
																																						{/if}
																																					</p>
																																				</td>

																																				<td class="align-middle">
																																					<p class="text-wrap">
																																						{revision.observacion}
																																					</p>
																																				</td>

																																				<td class="align-middle">
																																					<p class="text-wrap">
																																						{#if revision.estado == 4}
																																							<Badge color="warning"
																																								>{revision.estado_display}</Badge
																																							>
																																						{/if}

																																						{#if revision.estado == 3}
																																							<Badge
																																								color="secondary"
																																								>{revision.estado_display}</Badge
																																							>
																																						{/if}

																																						{#if revision.estado == 2}
																																							<Badge color="success"
																																								>{revision.estado_display}</Badge
																																							>
																																						{/if}

																																						{#if revision.estado == 1}
																																							<Badge color="info"
																																								>{revision.estado_display}</Badge
																																							>
																																						{/if}
																																					</p>
																																				</td>
																																				<td class="align-middle">
																																					<a
																																						href="javascript:void(0)"
																																						class=" accordion-button"
																																						type="button"
																																						role="button"
																																						data-bs-toggle="collapse"
																																						data-bs-target="#collapseExample_{revision.id}"
																																						aria-expanded="true"
																																						aria-controls="collapseOne"
																																					>
																																						ver archivos
																																					</a>
																																				</td>
																																			</tr>
																																			<tr
																																				class="collapse"
																																				id="collapseExample_{revision.id}"
																																			>
																																				<td colspan="6">
																																					<table
																																						class="table table-success mb-0 text-nowrap"
																																					>
																																						<thead>
																																							<tr>
																																								<th
																																									scope="col"
																																									class="border-0 text-center text-uppercase w-25"
																																								>
																																									N°
																																								</th>
																																								<th
																																									scope="col"
																																									class="border-0 text-center text-uppercase w-25"
																																								>
																																									Archivo
																																								</th>
																																								<th
																																									scope="col"
																																									class="border-0 text-center text-uppercase w-25"
																																								>
																																									Fecha
																																								</th>
																																								<th
																																									scope="col"
																																									class="border-0 text-center text-uppercase w-25"
																																								/>
																																							</tr>
																																						</thead>
																																						<tbody>
																																							{#each revision.archivos as doc, index}
																																								<!-- content here -->
																																								<tr>
																																									<td
																																										scope="col"
																																										class="fs-6 align-middle border-top-0 text-center text-wrap"
																																									>
																																										{index + 1}
																																									</td>

																																									<td
																																										scope="col"
																																										class="fs-6 align-middle border-top-0 text-center text-wrap"
																																									>
																																										{#if doc.archivo}
																																											<a
																																												href="{variables.BASE_API}{doc.archivo}"
																																												target="_blank"
																																												><i
																																													class="bi bi-download"
																																												/>
																																												{doc.tipodisplay}
																																											</a>
																																										{/if}
																																									</td>

																																									<td
																																										scope="col"
																																										class="fs-6 align-middle border-top-0 text-center text-wrap"
																																									>
																																										{doc.fecha}
																																									</td>

																																									<td
																																										scope="col"
																																										class="fs-6 align-middle border-top-0 text-center text-wrap"
																																									>
																																										{#if revision.estado == 1 && !(doc.tipo == 3)}
																																											<button
																																												on:click={() =>
																																													toggleModalEditDocFinalTitulacion(
																																														doc.id
																																													)}
																																												class="btn btn-mini btn-info btn-xs"
																																												><i
																																													class="fe fe-edit"
																																												/></button
																																											>
																																										{/if}
																																									</td>
																																								</tr>
																																							{:else}
																																								No existen
																																								documentos
																																							{/each}
																																						</tbody>
																																					</table>
																																				</td>
																																			</tr>
																																		{:else}
																																			<td
																																				colspan="7"
																																				class="text-center"
																																				>NO EXISTEN REGISTROS DE
																																				REVISIONES DE TUTORIA
																																			</td>
																																		{/each}
																																	</tbody>
																																</table>
																															{:else}
																																<table
																																	class="table mb-0 text-nowrap mb-5"
																																>
																																	<thead class="table-active">
																																		<tr>
																																			<th
																																				scope="col"
																																				class=" border-top-0"
																																			>
																																				Revisión
																																			</th>
																																			<th
																																				scope="col"
																																				class=" border-top-0"
																																			>
																																				Avance tutoria
																																			</th>
																																			<th
																																				scope="col"
																																				class=" border-top-0"
																																			>
																																				Correcciones
																																			</th>
																																			<th
																																				scope="col"
																																				class=" border-top-0"
																																			>
																																				Observaciones
																																			</th>
																																			<th
																																				scope="col"
																																				class=" border-top-0"
																																			>
																																				Acciones
																																			</th>
																																		</tr>
																																	</thead>
																																	<tbody>
																																		{#each tutoria.revisiones_tutoria as revision, index}
																																			<tr>
																																				<td
																																					class="fs-6 align-middle border-top-0 text-center text-wrap"
																																				>
																																					<div
																																						class="d-flex align-items-center"
																																					>
																																						{#if revision.fecharevision}
																																							{revision.fecharevision}
																																						{:else}
																																							<Badge color="danger"
																																								>Sin revisar</Badge
																																							>
																																						{/if}
																																					</div>
																																				</td>
																																				<td
																																					class="fs-6 align-middle border-top-0 text-center text-wrap"
																																				>
																																					<div
																																						class="d-flex align-items-center"
																																					>
																																						{#if revision.tutoria_avance}
																																							<a
																																								class="btn btn-info btn-xs"
																																								target="_blank"
																																								href="{variables.BASE_API}{revision.tutoria_avance}"
																																								title="Evidencia"
																																							>
																																								<i
																																									class="bi bi-download"
																																								/>
																																							</a>
																																						{:else}
																																							S/N
																																						{/if}
																																					</div>
																																				</td>

																																				<td
																																					class="fs-6 align-middle border-top-0 text-center text-wrap"
																																				>
																																					<div
																																						class="d-flex align-items-center"
																																					>
																																						{#if revision.correccion}
																																							{#if revision.correccion.archivo}
																																								<a
																																									class="btn btn-info btn-xs"
																																									target="_blank"
																																									href="{variables.BASE_API}{revision
																																										.correccion
																																										.archivo}"
																																									title="Evidencia"
																																								>
																																									<i
																																										class="bi bi-download"
																																									/>
																																								</a>
																																							{:else}
																																								S/N
																																							{/if}
																																						{/if}
																																					</div>
																																				</td>

																																				<td
																																					class="fs-6 align-middle border-top-0 text-center text-wrap"
																																				>
																																					<p class="text-wrap">
																																						{revision.observacion}
																																					</p>
																																				</td>

																																				<td
																																					class="fs-6 align-middle border-top-0 text-center text-wrap"
																																				/>
																																			</tr>
																																		{:else}
																																			<td
																																				colspan="7"
																																				class="text-center"
																																				>NO EXISTEN REGISTROS DE
																																				REVISIONES DE TUTORIA
																																			</td>
																																		{/each}
																																	</tbody>
																																</table>
																															{/if}
																														</div>
																													</td>
																												</tr>
																											</table>
																										</div>
																									{/if}
																								{/if}
																							{/each}
																						</div>
																					</div>
																				</div>
																			</div>
																		</div>
																	</div>
																{/each}
															</div>
														</div>
													</div>
												</div>
											</div>
										{/if}
									</div>
								{:else}
									<!-- tutorias individuales -->
									<div class="accordion mt-2 " id="accordionExample">
										<div class="accordion-item ">
											<h2 class="accordion-header" id="headingOne">
												<button
													class="accordion-button"
													type="button"
													data-bs-toggle="collapse"
													data-bs-target="#collapseOne"
													aria-expanded="true"
													aria-controls="collapseOne"
												>
													<strong>Selección de tutor</strong>
												</button>
											</h2>
											<div
												id="collapseOne"
												class="accordion-collapse collapse show "
												aria-labelledby="headingOne"
												data-bs-parent="#accordionExample"
											>
												<div class="accordion-body">
													<div class="row-fluid">
														{#if disponible_elejirTutor}
															<!-- content here -->
															<!-- content here -->
															<Alert color="info" dismissible>
																<strong>Selección de tutor!</strong> <br />
																A continuación puede <strong>seleccionar</strong> a su tutor
																acompañante en el proceso de titulación.
																<br />
																Una vez seleccionado su tutor, tiene la opción de cambiar de tutor; siempre
																y cuando las tutorias no hayan empezado y la fecha de selección este
																dentro del cronograma.
															</Alert>
														{:else}
															<!-- else content here -->
															<!-- content here -->
															<Alert color="warning" dismissible>
																<strong>Selección tutor!</strong> <br />
																La opción de seleccionar tutor no está disponible, las tutorías ya empezaron.
															</Alert>
														{/if}
														<!-- Card -->
														<div class="card h-100">
															<!-- Card body -->
															<div class="card-body">
																<!-- List group -->

																{#if profesores_disponibles.length > 0}
																	<!-- content here -->
																	<ul class="list-group list-group-flush">
																		{#each profesores_disponibles as docente}
																			<!-- content here -->

																			<li class="list-group-item px-0 pt-0 mt-3">
																				<div class="row">
																					<div class="col-auto">
																						<div
																							class="avatar avatar-md avatar-indicators avatar-offline"
																						>
																							{#if docente.profesor.persona.obtenerfoto}
																								<!-- content here -->
																								<img
																									src="{variables.BASE_API}{docente.profesor.persona
																										.obtenerfoto.foto}"
																									class="rounded-circle avatar-xl mb-3"
																									alt=""
																								/>
																							{:else if docente.profesor.persona.sexo == 1}
																								<!-- content here -->
																								<img
																									src="{variables.BASE_API_STATIC}/images/iconos/mujer.png"
																									class="rounded-circle avatar-xl mb-3"
																									alt=""
																								/>
																							{:else}
																								<!-- else content here -->
																								<img
																									src="{variables.BASE_API_STATIC}/images/iconos/hombre.png"
																									class="rounded-circle avatar-xl mb-3"
																									alt=""
																								/>
																							{/if}
																						</div>
																					</div>
																					<div class="col ms-n3">
																						<h4 class="mb-0 h5">
																							<a
																								id="id_docente_disp_tutor"
																								href="javascript:void(0)"
																								on:click={() =>
																									toggleDetalleTutor(docente.profesor.id)}
																								>{docente.profesor.display}</a
																							>
																							<Tooltip
																								target="id_docente_disp_tutor"
																								placement="top">Ver información del docente</Tooltip
																							>
																						</h4>

																						<span class="fs-6">
																							<span class="text-dark  me-1 fw-semi-bold"
																								>{docente.profesor.persona.email}</span
																							>
																						</span>
																					</div>
																					<div class="col-auto ">
																						{#if docente.estado_estudiante == 1}
																							<Badge color="warning"
																								>{docente.obtener_estado_seleccion_estudiante}</Badge
																							>
																						{/if}
																						{#if docente.estado_estudiante == 2}
																							<Badge color="success"
																								>{docente.obtener_estado_seleccion_estudiante}</Badge
																							>
																						{/if}

																						{#if docente.estado_estudiante == 3}
																							<Badge color="danger"
																								>{docente.obtener_estado_seleccion_estudiante}</Badge
																							>
																						{/if}
																					</div>
																					<div class="col-auto">
																						<button
																							class="btn btn-info  btn-xs"
																							id="id_historial"
																							title="Historial"
																							on:click={() =>
																								toggleModalHistorialAprobacionTutor(docente.id)}
																						>
																							<i class="bi bi-list-task" />
																						</button>
																						<Tooltip target="id_historial" placement="top"
																							>Historial de aprobación</Tooltip
																						>
																					</div>
																					<div class="col-auto ">
																						{#if disponible_elejirTutor}
																							<!-- content here -->
																							<button
																								class="btn btn-outline-white btn-sm"
																								on:click={() =>
																									toggleOffCanvasSeleccionarTutor(docente.id)}
																								>Aprobar / rechazar</button
																							>
																						{/if}
																					</div>
																				</div>
																			</li>
																		{/each}
																	</ul>
																{:else}
																	<!-- else content here -->
																	No existen docentes aptos para seleccionar.
																{/if}
															</div>
														</div>
													</div>
												</div>
											</div>
										</div>
										{#if disponible_elejirTutor == false && tematitulacionposgradomatricula_serializers.tutor != null}
											<div class="accordion-item ">
												<h2 class="accordion-header" id="headingTwo">
													<button
														class="accordion-button collapsed"
														type="button"
														data-bs-toggle="collapse"
														data-bs-target="#collapseTwo"
														aria-expanded="true"
														aria-controls="collapseTwo"
													>
														<strong>Seguimiento de tutorias</strong>
													</button>
												</h2>
												<div
													id="collapseTwo"
													class="accordion-collapse collapse"
													aria-labelledby="headingTwo"
													data-bs-parent="#accordionExample"
												>
													<div class="accordion-body">
														<!-- content here -->
														<div class="row-fluid">
															<h4 class="accordion-header">
																{#if tematitulacionposgradomatricula_serializers.tema_correcto}
																	<!-- content here -->
																	<Alert color="warning">
																		<strong>TEMA:</strong><br />
																		{tematitulacionposgradomatricula_serializers.tema_correcto}
																	</Alert>
																{:else}
																	<!-- else content here -->
																	<Alert color="info" dismissible
																		><strong>Aviso importante!</strong> No se ha definido el tema
																		final de su propuesta de titulación, favor comunicar a su tutor.
																		<br />
																	</Alert>
																{/if}
															</h4>
														</div>

														<div class="row mt-4 pb-5">
															{#each configuracion_programa_etapa as programa_etapa}
																<!-- card -->
																<div class=" shadow-none rounded-3  me-4 align-top  task-card">
																	<!-- card body -->
																	<div class="card-body p-3">
																		<!-- task list -->

																		<div
																			class="accordion"
																			id="configuracion_programa_etapa_{programa_etapa.etapatutoria
																				.id}"
																		>
																			<div class="accordion-item">
																				<div
																					class="accordion-header"
																					id="panelsStayOpen-headingOne_{programa_etapa.etapatutoria
																						.id}"
																				>
																					<button
																						class="accordion-button"
																						type="button"
																						data-bs-toggle="collapse"
																						data-bs-target="#panelsStayOpen-collapseOne_{programa_etapa
																							.etapatutoria.id}"
																						aria-expanded="true"
																						aria-controls="panelsStayOpen-collapseOne"
																					>
																						{programa_etapa.etapatutoria.display}
																					</button>
																				</div>
																				<div
																					id="panelsStayOpen-collapseOne_{programa_etapa
																						.etapatutoria.id}"
																					class="accordion-collapse collapse show"
																					aria-labelledby="panelsStayOpen-headingOne_{programa_etapa
																						.etapatutoria.id}"
																				>
																					<div class="accordion-body">
																						{#each lista_tutorias_individuales as tutoria, index}
																							{#if tutoria.programaetapatutoria != null}
																								{#if tutoria.programaetapatutoria.etapatutoria.obtener_id == programa_etapa.etapatutoria.obtener_id}
																									<div class="table-responsive">
																										<table
																											class="table table-bordered table-striped "
																										>
																											<tr class="bg-light mb-5 ">
																												<td>
																													<div
																														class="d-flex justify-content-between  align-items-center "
																													>
																														<div>
																															<!-- heading -->
																															<h4 class="mb-0 ">
																																{tutoria.observacion} :
																																{tutoria.fecharegistro}
																																de {tutoria.horainicio} a {tutoria.horafin}
																															</h4>
																														</div>
																														<div class="d-flex align-items-center">
																															<!--  dropdown -->
																															<div class="dropdown dropstart">
																																<button
																																	class="btn-icon btn btn-ghost btn-sm rounded-circle"
																																	data-bs-toggle="dropdown"
																																	data-offset="-140"
																																	aria-haspopup="true"
																																	aria-expanded="false"
																																	><i
																																		class="bi bi-three-dots-vertical"
																																	/></button
																																>
																																<ul
																																	class="dropdown-menu pull-right"
																																>
																																	<li class="dropdown-item">
																																		<a
																																			href="javascript:void(0)"
																																			on:click={() =>
																																				toggleModalDetalleTutoriaPosgrado(
																																					tutoria.id
																																				)}
																																			><i class="bi bi-eye" /> Ver</a
																																		>
																																	</li>
																																	{#if tutoria.programaetapatutoria.etapatutoria.obtener_id == 8}
																																		{#if disponible}
																																			<li class="dropdown-item">
																																				{#if tematitulacionposgradomatricula_serializers.tiene_documentos_tutoria_configurado}
																																					<a
																																					href="javascript:void(0)"
																																					on:click={() =>
																																						toggleModalLoadFormAgregarDocumentoFinalPosgrado(
																																							tutoria.id,
																																							tematitulacionposgradomatricula_serializers.id
																																						)}
																																				>
																																					<i
																																						class="bi bi-file-plus-fill"
																																					/>Subir documentos </a
																																				>

																																				{:else}
																																					<a
																																					href="javascript:void(0)"
																																					on:click={() =>
																																						toggleModalLoadFormAgregarDocFinalPosgrado(
																																							tutoria.id,
																																							tematitulacionposgradomatricula_serializers.id
																																						)}
																																				>
																																					<i
																																						class="bi bi-file-plus-fill"
																																					/>Subir doc. Final </a
																																				>

																																				{/if}

																																			</li>
																																		{/if}
																																	{:else}
																																		<li class="dropdown-item">
																																			<a
																																				href="javascript:void(0)"
																																				on:click={() =>
																																					toggleModalLoadFormAgregarAvanceTutoriaPosgrado(
																																						tutoria.id
																																					)}
																																			>
																																				<i
																																					class="bi bi-plus-circle-dotted"
																																				/>
																																				Adicionar avance</a
																																			>
																																		</li>
																																	{/if}
																																</ul>
																															</div>
																														</div>
																													</div>
																												</td>
																											</tr>
																											<tr>
																												<td>
																													<div
																														class="table-responsive overflow-y-hidden"
																													>
																														{#if tutoria.programaetapatutoria.etapatutoria.obtener_id == 8}
																															<table
																																class="table mb-0 text-nowrap mb-5"
																															>
																																<thead class="table-active">
																																	<tr>
																																		<th
																																			scope="col"
																																			class=" border-top-0"
																																		>
																																			%
																																		</th>
																																		<th
																																			scope="col"
																																			class=" border-top-0"
																																		>
																																			Observaciones
																																		</th>
																																		<th
																																			scope="col"
																																			class=" border-top-0"
																																		>
																																			Estado
																																		</th>
																																		<th
																																			scope="col"
																																			class=" border-top-0"
																																		>
																																			Acciones
																																		</th>
																																	</tr>
																																</thead>
																																<tbody>
																																	{#each tutoria.revisiones_tutoria as revision, index}
																																		<tr>
																																			<td class="align-middle">
																																				<p class="text-wrap">
																																					{#if revision.porcentajeurkund}
																																						{converToDecimal(
																																							revision.porcentajeurkund
																																						)}
																																					{/if}
																																				</p>
																																			</td>

																																			<td class="align-middle">
																																				<p class="text-wrap">
																																					{revision.observacion}
																																				</p>
																																			</td>

																																			<td class="align-middle">
																																				<p class="text-wrap">
																																					{#if revision.estado == 4}
																																						<Badge color="warning"
																																							>{revision.estado_display}</Badge
																																						>
																																					{/if}

																																					{#if revision.estado == 3}
																																						<Badge color="secondary"
																																							>{revision.estado_display}</Badge
																																						>
																																					{/if}

																																					{#if revision.estado == 2}
																																						<Badge color="success"
																																							>{revision.estado_display}</Badge
																																						>
																																					{/if}

																																					{#if revision.estado == 1}
																																						<Badge color="info"
																																							>{revision.estado_display}</Badge
																																						>
																																					{/if}
																																				</p>
																																			</td>
																																			<td class="align-middle">
																																				<a
																																					href="javascript:void(0)"
																																					class=" accordion-button"
																																					type="button"
																																					role="button"
																																					data-bs-toggle="collapse"
																																					data-bs-target="#collapseExample_{revision.id}"
																																					aria-expanded="true"
																																					aria-controls="collapseOne"
																																				>
																																					ver archivos
																																				</a>
																																			</td>
																																		</tr>
																																		<tr
																																			class="collapse"
																																			id="collapseExample_{revision.id}"
																																		>
																																			<td colspan="6">
																																				<table
																																					class="table table-success mb-0 text-nowrap"
																																				>
																																					<thead>
																																						<tr>
																																							<th
																																								scope="col"
																																								class="border-0 text-center text-uppercase w-25"
																																							>
																																								N°
																																							</th>
																																							<th
																																								scope="col"
																																								class="border-0 text-center text-uppercase w-25"
																																							>
																																								Archivo
																																							</th>
																																							<th
																																								scope="col"
																																								class="border-0 text-center text-uppercase w-25"
																																							>
																																								Fecha
																																							</th>
																																							<th
																																								scope="col"
																																								class="border-0 text-center text-uppercase w-25"
																																							/>
																																						</tr>
																																					</thead>
																																					<tbody>
																																						{#each revision.archivos as doc, index}
																																							<!-- content here -->
																																							<tr>
																																								<td
																																									scope="col"
																																									class="fs-6 align-middle border-top-0 text-center text-wrap"
																																								>
																																									{index + 1}
																																								</td>

																																								<td
																																									scope="col"
																																									class="fs-6 align-middle border-top-0 text-center text-wrap"
																																								>
																																									{#if doc.archivo}
																																										<a
																																											href="{variables.BASE_API}{doc.archivo}"
																																											target="_blank"
																																											><i
																																												class="bi bi-download"
																																											/>
																																											{doc.tipodisplay}
																																										</a>
																																									{/if}
																																								</td>

																																								<td
																																									scope="col"
																																									class="fs-6 align-middle border-top-0 text-center text-wrap"
																																								>
																																									{doc.fecha}
																																								</td>

																																								<td
																																									scope="col"
																																									class="fs-6 align-middle border-top-0 text-center text-wrap"
																																								>
																																									{#if revision.estado == 1 && !(doc.tipo == 3)}
																																										<button
																																											on:click={() =>
																																												toggleModalEditDocFinalTitulacion(
																																													doc.id
																																												)}
																																											class="btn btn-mini btn-info btn-xs"
																																											><i
																																												class="fe fe-edit"
																																											/></button
																																										>
																																									{/if}
																																								</td>
																																							</tr>
																																						{:else}
																																							No existen documentos
																																						{/each}
																																					</tbody>
																																				</table>
																																			</td>
																																		</tr>
																																	{:else}
																																		<td
																																			colspan="7"
																																			class="text-center"
																																			>NO EXISTEN REGISTROS DE
																																			REVISIONES DE TUTORIA
																																		</td>
																																	{/each}
																																</tbody>
																															</table>
																														{:else}
																															<table
																																class="table mb-0 text-nowrap mb-5"
																															>
																																<thead class="table-active">
																																	<tr>
																																		<th
																																			scope="col"
																																			class=" border-top-0"
																																		>
																																			Revisión
																																		</th>
																																		<th
																																			scope="col"
																																			class=" border-top-0"
																																		>
																																			Avance tutoria
																																		</th>
																																		<th
																																			scope="col"
																																			class=" border-top-0"
																																		>
																																			Correcciones
																																		</th>
																																		<th
																																			scope="col"
																																			class=" border-top-0"
																																		>
																																			Observaciones
																																		</th>
																																		<th
																																			scope="col"
																																			class=" border-top-0"
																																		>
																																			Acciones
																																		</th>
																																	</tr>
																																</thead>
																																<tbody>
																																	{#each tutoria.revisiones_tutoria as revision, index}
																																		<tr>
																																			<td
																																				class="fs-6 align-middle border-top-0 text-center text-wrap"
																																			>
																																				<div
																																					class="d-flex align-items-center"
																																				>
																																					{#if revision.fecharevision}
																																						{revision.fecharevision}
																																					{:else}
																																						<Badge color="danger"
																																							>Sin revisar</Badge
																																						>
																																					{/if}
																																				</div>
																																			</td>
																																			<td
																																				class="fs-6 align-middle border-top-0 text-center text-wrap"
																																			>
																																				<div
																																					class="d-flex align-items-center"
																																				>
																																					{#if revision.tutoria_avance}
																																						<a
																																							class="btn btn-info btn-xs"
																																							target="_blank"
																																							href="{variables.BASE_API}{revision.tutoria_avance}"
																																							title="Evidencia"
																																						>
																																							<i
																																								class="bi bi-download"
																																							/>
																																						</a>
																																					{:else}
																																						S/N
																																					{/if}
																																				</div>
																																			</td>

																																			<td
																																				class="fs-6 align-middle border-top-0 text-center text-wrap"
																																			>
																																				<div
																																					class="d-flex align-items-center"
																																				>
																																					{#if revision.correccion}
																																						{#if revision.correccion.archivo}
																																							<a
																																								class="btn btn-info btn-xs"
																																								target="_blank"
																																								href="{variables.BASE_API}{revision
																																									.correccion
																																									.archivo}"
																																								title="Evidencia"
																																							>
																																								<i
																																									class="bi bi-download"
																																								/>
																																							</a>
																																						{:else}
																																							S/N
																																						{/if}
																																					{/if}
																																				</div>
																																			</td>

																																			<td
																																				class="fs-6 align-middle border-top-0 text-center text-wrap"
																																			>
																																				<p class="text-wrap">
																																					{revision.observacion}
																																				</p>
																																			</td>

																																			<td
																																				class="fs-6 align-middle border-top-0 text-center text-wrap"
																																			/>
																																		</tr>
																																	{:else}
																																		<td
																																			colspan="7"
																																			class="text-center"
																																			>NO EXISTEN REGISTROS DE
																																			REVISIONES DE TUTORIA
																																		</td>
																																	{/each}
																																</tbody>
																															</table>
																														{/if}
																													</div>
																												</td>
																											</tr>
																										</table>
																									</div>
																								{/if}
																							{/if}
																						{/each}
																					</div>
																				</div>
																			</div>
																		</div>
																	</div>
																</div>
															{/each}
														</div>
													</div>
												</div>
											</div>
										{/if}
									</div>
								{/if}
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- nav-tribunal-ev-tab -->
			<div
				class="row tab-pane fade bs-stepper-pane  show "
				id="nav-tribunal-rev"
				role="tabpanel"
				aria-labelledby="nav-tribunal-rev-tab"
			>
				<!-- Card -->
				<div class="card mb-3 ">
					<div class="card-header border-bottom px-4 py-3">
						<h4 class="mb-0">Revisión tribunal</h4>
					</div>
					<!-- Card body -->
					<div class="card-body">
						<div class="row">
							{#if es_en_pareja}
								<div class="col">
									<div class="table-responsive"></div>
									<table class="table mb-0  table-hover table-bordered align-middle">
										<thead class="table-light">
											<tr>
												<th colspan="6"
													><h5>
														REVISIÓN DEL TRABAJO DE TITULACIÓN POR LOS MIEMBROS DEL TRIBUNAL
													</h5></th
												>
											</tr>
											<tr>
												<th scope="col" class="border-top-0 text-center align-middle ">N°</th>
												<th scope="col" class="border-top-0 text-center align-middle "
													>Observación</th
												>

												<th scope="col" class="border-top-0 text-center align-middle "
													>Documento de titulación</th
												>
												<th scope="col" class="border-top-0 text-center align-middle "
													>Revisión emitida por el tribunal calificador</th
												>
												<th scope="col" class="border-top-0 text-center align-middle ">Dictamen</th>
												<th scope="col" class="border-top-0 text-center align-middle "
													>Correcciones</th
												>
											</tr>
										</thead>
										<tbody id="itemsbody" class="datatable">
											{#each revisiones_serializer as revision, index}
												<!-- content here -->
												<tr>
													<td scope="col" class=" align-middle border-top-0 text-center text-wrap">
														{index + 1}
													</td>

													<td scope="col" class=" align-middle border-top-0 text-center text-wrap">
														{revision.observacion}
													</td>

													<td scope="col" class=" align-middle border-top-0 text-center text-wrap">
														<a
															class="btn btn-success btn-mini btn-xs"
															href="{variables.BASE_API}{revision.archivo}"
															target="_blank"><i class="bi bi-file-text" /> Archivo</a
														>
													</td>

													<td scope="col" class=" align-middle border-top-0 text-center text-wrap">
														<a
															on:click={() => toggleModalRevisionDetalle(revision.id)}
															class="btn btn-info btn-xs"><i class="bi bi-file-text" /></a
														>
													</td>

													<td scope="col" class=" align-middle border-top-0 text-center text-wrap">
															<label for="">{revision.estado_display}</label>
													</td>
													{#if revision.estado == 3}
														{#if !revision.obtener_correccion}
															<!-- content here -->
															<td>
																<button
																	on:click={() =>
																		toggleModalLoadFormAgregarCorreccionRevisionTribunal(
																			tematitulacionposgradomatriculacabecera_serializers.id,
																			true
																		)}
																	class="btn btn-mini btn-info btn-xs">Subir corrección</button
																>
															</td>
														{:else}
															<!-- else content here -->
															<td>
																<a
																	href="javascript:void(0)"
																	class=" accordion-button"
																	type="button"
																	role="button"
																	data-bs-toggle="collapse"
																	data-bs-target="#collapseExample_{revision.id}"
																	aria-expanded="true"
																	aria-controls="collapseOne"
																>
																	ver corrección
																</a>
															</td>
														{/if}
														<!-- content here -->
													{/if}
												</tr>
												<tr class="collapse" id="collapseExample_{revision.id}">
													<td colspan="6">
														<table class="table table-success mb-0 text-nowrap">
															<thead>
																<tr>
																	<th scope="col" class="border-0 text-center text-uppercase w-25">
																		Archivo
																	</th>
																	<th scope="col" class="border-0 text-center text-uppercase w-25">
																		Estado
																	</th>
																	<th scope="col" class="border-0 text-center text-uppercase w-25">
																		Fecha Revisión
																	</th>
																	<th scope="col" class="border-0 text-center text-uppercase w-25">
																		Persona Revisión
																	</th>
																	<th scope="col" class="border-0 text-center text-uppercase w-25">
																		Acciones
																	</th>
																</tr>
															</thead>
															<tbody>
																<tr>
																	<td
																		class="fs-6 align-middle text-center border-top-0 text-justify text-wrap"
																	>
																		{#if revision.obtener_correccion.archivo}
																			<a
																				href="{variables.BASE_API}{revision.obtener_correccion
																					.archivo}"
																				target="_blank"
																				><i class="bi bi-file-text" /> Archivo
																			</a>
																		{/if}
																	</td>

																	<td
																		class="fs-6 align-middle  text-center border-top-0 text-justify text-wrap"
																	>
																		{#if revision.obtener_correccion.estado == 1}
																			EN REVISIÓN
																		{/if}
																		{#if revision.obtener_correccion.estado == 2}
																			APROBADO
																		{/if}
																	</td>
																	<td
																		class="fs-6 align-middle text-center border-top-0 text-justify text-wrap"
																	>
																		{#if revision.obtener_correccion.fechapersonaprueba}
																			<!-- content here -->
																			{revision.obtener_correccion.fechapersonaprueba}
																		{/if}
																	</td>
																	<td
																		class="fs-6 align-middle text-center border-top-0 text-justify text-wrap"
																	>
																		{#if revision.obtener_correccion.personaprueba}
																			<!-- content here -->
																			{revision.obtener_correccion.personaprueba.display}
																		{/if}
																	</td>
																	<td
																		class="fs-6 align-middle text-center border-top-0 text-justify text-wrap"
																	>
																		{#if revision.obtener_correccion.estado == 1}
																			<button
																				class="btn btn-mini btn-info btn-xs"
																				on:click={() =>
																					toggleModalLoadFormEditarCorreccionRevisionTribunal(
																						revision.obtener_correccion.id,
																						true
																					)}><i class="fe fe-edit" />Editar</button
																			>
																		{/if}
																	</td>
																</tr>
															</tbody>
														</table>
													</td>
												</tr>
											{:else}
												<!-- empty list -->
												<td colspan="4">No existen revisiones</td>
											{/each}
											{#if revisiones_serializer.length > 0}
												<!-- content here -->
												{#if puede_subir_correccion_revision_tribunal}
													<!-- content here -->
													<tr>
														<td class="align-middle " colspan="7">
															<div class="d-flex align-items-center">
																<a
																	on:click={() =>
																		toggleModalAddCorreccionTrabajoFinalPryTribunal(
																			tematitulacionposgradomatriculacabecera_serializers.id,
																			true
																		)}
																	href="javascript:void(0)"
																	class="text-muted border border-2 rounded-3 card-dashed-hover"
																>
																	<div class="icon-shape icon-sm ">+</div>
																</a>
																<div class="ms-3">
																	<h4 class="mb-0">
																		<a href="javascript:void(0)" class="text-inherit">Adicionar</a>
																	</h4>
																</div>
															</div>
														</td>
													</tr>
												{/if}
											{/if}
										</tbody>
									</table>
								</div>

								<!-- content here -->
							{:else}
								<div class="col">
									<div class="table-responsive">
										<table
										class="table table-responsive mb-0 table-hover table-bordered align-middle  "
									>
										<thead class="table-light">
											<tr>
												<th colspan="6"
													><h5>
														REVISIÓN DEL TRABAJO DE TITULACIÓN POR LOS MIEMBROS DEL TRIBUNAL
													</h5></th
												>
											</tr>
											<tr>
												<th scope="col" class="border-top-0 text-center align-middle ">N°</th>
												<th scope="col" class="border-top-0 text-center align-middle "
													>Observación</th
												>

												<th scope="col" class="border-top-0 text-center align-middle "
													>Documento de titulación</th
												>
												<th scope="col" class="border-top-0 text-center align-middle "
													>Revisión emitida por el tribunal calificador</th
												>
												<th scope="col" class="border-top-0 text-center align-middle ">Dictamen</th>
												<th scope="col" class="border-top-0 text-center align-middle "
													>Correcciones</th
												>
											</tr>
										</thead>
										<tbody id="itemsbody" class="datatable">
											{#each revisiones_serializer as revision, index}
												<!-- content here -->
												<tr>
													<td
														scope="col"
														class="fs-6 align-middle border-top-0 text-center text-wrap"
													>
														{index + 1}
													</td>

													<td scope="col" class=" align-middle border-top-0 text-center text-wrap">
														{revision.observacion}
													</td>

													<td scope="col" class=" align-middle border-top-0 text-center text-wrap">
														<a
															class="btn btn-success btn-mini btn-xs"
															href="{variables.BASE_API}{revision.archivo}"
															target="_blank"><i class="bi bi-file-text" /> Archivo</a
														>
													</td>

													<td scope="col" class=" align-middle border-top-0 text-center text-wrap">
														<a
															on:click={() => toggleModalRevisionDetalle(revision.id)}
															class="btn btn-info btn-xs"><i class="bi bi-file-text" /></a
														>
													</td>

													<td
														scope="col"
														class="fs-6 align-middle border-top-0 text-center text-wrap"
													>
															<label for="">{revision.estado_display}</label>
													</td>
													{#if revision.estado == 3}
														{#if !revision.obtener_correccion}
															<!-- content here -->
															<td>
																<button
																	on:click={() =>
																		toggleModalLoadFormAgregarCorreccionRevisionTribunal(
																			tematitulacionposgradomatricula_serializers.id,
																			false
																		)}
																	class="btn btn-mini btn-info btn-xs">Subir corrección</button
																>
															</td>
														{:else}
															<!-- else content here -->
															<td>
																<a
																	href="javascript:void(0)"
																	class=" accordion-button"
																	type="button"
																	role="button"
																	data-bs-toggle="collapse"
																	data-bs-target="#collapseExample_{revision.id}"
																	aria-expanded="true"
																	aria-controls="collapseOne"
																>
																	ver corrección
																</a>
															</td>
														{/if}
														<!-- content here -->
													{/if}
												</tr>
												<tr class="collapse" id="collapseExample_{revision.id}">
													<td colspan="6">
														<table class="table table-success mb-0 text-nowrap">
															<thead>
																<tr>
																	<th scope="col" class="border-0 text-center text-uppercase w-25">
																		Archivo
																	</th>
																	<th scope="col" class="border-0 text-center text-uppercase w-25">
																		Estado
																	</th>
																	<th scope="col" class="border-0 text-center text-uppercase w-25">
																		Fecha Revisión
																	</th>
																	<th scope="col" class="border-0 text-center text-uppercase w-25">
																		Persona Revisión
																	</th>
																	<th scope="col" class="border-0 text-center text-uppercase w-25">
																		Acciones
																	</th>
																</tr>
															</thead>
															<tbody>
																<tr>
																	<td
																		class="fs-6 align-middle text-center border-top-0 text-justify text-wrap"
																	>
																		{#if revision.obtener_correccion.archivo}
																			<a
																				href="{variables.BASE_API}{revision.obtener_correccion
																					.archivo}"
																				target="_blank"
																				><i class="bi bi-file-text" /> Archivo
																			</a>
																		{/if}
																	</td>

																	<td
																		class="fs-6 align-middle  text-center border-top-0 text-justify text-wrap"
																	>
																		{#if revision.obtener_correccion.estado == 1}
																			EN REVISIÓN
																		{/if}
																		{#if revision.obtener_correccion.estado == 2}
																			APROBADO
																		{/if}
																	</td>
																	<td
																		class="fs-6 align-middle text-center border-top-0 text-justify text-wrap"
																	>
																		{#if revision.obtener_correccion.fechapersonaprueba}
																			<!-- content here -->
																			{revision.obtener_correccion.fechapersonaprueba}
																		{/if}
																	</td>
																	<td
																		class="fs-6 align-middle text-center border-top-0 text-justify text-wrap"
																	>
																		{#if revision.obtener_correccion.personaprueba}
																			<!-- content here -->
																			{revision.obtener_correccion.personaprueba.display}
																		{/if}
																	</td>
																	<td
																		class="fs-6 align-middle text-center border-top-0 text-justify text-wrap"
																	>
																		{#if revision.obtener_correccion.estado == 1}
																			<!-- content here -->
																			<button
																				class="btn btn-mini btn-info btn-xs"
																				on:click={() =>
																					toggleModalLoadFormEditarCorreccionRevisionTribunal(
																						revision.obtener_correccion.id,
																						false
																					)}><i class="fe fe-edit" />Editar</button
																			>
																		{/if}
																	</td>
																</tr>
															</tbody>
														</table>
													</td>
												</tr>
											{:else}
												<!-- empty list -->
												<td colspan="4">No existen revisiones</td>
											{/each}
											{#if revisiones_serializer.length > 0}
												<!-- content here -->
												{#if puede_subir_correccion_revision_tribunal}
													<!-- content here -->
													<tr>
														<td class="align-middle " colspan="7">
															<div class="d-flex align-items-center">
																<a
																	on:click={() =>
																		toggleModalAddCorreccionTrabajoFinalPryTribunal(
																			tematitulacionposgradomatricula_serializers.id,
																			false
																		)}
																	href="javascript:void(0)"
																	class="text-muted border border-2 rounded-3 card-dashed-hover"
																>
																	<div class="icon-shape icon-sm ">+</div>
																</a>
																<div class="ms-3">
																	<h4 class="mb-0">
																		<a href="javascript:void(0)" class="text-inherit">Adicionar</a>
																	</h4>
																</div>
															</div>
														</td>
													</tr>
												{/if}
											{/if}
										</tbody>
									</table>
									</div>

								</div>
							{/if}
						</div>
					</div>
				</div>
			</div>

			<!-- nav-sustentacion-tab -->
			<div
				class="row tab-pane fade bs-stepper-pane  show "
				id="nav-sustentacion"
				role="tabpanel"
				aria-labelledby="nav-sustentacion-tab"
			>
				<!-- Card -->
				<div class="card mb-3 ">
					<div class="card-header border-bottom px-4 py-3">
						<h4 class="mb-0">Sustentación</h4>
					</div>
					<!-- Card body -->
					<div class="card-body">
						<div class="row">
							{#if detallecalificacion.length > 0}
								<div class="col">
									{#each grupo.detalletribunal as listadotribunal}
										<!-- content here -->
										<li
											class="list-group-item list-group-item-success"
											style="padding: 4px 6px;text-align: center;background-color: #dff0d8;"
										>
											<strong>TRIBUNAL CALIFICADOR<br /></strong>{listadotribunal.fechadefensa} |
											{listadotribunal.horadefensa} a
											{listadotribunal.horafindefensa}<br /><strong>Lugar:</strong>
											{listadotribunal.lugardefensa}
										</li>
										<li
											class="list-group-item list-group-item-success"
											style="padding: 2px 4px;"
										/>{/each}

									<!-- content here -->
									<div class=" table-responsive">
										<table class="table mb-0 text-nowrap table-hover table-bordered align-middle">
										<thead class="table-ligth">
											<tr>
												<th scope="col" class="border-top-0 text-center align-middle ">Tribunal</th>
												<th scope="col" class="border-top-0 text-center align-middle ">Nombres</th>
												<th scope="col" class="border-top-0 text-center align-middle "
													>Observación</th
												>
												{#if tematitulacionposgradomatricula_serializers.calificacion_completa}
												<th scope="col" class="border-top-0 text-center align-middle "
													>Notal final</th
												>
												{/if}
											</tr>
										</thead>
										<tbody>
											{#if detallecalificacion.length > 0}
												<!-- content here -->
												{#each detallecalificacion as detalle}
													<!-- content here -->
													<tr>
														<td
															scope="col"
															class="fs-6 align-middle border-top-0 text-justify text-wrap"
														>
															{detalle.tipojuradocalificador}
														</td>
														<td
															scope="col"
															class="fs-6 align-middle border-top-0 text-justify text-wrap"
														>
															{detalle.juradocalificador.display}
														</td>
														<td
															scope="col"
															class="fs-6 align-middle border-top-0 text-justify text-wrap"
														>
															{#if detalle.observacion}
																{detalle.observacion}
															{:else}
																S/N
															{/if}
														</td>
														{#if tematitulacionposgradomatricula_serializers.calificacion_completa}
														<td
															scope="col"
															class="fs-6 align-middle border-top-0 text-justify text-wrap"
														>
															{converToDecimal(detalle.puntajerubricas)}
														</td>
														{/if}
													</tr>
												{/each}
											{:else}
												<!-- else content here -->
												No existen registros
											{/if}
										</tbody>
										{#if tematitulacionposgradomatricula_serializers.calificacion_completa}
										<tfoot>
											<tr>
												<th
													colspan="3"
													scope="col"
													class="fs-6 align-middle border-top-0 text-justify text-wrap"
												>
													PROMEDIO
												</th>
												<th
													scope="col"
													class="fs-6 align-middle border-top-0 text-justify text-wrap"
												>
													{converToDecimal(grupo.calificacion)}
												</th>
											</tr>
										</tfoot>
										{/if}
									</table>
									</div>
									<div class="row mt-5">
										<div class="container">
											{#if grupo.actacerrada}
											 <div class="card-body text-center" style="height: 50vh">
												<span class="text-danger d-none text-left" id="helptext_error_acta_sustentacion"></span>
												 {#if grupo.archivo_acta_sustentacion }
													 <iframe id="id_archivo_acta_sustentacion" src="{grupo.archivo_acta_sustentacion}" width="100%" style="height:50vh" frameborder="0"></iframe>
												 {/if}

											</div>
											<br>
											<div class="d-flex align-items-center">
												<div class="ms-3 mt-3">
													<a href="Javascript:void(0);"
													   on:click={() => openFirmaSolicitud(grupo.id)}
													   class="btn btn-success"> Firmar acta de sustentación</a>

												</div>
											</div>
										{/if}

										</div>

									</div>

								</div>
							{:else}
								<!-- else content here -->
								<Alert color="info">
									<strong>Aviso importante!</strong> <br />
									Se le comunica que no están definidos los miembros del tribunal calificador para su
									sustentación, por favor siga esperando.
								</Alert>
							{/if}
						</div>
					</div>
				</div>
			</div>
		{/if}
		{#if tematitulacionposgradomatricula_serializers.idmecanismotitulacion == 15 ||tematitulacionposgradomatricula_serializers.idmecanismotitulacion == 21}
			{#if tematitulacionposgradomatricula_serializers.estadoaprobacion == 2}
				<!-- nav-complexivo-tab -->
				<div
					class="row tab-pane fade bs-stepper-pane  show "
					id="nav-complexivo"
					role="tabpanel"
					aria-labelledby="nav-complexivo-tab"
				>
					<!-- Card -->
					<div class="card mb-3 ">
						<div class="card-header border-bottom px-4 py-3">
							<h4 class="mb-0">Complexivo</h4>
						</div>
						<!-- Card body -->
						<div class="card-body">
							<div class="row">
								<div class="col-md-3">
									<div class="row">
										<!-- Card -->
										<div class="card mb-4">
											<!-- Card body -->
											<div class="card-body">
												<h5 class="mb-0">
													CRONOGRAMA DE REGISTRO DE DOCUMENTOS DE TRABAJO DE TITULACIÓN
												</h5>
												<div class="d-flex justify-content-between border-bottom py-2 mt-3">
													<span>Nº. revisión</span>
													<span class="text-dark">1</span>
												</div>
												<div class="d-flex justify-content-between border-bottom py-2">
													<span>Fecha inicio:</span>
													<span>{cronograma.fechainiciotutoria} </span>
												</div>
												<div class="d-flex justify-content-between pt-2">
													<span>Fecha fin:</span>
													<span class="text-dark"> {cronograma.fechafintutoria} </span>
												</div>
											</div>
										</div>
									</div>
									<div class="row" />
								</div>
								<div class="col-md-9">
									<div class="row-fluid">
										<div class="accordion" id="accordionExample">
											<div class="accordion-item">
												<h2 class="accordion-header" id="headingOne">
													{#if (cronograma.tipocomponente == 1) | (cronograma.tipocomponente == 2)}
														<button
															class="accordion-button"
															type="button"
															data-bs-toggle="collapse"
															data-bs-target="#collapseOne"
															aria-expanded="true"
															aria-controls="collapseOne"
														>
															Componente práctico
														</button>
													{/if}
												</h2>
												<div
													id="collapseOne"
													class="accordion-collapse collapse show"
													aria-labelledby="headingOne"
													data-bs-parent="#accordionExample"
												>
													<div class="accordion-body">
														<div class="card h-100">
															<!-- Card header -->
															<div
																class="card-header d-flex align-items-center
													justify-content-between card-header-height"
															>
																<h4 class="mb-0">
																	Subida del documento y revisión del componente práctico
																</h4>
																{#if disponible}
																	<button
																		on:click={() => toggleModalAddComponentePractico(grupo.id)}
																		class="btn btn-outline-primary btn-sm">Agregar</button
																	>
																{/if}
															</div>
															<!-- Card body -->
															<div class="card-body">
																<!-- List group flush -->
																<ul class="list-group list-group-flush">
																	<li class="list-group-item px-0 pt-0">
																		<div class="table-responsive border-0 overflow-y-hidden">
																			<table class="table table-light mb-0 text-nowrap">
																				<thead class="table-light">
																					<th
																						scope="col"
																						class="border-0 text-center text-uppercase ">N°</th
																					>
																					<th
																						scope="col"
																						class="border-0 text-center text-uppercase "
																						>Observaciones</th
																					>
																					<th
																						scope="col"
																						class="border-0 text-center text-uppercase">Estado</th
																					>
																					<th
																						scope="col"
																						class="border-0 text-center text-uppercase"
																						>Calificación</th
																					>
																					<th
																						scope="col"
																						class="border-0 text-center text-uppercase">Revisión</th
																					>
																					<th
																						scope="col"
																						class="border-0 text-center text-uppercase"
																					/>
																				</thead>
																				<tbody>
																					{#each propuestas_ensayo as propuesta, index}
																						<tr>
																							<td
																								scope="col"
																								class="fs-6 align-middle border-top-0 text-center text-wrap"
																							>
																								{index + 1}
																							</td>
																							<td
																								scope="col"
																								class="fs-6 align-middle border-top-0 text-center text-wrap"
																							>
																								{propuesta.observacion}
																							</td>
																							<td
																								scope="col"
																								class="fs-6 align-middle border-top-0 text-center text-wrap"
																							>
																								{#if propuesta.estado == 4}
																									<Badge color="warning"
																										>POR REVISIÓN DE PLAGIO</Badge
																									>
																								{:else if propuesta.estado == 3}
																									<Badge color="danger">CORRECIÓN TUTORIA</Badge>
																								{:else if propuesta.estado == 2}
																									<Badge color="success">APTO PARA SUSTENTAR</Badge>
																								{:else}
																									<Badge color="primary">PENDIENTE</Badge>
																								{/if}
																							</td>
																							<td
																								scope="col"
																								class="fs-6 align-middle border-top-0 text-center text-wrap"
																							>
																								{#if propuesta.estado == 2}
																									<!-- content here -->
																									<p>
																										<strong>Calificación: </strong>
																										{converToDecimal(propuesta.calificacion)}
																									</p>

																									<p>
																										<strong>Plagio: </strong>
																										{#if !(propuesta.porcentajeurkund == null)}
																											{converToDecimal(propuesta.porcentajeurkund)} %
																										{/if}
																									</p>
																								{/if}
																							</td>

																							<td>
																								<a
																									href="javascript:void(0)"
																									class=" accordion-button"
																									type="button"
																									role="button"
																									data-bs-toggle="collapse"
																									data-bs-target="#collapseExample_{propuesta.id}"
																									aria-expanded="true"
																									aria-controls="collapseOne"
																								>
																									ver archivos
																								</a>
																							</td>
																						</tr>
																						<tr
																							class="collapse"
																							id="collapseExample_{propuesta.id}"
																						>
																							<td colspan="6">
																								<table class="table table-success mb-0 text-nowrap">
																									<thead>
																										<tr>
																											<th
																												scope="col"
																												class="border-0 text-center text-uppercase w-25"
																											>
																												N°
																											</th>
																											<th
																												scope="col"
																												class="border-0 text-center text-uppercase w-25"
																											>
																												Archivo
																											</th>
																											<th
																												scope="col"
																												class="border-0 text-center text-uppercase w-25"
																											>
																												Fecha
																											</th>
																											<th
																												scope="col"
																												class="border-0 text-center text-uppercase w-25"
																											>
																												Acciones
																											</th>
																										</tr>
																									</thead>
																									<tbody>
																										{#each propuesta.archivos as doc, index}
																											<!-- content here -->
																											<tr>
																												<td
																													scope="col"
																													class="fs-6 align-middle border-top-0 text-center text-wrap"
																												>
																													{index + 1}
																												</td>

																												<td
																													scope="col"
																													class="fs-6 align-middle border-top-0 text-center text-wrap"
																												>
																													{#if doc.archivo}
																														<a
																															href="{variables.BASE_API}{doc.archivo}"
																															target="_blank"
																															><i class="bi bi-download" />
																															{doc.tipodisplay}
																														</a>
																													{/if}
																												</td>

																												<td
																													scope="col"
																													class="fs-6 align-middle border-top-0 text-center text-wrap"
																												>
																													{doc.fecha}
																												</td>

																												<td
																													scope="col"
																													class="fs-6 align-middle border-top-0 text-center text-wrap"
																												>
																													{#if propuesta.estado == 1 && !(doc.tipo == 3)}
																														<button
																															on:click={() =>
																																toggleModalEditDocComponentePractico(
																																	doc.id
																																)}
																															class="btn btn-mini btn-info btn-xs"
																															><i class="fe fe-edit" /></button
																														>
																													{/if}
																												</td>
																											</tr>
																										{:else}
																											No existen documentos
																										{/each}
																									</tbody>
																								</table>
																							</td>
																						</tr>
																					{:else}
																						<tr> No existen documentos registrados </tr>
																					{/each}
																				</tbody>
																			</table>
																		</div>
																	</li>
																</ul>
															</div>
														</div>
													</div>
												</div>
											</div>

											<div class="accordion-item">
												<h2 class="accordion-header" id="headingTwo">
													{#if (cronograma.tipocomponente == 1) | (cronograma.tipocomponente == 3)}
														<button
															class="accordion-button collapsed"
															type="button"
															data-bs-toggle="collapse"
															data-bs-target="#collapseTwo"
															aria-expanded="false"
															aria-controls="collapseTwo"
														>
															Componente teórico
														</button>
													{/if}
												</h2>
												<div
													id="collapseTwo"
													class="accordion-collapse collapse"
													aria-labelledby="headingTwo"
													data-bs-parent="#accordionExample"
												>
													<div class="accordion-body">
														<div class="">
															<!-- Card -->
															<div class="card h-100">
																<!-- Card header -->
																<div
																	class="card-header d-flex align-items-center
														  justify-content-between card-header-height"
																>
																	<h4 class="mb-0">Grupo para rendir examen complexivo</h4>
																	{#if !tematitulacionposgradomatricula_serializers.cumple_malla_completa_aprobada || mensaje3 != ''}
																		{#if !tematitulacionposgradomatricula_serializers.cumple_malla_completa_aprobada}
																			<span class="text-warning">Tiene módulos pendientes</span>
																		{/if}

																		<span class="text-warning">{mensaje3}</span>
																	{:else}
																			<a href="javascript:void(0)" on:click={() =>
																			toggleModalSeleccionarGrupoExamenComplexivo(
																				tematitulacionposgradomatricula_serializers.id,
																				tematitulacionposgradomatricula_serializers.convocatoria.id
																			)}
																		class="btn btn-outline-white btn-sm">Seleccionar</a>

																	{/if}
																</div>
																<!-- Card body -->
																<div class="card-body">
																	{#if grupo_seleccionado.length == null}
																		<!-- List group -->
																		<ul class="list-group list-group-flush">
																			<li class="list-group-item px-0 pt-0 ">
																				<div class="row">
																					<div class="col-auto">
																						<div
																							class="avatar avatar-md avatar-indicators avatar-offline"
																						>
																							{#if grupo_seleccionado.grupoTitulacionPostgrado.tutor.persona.obtenerfoto}
																								<!-- content here -->
																								<img
																									src="{variables.BASE_API}{grupo_seleccionado
																										.grupoTitulacionPostgrado.tutor.persona
																										.obtenerfoto.foto}"
																									class="rounded-circle avatar-xl mb-3"
																									alt=""
																								/>
																							{:else if grupo_seleccionado.grupoTitulacionPostgrado.tutor.persona.sexo == 1}
																								<!-- content here -->
																								<img
																									src="{variables.BASE_API_STATIC}/images/iconos/mujer.png"
																									class="rounded-circle avatar-xl mb-3"
																									alt=""
																								/>
																							{:else}
																								<!-- else content here -->
																								<img
																									src="{variables.BASE_API_STATIC}/images/iconos/hombre.png"
																									class="rounded-circle avatar-xl mb-3"
																									alt=""
																								/>
																							{/if}
																						</div>
																					</div>
																					<div class="col ms-n4">
																						<h4 class="mb-0 h5">
																							{grupo_seleccionado.grupoTitulacionPostgrado.tutor
																								.display}
																						</h4>
																						<span class="me-2 fs-6">
																							<span class="text-dark  me-1 fw-semi-bold"
																								>Telf. Móvil:</span
																							>{grupo_seleccionado.grupoTitulacionPostgrado.tutor
																								.persona.telefono}
																							{#if grupo_seleccionado.grupoTitulacionPostgrado.tutor.persona.telefono}
																								<a
																									href="https://web.whatsapp.com/send?l=en&phone=+593{grupo_seleccionado
																										.grupoTitulacionPostgrado.tutor.persona
																										.telefono}&text=Hola {grupo_seleccionado
																										.grupoTitulacionPostgrado.tutor.display}"
																									target="_blank"
																									class="btn btn-mini btn-success btn-xs"
																									title="Enviar mensaje por whatsapp"
																								>
																									<i class="bi bi-whatsapp" />
																								</a>
																							{/if}
																						</span><br />
																						<span class="me-2 fs-6">
																							{#each grupo_seleccionado.grupoTitulacionPostgrado.tutor.persona.lista_emails as item}
																								{item}
																							{:else}
																								No tiene correos
																							{/each}
																						</span>
																					</div>
																					<div class="col ms-n2">
																						<span class="me-2 fs-6">
																							<span class="text-dark  me-1 fw-semi-bold"
																								>Cupos disponibles:</span
																							>{grupo_seleccionado.grupoTitulacionPostgrado
																								.cuposdisponibles} / {grupo_seleccionado
																								.grupoTitulacionPostgrado.cupo}</span
																						>
																						<br />
																						<span class="me-2 fs-6">
																							<span class="text-dark  me-1 fw-semi-bold">
																								Fecha:</span
																							>
																							{grupo_seleccionado.grupoTitulacionPostgrado.fecha} -
																							<span class="text-dark  me-1 fw-semi-bold">
																								Hora:</span
																							>
																							{grupo_seleccionado.grupoTitulacionPostgrado.hora}
																						</span>

																						<br />
																						<span class="fs-6">
																							<span class="text-dark  me-1 fw-semi-bold"
																								>Url Zoom:</span
																							>
																							<a
																								target="_blank"
																								href={grupo_seleccionado.grupoTitulacionPostgrado
																									.link_zoom}
																								>{grupo_seleccionado.grupoTitulacionPostgrado
																									.link_zoom}</a
																							>
																						</span>
																						<br />
																						<span class="me-2 fs-6">
																							<span class="text-dark  me-1 fw-semi-bold ">
																								Paralelo:</span
																							>
																							<span class="text-uppercase"
																								>{grupo_seleccionado.grupoTitulacionPostgrado
																									.paralelo}</span
																							>
																						</span>
																					</div>
																				</div>
																			</li>
																		</ul>
																	{:else}
																		No tiene grupo seleccionado para rendir el examen complexivo,
																		por favor <strong>seleccionar</strong> uno.
																	{/if}
																</div>
															</div>
														</div>
													</div>
												</div>
											</div>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- nav-calificaciones-tab -->
				<div
					class="row tab-pane fade bs-stepper-pane  show "
					id="nav-calificaciones"
					role="tabpanel"
					aria-labelledby="nav-calificaciones-tab"
				>
					<!-- Card -->
					<div class="card mb-3 ">
						<div class="card-header border-bottom px-4 py-3">
							<h4 class="mb-0" />
						</div>
						<!-- Card body -->
						<div class="card-body">
							<div class="row">
								{#if tiene_notas_complexivo}
									<div class="col">
										<table class="table mb-0 text-nowrap table-hover table-bordered align-middle">
											<thead class="table-light">
												<tr>
													<th colspan="4"><h5>Firmas acta de aprobación complexivo</h5></th>
												</tr>
												<tr>
													<th scope="col" class="border-top-0 text-center align-middle ">Persona</th
													>
													<th scope="col" class="border-top-0 text-center align-middle ">Archivo</th
													>
													<th scope="col" class="border-top-0 text-center align-middle ">Estado</th>
													<th scope="col" class="border-top-0 text-center align-middle ">Fecha</th>
												</tr>
											</thead>
											<tbody id="itemsbody" class="datatable">
												{#if historial_firma.length > 0}
													{#each historial_firma as historial}
														<tr>
															<td class="fs-6 align-middle border-top-0 text-justify text-wrap">
																{historial.persona.nombre_completo}
															</td>
															<td class="fs-6 align-middle border-top-0 text-center text-wrap">
																<a
																	class="btn btn-info btn-xs"
																	href="{variables.BASE_API}{historial.actaaprobacionfirmada}"
																	target="_blank"
																>
																	<i class="bi bi-download" />
																</a>
															</td>

															<td class="fs-6 align-middle border-top-0 text-justify text-wrap">
																{historial.estado_acta_firma}
															</td>

															<td class="fs-6 align-middle border-top-0 text-justify text-wrap">
																{historial.fecha_creacion}
															</td>
														</tr>
													{/each}
												{:else}
													<tr>
														<td colspan="8" class="text-center">NO EXISTEN REGISTROS</td>
													</tr>
												{/if}
											</tbody>
											<tfoot>
												<tr>
													{#if tematitulacionposgradomatricula_serializers.estado_acta_firma == 1 || tematitulacionposgradomatricula_serializers.estado_acta_firma == 2}
														<td colspan="4">
															<button
																on:click={() =>
																	toggleModalAddActaFirmada(
																		tematitulacionposgradomatricula_serializers.id
																	)}
																class="btn btn-success btn-mini btn-xs"
															>
																Adicionar</button
															>

															<a
																on:click={() =>descargar_pdf_complexivo(tematitulacionposgradomatricula_serializers.id,variables.BASE_API)}
																href="Javascript:void(0);"
																class="btn btn-info btn-mini btn-xs"
															>
																<span class="bi bi-download" aria-hidden="true" /> Formato acta complexivo</a
															>
														</td>
													{/if}
												</tr>
											</tfoot>
										</table>
									</div>
								{/if}

								<div class="col">
									<table class="table mb-0 text-nowrap table-hover table-bordered align-middle">
										<thead class="table-light">
											<tr>
												<th colspan="4"><h5>DETALLE DE CALIFICACIÓN</h5></th>
											</tr>
											<tr>
												<th scope="col" class="border-top-0 text-center align-middle "
													>COMPONENTE DE TITULACIÓN</th
												>
												<th scope="col" class="border-top-0 text-center align-middle ">NOTA</th>
											</tr>
										</thead>
										<tbody id="itemsbody" class="datatable">
											{#if (cronograma.tipocomponente == 1) | (cronograma.tipocomponente == 2)}
												<tr>
													<td
														scope="col"
														class="fs-6 align-middle border-top-0 text-justify text-wrap"
													>
														COMPONENTE PRÁCTICO (Ensayo)
													</td>
													<td
														scope="col"
														class="fs-6 align-middle border-top-0 text-center text-wrap"
													>
														{converToDecimal(
															tematitulacionposgradomatricula_serializers.obtener_calificacion_ensayo
														)}
													</td>
												</tr>
											{/if}
											{#if (cronograma.tipocomponente == 1) | (cronograma.tipocomponente == 3)}
												<tr>
													<td
														scope="col"
														class="fs-6 align-middle border-top-0 text-justify text-wrap"
													>
														COMPONENTE TEÓRICO (Examen)
													</td>
													<td
														scope="col"
														class="fs-6 align-middle border-top-0 text-center text-wrap"
													>
														{converToDecimal(
															tematitulacionposgradomatricula_serializers.obtener_nota_examen_complexivo
														)}
													</td>
												</tr>
											{/if}
										</tbody>
										<tfoot>
											<tr>
												<td colspan="1">
													<strong>Nota final:</strong>
												</td>
												<td
													colspan="1"
													scope="col"
													class="fs-6 align-middle border-top-0 text-center text-wrap"
												>
													<strong>
														{#if cronograma.tipocomponente != 3}
															{converToDecimal(
																tematitulacionposgradomatricula_serializers.obtener_calificacion_total_complexivo
															)}
														{:else}
															{converToDecimal(
																tematitulacionposgradomatricula_serializers.obtener_nota_examen_complexivo
															)}
														{/if}
													</strong>
												</td>
											</tr>
										</tfoot>
									</table>
								</div>
							</div>
						</div>
					</div>
				</div>
			{/if}
		{/if}
	</div>
</div>
{:else}
	<ModuleError title="Proceso Titulación Posgrado" message="{message_error}"/>
{/if}

{#if mOpenModalGenerico}
	<ModalGenerico
		mToggle={mToggleModalGenerico}
		mOpen={mOpenModalGenerico}
		modalContent={modalDetalleContent}
		title={modalTitle}
		aData={aDataModal}
		size="xl"
		on:actionRun={actionRun}
	/>
{/if}

{#if mOpenOffCanvasGenerico}
	<OffCanvasGenerico
		mToggle={mToggleOffCanvasGenerico}
		mOpen={mOpenOffCanvasGenerico}
		OffCanvasContent={modalDetalleOffCanvasContent}
		aData={aDataModal}
		placement={aplacement}
		{modalTitle}
		on:actionRun={actionRun}
	/>
{/if}


<Modal
	isOpen={mOpenFirmaSolicitud}
	toggle={mToggleFirmaSolicitud}
	size={mSizeFirmaSolicitud}
	class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
	backdrop="static"
	fade={false}
>
	<ModalHeader toggle={mToggleFirmaSolicitud}>
		<h4>{titleFirmaSolicitud}</h4>
	</ModalHeader>
	<ModalBody>
		<form
			id="frmFirmaSolicitud"
			on:submit|preventDefault={() => saveFirmaSolicitud(grupo.id)}
			autocomplete="off"
		>
			<div class="card-body">
				<div class="row g-3">
					{#if true}
						<button
							class="btn btn-link btn-sm p-0 m-0"
							on:click|preventDefault={async () =>
								await downloadsoli(grupo.archivo_acta_sustentacion)}
						>
							Click aquí para descargar el archivo acta de sustentación</button
						>
					{/if}
					<div class="col-md-12">
						<input
							type="checkbox"
							class="form-check-input"
							id="id_firmararchivo"
							on:change={changetypeval2}
						/>
						<label class="form-check-label" for="id_firmararchivo" />
						<b
							>Marque esta casilla si no tiene firma electrónica, para subir directamente el archivo
							firmado.</b
						><br />
					</div>
					<div class="col-md-12" id="id_div_solicitud">
						<label for="eFileSolicitudForm" class="form-label fw-bold"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> Archivo de firma ec:</label
						>
						<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
						<FilePond
							class="pb-0 mb-0"
							id="eFileSolicitudForm"
							bind:this={pondFirmaSolicitud}
							{nameFirmaSolicitud}
							name="eFileSolicitudForm"
							labelIdle={[
								'<span class="filepond--label-action">Subir archivo de firma electrónica</span>'
							]}
							allowMultiple={true}
							oninit={handleInit}
							onaddfile={handleAddFileFirmaSolicitud}
							credits=""
							acceptedFileTypes={['application/pdf']}
							labelInvalidField="El campo contiene archivos no válidos"
							maxFiles="1"
							maxFileSize="10MB"
							maxParallelUploads="1"
						/>
						<small class="text-warning">Tamaño máximo permitido 10Mb</small>
					</div>
					<div class="col-md-12" id="id_div_password">
						<label for="ePassword" class="form-label fw-bold"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> Contraseña:
						</label>
						<input
							type="password"
							class="form-control"
							id="ePassword"
							name="ePassword"
							bind:value={ePassword}
						/>
					</div>

					<div class="col-md-12" id="id_div_solicitudsign" style="display: none;">
						<label for="eFileSolicitudSignForm" class="form-label fw-bold"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> Archivo de solicitud firmado por el inscrito:</label
						>
						<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
						<FilePond
							class="pb-0 mb-0"
							id="eFileSolicitudSignForm"
							bind:this={pondFirmaSolicitudSign}
							{nameFirmaSolicitudSign}
							name="eFileSolicitudSignForm"
							labelIdle={['<span class="filepond--label-action">Subir archivo de firmado</span>']}
							allowMultiple={true}
							oninit={handleInit}
							onaddfile={handleAddFileFirmaSolicitudSign}
							credits=""
							acceptedFileTypes={['application/pdf']}
							labelInvalidField="El campo contiene archivos no válidos"
							maxFiles="1"
							maxFileSize="10MB"
							maxParallelUploads="1"
						/>
						<small class="text-warning">Tamaño máximo permitido 10Mb. Formato permitido: pdf</small
						><br />
						<small class="text-warning"
							>Recuerde que el archivo de solicitud de homologación debe ser firmado por el
							inscrito, caso contrario no se podrá proceder con su proceso de homologación.</small
						>
					</div>
				</div>
				<div class="card-footer text-muted">
					<div class="d-grid gap-2 d-md-flex justify-content-md-end">
						<!--<button class="btn btn-primary me-md-2" type="button">Button</button>-->
						<button type="submit" class="btn btn-info"
						style="background-color: #FF9A01; border-color: #FF9A01">Guardar</button>
						<a
							href=""
							class="btn btn-danger"
							style="background-color: #13344B; border-color: #13344B"
							on:click={() => closeFirmaSolicitudForm()}>Cerrar</a
						>
					</div>
				</div>
			</div>
		</form>
	</ModalBody>
</Modal>

<style>
	/* 	CSS variables can be used to control theming.
			https://github.com/rob-balfre/svelte-select/blob/master/docs/theming_variables.md
	*/

	form {
		/*max-width: 400px;*/
		background: #f4f4f4;
		padding: 0;
		border-radius: 4px;
	}

	label {
		margin: 0 0 10px;
	}
	.themed {
		--border: 3px solid blue;
		--borderRadius: 10px;
		--placeholderColor: blue;
	}
</style>
