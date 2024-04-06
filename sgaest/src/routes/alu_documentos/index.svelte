<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';
	import { variables } from '$lib/utils/constants';

	export const load: Load = async ({ fetch }) => {
		let eMateriasAsignadas = [];
		let eMatricula = {};
		let es_admision = false;
		let es_pregrado = false;
		let eMalla = {};
		let ePeriodo = {};
		let eInscripcion = {};
		let puede_elegir_sede_examen = false;
		const ds = browserGet('dataSession');
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/aulavirtual', {});
			loading.setLoading(false, 'Cargando, espere por favor...');
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
					eMateriasAsignadas = res.data['eMateriasAsignadas'];
					eMatricula = res.data['eMatricula'];
					es_admision = res.data['es_admision'];
					es_pregrado = res.data['es_pregrado'];
					eMalla = res.data['eMalla'];
					ePeriodo = res.data['ePeriodo'];
					puede_elegir_sede_examen = res.data['puede_elegir_sede_examen'];
					eInscripcion = res.data['eInscripcion']
				}
			}
		}

		return {
			props: {
				eMatricula,
				eMateriasAsignadas,
				es_admision,
				es_pregrado,
				eMalla,
				ePeriodo,
				puede_elegir_sede_examen,
				eInscripcion
			}
		};
	};
</script>

