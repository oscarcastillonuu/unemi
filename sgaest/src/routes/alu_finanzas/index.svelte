<script context="module" lang="ts">
	import type { Load } from '@sveltejs/kit';
	export const load: Load = async ({ fetch }) => {
		let eReportes = [];
		let ePersona = {};
		let eCompromisoPagoPosgrado = [];
		let eRubros = [];
		let tipoperiodo = 0;
		let eMatricula = {};
		let ePeriodoMatricula = {};
		let canlespago = '';
		let compromisopago = {};
		let estado_civil = [];
		let imprimircompromiso = false;
		const ds = browserGet('dataSession');
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			const [res, errors] = await apiGET(fetch, 'alumno/finanzas', {});
			loading.setLoading(false, 'Cargando, espere por favor...');
			//console.log(res);
			if (errors.length > 0) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				return {
					status: 302,
					redirect: '/'
				};
			} else {
				if (!res.isSuccess) {
					if (!res.module_access) {
						if (res.redirect) {
							if (res.token) {
								return (window.location.href = `${connectionToken}&ret=/${res.redirect}`);
							} else {
								addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
								return {
									status: 302,
									redirect: `/${res.redirect}`
								};
							}
						} else {
							addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
							return {
								status: 302,
								redirect: '/'
							};
						}
					} else {
						addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
						return {
							status: 302,
							redirect: '/'
						};
					}
				} else {
					// console.log(res.data);
					eRubros = res.data['eRubros'];
					eReportes = res.data['eReportes'];
					ePersona = res.data['ePersona'];
					tipoperiodo = res.data['tipoperiodo'];
					eMatricula = res.data['eMatricula'];
					ePeriodoMatricula = res.data['ePeriodoMatricula'];
					canlespago = res.data['canlespago'];
					compromisopago = res.data['compromisopago'];
					estado_civil = res.data['estado_civil'];
					imprimircompromiso = res.data['imprimircompromiso'];
				}
			}
		}

		return {
			props: {
				eReportes,
				eRubros,
				ePersona,
				tipoperiodo,
				eMatricula,
				ePeriodoMatricula,
				canlespago,
				compromisopago,
				estado_civil,
				imprimircompromiso
			}
		};
	};
</script>

