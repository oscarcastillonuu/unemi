<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';

	export const load: Load = async ({ fetch }) => {
		let eMateriasAsignadas = [];
		let eMatricula = {};
		let es_admision = false;
		let es_pregrado = false;
		let eMalla = {};
		let ePeriodo = {};
		/*let tiene_termino_condicion_examen = false;
		let mostrar_terminos_examenes = false;
		let termino_condicion_examen = '';*/
		const ds = browserGet('dataSession');
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/aulavirtual/examenes', {});
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
					}
				} else {
					eMateriasAsignadas = res.data['eMateriasAsignadas'];
					eMatricula = res.data['eMatricula'];
					es_admision = res.data['es_admision'];
					es_pregrado = res.data['es_pregrado'];
					eMalla = res.data['eMalla'];
					ePeriodo = res.data['ePeriodo'];
					/*tiene_termino_condicion_examen = res.data['tiene_termino_condicion_examen'];
					mostrar_terminos_examenes = res.data['mostrar_terminos_examenes'];
					termino_condicion_examen = res.data['termino_condicion_examen'];*/
				}
			}
		}

		return {
			props: {
				eMateriasAsignadas,
				eMatricula,
				es_admision,
				es_pregrado,
				eMalla,
				ePeriodo
				/*tiene_termino_condicion_examen,
				mostrar_terminos_examenes,
				termino_condicion_examen*/
			}
		};
	};
</script>