<script lang="ts">
	import Swal from 'sweetalert2';
	import { onMount } from 'svelte';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import ComponenteCompanero from './_modal/bibliografia.svelte';
	import ComponenteSilabo from './_modal/silabo.svelte';
	import ComponenteGuia from './_modal/guiapractica.svelte';
	import ComponenteComuni from './_modal/comunicacion.svelte';
	import ComponenteControl from './_modal/controlacademico.svelte';
	import ComponenteCalendarioActividad from '$components/Alumno/Actividad/Calendario.svelte';
	import ModalVerificacionExamenesFinales from './_modal/identity_verification.svelte';
	import ModalDatosVerificacionExamenesFinales from './_modal/datos_identity_verification.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { converToDecimal } from '$lib/formats/formatDecimal';
	import { addNotification } from '$lib/store/notificationStore';
	import { Button, Spinner } from 'sveltestrap';
	import Error from '../__error.svelte';
	export let es_admision;
	export let es_pregrado;
	export let eMateriasAsignadas;
	export let eMalla;
	export let eMatricula;
	export let ePeriodo;
	export let eInscripcion;
	export let puede_elegir_sede_examen;
	let load = true;
	let aDataModal = {};
	let modalDetalleContent;
	let mOpenModalGenerico = false;
	let modalTitle = '';
	let mClassModal =
		'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down';
	let mSizeModal = 'xl';
	let eMatriculaSedeExamen = {};
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);
	const DEBUG = import.meta.env.DEV;
	let itemsBreadCrumb = [{ text: 'Aula Virtual', active: true, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {
		console.log('DEBUG: ', DEBUG);
		let loadSwal = false;
		if (eMatricula && ePeriodo) {
			load = false;
			if (ePeriodo.idm === 224) {
				if (es_pregrado || es_admision) {
					if (puede_elegir_sede_examen) {
						if (!eMatricula.cerrada && eMalla.modalidad === 3) {
							if (!eMatricula.tiene_matricula_sede_examen) {
								await loadMensajeSedeExamenes();
								loadSwal = true;
							}
						}
					}
				}
			}
			const valida = await validaHorarioExamen();
			if (valida) {
				if (!loadSwal) {
					const data = await loadDataArchivoIdentidad();
					if (data) {
						if (data.eMatriculaSedeExamen) {
							eMatriculaSedeExamen = { ...data.eMatriculaSedeExamen };
							if (eMatriculaSedeExamen) {
								const tiene_fase_1 = eMatriculaSedeExamen.tiene_fase_1 ?? false;
								if (tiene_fase_1 == false) {
									aDataModal = { ...eMatriculaSedeExamen };
									modalDetalleContent = ModalVerificacionExamenesFinales;
									mOpenModalGenerico = !mOpenModalGenerico;
									modalTitle = undefined;
									mClassModal =
										'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
									mSizeModal = 'xl';
								}
							}
						}
					}
				}
			}
		}
	});

	const validaHorarioExamen = () => {
		if (!eMatricula.cerrada) {
			if (ePeriodo.idm === 224) {
				if (es_pregrado) {
					if (eMalla.modalidad === 3 || eMatricula.tiene_matricula_sede_examen) {
						return true;
					}
					return false;
				} else if (es_admision) {
					return true;
				}
			}
		}
		return false;
	};

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

	const loadMensajeSedeExamenes = async () => {
		const mensaje_1 = {
			title: `Atención`,
			html: 'Elige la sede para tus exámenes finales presenciales</b>',
			icon: 'warning',
			//iconHtml: `<img src='${variables.BASE_API}/static/images/icons/icono_aulavirtual.svg' style='height: 150%;'>`,
			//customClass: { icon: 'no-border', cancelButton: 'swalBtnP' },
			showCancelButton: true,
			showConfirmButton: true,
			confirmButtonColor: '#FE9900',
			cancelButtonColor: '#335f7f',
			allowOutsideClick: false,
			allowEscapeKey: false,
			confirmButtonText: 'SANTO DOMINGO',
			cancelButtonText: 'MILAGRO'
		};
		Swal.fire(mensaje_1).then((result) => {
			console.log(result);
			if (result.value) {
				const mensaje_2 = {
					title: 'Atención!',
					html: '<b>¿Estás seguro?</b> <br> Recuerda que estás sleccionando la sede <b>SANTO DOMINGO</b> para rendir tus exámenes finales de forma presencial<b></b>',
					type: 'warning',
					allowOutsideClick: false,
					showCancelButton: true,
					confirmButtonText: 'Si, estoy seguro',
					cancelButtonText: 'No, estoy seguro',
					allowEscapeKey: false
				};
				Swal.fire(mensaje_2).then(async (result) => {
					if (result.value) {
						loading.setLoading(true, 'Guardando la información, espere por favor...');
						const [res, errors] = await apiPOST(fetch, 'alumno/aulavirtual', {
							action: 'saveSedeExamen',
							sedevirtual_id: 10
						});
						if (errors.length > 0) {
							addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
							loading.setLoading(false, 'Cargando, espere por favor...');
							return;
						} else {
							loading.setLoading(false, 'Cargando, espere por favor...');
							if (!res.isSuccess) {
								addToast({ type: 'error', header: '¡ERROR!', body: res.message });
								if (!res.module_access) {
									goto('/');
								}
								return;
							} else {
								addToast({
									type: 'success',
									header: 'Exitoso',
									body: 'Se guardo correctamente los datos'
								});
								goto('/');
							}
						}
					}
				});
			} else {
				const mensaje_3 = {
					title: 'Atención!',
					html: '<b>¿Estás seguro?</b> <br> Recuerda que estás sleccionando la sede <b>MILAGRO</b> para rendir tus exámenes finales de forma presencial ',
					type: 'warning',
					allowOutsideClick: false,
					showCancelButton: true,
					confirmButtonText: 'Si, estoy seguro',
					cancelButtonText: 'No, estoy seguro'
				};
				Swal.fire(mensaje_3).then(async (result) => {
					if (result.value) {
						loading.setLoading(true, 'Guardando la información, espere por favor...');
						const [res, errors] = await apiPOST(fetch, 'alumno/aulavirtual', {
							action: 'saveSedeExamen',
							sedevirtual_id: 1
						});
						if (errors.length > 0) {
							addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
							loading.setLoading(false, 'Cargando, espere por favor...');
							return;
						} else {
							loading.setLoading(false, 'Cargando, espere por favor...');
							if (!res.isSuccess) {
								addToast({ type: 'error', header: '¡ERROR!', body: res.message });
								if (!res.module_access) {
									goto('/');
								}
								return;
							} else {
								addToast({
									type: 'success',
									header: 'Exitoso',
									body: 'Se guardo correctamente los datos'
								});
								goto('/');
							}
						}
					}
				});
			}
		});
	};

	const loadDataArchivoIdentidad = async () => {
		loading.setLoading(true, 'Consultando la información, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/aulavirtual', {
			action: 'loadDataArchivoIdentidad'
		});
		loading.setLoading(false, 'Consultando la información, espere por favor...');
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			return undefined;
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: '¡ERROR!', body: res.message });
				if (!res.module_access) {
					goto('/');
				}
				return undefined;
			} else {
				return await { ...res.data };
			}
		}
		return undefined;
	};

	const toggleModalBibliografia = async (id, idp) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/aulavirtual', {
			action: 'listarBibliografia',
			id: id,
			idp: idp
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
				modalDetalleContent = ComponenteCompanero;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'Bibliografía básica y complementaria';
				mClassModal =
					'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down';
				mSizeModal = 'xl';
			}
		}
	};

	const toggleModalSilabo = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/aulavirtual', {
			action: 'listarSilabo',
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
				modalDetalleContent = ComponenteSilabo;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'Listado de sílabos';
				mClassModal =
					'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down';
				mSizeModal = 'xl';
			}
		}
	};

	const toggleModalGuiaPractica = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/aulavirtual', {
			action: 'guiapracticas',
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
				modalDetalleContent = ComponenteGuia;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'Guias de prácticas';
				mClassModal =
					'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down';
				mSizeModal = 'xl';
			}
		}
	};

	const toggleModalComunicaciones = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/aulavirtual', {
			action: 'comunicaciones',
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
				modalDetalleContent = ComponenteComuni;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'Comunicados';
				mClassModal =
					'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down';
				mSizeModal = 'xl';
			}
		}
	};

	const toggleModalControlAcademico = async (id, idins, idp) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/aulavirtual', {
			action: 'controlacademico',
			id: id,
			idins: idins,
			idp: idp
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
				modalDetalleContent = ComponenteControl;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'Orientación y Acompañamiento Académico';
				mClassModal =
					'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down';
				mSizeModal = 'xl';
			}
		}
	};

	const loadCalendarioActividades = async () => {
		const id = eMatricula.id;
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/general/data', {
			action: 'detail_calenar_student',
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
				modalDetalleContent = ComponenteCalendarioActividad;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'Calendario de actividades';
				mClassModal =
					'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down';
				mSizeModal = 'xl';
			}
		}
	};

	const descargarzip = async (id, tipo) => {
		const idmatricula = eMatricula.id;
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/aulavirtual', {
			action: tipo,
			idmateriaasignada: id,
			idmatricula: idmatricula
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
				let url = res.data['url'];
				window.open(`${variables.BASE_API}${url}`, '_blank');
			}
		}
	};

	const descargar_certificado_egresado_derecho =async (id) => {
		
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/aulavirtual', {
			action: 'certiderechoregresado',
			idinscripcion: id
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
				let url = res.data['url'];
				window.open(`${variables.BASE_API}${url}`, '_blank');
			}
		}
		
	}

	const openModalInformacionExamen = () => {
		aDataModal = { ...eMatriculaSedeExamen };
		modalDetalleContent = ModalDatosVerificacionExamenesFinales;
		mOpenModalGenerico = !mOpenModalGenerico;
		modalTitle = 'Documentación de la validación de identidad para los exámenes finales';
		mClassModal =
			'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
		mSizeModal = 'xl';
	};

	const actionRun = (event) => {
		//mOpenModal2 = false;
		//loading.setLoading(false, 'Cargando, espere por favor...');
		const detail = event.detail;
		const action = detail.action;
		if (action == 'changeMatriculaExamenSede') {
			eMatriculaSedeExamen = { ...detail.eMatriculaSedeExamen };
		}
	};