<script lang="ts">
	import { addToast } from '$lib/store/toastStore';
	import { browserGet, apiPOSTFormData, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import { Button, Icon, Modal, ModalBody, ModalFooter, ModalHeader } from 'sveltestrap';
	import FilePond, { registerPlugin, supported } from 'svelte-filepond';
	import FilePondPluginFileValidateType from 'filepond-plugin-file-validate-type';
	import { onMount } from 'svelte';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { navigating } from '$app/stores';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import componenteDetalleFinanza from './_detallefinanza.svelte';
	import { converToDecimal } from '$lib/formats/formatDecimal';
	import { addNotification } from '$lib/store/notificationStore';
	import { Spinner, Tooltip } from 'sveltestrap';
	import Swal from 'sweetalert2';
	import { goto } from '$app/navigation';
	import { createEventDispatcher, onDestroy } from 'svelte';
	import { dndzone, overrideItemIdKeyNameBeforeInitialisingDndZones } from 'svelte-dnd-action';
	import ComponenteGuia from './_mostrardocumentos.svelte';

	const dispatch = createEventDispatcher();
	export let ePersona;
	export let eRubros;
	export let eReportes;
	export let tipoperiodo;
	export let eMatricula;
	export let ePeriodoMatricula;
	export let canlespago;
	export let compromisopago;
	export let estado_civil;
	export let imprimircompromiso;
	let load = true;
	let conyuguedatos = [];
	let open = false;
	let itemsBreadCrumb = [{ text: 'Mis Finanzas', active: true, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };
	let aDataModal = {};
	let modalTitle = '';
	let modalDetalleContent;
	let mOpenModalGenerico = false;
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);

	let mSizeDocumentosPersonales = 'lg';
	let mOpenDocumentosPersonales = false;
	const mToggleDocumentosPersonales = () =>
		(mOpenDocumentosPersonales = !mOpenDocumentosPersonales);

	let mSizePagare = 'lg';
	let mOpenPagare = false;
	const mTogglePagare = () => (mOpenPagare = !mOpenPagare);
	let titlePagare;

	let mSizeDocumentosComprobante = 'lg';
	let mOpenDocumentosComprobante = false;
	const mToggleDocumentosComprobante = () =>
		(mOpenDocumentosComprobante = !mOpenDocumentosComprobante);

	let mSizeGarante = 'lg';
	let mOpenGarante = false;
	const mToggleGarante = () => (mOpenGarante = !mOpenGarante);

	let mSizeConyuge = 'lg';
	let mOpenConyuge = false;
	const mToggleConyuge = () => (mOpenConyuge = !mOpenConyuge);

	let mSizeConyugeGarante = 'lg';
	let mOpenConyugeGarante = false;
	const mToggleConyugeGarante = () => (mOpenConyugeGarante = !mOpenConyugeGarante);

	let pondDocumento;
	let pondDocumentoVotacion;

	let nameDocumento = 'fileDocumento';
	let nameVotacion = 'fileVotacion';

	let pondDocumentoConyugue;
	let pondDocumentoVotacionConyugue;

	let nameDocumentoConyugue = 'fileDocumentoConyugue';
	let nameVotacionConyugue = 'fileVotacionConyugue';

	let pondComprobante;
	let nameComrpobante = 'fileDocumentoComprobante';

	let pondDocumentoGarante;
	let pondDocumentoVotacionGarante;

	let nameDocumentoGarante = 'fileDocumentoGarante';
	let nameVotacionGarante = 'fileVotacionGarante';

	// PERSONA JURIDICA SI

	let pondCopiaConstitucionGarante;
	let nameCopiaConstitucionGarante = 'fileCopiaConstitucionGarante';

	let pondCertificacionLegal;
	let nameCertificacionLegal = 'fileCertificacionLegal';

	let pondDeclaracionRenta;
	let nameDeclaracionRenta = 'fileCertificacionLegal';

	let pondNombramientoRepre;
	let nameNombramientoRepre = 'fileNombramientoRepre';

	let pondActaJunta;
	let nameActaJunta = 'fileActaJunta';

	let pondRUC;
	let nameRUC = 'fileRUC';

	// Trabajador Relación Dependencia SI
	let pondRolPago;
	let nameRolPago = 'fileRolPago';

	// Trabajador Relación Dependencia NO
	let pondPagoImpuestosPre;
	let namePagoImpuestosPre = 'filePagoImpuestosPre';

	let pondFacturaServicioBasico;
	let nameFacturaServicioBasico = 'fileFacturaServicioBasico';

	let pondRISEoRUC;
	let nameRISEoRUC = 'fileRISEoRUC';

	let pondTablaAmortizacion;
	let pondContratoMaestria;
	let pondPagare;

	let nameTablaAmortizacion = 'fileTablaAmortizacion';
	let nameContratoMaestria = 'fileContratoMaestria';
	let namePagare = 'filePagare';

	const toggle = () => (open = !open);

	let cedulaconyugue = '';
	let nombresconyugue = '';
	let apellido1conyugue = '';
	let apellido2conyugue = '';
	let direcionconyugue = '';
	let sexo_id_conyugue;
	let conyugue_estadocivil;

	let accion_conyugue = '';

	let persona_juridica = false;

	let trabajador_relacion_dependencia = 0;

	let cedulagarante = '';
	let nombresgarante = '';
	let apellido1garante = '';
	let apellido2garante = '';
	let direciongarante = '';
	let sexo_id_garante;
	let estado_civil_garante;

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	let clasificacion = 0;

	onMount(async () => {
		registerPlugin(FilePondPluginFileValidateType);
		const ds = browserGet('dataSession');
		const dataSession = JSON.parse(ds);
		const coordinacion = dataSession['coordinacion'];
		clasificacion = coordinacion.clasificacion;
		if (ePersona) {
			load = false;
		}
		sexo_id_conyugue = 0;
		conyugue_estadocivil = 0;
	});

	const handleInit = () => {
		console.log('FilePond has initialised');
	};

	const handleAddFile = (err, fileItem) => {
		console.log(pondDocumento.getFiles());
		console.log('A file has been added', fileItem);
	};
	const handleAddFileComprobante = (err, fileItem) => {
		console.log(pondComprobante.getFiles());
		console.log('A file has been added', fileItem);
	};

	const handleAddFileVotacion = (err, fileItem) => {
		console.log(pondDocumentoVotacion.getFiles());
		console.log('A file has been added', fileItem);
	};

	const handleAddFileConyugue = (err, fileItem) => {
		console.log(pondDocumentoConyugue.getFiles());
		console.log('A file has been added', fileItem);
	};

	const handleAddFileVotacionGarante = (err, fileItem) => {
		console.log(pondDocumentoVotacionGarante.getFiles());
		console.log('A file has been added', fileItem);
	};

	const handleAddFileGarante = (err, fileItem) => {
		console.log(pondDocumentoGarante.getFiles());
		console.log('A file has been added', fileItem);
	};

	//PERSONA JURIDICA SI

	const handleAddFileVotacionConyugue = (err, fileItem) => {
		console.log(pondDocumentoVotacionConyugue.getFiles());
		console.log('A file has been added', fileItem);
	};

	const handleAddFileCopiaConstitucion = (err, fileItem) => {
		console.log(pondCopiaConstitucionGarante.getFiles());
		console.log('A file has been added', fileItem);
	};

	const handleAddFileCertificadoExistencia = (err, fileItem) => {
		console.log(pondCertificacionLegal.getFiles());
		console.log('A file has been added', fileItem);
	};

	const handleAddFileDeclaracionRenta = (err, fileItem) => {
		console.log(pondDeclaracionRenta.getFiles());
		console.log('A file has been added', fileItem);
	};

	const handleAddFileNombramientoRepresentante = (err, fileItem) => {
		console.log(pondNombramientoRepre.getFiles());
		console.log('A file has been added', fileItem);
	};

	const handleAddFileActaJuntaAcciones = (err, fileItem) => {
		console.log(pondActaJunta.getFiles());
		console.log('A file has been added', fileItem);
	};

	const handleAddFileRUC = (err, fileItem) => {
		console.log(pondRUC.getFiles());
		console.log('A file has been added', fileItem);
	};

	//trabajador relacion dependencia SI

	const handleAddFileRolPago = (err, fileItem) => {
		console.log(pondRolPago.getFiles());
		console.log('A file has been added', fileItem);
	};

	//trabajador relacion dependencia NO

	const handleAddFilePagoImpuestoPrediales = (err, fileItem) => {
		console.log(pondPagoImpuestosPre.getFiles());
		console.log('A file has been added', fileItem);
	};

	const handleAddFileFacturaServicioBasico = (err, fileItem) => {
		console.log(pondFacturaServicioBasico.getFiles());
		console.log('A file has been added', fileItem);
	};

	const handleAddFileRISEoRUC = (err, fileItem) => {
		console.log(pondRISEoRUC.getFiles());
		console.log('A file has been added', fileItem);
	};

	const handleAddFileTableAmortizacion = (err, fileItem) => {
		console.log(pondTablaAmortizacion.getFiles());
		console.log('A file has been added', fileItem);
	};

	const handleAddFileContratoM = (err, fileItem) => {
		console.log(pondContratoMaestria.getFiles());
		console.log('A file has been added', fileItem);
	};

	const handleAddFilePagare = (err, fileItem) => {
		console.log(pondPagare.getFiles());
		console.log('A file has been added', fileItem);
	};

	const action_init_load = async () => {
		const ds = browserGet('dataSession');
		loading.setLoading(true, 'Cargando, espere por favor...');
		if (ds != null || ds != undefined) {
			const [res, errors] = await apiGET(fetch, 'alumno/finanzas', {});

			//console.log(res);
			if (errors.length > 0) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				return {
					status: 302,
					redirect: '/'
				};
			} else {
				if (!res.isSuccess) {
					addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
					return {
						status: 302,
						redirect: '/'
					};
				} else {
					//console.log(res.data);
					eRubros = res.data['eRubros'];
					eReportes = res.data['eReportes'];
					ePersona = res.data['ePersona'];
					tipoperiodo = res.data['tipoperiodo'];
					eMatricula = res.data['eMatricula'];
					ePeriodoMatricula = res.data['ePeriodoMatricula'];
					canlespago = res.data['canlespago'];
				}
			}
		}
		loading.setLoading(false, 'Cargando, espere por favor...');
	};

	const action_to_show_rubro = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/finanzas', {
			action: 'loadPagos',
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
				//console.log(res.data);
				aDataModal = res.data;
				modalDetalleContent = componenteDetalleFinanza;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'Pagos del rubro';
			}
		}
	};

	const action_to_differ = async () => {
		const fnLoad = async () => {
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiPOST(fetch, 'alumno/finanzas', {
				action: 'to_differ',
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
					addNotification({
						msg: 'Se ha diferido el arancel correctamente',
						type: 'success'
					});
					await action_init_load();
				}
			}
		};
		const mensaje = {
			title: `¡Advertencia!`,
			html: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
				ePersona.nombre_completo
			}, ¿desea diferir el valor de <strong>$ ${
				eMatricula.rubro_arancel.valorarancel
			}</strong> del rubro <strong>${eMatricula.rubro_arancel.descripcion}</strong> a <strong>${
				ePeriodoMatricula.num_cuotas_rubro
			}</strong> ${ePeriodoMatricula.num_cuotas_rubro > 1 ? 'meses' : 'mes'}?
			${
				ePeriodoMatricula.valida_rubro_acta_compromiso
					? '<h4>Recordatorio</h4><p>Al final del proceso se generará una acta de compromiso</p>'
					: ''
			}
			`,
			type: 'warning',
			icon: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: 'Si',
			cancelButtonText: 'No'
		};
		Swal.fire(mensaje)
			.then((result) => {
				if (result.value) {
					fnLoad();
				} else {
					addNotification({
						msg: 'Se ha cancelado la acción, el valor del arancel no se diferio',
						type: 'info'
					});
				}
			})
			.catch((error) => {
				addNotification({ msg: error.message, type: 'error' });
			});
	};

	const openDocumentosPersonales = () => {
		loading.setLoading(false, 'Cargando, espere por favor...');
		mSizeDocumentosPersonales = 'lg';
		mOpenDocumentosPersonales = true;
	};

	const openComprobantePago = () => {
		loading.setLoading(false, 'Cargando, espere por favor...');
		mSizeDocumentosComprobante = 'lg';
		mOpenDocumentosComprobante = true;
	};

	const openPagare = () => {
		loading.setLoading(false, 'Cargando, espere por favor...');
		if (compromisopago.tipo == 1) {
			titlePagare = 'Subir Tabla amortización, Contrato y Pagaré';
		} else {
			titlePagare = 'Subir Tabla amortización y Pagaré';
		}
		mSizePagare = 'lg';
		mOpenPagare = true;
	};

	const openGarante = async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/finanzas', {
			action: 'datosgarante',
			id: compromisopago.id
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
				let garantedatos = [];
				garantedatos = res.data['datos_garante'];
				if (garantedatos) {
					cedulagarante = garantedatos.cedula;
					nombresgarante = garantedatos.nombres;
					apellido1garante = garantedatos.apellido1;
					apellido2garante = garantedatos.apellido2;
					direciongarante = garantedatos.direccion;
					sexo_id_garante = garantedatos.genero;
					estado_civil_garante = garantedatos.estadocivil;
					persona_juridica = res.data['persona_juridica'];
					trabajador_relacion_dependencia = res.data['relacion_dependencia'];
				} else {
					cedulagarante = '';
					nombresgarante = '';
					apellido1garante = '';
					apellido2garante = '';
					direciongarante = '';
					sexo_id_garante = 0;
					estado_civil_garante = 0;
					persona_juridica = false;
					trabajador_relacion_dependencia = 0;
				}

				mSizeGarante = 'xl';
				mOpenGarante = true;
			}
		}
	};

	const openDatosConyugueGarante = async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/finanzas', {
			action: 'datosconyuguegarante',
			id: compromisopago.id
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
				let conyuguedatos_garante = [];
				conyuguedatos_garante = res.data['datos_conyugue_garante'];
				accion_conyugue = 'guardardatosconyugegarante';
				modalTitle = 'Datos del Cónyuge del Garante';

				if (conyuguedatos_garante) {
					cedulaconyugue = conyuguedatos_garante.cedula;
					nombresconyugue = conyuguedatos_garante.nombres;
					apellido1conyugue = conyuguedatos_garante.apellido1;
					apellido2conyugue = conyuguedatos_garante.apellido2;
					direcionconyugue = conyuguedatos_garante.direccion;
					sexo_id_conyugue = conyuguedatos_garante.genero;
					conyugue_estadocivil = conyuguedatos_garante.estadocivil;
				} else {
					cedulaconyugue = '';
					nombresconyugue = '';
					apellido1conyugue = '';
					apellido2conyugue = '';
					direcionconyugue = '';
					sexo_id_conyugue = 0;
					conyugue_estadocivil = 0;
				}

				mSizeConyuge = 'lg';
				mOpenConyuge = true;
			}
		}
	};
	const openDatosConyugue = async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/finanzas', {
			action: 'datosconyugue',
			id: compromisopago.id
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
				conyuguedatos = res.data['datos_conyugue'];
				modalTitle = 'Datos del Cónyuge del Alumno';
				accion_conyugue = 'guardardatosconyuge';

				if (conyuguedatos) {
					cedulaconyugue = conyuguedatos.cedula;
					nombresconyugue = conyuguedatos.nombres;
					apellido1conyugue = conyuguedatos.apellido1;
					apellido2conyugue = conyuguedatos.apellido2;
					direcionconyugue = conyuguedatos.direccion;
					sexo_id_conyugue = conyuguedatos.genero;
					conyugue_estadocivil = conyuguedatos.estadocivil;
				} else {
					cedulaconyugue = '';
					nombresconyugue = '';
					apellido1conyugue = '';
					apellido2conyugue = '';
					direcionconyugue = '';
					sexo_id_conyugue = 0;
					conyugue_estadocivil = 0;
				}

				mSizeConyuge = 'lg';
				mOpenConyuge = true;
			}
		}
	};
	const closeDocumentosPersonales = () => {
		mOpenDocumentosPersonales = false;
	};
	const closePagare = () => {
		mOpenPagare = false;
	};
	const closeComprobante = () => {
		mOpenDocumentosComprobante = false;
	};
	const closeConyugue = () => {
		mOpenConyuge = false;
	};
	const closeGarante = () => {
		mOpenGarante = false;
	};

	const toggleModalDetalleOferta = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/finanzas', {
			action: 'mostrardocumentos',
			id: id,
			idmatricula: eMatricula.id
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
				console.log(res.data);
				aDataModal = res.data;
				modalDetalleContent = ComponenteGuia;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'Mostrar documentos ingresados';
			}
		}
	};

	const saveInfoArchivo = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmInfoArchivo = document.querySelector('#frmInfoArchivo');
		const formData = new FormData($frmInfoArchivo);

		formData.append('action', 'addDocumentosPersonales');

		formData.append('id', compromisopago.id);
		formData.append('id_matri', eMatricula.id);

		let fileDocumento = pondDocumento.getFiles();
		if (fileDocumento.length == 0) {
			addNotification({
				msg: 'Debe subir un archivo',
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
		if (pondDocumento && pondDocumento.getFiles().length > 0) {
			eFileDocumento = pondDocumento.getFiles()[0];
		}
		//console.log(eFileDocumento);
		formData.append('fileDocumento', eFileDocumento.file);

		let fileDocumentoVotacion = pondDocumentoVotacion.getFiles();
		if (fileDocumentoVotacion.length == 0) {
			addNotification({
				msg: 'Debe subir un documento de votación',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		if (fileDocumentoVotacion.length > 1) {
			addNotification({
				msg: 'Archivo de documento debe ser único',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		let eFileDocumentoVotacion = undefined;
		if (pondDocumentoVotacion && pondDocumentoVotacion.getFiles().length > 0) {
			eFileDocumentoVotacion = pondDocumentoVotacion.getFiles()[0];
		}
		//console.log(eFileDocumento);
		formData.append('eFileDocumentoVotacion', eFileDocumentoVotacion.file);

		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/finanzas', formData);

		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				if (!res.module_access) {
					goto('/');
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				dispatch('actionRun', { action: 'nextProccess', value: 1 });
				loading.setLoading(false, 'Cargando, espere por favor...');
				mOpenDocumentosPersonales = false;
				action_init_load();
			}
		}
		//addNotification({ msg: 'entro', type: 'error', target: 'newNotificationToast' });
	};

	const saveInfoPagare = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmInfoPagare = document.querySelector('#frmInfoPagare');
		const formData = new FormData($frmInfoPagare);

		formData.append('action', 'subirdocumentopagare');

		formData.append('id', compromisopago.id);
		console.log('ENTRA A VALIDACION CONTRATO M');

		if (compromisopago.tipo === 1) {
			console.log('ENTRA A CONTRATO M');
			let fileContratoM = pondContratoMaestria.getFiles();
			if (fileContratoM.length == 0) {
				addNotification({
					msg: 'Debe subir un archivo',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			if (fileContratoM.length > 1) {
				addNotification({
					msg: 'Archivo de documento debe ser único',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			let eFileContrato = undefined;
			if (pondContratoMaestria && pondContratoMaestria.getFiles().length > 0) {
				eFileContrato = pondContratoMaestria.getFiles()[0];
			}
			//console.log(eFileDocumento);
			formData.append('eFileContratoM', eFileContrato.file);
		}
		let fileTablaA = pondTablaAmortizacion.getFiles();
		if (fileTablaA.length == 0) {
			addNotification({
				msg: 'Debe subir un archivo',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		if (fileTablaA.length > 1) {
			addNotification({
				msg: 'Archivo de documento debe ser único',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		let eFiletablaM = undefined;
		if (pondTablaAmortizacion && pondTablaAmortizacion.getFiles().length > 0) {
			eFiletablaM = pondTablaAmortizacion.getFiles()[0];
		}
		//console.log(eFileDocumento);
		formData.append('eFileTablaAmortizacion', eFiletablaM.file);

		let filePagare = pondPagare.getFiles();
		if (filePagare.length == 0) {
			addNotification({
				msg: 'Debe subir un archivo',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		if (filePagare.length > 1) {
			addNotification({
				msg: 'Archivo de documento debe ser único',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		let eFilePagare = undefined;
		if (pondPagare && pondPagare.getFiles().length > 0) {
			eFilePagare = pondPagare.getFiles()[0];
		}
		//console.log(eFileDocumento);
		formData.append('eFilePagare', eFilePagare.file);

		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/finanzas', formData);

		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				if (!res.module_access) {
					goto('/');
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				dispatch('actionRun', { action: 'nextProccess', value: 1 });
				loading.setLoading(false, 'Cargando, espere por favor...');
				mOpenPagare = false;
			}
		}
		//addNotification({ msg: 'entro', type: 'error', target: 'newNotificationToast' });
	};

	const saveInfoComprobante = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmInfoComprobante = document.querySelector('#frmInfoComprobante');
		const formData = new FormData($frmInfoComprobante);

		formData.append('action', 'subircomprobantepago');

		formData.append('id', compromisopago.id);
		formData.append('id_matri', eMatricula.id);

		let fileDocumento = pondComprobante.getFiles();
		if (fileDocumento.length == 0) {
			addNotification({
				msg: 'Debe subir un archivo',
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
		if (pondComprobante && pondComprobante.getFiles().length > 0) {
			eFileDocumento = pondComprobante.getFiles()[0];
		}
		//console.log(eFileDocumento);
		formData.append('fileDocumentoComprobante', eFileDocumento.file);

		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/finanzas', formData);

		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				if (!res.module_access) {
					goto('/');
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				dispatch('actionRun', { action: 'nextProccess', value: 1 });
				loading.setLoading(false, 'Cargando, espere por favor...');
				mOpenDocumentosComprobante = false;
			}
		}
		//addNotification({ msg: 'entro', type: 'error', target: 'newNotificationToast' });
	};

	const saveInfoGarante = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmInfoGarante = document.querySelector('#frmInfoGarante');
		const formData = new FormData($frmInfoGarante);

		formData.append('action', 'guardardatosgarante');

		formData.append('id', compromisopago.id);
		formData.append('id_matri', eMatricula.id);

		if (!cedulagarante) {
			addNotification({
				msg: 'Favor complete el campo de cedula',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('cedulagarante', cedulagarante);
		}

		if (persona_juridica) {
			trabajador_relacion_dependencia = 0;
			formData.append(
				'trabajador_relacion_dependencia',
				trabajador_relacion_dependencia.toString()
			);
		} else {
			if (!trabajador_relacion_dependencia || trabajador_relacion_dependencia === 0) {
				addNotification({
					msg: 'Favor complete el campo trabajador relación dependencia',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			} else {
				formData.append(
					'trabajador_relacion_dependencia',
					trabajador_relacion_dependencia.toString()
				);
			}
		}

		formData.append('persona_juridica', persona_juridica);

		if (!nombresgarante) {
			addNotification({
				msg: 'Favor complete el campo de nombres',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('nombresgarante', nombresgarante);
		}
		if (!apellido1garante) {
			addNotification({
				msg: 'Favor complete el campo de apellido 1',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('apellido1garante', apellido1garante);
		}
		if (!apellido2garante) {
			addNotification({
				msg: 'Favor complete el campo de apellido 2',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('apellido2garante', apellido2garante);
		}
		if (!direciongarante) {
			addNotification({
				msg: 'Favor complete el campo de dirección',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('direciongarante', direciongarante);
		}

		if (!sexo_id_garante || sexo_id_garante === 0) {
			addNotification({
				msg: 'Favor complete el campo de genero',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('sexo_id_garante', sexo_id_garante);
		}

		if (!estado_civil_garante || estado_civil_garante === 0) {
			addNotification({
				msg: 'Favor complete el campo de genero',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('estado_civil_garante', estado_civil_garante);
		}

		let fileDocumentoGarante = pondDocumentoGarante.getFiles();
		if (fileDocumentoGarante.length == 0) {
			addNotification({
				msg: 'Debe subir un archivo',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		if (fileDocumentoGarante.length > 1) {
			addNotification({
				msg: 'Archivo de documento debe ser único',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		let eFileDocumentoGarante = undefined;
		if (pondDocumentoGarante && pondDocumentoGarante.getFiles().length > 0) {
			eFileDocumentoGarante = pondDocumentoGarante.getFiles()[0];
		}
		//console.log(eFileDocumento);
		formData.append('fileDocumentoGarante', eFileDocumentoGarante.file);

		let fileDocumentoVotacionGarante = pondDocumentoVotacionGarante.getFiles();
		if (fileDocumentoVotacionGarante.length == 0) {
			addNotification({
				msg: 'Debe subir un archivo',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		if (fileDocumentoVotacionGarante.length > 1) {
			addNotification({
				msg: 'Archivo de documento debe ser único',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		let eFileDocumentoVotacionGarante = undefined;
		if (pondDocumentoVotacionGarante && pondDocumentoVotacionGarante.getFiles().length > 0) {
			eFileDocumentoVotacionGarante = pondDocumentoVotacionGarante.getFiles()[0];
		}
		//console.log(eFileDocumento);
		formData.append('fileDocumentoVotacionGarante', eFileDocumentoVotacionGarante.file);

		if (persona_juridica) {
			let fileDocumentoCopiaConstitucion = pondCopiaConstitucionGarante.getFiles();
			if (fileDocumentoCopiaConstitucion.length == 0) {
				addNotification({
					msg: 'Debe subir un archivo ',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			if (fileDocumentoCopiaConstitucion.length > 1) {
				addNotification({
					msg: 'Archivo de documento debe ser único',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			let eFileDocumentoCopiaConstitucion = undefined;
			if (pondCopiaConstitucionGarante && pondCopiaConstitucionGarante.getFiles().length > 0) {
				eFileDocumentoCopiaConstitucion = pondCopiaConstitucionGarante.getFiles()[0];
			}
			//console.log(eFileDocumento);
			formData.append('fileDocumentoCopiaConstitucion', eFileDocumentoCopiaConstitucion.file);

			let fileCertificadoLegal = pondCertificacionLegal.getFiles();
			if (fileCertificadoLegal.length == 0) {
				addNotification({
					msg: 'Debe subir un arfileDocumentoCopiaConstitucionchivo ',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			if (fileCertificadoLegal.length > 1) {
				addNotification({
					msg: 'Archivo de documento debe ser único',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			let eFileCertificadoLegal = undefined;
			if (pondCertificacionLegal && pondCertificacionLegal.getFiles().length > 0) {
				eFileCertificadoLegal = pondCertificacionLegal.getFiles()[0];
			}
			//console.log(eFileDocumento);
			formData.append('fileCertificacionLegal', eFileCertificadoLegal.file);

			let fileDeclaracionImpuestoRenta = pondDeclaracionRenta.getFiles();
			if (fileDeclaracionImpuestoRenta.length == 0) {
				addNotification({
					msg: 'Debe subir un archivo ',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			if (fileDeclaracionImpuestoRenta.length > 1) {
				addNotification({
					msg: 'Archivo de documento debe ser único',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			let eFileDeclaracionRenta = undefined;
			if (pondDeclaracionRenta && pondDeclaracionRenta.getFiles().length > 0) {
				eFileDeclaracionRenta = pondDeclaracionRenta.getFiles()[0];
			}
			//console.log(eFileDocumento);
			formData.append('fileDeclaracionRenta', eFileDeclaracionRenta.file);

			let fileNombramientoRepresenta = pondNombramientoRepre.getFiles();
			if (fileNombramientoRepresenta.length == 0) {
				addNotification({
					msg: 'Debe subir un archivo ',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			if (fileNombramientoRepresenta.length > 1) {
				addNotification({
					msg: 'Archivo de documento debe ser único',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			let eFileNombramientoRepre = undefined;
			if (pondNombramientoRepre && pondNombramientoRepre.getFiles().length > 0) {
				eFileNombramientoRepre = pondNombramientoRepre.getFiles()[0];
			}
			//console.log(eFileDocumento);
			formData.append('fileNombramientoRepresentante', eFileNombramientoRepre.file);

			let fileActaJunta = pondActaJunta.getFiles();
			if (fileActaJunta.length == 0) {
				addNotification({
					msg: 'Debe subir un archivo ',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			if (fileActaJunta.length > 1) {
				addNotification({
					msg: 'Archivo de documento debe ser único',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			let eFileActaJunta = undefined;
			if (pondActaJunta && pondActaJunta.getFiles().length > 0) {
				eFileActaJunta = pondActaJunta.getFiles()[0];
			}
			//console.log(eFileDocumento);
			formData.append('fileActaJunta', eFileActaJunta.file);

			let fileRUC = pondRUC.getFiles();
			if (fileRUC.length == 0) {
				addNotification({
					msg: 'Debe subir un archivo ',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			if (fileRUC.length > 1) {
				addNotification({
					msg: 'Archivo de documento debe ser único',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			let eFileRUC = undefined;
			if (pondRUC && pondRUC.getFiles().length > 0) {
				eFileRUC = pondRUC.getFiles()[0];
			}
			//console.log(eFileDocumento);
			formData.append('fileRUC', eFileRUC.file);
		}

		if (!persona_juridica && trabajador_relacion_dependencia == 1) {
			let fileRolPago = pondRolPago.getFiles();
			if (fileRolPago.length == 0) {
				addNotification({
					msg: 'Debe subir un archivo ',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			if (fileRolPago.length > 1) {
				addNotification({
					msg: 'Archivo de documento debe ser único',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			let eFileRolPago = undefined;
			if (pondRolPago && pondRolPago.getFiles().length > 0) {
				eFileRolPago = pondRolPago.getFiles()[0];
			}
			//console.log(eFileDocumento);
			formData.append('fileRolPago', eFileRolPago.file);
		}

		if (!persona_juridica && trabajador_relacion_dependencia == 2) {
			let filePagoImpuestosPre = pondPagoImpuestosPre.getFiles();
			if (filePagoImpuestosPre.length == 0) {
				addNotification({
					msg: 'Debe subir un archivo ',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			if (filePagoImpuestosPre.length > 1) {
				addNotification({
					msg: 'Archivo de documento debe ser único',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			let eFileimpuestopre = undefined;
			if (pondPagoImpuestosPre && pondPagoImpuestosPre.getFiles().length > 0) {
				eFileimpuestopre = pondPagoImpuestosPre.getFiles()[0];
			}
			//console.log(eFileDocumento);
			formData.append('fileImpuestoPrediales', eFileimpuestopre.file);

			let fileFacturaServicioBasico = pondFacturaServicioBasico.getFiles();
			if (fileFacturaServicioBasico.length == 0) {
				addNotification({
					msg: 'Debe subir un archivo ',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			if (fileFacturaServicioBasico.length > 1) {
				addNotification({
					msg: 'Archivo de documento debe ser único',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			let eFileFacturaServicio = undefined;
			if (pondFacturaServicioBasico && pondFacturaServicioBasico.getFiles().length > 0) {
				eFileFacturaServicio = pondFacturaServicioBasico.getFiles()[0];
			}
			//console.log(eFileDocumento);
			formData.append('fileServicioBasico', eFileFacturaServicio.file);

			let fileRISEoRUC = pondRISEoRUC.getFiles();
			if (fileRISEoRUC.length == 0) {
				addNotification({
					msg: 'Debe subir un archivo ',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			if (fileRISEoRUC.length > 1) {
				addNotification({
					msg: 'Archivo de documento debe ser único',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			let eFileRICEoRUC = undefined;
			if (pondRISEoRUC && pondRISEoRUC.getFiles().length > 0) {
				eFileRICEoRUC = pondRISEoRUC.getFiles()[0];
			}
			//console.log(eFileDocumento);
			formData.append('fileRISEoRUC', eFileRICEoRUC.file);
		}

		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/finanzas', formData);

		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				if (!res.module_access) {
					goto('/');
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				dispatch('actionRun', { action: 'nextProccess', value: 1 });
				loading.setLoading(false, 'Cargando, espere por favor...');
				mOpenGarante = false;
			}
		}
		//addNotification({ msg: 'entro', type: 'error', target: 'newNotificationToast' });
	};

	const saveInfoConyugue = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmInfoConyugue = document.querySelector('#frmInfoConyugue');
		const formData = new FormData($frmInfoConyugue);

		formData.append('action', accion_conyugue);

		formData.append('id', compromisopago.id);
		formData.append('id_matri', eMatricula.id);
		console.log(cedulaconyugue);
		if (!cedulaconyugue) {
			addNotification({
				msg: 'Favor complete el campo de cedula',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('cedulaconyugue', cedulaconyugue);
		}
		if (!nombresconyugue) {
			addNotification({
				msg: 'Favor complete el campo de nombres',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('nombresconyugue', nombresconyugue);
		}
		if (!apellido1conyugue) {
			addNotification({
				msg: 'Favor complete el campo de apellido 1',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('apellido1conyugue', apellido1conyugue);
		}
		if (!apellido2conyugue) {
			addNotification({
				msg: 'Favor complete el campo de apellido 2',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('apellido2conyugue', apellido2conyugue);
		}
		if (!direcionconyugue) {
			addNotification({
				msg: 'Favor complete el campo de dirección',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('direcionconyugue', direcionconyugue);
		}

		if (!sexo_id_conyugue || sexo_id_conyugue === 0) {
			addNotification({
				msg: 'Favor complete el campo de genero',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('sexo_id_conyugue', sexo_id_conyugue);
		}

		if (!conyugue_estadocivil || conyugue_estadocivil === 0) {
			addNotification({
				msg: 'Favor complete el campo de genero',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('conyugue_estadocivil', conyugue_estadocivil);
		}

		let fileDocumentoConyugue = pondDocumentoConyugue.getFiles();
		if (fileDocumentoConyugue.length == 0) {
			addNotification({
				msg: 'Debe subir un archivo',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		if (fileDocumentoConyugue.length > 1) {
			addNotification({
				msg: 'Archivo de documento debe ser único',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		let eFileDocumentoConyugue = undefined;
		if (pondDocumentoConyugue && pondDocumentoConyugue.getFiles().length > 0) {
			eFileDocumentoConyugue = pondDocumentoConyugue.getFiles()[0];
		}
		//console.log(eFileDocumento);
		formData.append('fileDocumentoConyugue', eFileDocumentoConyugue.file);

		let fileDocumentoVotacionConyugue = pondDocumentoVotacionConyugue.getFiles();
		if (fileDocumentoVotacionConyugue.length == 0) {
			addNotification({
				msg: 'Debe subir un documento de votación',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		if (fileDocumentoVotacionConyugue.length > 1) {
			addNotification({
				msg: 'Archivo de documento debe ser único',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		let eFileDocumentoVotacionConyugue = undefined;
		if (pondDocumentoVotacionConyugue && pondDocumentoVotacionConyugue.getFiles().length > 0) {
			eFileDocumentoVotacionConyugue = pondDocumentoVotacionConyugue.getFiles()[0];
		}
		//console.log(eFileDocumento);
		formData.append('eFileDocumentoVotacionConyugue', eFileDocumentoVotacionConyugue.file);

		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/finanzas', formData);

		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				if (!res.module_access) {
					goto('/');
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			} else {
				action_init_load();
				addToast({
					type: 'success',
					header: 'Exitoso',
					body: 'Se guardo correctamente los datos del conyugue'
				});
				dispatch('actionRun', { action: 'nextProccess', value: 1 });
				loading.setLoading(false, 'Cargando, espere por favor...');
				mOpenConyuge = false;
			}
		}
		//addNotification({ msg: 'entro', type: 'error', target: 'newNotificationToast' });
	};

	const saveComprobante = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmInfoArchivo = document.querySelector('#frmInfoArchivo');
		const formData = new FormData($frmInfoArchivo);

		formData.append('action', 'addDocumentosPersonales');

		formData.append('id', compromisopago.id);
		formData.append('id_matri', eMatricula.id);

		let fileDocumento = pondDocumento.getFiles();
		if (fileDocumento.length == 0) {
			addNotification({
				msg: 'Debe subir un archivo',
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
		if (pondDocumento && pondDocumento.getFiles().length > 0) {
			eFileDocumento = pondDocumento.getFiles()[0];
		}
		//console.log(eFileDocumento);
		formData.append('fileDocumento', eFileDocumento.file);

		let fileDocumentoVotacion = pondDocumentoVotacion.getFiles();
		if (fileDocumentoVotacion.length == 0) {
			addNotification({
				msg: 'Debe subir un documento de votación',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		if (fileDocumentoVotacion.length > 1) {
			addNotification({
				msg: 'Archivo de documento debe ser único',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		let eFileDocumentoVotacion = undefined;
		if (pondDocumentoVotacion && pondDocumentoVotacion.getFiles().length > 0) {
			eFileDocumentoVotacion = pondDocumentoVotacion.getFiles()[0];
		}
		//console.log(eFileDocumento);
		formData.append('eFileDocumentoVotacion', eFileDocumentoVotacion.file);

		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/finanzas', formData);

		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				if (!res.module_access) {
					goto('/');
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				dispatch('actionRun', { action: 'nextProccess', value: 1 });
				loading.setLoading(false, 'Cargando, espere por favor...');
				mOpenDocumentosPersonales = false;
				action_init_load();
			}
		}
		//addNotification({ msg: 'entro', type: 'error', target: 'newNotificationToast' });
	};

	const payRubros = async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const url = `alumno/finanzas`;
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
			} else {
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
</script>

<svelte:head>
	<title>Mis Finanzas</title>
</svelte:head>

{#if !load}
	<BreadCrumb title="Mis Finanzas" items={itemsBreadCrumb} back={backBreadCrumb} />
	<div class="row">
		<div class="col-12">
			<div class="card mb-4">
				<!-- Card header -->
				<div class="card-header">
					<h3 class="mb-0">Listado de Rubros</h3>
					<!--<p class="mb-0">
					Order Dashboard is a quick overview of all current orders.
				</p>-->
				</div>
				<div class="card-header">
					<!-- DESCOMENTAR -->
					<div class="dropdown">
						<!-- {#if imprimircompromiso}
							{#if ePersona.estado_civil && ePersona.sexo && ePersona.datos_domicilio_completos}
								<button class="btn btn-secondary btn-sm dropdown-toggle" type="button" id="dropdownMenu2" data-bs-toggle="dropdown" aria-expanded="false">
									Legalizar Contrato Maestría 
								</button>
								<ul class="dropdown-menu" aria-labelledby="dropdownMenu2">
									
									<li><button class="dropdown-item" on:click|preventDefault={() => toggleModalDetalleOferta(compromisopago.id)} type="button"> Mostrar Documentos</button></li>
									{#if compromisopago.puede_subir_documentos_personales}
										<li><button class="dropdown-item" on:click|preventDefault={() => openDocumentosPersonales()} type="button"> Subir Cédula y Votación (Alumno)</button></li>
									{/if}
									{#if compromisopago.puede_subir_comprobante_pago}
										<li><button class="dropdown-item" on:click|preventDefault={() => openComprobantePago()} type="button"> Subir Comprobante de Pago</button></li>
									{/if}
									{#if ePersona.estado_civil == 2 && compromisopago.puede_agregar_conyuge }
										<li><button class="dropdown-item" on:click|preventDefault={() => openDatosConyugue()} type="button">Datos del Cónyuge (Alumno)</button></li>
									{/if}
									{#if compromisopago.puede_agregar_garante}
										<li><button class="dropdown-item" on:click|preventDefault={() => openGarante()} type="button"> Datos del Garante</button></li>

									{/if}
									{#if compromisopago.puede_agregar_conyuge_garante }
										<li><button class="dropdown-item" on:click|preventDefault={() => openDatosConyugueGarante()} type="button">Datos del Cónyuge (Garante)</button></li>
									{/if}
									<li><button class="dropdown-item" on:click|preventDefault={() => openPagare()} type="button"> Subir Tabla amortización{#if compromisopago.tipo == 1 }, Contrato{/if} y Pagaré</button></li>

								</ul>
								{#if compromisopago.estado.valor == 4 }
									<span class="badge bg-danger"
									>Novedades: {compromisopago.observacion}</span
									>								
								{/if}
							{:else}
								<div class="card-header">
									<div class="alert alert-danger d-flex align-items-center" role="alert">
										<svg
											xmlns="http://www.w3.org/2000/svg"
											width="24"
											height="24"
											fill="currentColor"
											class="bi bi-info-circle-fill me-2"
											viewBox="0 0 16 16"
										>
											<path
												d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"
											/>
										</svg>
										<div>
											{#if ePersona.sexo_id == 1 }Estimada{:else}Estimado{/if} por favor actualizar en el Módulo Hoja de Vida
												la siguiente información:
												{#if !ePersona.datos_domicilio_completos}
													<span class="label label-info">Datos del domicilio</span>
												{/if}
												{#if !ePersona.sexo }
													<span class="label label-info">Genero</span>
												{/if}
												{#if !ePersona.estado_civil }
													<span class="label label-info">Estado civil</span>
												{/if}
										</div>
									</div>
								</div>
							{/if}
						{/if} -->

						{#if tipoperiodo == 3 || tipoperiodo == 4}
							<a
								href=""
								on:click|preventDefault={() => goto('/alu_finanzas/listacomprobantes')}
								class="btn btn-success btn-sm"
								target="_blank"
							>
								<i class="bi bi-journal-medical" />
								Listado de Comprobantes
							</a>
						{/if}
						{#if clasificacion == 1 || clasificacion == 3}
							{#if eMatricula.inscripcion.coordinacion <= 5 || eMatricula.inscripcion.coordinacion == 9}
								<a
									href={canlespago}
									style="background-color: #2d8cff!important;"
									class="btn btn-secondary btn-sm"
									target="_blank"
								>
									<i class="bi bi-cash-coin" /> Nuestros canales de pago
								</a>
								<button
									on:click|preventDefault={() => goto('/alu_finanzas/comprobantespagos')}
									class="btn btn-warning btn-sm"
								>
									<i class="bi bi-journal-check" /> Registro de comprobantes
								</button>
							{/if}
						{/if}
						{#if eMatricula.inscripcion.coordinacion == 7}
							<a class="btn btn-warning btn-sm" on:click={() => payRubros()}>
								<i class="bi bi-currency-exchange" /> Pagar con tarjeta</a
							>
						{/if}
					</div>

					{#if eMatricula && ePeriodoMatricula}
						{#if eMatricula.puede_diferir_rubro_arancel && eMatricula.rubro_arancel.valorarancel > 0 && ePeriodoMatricula.valida_cuotas_rubro && ePeriodoMatricula.num_cuotas_rubro > 1 && eMatricula.rubro_arancel.valorarancel > ePeriodoMatricula.monto_rubro_cuotas}
							<button
								id={`Tooltip_matricula_arancel_${eMatricula.id}`}
								class="btn btn-secondary btn-sm"
								on:click|preventDefault={() => action_to_differ()}
								>Diferir {eMatricula.rubro_arancel.descripcion} ${eMatricula.rubro_arancel
									.valorarancel}</button
							>
							<Tooltip target={`Tooltip_matricula_arancel_${eMatricula.id}`} placement="top"
								>Matrícula del Periodo {eMatricula.nivel.periodo.nombre}</Tooltip
							>
						{/if}
					{/if}
					{#if eMatricula && ePeriodoMatricula}
						{#if ePeriodoMatricula.valida_rubro_acta_compromiso && eMatricula.aranceldiferido === 1 && eMatricula.actacompromiso}
							<a class="btn btn-link btn-sm" href={eMatricula.actacompromiso} target="_blank"
								>Descargar acta de compromiso</a
							>
						{/if}
					{/if}
				</div>
				<!-- Card body -->
				<div class="card-body">
					<!--<div class="alert bg-light-warning text-dark-warning alert-dismissible fade show" role="alert">
					<strong>payout@geeks.com</strong>
					<p class="mb-0">
						Your selected payout method was confirmed on Next Payout on
						15 July, 2020
					</p>
					<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close">

					</button>
				</div>-->
					<div class="row">
						<div class="col-xl-3 col-lg-6 col-md-12 col-12" />
						<!-- col -->
						<div class="col-xl-3 col-lg-6 col-md-12 col-12">
							<!-- Card -->
							<div class="card mb-4">
								<!-- Card Body -->

								<div class="card-body">
									<span class="fs-6 text-uppercase fw-semi-bold">Total de Rubros</span>
									<div class="mt-2 d-flex justify-content-between align-items-center">
										<div class="lh-1">
											<h2 class="h1 fw-bold mb-1">${converToDecimal(ePersona.total_rubros)}</h2>
										</div>
										<div>
											<div class="icon-shape icon-lg bg-light-primary text-primary rounded-circle">
												<i class="fe fe-dollar-sign fs-3" />
											</div>
										</div>
									</div>
								</div>
							</div>
						</div>
						<div class="col-xl-3 col-lg-6 col-md-12 col-12">
							<!-- Card -->
							<div class="card mb-4">
								<!-- Card Body -->
								<div class="card-body">
									<span class="fs-6 text-uppercase fw-semi-bold">Total Pagado</span>
									<div class="mt-2 d-flex justify-content-between align-items-center">
										<div class="lh-1">
											<h2 class="h1 fw-bold mb-1">${converToDecimal(ePersona.total_pagado)}</h2>
										</div>
										<div>
											<div class="icon-shape icon-lg bg-light-primary text-primary rounded-circle">
												<i class="fe fe-dollar-sign fs-3" />
											</div>
										</div>
									</div>
								</div>
							</div>
						</div>
						<div class="col-xl-3 col-lg-6 col-md-12 col-12">
							<!-- Card -->
							<div class="card mb-4">
								<!-- Card Body -->
								<div class="card-body">
									<span class="fs-6 text-uppercase fw-semi-bold">Total Por Pagar</span>
									<div class="mt-2 d-flex justify-content-between align-items-center">
										<div class="lh-1">
											<h2 class="h1 fw-bold mb-1">${converToDecimal(ePersona.total_adeudado)}</h2>
										</div>
										<div>
											<div class="icon-shape icon-lg bg-light-primary text-primary rounded-circle">
												<i class="fe fe-dollar-sign fs-3" />
											</div>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
					<div class="table-responsive">
						<!--border-0 table-invoice-->
						<table class="table mb-0 text-nowrap table-hover table-bordered align-middle">
							<thead class="table-light">
								<tr>
									<th scope="col" class="border-top-0 text-center" style="text-align: center;"
										>RUBRO</th
									>
									<th scope="col" class="border-top-0 text-center" style="text-align: center;"
										>CÓDIGO INTERMÁTICO</th
									>
									<th scope="col" class="border-top-0 text-center" style="text-align: center;"
										>FECHA MÁXIMA DE PAGO</th
									>
									<th scope="col" class="border-top-0 text-center" style="text-align: center;"
										>VALOR</th
									>
									<th scope="col" class="border-top-0 text-center" style="text-align: center;"
										>PAGADO</th
									>
									<th scope="col" class="border-top-0 text-center" style="text-align: center;"
										>POR PAGAR</th
									>
									<th scope="col" class="border-top-0 text-center" style="text-align: center;"
										>CANCELADO</th
									>
									<th scope="col" class="border-top-0 text-center" style="text-align: center;"
										>FACTURA</th
									>
								</tr>
							</thead>
							<tbody>
								{#if eRubros.length > 0}
									{#each eRubros as eRubro}
										<tr>
											<td class="text-wrap fs-6">
												({eRubro.idm}) - {eRubro.nombre}
												{#if eRubro.matricula}
													{#if eRubro.matricula.gratuidad == 2}
														<p class="text-wrap p-0 m-0">
															Con base al Art.5 del Reglamento para garantizar el cumplimiento de la
															gratuidad emitido por el Concejo de Educaci&oacute;n Superior (CES) y
															en relaci&oacute;n a los Arts. 6, 7 y 12 del Reglamento interno para
															garantizar el ejercicio del derecho a la gratuidad en la Universidad
															Estatal de Milagro. Su estado es P&Eacute;RDIDA PARCIAL DE LA
															GRATUIDAD y tendr&aacute; que cancelar el valor correspondiente entre
															matr&iacute;cula y arancel.
														</p>
													{/if}
													{#if eRubro.matricula.gratuidad == 3}
														{#if eRubro.matricula.inscripcion.persona.tiene_otro_titulo}
															<p class="text-wrap p-0 m-0">
																De acuerdo al contenido de la Matriz de Tercer Nivel remitida por la
																Secretaría de Educación, Ciencia, Tecnología e Innovación SENESCYT a
																nuestra IES, en concordancia con lo estipulado en el artículo 63 del
																Reglamento del SNNA y en la Disposición General Séptima del
																Reglamento de Régimen Académico, se informa que usted, actualmente,
																se encuentra SIN GRATUIDAD en la educación superior pública; motivo
																por el cual deberá cancelar los valores correspondientes, durante el
																desarrollo de su carrera universitaria.
															</p>
															<p class="text-wrap p-0 m-0">
																Estimado/a estudiante registra título en otra IES Pública. Su estado
																es de pérdida total de la gratuidad. Debe cancelar por todas las
																asignaturas.
															</p>
														{:else if eRubro.matricula.inscripcion.perdida_gratuidad_senescyt}
															<p class="text-wrap p-0 m-0">
																De acuerdo al contenido de la Matriz de Tercer Nivel remitida por la
																Secretaría de Educación, Ciencia, Tecnología e Innovación SENESCYT a
																nuestra IES, en concordancia con lo estipulado en el artículo 63 del
																Reglamento del SNNA y en la Disposición General Séptima del
																Reglamento de Régimen Académico, se informa que usted, actualmente,
																se encuentra SIN GRATUIDAD en la educación superior pública; motivo
																por el cual deberá cancelar los valores correspondientes, durante el
																desarrollo de su carrera universitaria.
															</p>
															<p class="text-wrap p-0 m-0">
																Estimado/a estudiante registra perdida de gratuidad reportado por la
																SENESCYT. Su estado es de pérdida total de la gratuidad. Debe
																cancelar por todas las asignaturas.
															</p>
														{:else}
															<p class="text-wrap p-0 m-0">
																Con base al Art.11 del Reglamento para garantizar el cumplimiento de
																la gratuidad emitido por el Concejo de Educaci&oacute;n Superior
																(CES) y en relaci&oacute;n al Art.11 del Reglamento interno para
																garantizar el ejercicio del derecho a la gratuidad en la Universidad
																Estatal de Milagro. Usted supera el 30% de las asignaturas
																reprobadas correspondientes al plan de estudios como indica la Ley.
																Su estado es P&Eacute;RDIDA DEFINITIVA DE LA GRATUIDAD. A partir de
																este momento todas las asignaturas, cursos o sus equivalentes hasta
																la culminaci&oacute;n de su carrera, cancelar&aacute; los valores
																respectivos a matr&iacute;culas y aranceles.
															</p>
														{/if}
													{/if}
												{/if}
												<div>
													{#if eRubro.idrubroepunemi}
														<span class="badge bg-warning">{eRubro.idrubroepunemi}</span>
													{/if}
													{#if eRubro.esta_anulado}
														<span class="badge bg-danger">ANULADO</span>
													{/if}
													{#if eRubro.cancelado}
														{#if eRubro.rubro_devolucion}
															<span class="badge bg-danger"
																>El estudiante deberá acercarse al Departamento de Auditotía Interna
																de la Institución</span
															>
														{/if}
													{/if}
													{#if eRubro.epunemi}
														<span class="badge bg-warning">EPUNEMI</span>
													{:else}
														<span class="badge bg-success">UNEMI</span>
													{/if}
												</div>
											</td>
											<td class="fs-6" style="text-align: center;">
												{#if !eRubro.epunemi}
													<span class="badge bg-success">{eRubro.codigo_intermatico}</span>
												{/if}
											</td>
											<td class="fs-6" style="text-align: center;">
												{#if eRubro.no_salga}
													{eRubro.fechavence}
													{#if eRubro.vencido}
														<br /><span class="badge bg-danger">VENCIDA</span>
													{/if}
												{/if}
											</td>
											<td class="fs-6" style="text-align: right;">
												$ {converToDecimal(eRubro.valor)}
											</td>
											<td class="fs-6" style="text-align: right;">
												$ {converToDecimal(eRubro.total_pagado)}
											</td>
											<td class="fs-6" style="text-align: right;">
												{#if eRubro.saldo}
													{#if eRubro.vencido}
														<span class="badge bg-danger">$ {converToDecimal(eRubro.saldo)}</span>
													{:else}
														<span class="badge bg-success">$ {converToDecimal(eRubro.saldo)}</span>
													{/if}
												{:else}
													$ {converToDecimal(eRubro.saldo)}
												{/if}
											</td>
											<td class="fs-6" style="text-align: center;">
												{#if !eRubro.esta_liquidado}
													{#if eRubro.cancelado}
														<span class="badge bg-success">SI</span>
													{:else}
														<span class="badge bg-danger">NO</span>
													{/if}
												{:else}
													<span class="badge bg-danger">LIQUIDADO</span>
												{/if}
											</td>
											<td class="fs-6" style="text-align: center;">
												{#if eRubro.tiene_factura}
													<button
														on:click|preventDefault={() => action_to_show_rubro(eRubro.id)}
														class="btn btn-success p-1 fs-6"
													>
														<i class="fe fe-file" /> Ver Factura</button
													>
												{/if}
											</td>
										</tr>
									{/each}
								{:else}
									<tr>
										<td colspan="8" class="text-center">NO EXISTEN RUBROS DISPONIBLES</td>
									</tr>
								{/if}
							</tbody>
							<!--{#if eFinanzas && totales}
							<tfoot>
								<tr>
									<td colspan="2"><b>Totales</b></td>
									<td />
									<td style="text-align: right;"
										><b>$ {converToDecimal(totales.total_rubros)}</b></td
									>
									<td style="text-align: right;"
										><b>$ {converToDecimal(totales.total_pagado)}</b></td
									>
									<td style="text-align: right;"
										><b>$ {converToDecimal(totales.total_adeudado)}</b></td
									>
									<td style="text-align: right;" colspan="3"><b /></td>
								</tr>
							</tfoot>
						{/if}-->
						</table>
					</div>
				</div>
			</div>
		</div>
	</div>
{:else}
	<div
		class="mt-4 vh-100 row justify-content-center align-items-center"
		style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 1000; display: flex; flex-direction: column; align-items: center; justify-content: center;"
	>
		<div class="col-auto text-center">
			<Spinner color="primary" type="border" style="width: 3rem; height: 3rem;" />
			<h3>Verificando la información, espere por favor...</h3>
		</div>
	</div>
{/if}

<Modal
	isOpen={mOpenDocumentosPersonales}
	toggle={mToggleDocumentosPersonales}
	size={mSizeDocumentosPersonales}
	class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
	backdrop="static"
	fade={false}
>
	<ModalHeader toggle={mToggleDocumentosPersonales}>
		<h4>Subir documentos personales</h4>
	</ModalHeader>
	<ModalBody>
		<form id="frmInfoArchivo" on:submit|preventDefault={saveInfoArchivo}>
			<div class="card-body">
				<div class="row g-3">
					<div class="col-md-12">
						<label for="ePersonaFileDocumento" class="form-label fw-bold"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> Cédula de ciudadanía:</label
						>
						<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
						<FilePond
							class="pb-0 mb-0"
							id="ePersonaFileDocumento"
							bind:this={pondDocumento}
							{nameDocumento}
							name="fileDocumento"
							labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
							allowMultiple={true}
							oninit={handleInit}
							onaddfile={handleAddFile}
							credits=""
							acceptedFileTypes={['application/pdf']}
							labelInvalidField="El campo contiene archivos no válidos"
							maxFiles="1"
							maxParallelUploads="1"
						/>
						<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
					</div>
					<div class="col-md-12">
						<label for="ePersonaFileDocumento" class="form-label fw-bold"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> Papeleta de Votación:</label
						>
						<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
						<FilePond
							class="pb-0 mb-0"
							id="ePersonaFileDocumento"
							bind:this={pondDocumentoVotacion}
							{nameVotacion}
							name="fileDocumentoVotacion"
							labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
							allowMultiple={true}
							oninit={handleAddFileVotacion}
							onaddfile={handleAddFile}
							credits=""
							acceptedFileTypes={['application/pdf']}
							labelInvalidField="El campo contiene archivos no válidos"
							maxFiles="1"
							maxParallelUploads="1"
						/>
						<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
					</div>
				</div>
				<div class="card-footer text-muted">
					<div class="d-grid gap-2 d-md-flex justify-content-md-end">
						<!--<button class="btn btn-primary me-md-2" type="button">Button</button>-->
						<button type="submit" class="btn btn-info">Guardar</button>
						<a color="danger" class="btn btn-danger" on:click={() => closeDocumentosPersonales()}
							>Cerrar</a
						>
					</div>
				</div>
			</div>
		</form>
	</ModalBody>
</Modal>

<Modal
	isOpen={mOpenDocumentosComprobante}
	toggle={mToggleDocumentosComprobante}
	size={mSizeDocumentosComprobante}
	class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
	backdrop="static"
	fade={false}
>
	<ModalHeader toggle={mToggleDocumentosComprobante}>
		<h4>Subir Comprobante de Pago</h4>
	</ModalHeader>
	<ModalBody>
		<form id="frmInfoComprobante" on:submit|preventDefault={saveInfoComprobante}>
			<div class="card-body">
				<div class="row g-3">
					<div class="col-md-12">
						<label for="ePersonaFileDocumento" class="form-label fw-bold"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> Comprobante de pago:</label
						>
						<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
						<FilePond
							class="pb-0 mb-0"
							id="ePersonaFileDocumento"
							bind:this={pondComprobante}
							{nameComrpobante}
							name="fileDocumento"
							labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
							allowMultiple={true}
							oninit={handleInit}
							onaddfile={handleAddFileComprobante}
							credits=""
							acceptedFileTypes={['application/pdf']}
							labelInvalidField="El campo contiene archivos no válidos"
							maxFiles="1"
							maxParallelUploads="1"
						/>
						<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
					</div>
				</div>
				<div class="card-footer text-muted">
					<div class="d-grid gap-2 d-md-flex justify-content-md-end">
						<!--<button class="btn btn-primary me-md-2" type="button">Button</button>-->
						<button type="submit" class="btn btn-info">Guardar</button>
						<a color="danger" class="btn btn-danger" on:click={() => closeComprobante()}>Cerrar</a>
					</div>
				</div>
			</div>
		</form>
	</ModalBody>
</Modal>

<Modal
	isOpen={mOpenGarante}
	toggle={mToggleGarante}
	size={mSizeGarante}
	class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
	backdrop="static"
	fade={false}
>
	<ModalHeader toggle={mToggleGarante}>
		<h4>Datos del Garante</h4>
	</ModalHeader>
	<ModalBody>
		<form id="frmInfoGarante" on:submit|preventDefault={saveInfoGarante}>
			<div class="card-body">
				<div class="row g-3">
					<div class="col-md-4">
						<label for="eConyugueCedula" class="form-label fw-bold"> Cédula: </label>
						<input
							type="text"
							class="form-control"
							id="eConyugueCedula"
							bind:value={cedulagarante}
						/>
					</div>
					<div class="col-md-4">
						<label for="eConyugueCedula" class="form-label fw-bold"> Persona jurídica: </label>
						<div class="form-check form-switch ">
							<input
								class="form-control form-check-input"
								type="checkbox"
								id="ePersonaDiscapacidad"
								bind:checked={persona_juridica}
							/>
							<label class="form-check-label fs-bold" for="ePersonaDiscapacidad"
								>¿Es persona jurídica?</label
							>
						</div>
					</div>
					{#if !persona_juridica}
						<div class="col-md-4">
							<label for="ePersonaSexo" class="form-label fw-bold"
								><span class="fs-bold text-danger">(*)</span> Trabajador Relación Dependencia:</label
							>
							<select
								class="form-control form-select"
								id="ePersonaSexo"
								bind:value={trabajador_relacion_dependencia}
							>
								{#each [{ value: 0, text: 'NINGUNO' }, { value: 1, text: 'SI' }, { value: 2, text: 'NO' }] as traba}
									<option value={traba.value}>
										{traba.text}
									</option>
								{/each}
							</select>
						</div>
					{/if}
					<div class="col-md-12">
						<label for="eConyugueNombres" class="form-label fw-bold"> Nombres: </label>
						<input
							type="text"
							class="form-control"
							id="eConyugueNombres"
							bind:value={nombresgarante}
						/>
					</div>
					<div class="col-md-6">
						<label for="eConyugueNombres" class="form-label fw-bold"> 1er Apellido: </label>
						<input
							type="text"
							class="form-control"
							id="eConyugueNombres"
							bind:value={apellido1garante}
						/>
					</div>
					<div class="col-md-6">
						<label for="eConyugueNombres" class="form-label fw-bold"> 2do Apellido: </label>
						<input
							type="text"
							class="form-control"
							id="eConyugueNombres"
							bind:value={apellido2garante}
						/>
					</div>
					<div class="col-md-6">
						<label for="ePersonaSexo" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Sexo:</label
						>
						<select class="form-control form-select" id="ePersonaSexo" bind:value={sexo_id_garante}>
							{#each [{ value: 0, text: 'NINGUNO' }, { value: 1, text: 'MUJER' }, { value: 2, text: 'HOMBRE' }] as sexo}
								<option value={sexo.value}>
									{sexo.text}
								</option>
							{/each}
						</select>
					</div>
					<div class="col-md-6">
						<label for="ePersonaSexo" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Estado civil:</label
						>
						<select
							class="form-control form-select"
							id="eCuentaBanco"
							bind:value={estado_civil_garante}
						>
							{#each estado_civil as civil}
								<option value={civil.idm}>
									{civil.nombre}
								</option>
							{/each}
						</select>
					</div>
					<div class="col-md-12">
						<label for="eConyugueNombres" class="form-label fw-bold"> Dirección Domicilio: </label>
						<input
							type="text"
							class="form-control"
							id="eConyugueDireccion"
							bind:value={direciongarante}
						/>
					</div>
					<div class="col-md-6">
						<label for="fileDocumentoVotacion" class="form-label fw-bold"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> Cédula de ciudadanía:</label
						>
						<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
						<FilePond
							class="pb-0 mb-0"
							id="eConyugueFileDocumento"
							bind:this={pondDocumentoGarante}
							{nameDocumentoGarante}
							name="fileDocumentoVotacion"
							labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
							allowMultiple={true}
							oninit={handleInit}
							onaddfile={handleAddFileGarante}
							credits=""
							acceptedFileTypes={['application/pdf']}
							labelInvalidField="El campo contiene archivos no válidos"
							maxFiles="1"
							maxParallelUploads="1"
						/>
						<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
					</div>
					<div class="col-md-6">
						<label for="ConyugueFileDocumentoVotacion" class="form-label fw-bold"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> Papeleta de Votación:</label
						>
						<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
						<FilePond
							class="pb-0 mb-0"
							id="ConyugueFileDocumentoVotacion"
							bind:this={pondDocumentoVotacionGarante}
							{nameVotacionGarante}
							name="fileDocumentoVotacion"
							labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
							allowMultiple={true}
							oninit={handleInit}
							onaddfile={handleAddFileVotacionGarante}
							credits=""
							acceptedFileTypes={['application/pdf']}
							labelInvalidField="El campo contiene archivos no válidos"
							maxFiles="1"
							maxParallelUploads="1"
						/>
						<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
					</div>

					{#if persona_juridica}
						<div class="col-md-4">
							<label for="ConyugueFileDocumentoVotacion" class="form-label fw-bold"
								><i
									title="Campo obligatorio"
									class="bi bi-exclamation-circle-fill"
									style="color: red"
								/> Copia Constitución y estatutos:</label
							>
							<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
							<FilePond
								class="pb-0 mb-0"
								id="ConyugueFileDocumentoVotacion"
								bind:this={pondCopiaConstitucionGarante}
								{nameCopiaConstitucionGarante}
								name="fileDocumentoVotacion"
								labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
								allowMultiple={true}
								oninit={handleInit}
								onaddfile={handleAddFileCopiaConstitucion}
								credits=""
								acceptedFileTypes={['application/pdf']}
								labelInvalidField="El campo contiene archivos no válidos"
								maxFiles="1"
								maxParallelUploads="1"
							/>
							<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
						</div>
						<div class="col-md-4">
							<label for="ConyugueFileDocumentoVotacion" class="form-label fw-bold"
								><i
									title="Campo obligatorio"
									class="bi bi-exclamation-circle-fill"
									style="color: red"
								/> Certificado Existencia legal:</label
							>
							<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
							<FilePond
								class="pb-0 mb-0"
								id="ConyugueFileDocumentoVotacion"
								bind:this={pondCertificacionLegal}
								{nameCertificacionLegal}
								name="fileDocumentoVotacion"
								labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
								allowMultiple={true}
								oninit={handleInit}
								onaddfile={handleAddFileCertificadoExistencia}
								credits=""
								acceptedFileTypes={['application/pdf']}
								labelInvalidField="El campo contiene archivos no válidos"
								maxFiles="1"
								maxParallelUploads="1"
							/>
							<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
						</div>
						<div class="col-md-4">
							<label for="ConyugueFileDocumentoVotacion" class="form-label fw-bold"
								><i
									title="Campo obligatorio"
									class="bi bi-exclamation-circle-fill"
									style="color: red"
								/>
								Declaración impuesto renta:</label
							>
							<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
							<FilePond
								class="pb-0 mb-0"
								id="ConyugueFileDocumentoVotacion"
								bind:this={pondDeclaracionRenta}
								{nameDeclaracionRenta}
								name="fileDocumentoVotacion"
								labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
								allowMultiple={true}
								oninit={handleInit}
								onaddfile={handleAddFileDeclaracionRenta}
								credits=""
								acceptedFileTypes={['application/pdf']}
								labelInvalidField="El campo contiene archivos no válidos"
								maxFiles="1"
								maxParallelUploads="1"
							/>
							<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
						</div>
						<div class="col-md-4">
							<label for="ConyugueFileDocumentoVotacion" class="form-label fw-bold"
								><i
									title="Campo obligatorio"
									class="bi bi-exclamation-circle-fill"
									style="color: red"
								/>
								Nombramiento representante:</label
							>
							<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
							<FilePond
								class="pb-0 mb-0"
								id="ConyugueFileDocumentoVotacion"
								bind:this={pondNombramientoRepre}
								{nameNombramientoRepre}
								name="fileDocumentoVotacion"
								labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
								allowMultiple={true}
								oninit={handleInit}
								onaddfile={handleAddFileNombramientoRepresentante}
								credits=""
								acceptedFileTypes={['application/pdf']}
								labelInvalidField="El campo contiene archivos no válidos"
								maxFiles="1"
								maxParallelUploads="1"
							/>
							<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
						</div>

						<div class="col-md-4">
							<label for="ConyugueFileDocumentoVotacion" class="form-label fw-bold"
								><i
									title="Campo obligatorio"
									class="bi bi-exclamation-circle-fill"
									style="color: red"
								/>
								Acta junta accionistas:</label
							>
							<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
							<FilePond
								class="pb-0 mb-0"
								id="ConyugueFileDocumentoVotacion"
								bind:this={pondActaJunta}
								{nameActaJunta}
								name="fileDocumentoVotacion"
								labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
								allowMultiple={true}
								oninit={handleInit}
								onaddfile={handleAddFileActaJuntaAcciones}
								credits=""
								acceptedFileTypes={['application/pdf']}
								labelInvalidField="El campo contiene archivos no válidos"
								maxFiles="1"
								maxParallelUploads="1"
							/>
							<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
						</div>

						<div class="col-md-4">
							<label for="ConyugueFileDocumentoVotacion" class="form-label fw-bold"
								><i
									title="Campo obligatorio"
									class="bi bi-exclamation-circle-fill"
									style="color: red"
								/>
								RUC:</label
							>
							<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
							<FilePond
								class="pb-0 mb-0"
								id="ConyugueFileDocumentoVotacion"
								bind:this={pondRUC}
								{nameRUC}
								name="fileDocumentoVotacion"
								labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
								allowMultiple={true}
								oninit={handleInit}
								onaddfile={handleAddFileRUC}
								credits=""
								acceptedFileTypes={['application/pdf']}
								labelInvalidField="El campo contiene archivos no válidos"
								maxFiles="1"
								maxParallelUploads="1"
							/>
							<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
						</div>
					{/if}
					{#if !persona_juridica}
						{#if trabajador_relacion_dependencia == 1}
							<div class="col-md-4">
								<label for="ConyugueFileDocumentoVotacion" class="form-label fw-bold"
									><i
										title="Campo obligatorio"
										class="bi bi-exclamation-circle-fill"
										style="color: red"
									/>
									Rol de Pago:</label
								>
								<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
								<FilePond
									class="pb-0 mb-0"
									id="ConyugueFileDocumentoVotacion"
									bind:this={pondRolPago}
									{nameRolPago}
									name="fileDocumentoVotacion"
									labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
									allowMultiple={true}
									oninit={handleInit}
									onaddfile={handleAddFileRolPago}
									credits=""
									acceptedFileTypes={['application/pdf']}
									labelInvalidField="El campo contiene archivos no válidos"
									maxFiles="1"
									maxParallelUploads="1"
								/>
								<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
							</div>
						{:else if trabajador_relacion_dependencia == 2}
							<div class="col-md-4">
								<label for="ConyugueFileDocumentoVotacion" class="form-label fw-bold"
									><i
										title="Campo obligatorio"
										class="bi bi-exclamation-circle-fill"
										style="color: red"
									/>
									Pago Impuesto Prediales:</label
								>
								<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
								<FilePond
									class="pb-0 mb-0"
									id="ConyugueFileDocumentoVotacion"
									bind:this={pondPagoImpuestosPre}
									{namePagoImpuestosPre}
									name="fileDocumentoVotacion"
									labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
									allowMultiple={true}
									oninit={handleInit}
									onaddfile={handleAddFilePagoImpuestoPrediales}
									credits=""
									acceptedFileTypes={['application/pdf']}
									labelInvalidField="El campo contiene archivos no válidos"
									maxFiles="1"
									maxParallelUploads="1"
								/>
								<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
							</div>
							<div class="col-md-4">
								<label for="ConyugueFileDocumentoVotacion" class="form-label fw-bold"
									><i
										title="Campo obligatorio"
										class="bi bi-exclamation-circle-fill"
										style="color: red"
									/>
									Factura Servicio básico:</label
								>
								<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
								<FilePond
									class="pb-0 mb-0"
									id="ConyugueFileDocumentoVotacion"
									bind:this={pondFacturaServicioBasico}
									{nameFacturaServicioBasico}
									name="fileDocumentoVotacion"
									labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
									allowMultiple={true}
									oninit={handleInit}
									onaddfile={handleAddFileFacturaServicioBasico}
									credits=""
									acceptedFileTypes={['application/pdf']}
									labelInvalidField="El campo contiene archivos no válidos"
									maxFiles="1"
									maxParallelUploads="1"
								/>
								<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
							</div>
							<div class="col-md-4">
								<label for="ConyugueFileDocumentoVotacion" class="form-label fw-bold"
									><i
										title="Campo obligatorio"
										class="bi bi-exclamation-circle-fill"
										style="color: red"
									/>

									RISE o RUC:</label
								>
								<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
								<FilePond
									class="pb-0 mb-0"
									id="ConyugueFileDocumentoVotacion"
									bind:this={pondRISEoRUC}
									{nameRISEoRUC}
									name="fileDocumentoVotacion"
									labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
									allowMultiple={true}
									oninit={handleInit}
									onaddfile={handleAddFileRISEoRUC}
									credits=""
									acceptedFileTypes={['application/pdf']}
									labelInvalidField="El campo contiene archivos no válidos"
									maxFiles="1"
									maxParallelUploads="1"
								/>
								<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
							</div>
						{/if}
					{/if}
				</div>
			</div>

			<div class="card-footer text-muted">
				<div class="d-grid gap-2 d-md-flex justify-content-md-end">
					<!--<button class="btn btn-primary me-md-2" type="button">Button</button>-->
					<button type="submit" class="btn btn-info">Guardar</button>
					<a color="danger" class="btn btn-danger" on:click={() => closeGarante()}>Cerrar</a>
				</div>
			</div>
		</form>
	</ModalBody>
</Modal>

<Modal
	isOpen={mOpenConyuge}
	toggle={mToggleConyuge}
	size={mSizeConyuge}
	class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
	backdrop="static"
	fade={false}
>
	<ModalHeader toggle={mToggleConyuge}>
		<h4>{modalTitle}</h4>
	</ModalHeader>
	<ModalBody>
		<form id="frmInfoConyugue" on:submit|preventDefault={saveInfoConyugue}>
			<div class="card-body">
				<div class="row g-3">
					<div class="col-md-6">
						<label for="eConyugueCedula" class="form-label fw-bold"> Cédula: </label>
						<input
							type="text"
							class="form-control"
							id="eConyugueCedula"
							bind:value={cedulaconyugue}
						/>
					</div>
					<div class="col-md-12">
						<label for="eConyugueNombres" class="form-label fw-bold"> Nombres: </label>
						<input
							type="text"
							class="form-control"
							id="eConyugueNombres"
							bind:value={nombresconyugue}
						/>
					</div>
					<div class="col-md-6">
						<label for="eConyugueNombres" class="form-label fw-bold"> 1er Apellido: </label>
						<input
							type="text"
							class="form-control"
							id="eConyugueNombres"
							bind:value={apellido1conyugue}
						/>
					</div>
					<div class="col-md-6">
						<label for="eConyugueNombres" class="form-label fw-bold"> 2do Apellido: </label>
						<input
							type="text"
							class="form-control"
							id="eConyugueNombres"
							bind:value={apellido2conyugue}
						/>
					</div>
					<div class="col-md-6">
						<label for="ePersonaSexo" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Sexo:</label
						>
						<select
							class="form-control form-select"
							id="ePersonaSexo"
							bind:value={sexo_id_conyugue}
						>
							{#each [{ value: 0, text: 'NINGUNO' }, { value: 1, text: 'MUJER' }, { value: 2, text: 'HOMBRE' }] as sexo}
								<option value={sexo.value}>
									{sexo.text}
								</option>
							{/each}
						</select>
					</div>
					<div class="col-md-6">
						<label for="ePersonaSexo" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Estado civil:</label
						>
						<select
							class="form-control form-select"
							id="eCuentaBanco"
							bind:value={conyugue_estadocivil}
						>
							{#each estado_civil as civil}
								<option value={civil.idm}>
									{civil.nombre}
								</option>
							{/each}
						</select>
					</div>
					<div class="col-md-12">
						<label for="eConyugueNombres" class="form-label fw-bold"> Dirección Domicilio: </label>
						<input
							type="text"
							class="form-control"
							id="eConyugueDireccion"
							bind:value={direcionconyugue}
						/>
					</div>
					<div class="col-md-6">
						<label for="fileDocumentoVotacion" class="form-label fw-bold"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> Cédula de ciudadanía:</label
						>
						<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
						<FilePond
							class="pb-0 mb-0"
							id="eConyugueFileDocumento"
							bind:this={pondDocumentoConyugue}
							{nameDocumentoConyugue}
							name="fileDocumentoVotacion"
							labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
							allowMultiple={true}
							oninit={handleAddFileConyugue}
							onaddfile={handleAddFileConyugue}
							credits=""
							acceptedFileTypes={['application/pdf']}
							labelInvalidField="El campo contiene archivos no válidos"
							maxFiles="1"
							maxParallelUploads="1"
						/>
						<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
					</div>
					<div class="col-md-6">
						<label for="ConyugueFileDocumentoVotacion" class="form-label fw-bold"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> Papeleta de Votación:</label
						>
						<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
						<FilePond
							class="pb-0 mb-0"
							id="ConyugueFileDocumentoVotacion"
							bind:this={pondDocumentoVotacionConyugue}
							{nameVotacionConyugue}
							name="fileDocumentoVotacion"
							labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
							allowMultiple={true}
							oninit={handleAddFileVotacionConyugue}
							onaddfile={handleAddFileVotacionConyugue}
							credits=""
							acceptedFileTypes={['application/pdf']}
							labelInvalidField="El campo contiene archivos no válidos"
							maxFiles="1"
							maxParallelUploads="1"
						/>
						<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
					</div>
				</div>
			</div>
			<div class="card-footer text-muted">
				<div class="d-grid gap-2 d-md-flex justify-content-md-end">
					<!--<button class="btn btn-primary me-md-2" type="button">Button</button>-->
					<button type="submit" class="btn btn-info">Guardar</button>
					<a color="danger" class="btn btn-danger" on:click={() => closeConyugue()}>Cerrar</a>
				</div>
			</div>
		</form>
	</ModalBody>
</Modal>

<Modal
	isOpen={mOpenPagare}
	toggle={mTogglePagare}
	size={mSizePagare}
	class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
	backdrop="static"
	fade={false}
>
	<ModalHeader toggle={mTogglePagare}>
		<h4>{titlePagare}</h4>
	</ModalHeader>
	<ModalBody>
		<form id="frmInfoPagare" on:submit|preventDefault={saveInfoPagare}>
			<div class="card-body">
				<div class="row g-3">
					<div class="col-md-12">
						<label for="ePersonaFileDocumento" class="form-label fw-bold"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> Tabla de Amortización:</label
						>
						<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
						<FilePond
							class="pb-0 mb-0"
							id="ePersonaFileDocumento"
							bind:this={pondTablaAmortizacion}
							{nameTablaAmortizacion}
							name="fileDocumento"
							labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
							allowMultiple={true}
							oninit={handleInit}
							onaddfile={handleAddFileTableAmortizacion}
							credits=""
							acceptedFileTypes={['application/pdf']}
							labelInvalidField="El campo contiene archivos no válidos"
							maxFiles="1"
							maxParallelUploads="1"
						/>
						<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
					</div>
					<div class="col-md-12">
						<label for="ePersonaFileDocumento" class="form-label fw-bold"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> Contrato de Maestría:</label
						>
						<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
						<FilePond
							class="pb-0 mb-0"
							id="ePersonaFileDocumento"
							bind:this={pondContratoMaestria}
							{nameContratoMaestria}
							name="fileDocumentoVotacion"
							labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
							allowMultiple={true}
							oninit={handleInit}
							onaddfile={handleAddFileContratoM}
							credits=""
							acceptedFileTypes={['application/pdf']}
							labelInvalidField="El campo contiene archivos no válidos"
							maxFiles="1"
							maxParallelUploads="1"
						/>
						<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
					</div>
					<div class="col-md-12">
						<label for="ePersonaFileDocumento" class="form-label fw-bold"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> Pagaré:</label
						>
						<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
						<FilePond
							class="pb-0 mb-0"
							id="ePersonaFileDocumento"
							bind:this={pondPagare}
							{namePagare}
							name="fileDocumentoVotacion"
							labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
							allowMultiple={true}
							oninit={handleInit}
							onaddfile={handleAddFilePagare}
							credits=""
							acceptedFileTypes={['application/pdf']}
							labelInvalidField="El campo contiene archivos no válidos"
							maxFiles="1"
							maxParallelUploads="1"
						/>
						<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
					</div>
				</div>
				<div class="card-footer text-muted">
					<div class="d-grid gap-2 d-md-flex justify-content-md-end">
						<!--<button class="btn btn-primary me-md-2" type="button">Button</button>-->
						<button type="submit" class="btn btn-info">Guardar</button>
						<a color="danger" class="btn btn-danger" on:click={() => closePagare()}>Cerrar</a>
					</div>
				</div>
			</div>
		</form>
	</ModalBody>
</Modal>

{#if mOpenModalGenerico}
	<ModalGenerico
		mToggle={mToggleModalGenerico}
		mOpen={mOpenModalGenerico}
		modalContent={modalDetalleContent}
		title={modalTitle}
		aData={aDataModal}
		size="xl"
	/>
{/if}

<style global>
	@import 'filepond/dist/filepond.css';
</style>