<script lang="ts">
	import Swal from 'sweetalert2';
	import { onMount } from 'svelte';
	import { variables } from '$lib/utils/constants';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import Horarioexamen from './_data.svelte';
	import ComponentTerminosCondicionesExamen from './_modal/terminos_condiciones_examen.svelte';
	import ComponentViewPDF from '$components/viewPDF.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { converToDecimal } from '$lib/formats/formatDecimal';
	import { addNotification } from '$lib/store/notificationStore';
	import { Button, Spinner } from 'sveltestrap';
	import ModalDinamico from '$components/Alumno/ModalDinamico.svelte';
	import { action_print_ireport } from '$lib/helpers/baseHelper';
	export let eMateriasAsignadas;
	export let es_admision;
	export let es_pregrado;
	export let eMalla;
	export let eMatricula;
	export let ePeriodo;
	//export let tiene_termino_condicion_examen;
	//export let mostrar_terminos_examenes;
	//export let termino_condicion_examen;
	let load = true;
	let aDataModal = {};
	let modalDetalleContent;
	let mOpenModal = false;
	let mTitle = '';
	let mClassModal =
		'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down';
	let mSizeModal = 'xl';
	const mToggleModal = () => (mOpenModal = !mOpenModal);
	let acept_t_ex = false;
	let eMatriculaSedeExamen = {};

	/*const mToggleModal = () => {
		mOpenModal = !mOpenModal;
		closeTerminoCondicionExamen();
	};*/

	let itemsBreadCrumb = [
		{ text: 'Aula Virtual', active: false, href: '/alu_documentos' },
		{ text: 'Horario de examen', active: true, href: undefined }
	];
	let backBreadCrumb = { href: '/alu_documentos', text: 'Atrás' };

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {
		/*if (eMateriasAsignadas) {
			load = false;
		}*/
		const valid = await validaHorarioExamen();
		if (valid) {
			const data = await loadDataArchivoIdentidad();
			if (data) {
				if (data.eMatriculaSedeExamen) {
					eMatriculaSedeExamen = { ...data.eMatriculaSedeExamen };
					if (eMatriculaSedeExamen) {
						const tiene_fase_1 = eMatriculaSedeExamen.tiene_fase_1 ?? false;
						if (tiene_fase_1 == false) {
							const mensaje = {
								title: `Atención`,
								html: 'Para visualizar tu horario de exámenes finales, debes completar la primera fase de verificación de identidad',
								icon: 'warning',
								//iconHtml: `<img src='${variables.BASE_API}/static/images/icons/icono_aulavirtual.svg' style='height: 150%;'>`,
								//customClass: { icon: 'no-border', cancelButton: 'swalBtnP' },
								showCancelButton: true,
								showConfirmButton: true,
								confirmButtonColor: '#FE9900',
								cancelButtonColor: '#335f7f',
								allowOutsideClick: false,
								allowEscapeKey: false,
								confirmButtonText: 'Ir a completar fase 1',
								cancelButtonText: 'Continuar'
							};
							Swal.fire(mensaje).then((result) => {
								console.log(result);
								if (result.value) {
									goto('/alu_documentos');
								}
							});
						} else {
							const tiene_fase_2 = eMatriculaSedeExamen.tiene_fase_2 ?? false;
							const terminos_examenes = eMatriculaSedeExamen.terminos_examenes ?? {};
							const tiene_materia_codigo_qr = eMatriculaSedeExamen.tiene_materia_codigo_qr ?? false;
							if (tiene_materia_codigo_qr === true) {
								if (tiene_fase_2 === false && terminos_examenes.view === true) {
									aDataModal = { ...eMatriculaSedeExamen };
									modalDetalleContent = ComponentTerminosCondicionesExamen;
									mOpenModal = !mOpenModal;
									mTitle = 'Términos y condiciones para rendir los exámenes';
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
		load = false;
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

	const actionRun = (event) => {
		//mOpenModal2 = false;
		//loading.setLoading(false, 'Cargando, espere por favor...');
		const detail = event.detail;
		const action = detail.action;
		if (action == 'closeModal') {
			closeTerminoCondicionExamen();
		}
	};

	const closeTerminoCondicionExamen = () => {
		goto('/');
	};

	const view_pdf = (url) => {
		aDataModal = { url: url };
		modalDetalleContent = ComponentViewPDF;
		mOpenModal = !mOpenModal;
		mTitle = 'Ver pdf';
		mClassModal =
			'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
		mSizeModal = 'xl';
	};

	const action_to_download = async () => {
		let parms = {};
		let res = undefined;
		loading.setLoading(true, 'Cargando, espere por favor...');
		parms['n'] = 'rpt_certificado_horario_examenes';
		parms['vqr'] = eMatricula.id;
		res = await action_print_ireport('pdf', parms);
		if (res !== undefined) {
			if (res.data.es_background) {
				const noti = {
					//toast: true,
					position: 'top-center',
					type: 'info',
					icon: 'info',
					title: res.message,
					showConfirmButton: true
					//timer: 6000
				};
				Swal.fire(noti);
			} else {
				window.open(`${res.data.reportfile}`, '_blank');
			}
		}
		loading.setLoading(false, 'Cargando, espere por favor...');
		return;
	};
</script>

<svelte:head>
	<title>Horario de examen</title>
</svelte:head>

{#if !load}
	<BreadCrumb title="Horario de exámenes" items={itemsBreadCrumb} back={backBreadCrumb} />

	<div class="container-fluid">
		<div class="alert alert-info d-flex align-items-center" role="alert">
			<div>
				<h4 class="alert-heading fw-bold">ACCESO AL EXAMEN</h4>
				Estimado/a estudiante, si no le sale el botón de acceso al examen, debe actualizar la página.
				Recuerde que el botón se habilita 15 minutos antes de la hora programada del inicio al examen
				y finaliza en la hora exacta.
			</div>
		</div>
		{#if eMatriculaSedeExamen}
			{#if validaHorarioExamen()}
				{#if eMatriculaSedeExamen.aceptotermino && eMatriculaSedeExamen.fechaaceptotermino && eMatriculaSedeExamen.urltermino}
					<div class="pb-3 mb-3 d-lg-flex justify-content-start align-items-center">
						<div class="mb-3 mb-lg-0 mx-2">
							<h3 class="mb-0 h4 fw-bold text-primary">
								Aquí podras ver el ACUERDO DE TÉRMINOS Y CONDICIONES PARA RENDIR LOS EXÁMENES
							</h3>
						</div>
						<div class="d-grid gap-2 d-md-flex justify-content-start">
							<a
								class="btn btn-warning btn-sm rounded-pill text-black"
								on:click={() => view_pdf(eMatriculaSedeExamen.urltermino)}
							>
								Documento
								<svg
									xmlns="http://www.w3.org/2000/svg"
									width="16"
									height="16"
									fill="currentColor"
									class="bi bi-filetype-pdf"
									viewBox="0 0 16 16"
								>
									<path
										fill-rule="evenodd"
										d="M14 4.5V14a2 2 0 0 1-2 2h-1v-1h1a1 1 0 0 0 1-1V4.5h-2A1.5 1.5 0 0 1 9.5 3V1H4a1 1 0 0 0-1 1v9H2V2a2 2 0 0 1 2-2h5.5L14 4.5ZM1.6 11.85H0v3.999h.791v-1.342h.803c.287 0 .531-.057.732-.173.203-.117.358-.275.463-.474a1.42 1.42 0 0 0 .161-.677c0-.25-.053-.476-.158-.677a1.176 1.176 0 0 0-.46-.477c-.2-.12-.443-.179-.732-.179Zm.545 1.333a.795.795 0 0 1-.085.38.574.574 0 0 1-.238.241.794.794 0 0 1-.375.082H.788V12.48h.66c.218 0 .389.06.512.181.123.122.185.296.185.522Zm1.217-1.333v3.999h1.46c.401 0 .734-.08.998-.237a1.45 1.45 0 0 0 .595-.689c.13-.3.196-.662.196-1.084 0-.42-.065-.778-.196-1.075a1.426 1.426 0 0 0-.589-.68c-.264-.156-.599-.234-1.005-.234H3.362Zm.791.645h.563c.248 0 .45.05.609.152a.89.89 0 0 1 .354.454c.079.201.118.452.118.753a2.3 2.3 0 0 1-.068.592 1.14 1.14 0 0 1-.196.422.8.8 0 0 1-.334.252 1.298 1.298 0 0 1-.483.082h-.563v-2.707Zm3.743 1.763v1.591h-.79V11.85h2.548v.653H7.896v1.117h1.606v.638H7.896Z"
									/>
								</svg>
							</a>
						</div>
					</div>
					<div class="row">
						<div class="col-lg-12 col-md-12 col-12">
							<div class="border-bottom pb-3 mb-3 d-lg-flex justify-content-end align-items-center">
								<!--<div class="mb-3 mb-lg-0">
									<h1 class="mb-0 h2 fw-bold">Certificado</h1>
								</div>-->
								<div class="d-flex">
									<a
										class="btn btn-info btn-sm rounded-pill text-black"
										href="#certificado-examen"
										on:click|preventDefault={() => action_to_download()}
									>
										Certificado
										<svg
											xmlns="http://www.w3.org/2000/svg"
											width="16"
											height="16"
											fill="currentColor"
											class="bi bi-journal-text"
											viewBox="0 0 16 16"
										>
											<path
												d="M5 10.5a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 0 1h-2a.5.5 0 0 1-.5-.5zm0-2a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5zm0-2a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5zm0-2a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5z"
											/>
											<path
												d="M3 0h10a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2v-1h1v1a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H3a1 1 0 0 0-1 1v1H1V2a2 2 0 0 1 2-2z"
											/>
											<path
												d="M1 5v-.5a.5.5 0 0 1 1 0V5h.5a.5.5 0 0 1 0 1h-2a.5.5 0 0 1 0-1H1zm0 3v-.5a.5.5 0 0 1 1 0V8h.5a.5.5 0 0 1 0 1h-2a.5.5 0 0 1 0-1H1zm0 3v-.5a.5.5 0 0 1 1 0v.5h.5a.5.5 0 0 1 0 1h-2a.5.5 0 0 1 0-1H1z"
											/>
										</svg>
									</a>
								</div>
							</div>
						</div>
					</div>
				{/if}
			{/if}
		{/if}
		{#if eMateriasAsignadas.length > 0}
			<div
				class="row row-cols-1 row-cols-md-2 row-cols-sm-1 row-cols-lg-3 row-cols-xl-3 row-cols-xxl-3 justify-content-center g-4"
			>
				{#each eMateriasAsignadas as eMateriaAsignada}
					<div class="col">
						<div class="card mb-0 mb-xl-0 card-hover border h-100">
							<div class="card-body">
								<h3 class="mb-4 text-center">
									<a href="#!" class="h5 fw-bold">{eMateriaAsignada.materia.asignatura.nombre}</a>
								</h3>
								<div class="mb-0">
									{#if eMateriaAsignada.visiblehorarioexamen}
										<svelte:component
											this={Horarioexamen}
											{eMateriaAsignada}
											{eMatriculaSedeExamen}
										/>
									{/if}
									<!--<div class="mb-3 lh-1">
										<span class="me-1">
											<i class="bi bi-calendar-check" />
										</span>
										<span>Thu, November 10, 2023</span>
									</div>
									<div class="lh-1">
										<span class="me-1">
											<i class="bi bi-clock" />
										</span>
										<span>6:00 PM – 8:00 PM GMT</span>
									</div>-->
								</div>
								<!--<a href="#!" class="btn btn-light-primary text-primary">Register Now</a>-->
							</div>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
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

{#if mOpenModal}
	<svelte:component
		this={modalDetalleContent}
		{mOpenModal}
		{mTitle}
		aData={aDataModal}
		mToggle={mToggleModal}
		on:actionRun={actionRun}
	/>
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