</script>

<svelte:head>
	<title>Aula Virtual</title>
</svelte:head>

{#if !load}
	<BreadCrumb title="Aula Virtual" items={itemsBreadCrumb} back={backBreadCrumb} />
	<div class="row">
		<div class="container">
			{#if !es_admision}
				<button
					class="btn btn-primary btn-sm mb-1"
					type="button"
					data-bs-toggle="offcanvas"
					data-bs-target="#offcanvasWithBothOptions"
					aria-controls="offcanvasWithBothOptions">Información de la Carrera</button
				>
			{/if}

			<button
				class="btn btn-secondary btn-sm mb-1"
				type="button"
				on:click|preventDefault={loadCalendarioActividades}>Calendario de actividades</button
			>
			{#if ePeriodo.idm === 224}
				{#if es_pregrado || es_admision}
					{#if puede_elegir_sede_examen}
						{#if !eMatricula.cerrada && eMalla.modalidad === 3}
							{#if !eMatricula.tiene_matricula_sede_examen}
								<button
									class="btn btn-danger btn-sm mb-1"
									type="button"
									on:click|preventDefault={loadMensajeSedeExamenes}
								>
									Elegir sede de examen</button
								>
							{/if}
						{/if}
					{/if}
				{/if}
			{/if}

			{#if eMatricula.esta_visible_horario_examen}
				<a class="btn btn-warning btn-sm mb-1 text-white" href="/alu_documentos/examenes">
					<span class="spinner-grow spinner-grow-sm text-danger" role="status" aria-hidden="true" />
					Horario de exámenes</a
				>
			{/if}
			{#if eMatriculaSedeExamen}
				{#if validaHorarioExamen()}
					{#if !eMatriculaSedeExamen.tiene_fase_1}
						<a
							class="btn btn-info btn-sm mb-1 text-white"
							href="/alu_documentos/identity_verification"
						>
							Verificación de identidad</a
						>
					{/if}
				{/if}
			{/if}
			<div
				class="offcanvas offcanvas-start"
				data-bs-scroll="true"
				data-bs-backdrop="true"
				tabindex="-1"
				id="offcanvasWithBothOptions"
				aria-labelledby="offcanvasWithBothOptionsLabel"
			>
				<div class="offcanvas-header">
					<h5 class="offcanvas-title" id="offcanvasWithBothOptionsLabel">
						<strong>INFORMACIÓN DE LA CARRERA</strong>
					</h5>
					<button
						type="button"
						class="btn-close text-reset"
						data-bs-dismiss="offcanvas"
						aria-label="Close"
					/>
				</div>
				<div class="offcanvas-body">
					<div class="accordion" id="accordionExample">
						{#if eMalla.misioncarrera}
							<div class="accordion-item">
								<h2 class="accordion-header" id="headingTwo">
									<button
										class="accordion-button collapsed"
										type="button"
										data-bs-toggle="collapse"
										data-bs-target="#collapseTwo"
										aria-expanded="false"
										aria-controls="collapseTwo"
									>
										<strong>MISIÓN DE LA CARRERA </strong>
									</button>
								</h2>
								<div
									id="collapseTwo"
									class="accordion-collapse collapse"
									aria-labelledby="headingTwo"
									data-bs-parent="#accordionExample"
								>
									<div class="accordion-body">
										<p class="text-justify">{eMalla.misioncarrera}</p>
									</div>
								</div>
							</div>
						{/if}
						{#if eMalla.perfilprofesional}
							<div class="accordion-item">
								<h2 class="accordion-header" id="headingThree">
									<button
										class="accordion-button collapsed"
										type="button"
										data-bs-toggle="collapse"
										data-bs-target="#collapseThree"
										aria-expanded="false"
										aria-controls="collapseThree"
									>
										<strong>PERFIL PROFESIONAL </strong>
									</button>
								</h2>
								<div
									id="collapseThree"
									class="accordion-collapse collapse"
									aria-labelledby="headingThree"
									data-bs-parent="#accordionExample"
								>
									<div class="accordion-body">
										<p class="text-justify">{@html eMalla.perfilprofesional}</p>
									</div>
								</div>
							</div>
						{/if}
						{#if eMalla.perfilegreso}
							<div class="accordion-item">
								<h2 class="accordion-header" id="headingFour">
									<button
										class="accordion-button collapsed"
										type="button"
										data-bs-toggle="collapse"
										data-bs-target="#collapseFour"
										aria-expanded="false"
										aria-controls="collapseFour"
									>
										<strong>PERFIL EGRESO </strong>
									</button>
								</h2>
								<div
									id="collapseFour"
									class="accordion-collapse collapse"
									aria-labelledby="headingFour"
									data-bs-parent="#accordionExample"
								>
									<div class="accordion-body">
										<p class="text-justify">{@html eMalla.perfilegreso}</p>
									</div>
								</div>
							</div>
						{/if}
						{#if eMalla.objetivocarrera}
							<div class="accordion-item">
								<h2 class="accordion-header" id="headingFive">
									<button
										class="accordion-button collapsed"
										type="button"
										data-bs-toggle="collapse"
										data-bs-target="#collapseFive"
										aria-expanded="false"
										aria-controls="collapseFive"
									>
										<strong>OBJETIVO DE LA CARRERA </strong>
									</button>
								</h2>
								<div
									id="collapseFive"
									class="accordion-collapse collapse"
									aria-labelledby="headingFive"
									data-bs-parent="#accordionExample"
								>
									<div class="accordion-body">
										<p class="text-justify">{@html eMalla.objetivocarrera}</p>
									</div>
								</div>
							</div>
						{/if}
					</div>
				</div>
			</div>
		</div>
		{#if eMatriculaSedeExamen}
			{#if validaHorarioExamen()}
				{#if eMatricula.tiene_matricula_sede_examen}
					<div class="container mt-2">
						<div class="alert alert-info">
							Tu sede seleccionada para rendir el examen final es: {eMatricula.sede_examen}
						</div>
					</div>
				{/if}
			{/if}
		{/if}
		{#if eMatriculaSedeExamen}
			{#if validaHorarioExamen()}
				{#if eMatriculaSedeExamen.tiene_fase_1}
					<div class="border-bottom pb-3 mb-3 d-lg-flex justify-content-start align-items-center">
						<div class="mb-3 mb-lg-0 mx-2">
							<h3 class="mb-0 h4 fw-bold text-primary">
								Aquí podras ver la información que subiste en la validación de identidad para los
								exámenes finales
							</h3>
						</div>
						<div class="d-grid gap-2 d-md-flex justify-content-start">
							<button
								class="btn btn-warning btn-sm rounded-pill text-black"
								on:click={openModalInformacionExamen}
							>
								<p class="m-0 p-0">Ver información</p>
							</button>
							<!--<a
								class="btn btn-warning btn-sm rounded-pill text-black"
								href={eMatriculaSedeExamen.download_archivoidentidad}
								target="_blank"
							>
								<p class="m-0 p-0">
									Documento de identidad
									<i class="bi bi-download" />
								</p>
							</a>
							<a
								class="btn btn-primary btn-sm rounded-pill text-white"
								href={eMatriculaSedeExamen.download_archivofoto}
								target="_blank"
							>
								<p class="m-0 p-0">
									Foto
									<i class="bi bi-download" />
								</p>
							</a>-->
						</div>
					</div>
				{/if}
			{/if}
		{/if}
		<!-- {#if eInscripcion.egresadocderecho}
			<div class="border-bottom pb-3 mb-3 d-lg-flex justify-content-start align-items-center">				
				<div class="d-grid gap-2 d-md-flex justify-content-start">
					<a
						class="btn btn-warning btn-sm rounded-pill text-black"
						on:click={() => descargar_certificado_egresado_derecho(eInscripcion.id)}
						target="_blank"
					>
						<p class="m-0 p-0">Certificado egresado</p>
					</a>				
					
					
				</div>
			</div>
		{/if} -->
		<div class="col-lg-12 col-xm-12 col-md-12">
			<div class="card shadow-none m-0 p-0" style="background-color: var(--bs-body-bg);">
				<div
					class="card-header mx-0 px-0 shadow-none border-0"
					style="background-color: var(--bs-body-bg);"
				>
					<h1 class="mb-0 h2 fw-bold">Mis materias</h1>
				</div>
				{#if eMatricula.bloqueomatricula}
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
								<h4 class="alert-heading">MATRÍCULA BLOQUEADA</h4>
								Estimado/a estudiante, mantiene cuotas vencidas en el módulos "Mis Finanzas" por lo tanto
								su matrícula se encuentra bloqueada para asistencia, tareas y registro de calificaciones.
							</div>
						</div>
					</div>
				{/if}
				{#if es_admision}
					{#if eMatricula.cerrado}
						{#if eMatricula.aprobado}
							{#if eMatricula.tiene_deuda}
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
											<h4 class="alert-heading">MATRÍCULA CONDICIONADA</h4>
											Estimado/a aspirante, mantiene cuotas vencidas en el módulos "Mis Finanzas" por
											lo tanto su matrícula se encuentra condicionada para asistencia, tareas y registro
											de calificaciones.
										</div>
									</div>
								</div>
							{:else}
								<div class="card-header">
									<div class="alert alert-info d-flex align-items-center" role="alert">
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
											<h4 class="alert-heading">APROBADO, USTED TIENE UN CUPO ASIGNADO</h4>
										</div>
									</div>
								</div>
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
										<h4 class="alert-heading">REPROBADO, NO TIENE UN CUPO ASIGNADO</h4>
									</div>
								</div>
							</div>
						{/if}
					{/if}
				{/if}

				<div class="card-body m-0 p-0">
					{#if eMateriasAsignadas.length > 0}
						<div
							class="row row-cols-1 row-cols-md-2 row-cols-sm-1 row-cols-lg-3 row-cols-xl-3 row-cols-xxl-3 g-4"
						>
							{#each eMateriasAsignadas as eMateriaAsignada}
								<div class="col">
									<div class="card h-100 shadow rounded-3 position-relative">
										<div class="position-absolute top-0 end-0">
											<div class="dropdown">
												<a
													class="btn-icon btn btn-ghost btn-sm rounded-circle dropdown-toggle p-1"
													href="#"
													role="button"
													id="dropdownMenuLink"
													data-bs-toggle="dropdown"
													aria-expanded="false"
												>
													<i class="fe fe-more-vertical" />
												</a>
												<ul class="dropdown-menu" aria-labelledby="dropdownMenuLink">
													{#if !eMateriaAsignada.cerrado}
														<li>
															<a class="dropdown-item" href="/alu_asistencias">
																<i class="bi bi-bell" /> Asistencias
															</a>
														</li>
													{/if}

													{#if eMateriaAsignada.es_modulo_ingles}
														<li>
															<a
																href="https:\\upei.buckcenter.edu.ec/course/view.php?id={eMateriaAsignada
																	.materia.idcursomoodle}"
																class="dropdown-item"
																target="_blank"><span class="fe fe-link" /> Ir al curso de moodle</a
															>
														</li>
													{:else if eMateriaAsignada.materia.idcursomoodle}
														<li>
															{#if es_admision}
																<a
																	class="dropdown-item"
																	target="_blank"
																	href="{ePeriodo.urlmoodle2}/course/view.php?id={eMateriaAsignada
																		.materia.idcursomoodle}"
																	><i class="bi bi-mortarboard-fill" /> Ir al curso de moodle</a
																>
															{:else}
																<a
																	class="dropdown-item"
																	target="_blank"
																	href="{ePeriodo.urlmoodle}/course/view.php?id={eMateriaAsignada
																		.materia.idcursomoodle}"
																	><i class="bi bi-mortarboard-fill" /> Ir al curso de moodle</a
																>
															{/if}
														</li>
													{/if}

													<li>
														<button
															class="dropdown-item"
															on:click={() =>
																toggleModalControlAcademico(
																	eMateriaAsignada.id,
																	eMatricula.inscripcion.id,
																	ePeriodo.id
																)}
														>
															<i class="bi bi-file-earmark-person" /> Acompañamiento Académico
														</button>
													</li>
													{#if eMateriaAsignada.materia.silabo}
														{#if eMateriaAsignada.materia.silabo.estado_planificacion_clases >= 100}
															<li>
																<button
																	class="dropdown-item"
																	on:click={() => toggleModalSilabo(eMateriaAsignada.materia.id)}
																>
																	<i class="bi bi-file-earmark-pdf" /> Silabo
																</button>
															</li>
														{/if}
													{/if}
													<li>
														<button
															class="dropdown-item"
															on:click={() =>
																toggleModalBibliografia(
																	eMateriaAsignada.materia.id,
																	eMatricula.inscripcion.persona.id
																)}
														>
															<i class="bi bi-bookmarks-fill" /> Bibliografía
														</button>
													</li>
													{#if eMateriaAsignada.materia.silabo}
														{#if eMateriaAsignada.materia.silabo.numero_guia_practicas}
															{#if eMateriaAsignada.materia.silabo.numero_guia_practicas > 0}
																<li>
																	<button
																		class="dropdown-item"
																		on:click={() =>
																			toggleModalGuiaPractica(eMateriaAsignada.materia.id)}
																	>
																		<i class="bi bi-file-earmark-pdf" /> Guia Practica
																	</button>
																</li>
															{/if}
														{/if}
													{/if}
													{#if eMateriaAsignada.materia.syllabusword}
														<li>
															<a
																target="_blank"
																class="dropdown-item"
																href={eMateriaAsignada.materia.syllabusword.download_link}
																><i class="fa fa-download " /> Descargar sílabo</a
															>
														</li>
													{/if}
													{#if eMatricula.esppl}
														<li><hr class="dropdown-divider" /></li>
														{#if eMateriaAsignada.tienesilabo}
															<li>
																<a
																	class="dropdown-item"
																	href="javascript:void(0)"
																	on:click={() =>
																		descargarzip(eMateriaAsignada.id, 'descargaractividades')}
																	><i class="bi bi-download " /> Descargar Actividades</a
																>
															</li>
															<li>
																<a
																	class="dropdown-item"
																	href="javascript:void(0)"
																	on:click={() =>
																		descargarzip(eMateriaAsignada.id, 'descargarrecursos')}
																	><i class="bi bi-download " /> Descargar Recursos</a
																>
															</li>
														{/if}
													{/if}
												</ul>
											</div>
										</div>
										<div class="position-absolute top-0 start-0">
											<div class="btn-group">
												<button
													data-bs-toggle="tooltip"
													data-placement="right"
													title="Comunicados"
													class="btn-warning rounded-circle icon-shape icon-md"
													on:click={() => toggleModalComunicaciones(eMateriaAsignada.id)}
													type="button"
												>
													<i class="fe fe-message-square" style="width:250px;" />
													<span
														class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
													>
														{eMateriaAsignada.materia.totalcomunicacionmasiva}
													</span>
												</button>
											</div>
										</div>
										<!-- Card body -->
										<div class="card-body">
											<div class="d-flex align-items-center">
												<div class="position-relative">
													{#if eMateriaAsignada.materia.profesor}
														<img
															src={eMateriaAsignada.materia.profesor.persona.foto_perfil}
															onerror="this.onerror=null;this.src='./image.png'"
															alt=""
															class="rounded-circle avatar-xl"
														/>
													{:else}
														<img
															src="./image.png"
															onerror="this.onerror=null;this.src='./image.png'"
															alt=""
															class="rounded-circle avatar-xl"
														/>
													{/if}
													<!-- <a
														href="#"
														class="position-absolute mt-2 ms-n3"
														data-bs-toggle="tooltip"
														data-placement="top"
														title=""
														data-bs-original-title="Verifed"
													>
														<img
															src="../assets/images/svg/checked-mark.svg"
															alt=""
															height="30"
															width="30"
														/>
													</a> -->
												</div>
												<div class="ms-4">
													<h4 class="mb-0">{eMateriaAsignada.materia.asignatura.nombre}</h4>
													<p class="mb-1 fs-6">
														{#if eMateriaAsignada.materia.profesor}
															{eMateriaAsignada.materia.profesor.persona.nombre_completo}
														{:else}
															SIN PROFESOR
														{/if}
													</p>
													<span class="fs-6">
														<span class="text-warning">
															{eMateriaAsignada.materia.asignaturamalla.nivelmalla.nombre}
														</span>
														<span class="fa fa-star text-warning me-2" />Paralelo:
														<strong>{eMateriaAsignada.materia.paralelomateria.nombre}</strong></span
													>
													{#if eMateriaAsignada.materia.asignatura.idm == 4837 && ePeriodo.idm == 123}
														<p class="fs-6">
															<a
																class="btn btn-link btn-mini tu p-0"
																href="https://facebook.com/UniversidadEstatalDeMilagro/live"
																target="_blank"><i class="fa fa-link" /> Ir a clase</a
															>
														</p>
													{/if}
												</div>
											</div>
											<div class="border-top row mt-3  mb-0 g-0">
												<div class="col">
													<div class="pe-1 ps-1 py-2 text-center fs-6">
														<h5 class="mb-0 fs-6">{eMateriaAsignada.materia.horas}</h5>
														<span>Horas totales de la materia</span>
													</div>
												</div>
												<div class="col border-start">
													<div class="pe-1 ps-2 py-2 text-center fs-6">
														<h5 class="mb-0 fs-6">{eMateriaAsignada.asistenciafinal}%</h5>
														<span>Asistencia final</span>
													</div>
												</div>
											</div>
											<div class="border-top row mt-0 border-bottom mb-3 g-0">
												<div class="col">
													<div class="pe-1 ps-1 py-2 text-center fs-6">
														<h5 class="mb-0 fs-6">{eMateriaAsignada.materia.inicio}</h5>
														<span>Fecha inicio</span>
													</div>
												</div>
												<div class="col border-start">
													<div class="pe-1 ps-2 py-2 text-center fs-6">
														<h5 class="mb-0 fs-6">{eMateriaAsignada.materia.fin}</h5>
														<span>Fecha fin</span>
													</div>
												</div>
											</div>
										</div>
									</div>
								</div>
							{/each}
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
	{#if mOpenModalGenerico}
		<ModalGenerico
			mToggle={mToggleModalGenerico}
			mOpen={mOpenModalGenerico}
			modalContent={modalDetalleContent}
			title={modalTitle}
			aData={aDataModal}
			mClass={mClassModal}
			size={mSizeModal}
			on:actionRun={actionRun}
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
