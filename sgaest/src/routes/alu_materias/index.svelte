<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';

	export const load: Load = async ({ fetch }) => {
		let eMateriasAsignadas = [];
		let eInscripcionencuesta = [];
		let eMatricula = {};
		let es_admision = false;
		let es_pregrado = false;
		let valorGrupo = 0;
		let horassegundos = 0;
		let eMalla = {};
		let ePeriodo = {};
		let coordinacion_detalle = 0;
		let es_graduado = false;
		let fechaactual = new Date();
		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/materias', {});
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
					valorGrupo = res.data['valorGrupo'];
					eMalla = res.data['eMalla'];
					ePeriodo = res.data['ePeriodo'];
					horassegundos = res.data['horassegundos'];
					coordinacion_detalle = res.data['coordinacion_detalles'];
					es_graduado = res.data['es_graduado'];
					fechaactual = new Date(res.data['fecha_actual']);
					eInscripcionencuesta = res.data['eInscripcionencuesta'];
				}
			}
		}

		return {
			props: {
				eMatricula,
				eMateriasAsignadas,
				es_admision,
				es_pregrado,
				valorGrupo,
				eMalla,
				ePeriodo,
				horassegundos,
				coordinacion_detalle,
				es_graduado,
				fechaactual,
				eInscripcionencuesta
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
	import ComponenteCompanero from './_companeros.svelte';
	import ComponenteObservacion from './_observacionmateria.svelte';
	import DetalleValores from '$components/Alumno/Matricula/DetalleValores.svelte';
    import EncuentaGeneral from '$components/Alumno/Encuesta/General.svelte';

	import { loading } from '$lib/store/loadingStore';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { converToDecimal } from '$lib/formats/formatDecimal';
	import { addNotification } from '$lib/store/notificationStore';
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
	export let es_admision;
	export let es_pregrado;
	export let eMateriasAsignadas;
	export let eMalla;
	export let eMatricula;
	export let valorGrupo = 0;
	export let ePeriodo;
	export let horassegundos;
	export let coordinacion_detalle;

	export let fechaactual;

	export let eInscripcionencuesta;


	let dia = fechaactual.getUTCDate();
	let mes = fechaactual.getMonth() + 1; // Agregar 1 porque los meses van del 0 al 11
	let anio = fechaactual.getFullYear();

	let fechaFormateada = `${anio}-${mes < 10 ? '0' + mes : mes}-${dia < 10 ? '0' + dia : dia}`;

    let eQuizzes_to_answer = [];
	let es_seguimiento = false;
	let eQuizzes_answered = [];

    let mOpenModal = false;
	const mToggleModal = () => (mOpenModal = !mOpenModal);
	export let es_graduado;
	let load = true;
	let eMateriaIngles = {};
	let aDataModal = {};
	let modalDetalleContent;
	let mOpenModalGenerico = false;
	let mOpenConfirmarImportarNotasIngles = false;
	let modalTitle = '';
	let contenidoConfirmarImportarNotasIngles = '';
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);
	const mToggleConfirmarImportarNotasIngles = () =>
		(mOpenConfirmarImportarNotasIngles = !mOpenConfirmarImportarNotasIngles);

	let itemsBreadCrumb = [{ text: 'Mis Materias', active: true, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {
		if (eMatricula != undefined) {
			load = false;
		}
	});

	const loadAjax = async (data, url, method = undefined) =>
		new Promise(async (resolve, reject) => {
			if (method === undefined) {
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
			} else {
				const [res, errors] = await apiGET(fetch, url, data);
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
			}
		});

	const loadInitial = () =>
		new Promise((resolve, reject) => {
			loadAjax({}, 'alumno/materias', 'GET')
				.then((response) => {
					if (response.value.isSuccess) {
						eMateriasAsignadas = response.value.data['eMateriasAsignadas'];
						eMatricula = response.value.data['eMatricula'];
						es_admision = response.value.data['es_admision'];
						es_pregrado = response.value.data['es_pregrado'];
						valorGrupo = response.value.data['valorGrupo'];
						eMalla = response.value.data['eMalla'];
						ePeriodo = response.value.data['ePeriodo'];
						horassegundos = response.value.data['horassegundos'];
						eInscripcionencuesta = response.value.data['eInscripcionencuesta'];

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

	const toggleModalDetalleCompaneros = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/materias', {
			action: 'listarCompanerios',
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
				modalDetalleContent = ComponenteCompanero;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'Mis compañeros de clase';
			}
		}
	};
	const toggleModalObservacionesMateria = async (observacion, nombremateria) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		observacion = observacion;
		let data={
			observacion: observacion,
			nombremateria: nombremateria,
		}
		loading.setLoading(false, 'Cargando, espere por favor...');
		
		aDataModal = {
			observacion: observacion,
			nombremateria: nombremateria,
		};
		modalDetalleContent = ComponenteObservacion;
		mOpenModalGenerico = !mOpenModalGenerico;
		modalTitle = 'Observacion Materia';
		
	};

	const toggleModalDetalleValores = async () => {
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
				aDataModal = res.data;
				modalDetalleContent = DetalleValores;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'Detalle de los valores generados en la matriculación';
			}
		}
	};
	const importarNotaIngles = async (_eMateriaIngles) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/materias', {
			action: 'preLoadImportarNotaIngles',
			id: _eMateriaIngles.id
		});
		loading.setLoading(false, 'Cargando, espere por favor...');
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			return {
				status: 302,
				redirect: '/'
			};
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				if (!res.module_access) {
					goto('/');
				}
			} else {
				contenidoConfirmarImportarNotasIngles = res.data.html;
				mOpenConfirmarImportarNotasIngles = true;
				eMateriaIngles = _eMateriaIngles;
			}
		}
	};
	const ActualizarMoodle = async (id, nombre) => {
		const mensaje = {
			title: `NOTIFICACIÓN`,
			html: `¿Está seguro(a) que desea actualizar su curso de moodle en: ${nombre}?`,
			type: 'info',
			icon: 'info',
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
					loading.setLoading(true, 'Cargando, espere por favor...');
					loadAjax(
						{
							action: 'actualizar_un_estudiante_moodle',
							id: id,
							idmatri: eMatricula.id
						},
						'alumno/materias'
					)
						.then((response) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							if (response.value.isSuccess) {
								loadInitial();

								addNotification({
									msg: 'Se ha matriculado al curso de ' + nombre + ' correctamente.',
									type: 'info'
								});
							} else {
								addNotification({
									msg: response.value.message,
									type: 'warning'
								});
							}
						})
						.catch((error) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							addNotification({
								msg: error.message,
								type: 'warning'
							});
						});
				} else {
					addNotification({
						msg: 'Se canceló.',
						type: 'warning'
					});
				}
			})
			.catch((error) => {
				addNotification({
					msg: error.message,
					type: 'error'
				});
			});
	};

	const confirmarAutomatricula = async (id) => {
		const mensaje = {
			title: `NOTIFICACIÓN`,
			text: `¿Esta ${
				eMatricula.inscripcion.persona.es_mujer ? 'segura' : 'seguro'
			} que desea confirmar el acceso al módulo de inglés?`,
			type: 'info',
			icon: 'info',
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
					loading.setLoading(true, 'Cargando, espere por favor...');
					loadAjax(
						{
							action: 'confirmarAutomatriculaMateriaAsignada',
							id: id
						},
						'alumno/materias'
					)
						.then((response) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							if (response.value.isSuccess) {
								window.open(response.value.data.url, '_blank');
								document.getElementById(`btnConfirmarAutomatricula${id}`).style.display = 'none'; // hide
							} else {
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
					addNotification({
						msg: 'Se canceló.',
						type: 'info'
					});
				}
			})
			.catch((error) => {
				addNotification({
					msg: error.message,
					type: 'error'
				});
			});
	};

	const confirmarImportacionNotasIngles = async () => {
		let _eMateriaIngles = eMateriaIngles;
		eMateriaIngles = {};
		const mensaje = {
			title: `NOTIFICACIÓN`,
			html: `¿Esta ${
				eMatricula.inscripcion.persona.es_mujer ? 'segura' : 'seguro'
			} que desea importar la nota del módulo de inglés? </br> Recuerde que al aceptar la importación de la nota del examen, está confirmando que esa calificación será la definitiva para aprobar o reprobar el módulo.`,
			type: 'info',
			icon: 'info',
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
					loading.setLoading(true, 'Cargando, espere por favor...');
					loadAjax(
						{
							action: 'confirmarImportarNotaIngles',
							id: _eMateriaIngles.id
						},
						'alumno/materias'
					)
						.then((response) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							if (response.value.isSuccess) {
								//document.getElementById(`btnConfirmarAutomatricula${id}`).style.display = 'none'; // hide
								// console.log(reresponse.values.data);
								eMateriasAsignadas = response.value.data['eMateriasAsignadas'];
								eMatricula = response.value.data['eMatricula'];
								horassegundos = response.value.data['horassegundos'];
								mOpenConfirmarImportarNotasIngles = false;
							} else {
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
					addNotification({
						msg: 'Se canceló.',
						type: 'info'
					});
				}
			})
			.catch((error) => {
				addNotification({
					msg: error.message,
					type: 'error'
				});
			});
	};

    const llamarmodalencuesta = async (id, nombreMateria) => {
        loading.setLoading(true, 'Cargando encuesta, espere por favor...');
        const [res, errors] = await apiGET(fetch, 'alumno/materias/get/quizzes', {
            action: 'traerEncuesta',
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
                let aux = res.data;
                eQuizzes_to_answer = aux['eQuizzes_to_answer']
                loading.setLoading(true, 'Cargando, espere por favor...');
                const eQuiz = eQuizzes_to_answer[0];
                if (eQuiz){
                     // aDataModal = eQuiz;
					aDataModal = { eQuiz: eQuiz, idMat: id, nombreMateria:nombreMateria };
                    mOpenModal = !mOpenModal;
					es_seguimiento = true;
                }
                loading.setLoading(false, 'Cargando, espere por favor...');
            }
        }
    };

	// $: {
	// 	//console.log(id_periodo);
	// 	//console.log(id_inscripcion);
	// }
</script>

<svelte:head>
	<title>Mis Materias</title>
</svelte:head>
<BreadCrumb title="Mis Materias" items={itemsBreadCrumb} back={backBreadCrumb} />
{#if !load}
	<div class="row">
		<div class="container">
			{#if !es_admision}
				<button
					class="btn btn-dark"
					type="button"
					data-bs-toggle="offcanvas"
					data-bs-target="#offcanvasWithBothOptions"
					aria-controls="offcanvasWithBothOptions">Información de la Carrera</button
				>
			{/if}
			{#if eMatricula.tiene_deuda}
				{#if coordinacion_detalle}
					{#if coordinacion_detalle < 6}
						{#if !es_admision || eMatricula.total_pagado_rubro > 0 || eMatricula.total_saldo_rubro > 0}
							<button
								class="btn btn-warning"
								type="button"
								on:click={() => toggleModalDetalleValores()}
								>Detalle de los valores generados en la matriculación</button
							>
						{/if}
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
		<div class="col-lg-12 col-xm-12 col-md-12">
			<br />
			<div class="card">
				<div class="card-header text-center">
					<h4 class="mb-0 display-6">Asignaturas de la matrícula</h4>
				</div>
				<div class="card-header text-left">
					{#if eMatricula.gruposocioeconomico}
						<h3>
							Nivel Socioeconómico: <span class="badge bg-success"
								>{eMatricula.gruposocioeconomico.nombre}</span
							>
							{#if eMatricula.tiene_deuda}
								<!--{#if valorGrupo}
									<span class="badge bg-warning"> VALOR GRUPO SOCIOECONÓMICO: {valorGrupo} </span>
								{/if}-->
							{/if}
						</h3>
					{/if}
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

				<div class="card-body">
					<div class="table-responsive">
						<table class="table table-sm mb-0 text-nowrap table-border table-hover">
							<thead class="table-light">
								<tr>
									<th
										scope="col"
										class="border-top-0 text-center align-middle "
										style="width: 22rem;">Asignatura</th
									>
									<th
										scope="col"
										class="border-top-0 text-center align-middle "
										style="width: 15rem;">Profesor</th
									>
									<th
										scope="col"
										class="border-top-0 text-center align-middle "
										style="width: 15rem;">Notas</th
									>
									<th scope="col" class="border-top-0 text-center align-middle ">Nota Final</th>
									<th scope="col" class="border-top-0 text-center align-middle ">Asist.</th>
									{#if !es_admision}
										<th scope="col" class="border-top-0 text-center align-middle ">Estado</th>
										<th scope="col" class="border-top-0 text-center align-middle ">Comp.</th>
									{/if}
									<th scope="col" class="border-top-0 text-center align-middle ">Acceso.</th>
								</tr>
							</thead>
							<tbody>
								{#if eMateriasAsignadas.length > 0}
									{#each eMateriasAsignadas as eMateriaAsignada}
										<tr>
											<td class="fs-6 align-middle border-top-0 text-wrap" style="width: 22rem;">
												{eMateriaAsignada.materia.nombre_mostrar}
												<br />
												{eMateriaAsignada.materia.inicio} - {eMateriaAsignada.materia.fin}

												{#if eMateriaAsignada.retirado}
													<br /><span class="badge bg-warning"> RETIRADO</span>
												{/if}

												<br />
												{#if eMateriaAsignada.materia.tipomateria === 3}
													<span class="badge bg-info s-f1DUnQdVr54d"> Materia Mooc </span>
												{/if}
												{#if eMateriaAsignada.actacompromisopracticas }
													<a href="{eMateriaAsignada.url_actacompromiso}" class="text-dark fw-bold lh-1" target="_blank"><i class="bi bi-file-pdf text-danger"></i> Acta de compromiso</a>
												{/if}
											</td>
											<td
												class="fs-6 align-middle border-top-0 text-center text-wrap"
												style="width: 15rem;"
											>
												{#if ePeriodo.idm == 112}
													<br />
													Profesor: {eMateriaAsignada.materia.profesor}
												{:else if eMateriaAsignada.materia.profesor}
													<div class="avatar avatar-md ">
														{#if eMateriaAsignada.materia.profesor.persona.foto_perfil}
															<img
																alt={eMateriaAsignada.materia.profesor.persona.nombre_completo}
																onerror="this.onerror=null;this.src='./image.png'"
																src={eMateriaAsignada.materia.profesor.persona.foto_perfil}
																class="rounded-circle"
															/>
														{:else}
															<img
																alt={eMateriaAsignada.materia.profesor.persona.nombre_completo}
																onerror="this.onerror=null;this.src='./image.png'"
																src="./images/iconos/profesor_small.png"
																class="rounded-circle"
															/>
														{/if}
													</div>

													<br />
													{eMateriaAsignada.materia.profesor.persona.nombre_completo}
												{/if}
											</td>
											<td
												class="fs-6 align-middle border-top-0 text-wrap text-center"
												style="width: 15rem;"
											>
												{#if eMatricula.tiene_deuda && es_admision}
													<button
														type="button"
														class="btn btn-danger btn-sm p-0"
														id="Tooltip_notas_id_{eMatricula.id}"><Icon name="info" /></button
													>
													<Tooltip target="Tooltip_notas_id_{eMatricula.id}" placement="top"
														>Estimado/a aspirante, aun le quedan VALORES PENDIENTES POR PAGAR</Tooltip
													>
												{:else if !ePeriodo.ocultarnota && !eMatricula.pasoayuda}
													{#if !eMatricula.bloqueomatricula}
														{#if eInscripcionencuesta.length > 0}
															{#each eInscripcionencuesta as eInscripcionencu}
																{#if eInscripcionencu.materia.id == eMateriaAsignada.materia.id}
																	{#if eInscripcionencu.respondio }
																		<table class="table mb-0 table-hover">
																			<tr>
																				{#each eMateriaAsignada.materia.modeloevaluativo.campos as campo}
																					<td style="text-align: center; vertical-align: middle;">
																						<p class="tl" title=""><b>{campo.nombre}</b></p>
																					</td>
																				{/each}

																				<td />
																			</tr>
																			<tr>
																				{#each eMateriaAsignada.materia.modeloevaluativo.campos as campo}
																					{#each eMateriaAsignada.evaluaciong as eg}
																						{#if campo.nombre === eg.detallemodeloevaluativo.nombre}
																							<td
																								style="text-align: center; width: 40px; vertical-align: middle;"
																							>
																								{converToDecimal(eg.valor, campo.decimales)}
																							</td>
																						{/if}
																					{/each}
																				{/each}
																				<td />
																			</tr>
																		</table>
																	{/if}
																{/if}
															{/each}
															{#if eMateriaAsignada.materia.tipomateria == 3 || !es_pregrado || eMateriaAsignada.materia.inglesepunemi}
															<table class="table mb-0 table-hover">
																<tr>
																	{#each eMateriaAsignada.materia.modeloevaluativo.campos as campo}
																		<td style="text-align: center; vertical-align: middle;">
																			<p class="tl" title=""><b>{campo.nombre}</b></p>
																		</td>
																	{/each}

																	<td />
																</tr>
																<tr>
																	{#each eMateriaAsignada.materia.modeloevaluativo.campos as campo}
																		{#each eMateriaAsignada.evaluaciong as eg}
																			{#if campo.nombre === eg.detallemodeloevaluativo.nombre}
																				<td
																					style="text-align: center; width: 40px; vertical-align: middle;"
																				>
																					{converToDecimal(eg.valor, campo.decimales)}
																				</td>
																			{/if}
																		{/each}
																	{/each}
																	<td />
																</tr>
															</table>
														{/if}
														{:else}
															<table class="table mb-0 table-hover">
																<tr>
																	{#each eMateriaAsignada.materia.modeloevaluativo.campos as campo}
																		<td style="text-align: center; vertical-align: middle;">
																			<p class="tl" title=""><b>{campo.nombre}</b>
																			</p>
																		</td>
																	{/each}

																	<td/>
																</tr>
																<tr>
																	{#each eMateriaAsignada.materia.modeloevaluativo.campos as campo}
																		{#each eMateriaAsignada.evaluaciong as eg}
																			{#if campo.nombre === eg.detallemodeloevaluativo.nombre}
																				<td
																						style="text-align: center; width: 40px; vertical-align: middle;"
																				>
																					{converToDecimal(eg.valor, campo.decimales)}
																				</td>
																			{/if}
																		{/each}
																	{/each}
																	<td/>
																</tr>
																
															</table>
															{#if eMateriaAsignada.observaciones && es_admision}
																<table class="table mb-0 table-hover">
																	<tr>
																		<td style="text-align: justify;">
																			<br>
																			<div id="observaciones">
																				<i>
																					{@html eMateriaAsignada.observaciones}
																				</i>
																			</div>
																																					
																		</td>
																	</tr>
																</table>
															{/if}
														{/if}
													{/if}
												{/if}
											</td>
											<td class="fs-6 align-middle border-top-0 text-center">
												{#if eMatricula.tiene_deuda && es_admision}
													<button
														type="button"
														class="btn btn-danger btn-sm  p-0"
														id="Tooltip_nota_final_id_{eMatricula.id}"><Icon name="info" /></button
													>
													<Tooltip target="Tooltip_nota_final_id_{eMatricula.id}" placement="top"
														>Estimado/a aspirante, aun le quedan VALORES PENDIENTES POR PAGAR</Tooltip
													>

												{:else if !ePeriodo.ocultarnota}
													{#if !eMatricula.bloqueomatricula}
														{#if eInscripcionencuesta.length > 0}
															{#each eInscripcionencuesta as eInscripcionencu}
																{#if eInscripcionencu.materia.id == eMateriaAsignada.materia.id}
																	{#if eInscripcionencu.respondio}
																		{converToDecimal(eMateriaAsignada.notafinal, 1)}
																	{/if}
																{/if}
															{/each}
															{#if eMateriaAsignada.materia.tipomateria == 3 || !es_pregrado || eMateriaAsignada.materia.inglesepunemi}
																{converToDecimal(eMateriaAsignada.notafinal, 1)}
															{/if}
														{:else}
															{converToDecimal(eMateriaAsignada.notafinal, 1)}
														{/if}
													{/if}
												{/if}
												<div>
													{#if eMateriaAsignada.observaciones && es_admision}
														<a
														class="btn btn-danger btn-xs "
																on:click={() => toggleModalObservacionesMateria(eMateriaAsignada.observaciones, eMateriaAsignada.materia.asignatura.nombre)}
															>
																Obs.														
														</a>														
													{/if}

												</div>
											</td>
											<td class="fs-6 align-middle border-top-0 text-center">
												{#if eMatricula.tiene_deuda && es_admision}
													<button
														type="button"
														class="btn btn-danger btn-sm  p-0"
														id="Tooltip_asistencia_id_{eMatricula.id}"><Icon name="info" /></button
													>
													<Tooltip target="Tooltip_asistencia_id_{eMatricula.id}" placement="top"
														>Estimado/a aspirante, aun le quedan VALORES PENDIENTES POR PAGAR</Tooltip
													>
												{:else if !eMateriaAsignada.homologa && !eMateriaAsignada.convalidada}
													{#if !eMatricula.bloqueomatricula}
														<span><b>{eMateriaAsignada.asistenciafinal}%</b></span>
														<br />
														<span class="smaller"
															>({eMateriaAsignada.asistencia_real} de {eMateriaAsignada.asistencia_plan})</span
														>
													{/if}
												{/if}
											</td>
											{#if !es_admision}
												<td class="fs-6 align-middle border-top-0 text-center">
													{#if eInscripcionencuesta.length > 0}
														{#each eInscripcionencuesta as eInscripcionencu}
															{#if eInscripcionencu.materia.id == eMateriaAsignada.materia.id}
																{#if eInscripcionencu.respondio}
																	{#if !eMateriaAsignada.homologa && !eMateriaAsignada.convalidada}
																		{#if eMateriaAsignada.retirado}
																			<span class="badge bg-warning"> RETIRADO</span>
																		{:else if eMateriaAsignada.estado.idm == 1}
																			<span class="badge bg-success">
																				{eMateriaAsignada.estado.display}
																			</span>
																		{:else if eMateriaAsignada.estado.idm == 2}
																			<span class="badge bg-danger">
																				{eMateriaAsignada.estado.display}
																			</span>
																		{:else}
																			<span class="badge bg-warning">
																				{eMateriaAsignada.estado.display}
																			</span>
																		{/if}
																	{:else}
																		<span class="badge bg-success"> HOMOLOGADA</span>
																	{/if}
																{/if}
															{/if}
														{/each}
														{#if eMateriaAsignada.materia.tipomateria == 3 || !es_pregrado || eMateriaAsignada.materia.inglesepunemi}
															{#if !eMateriaAsignada.homologa && !eMateriaAsignada.convalidada}
																{#if eMateriaAsignada.retirado}
																	<span class="badge bg-warning"> RETIRADO</span>
																{:else if eMateriaAsignada.estado.idm == 1}
																	<span class="badge bg-success">
																		{eMateriaAsignada.estado.display}
																	</span>
																{:else if eMateriaAsignada.estado.idm == 2}
																	<span class="badge bg-danger">
																		{eMateriaAsignada.estado.display}
																	</span>
																{:else}
																	<span class="badge bg-warning">
																		{eMateriaAsignada.estado.display}
																	</span>
																{/if}
															{:else}
																<span class="badge bg-success"> HOMOLOGADA</span>
															{/if}
														{/if}
													{:else}
														{#if !eMateriaAsignada.homologa && !eMateriaAsignada.convalidada}
															{#if eMateriaAsignada.retirado}
																<span class="badge bg-warning"> RETIRADO</span>
															{:else if eMateriaAsignada.estado.idm == 1}
																	<span class="badge bg-success">
																		{eMateriaAsignada.estado.display}
																	</span>
															{:else if eMateriaAsignada.estado.idm == 2}
																	<span class="badge bg-danger">
																		{eMateriaAsignada.estado.display}
																	</span>
															{:else}
																	<span class="badge bg-warning">
																		{eMateriaAsignada.estado.display}
																	</span>
															{/if}
														{:else}
															<span class="badge bg-success"> HOMOLOGADA</span>
														{/if}
													{/if}
												</td>
												<td class="fs-6 align-middle border-top-0 text-center">
													<a
														style="text-align: center; width: 150px; vertical-align: middle;"
														on:click={() => toggleModalDetalleCompaneros(eMateriaAsignada.id)}
													>
														<img
															style="width: 35px;"
															src="{variables.BASE_API_STATIC}/images/iconos/friends.png"
														/>
													</a>
												</td>
											{/if}
											<td class="fs-6 align-middle border-top-0 text-center">
												<div class="btn-group-vertical text-center align-items-center">
													{#if eMatricula.tiene_deuda && es_admision}
														<button
															type="button"
															class="btn btn-danger btn-sm mb-2  p-0"
															id="Tooltip_acceso_id_{eMatricula.id}"><Icon name="info" /></button
														>
														<Tooltip target="Tooltip_acceso_id_{eMatricula.id}" placement="top"
															>Estimado/a aspirante, aun le quedan VALORES PENDIENTES POR PAGAR</Tooltip
														>
													{:else if eMateriaAsignada.materia.idcursomoodle}
														{#if !eMateriaAsignada.es_modulo_ingles}
															<center>
																{#if es_admision}
																	<a
																		href="{ePeriodo.urlmoodle2}/course/view.php?id={eMateriaAsignada
																			.materia.idcursomoodle}"
																		class="btn btn-secondary btn-sm mb-2"
																		target="_blank"
																		><span class="fe fe-link" /> Ir al curso de moodle</a
																	>
																{:else}
																	<a
																		href="{ePeriodo.urlmoodle}/course/view.php?id={eMateriaAsignada
																			.materia.idcursomoodle}"
																		class="btn btn-secondary btn-sm mb-2"
																		target="_blank"
																		><span class="fe fe-link" /> Ir al curso de moodle</a
																	>
																{/if}
															</center>
														{/if}
														{#if eMateriaAsignada.es_modulo_ingles}
															<center>
																<a
																	href="https://upei.buckcenter.edu.ec/my/"
																	class="btn btn-secondary btn-sm mb-2"
																	target="_blank"
																	><span class="fe fe-link" /> Ir al curso de moodle</a
																>
															</center>
														{/if}
													{/if}

													{#if !es_admision}
														<!-- {#if !eMatricula.bloqueomatricula}
															{#if eMateriaAsignada.materia.idcursomoodle > 0}
																{#if coordinacion_detalle < 6}
																	{#if es_graduado == false}
																		<button
																			type="button"
																			class="btn btn-warning btn-sm mb-2"
																			id="btnImportarNota{eMateriaAsignada.id}"
																			on:click={() =>
																				ActualizarMoodle(
																					eMateriaAsignada.materia.id,
																					eMateriaAsignada.materia.asignatura.nombre
																				)}
																			><i class="bi bi-mortarboard-fill" /> Matricularme en la asignatura
																			de moodle</button
																		>
																	{/if}
																{/if}
															{/if}
														{/if} -->

														{#if eMateriaAsignada.materia.silabo}
															{#if eMateriaAsignada.materia.silabo.codigoqr}
																<a
																	target="_blank"
																	class="btn btn-success btn-sm mb-2"
																	href="{variables.BASE_API}/media/qrcode/silabodocente/qr_silabo_{eMateriaAsignada
																		.materia.silabo.id}.pdf?v={horassegundos}"
																	><i class="fa fa-qrcode" /> Sílabo digital QR</a
																>
															{:else}
																<center>
																	<span class="badge bg-warning text-dark">Sin Sílabo Aprobado</span
																	>
																</center>
															{/if}
														{/if}
														{#each eInscripcionencuesta as eInscripcionencu}
															{#if eMateriaAsignada.materia.fechainicioencuesta && eMateriaAsignada.materia.fechafinencuesta}
																{#if (new Date(eMateriaAsignada.materia.fechainicioencuesta) <= fechaactual && new Date(eMateriaAsignada.materia.fechafinencuesta) >= fechaactual) && eMateriaAsignada.materia.encuestaactiva}

																	{#if eMateriaAsignada.materia.tipoprofesor }
																		{#if (eMateriaAsignada.materia.tipoprofesor.includes(1) || eMateriaAsignada.materia.tipoprofesor.includes(14)) && eMateriaAsignada.materia.tipomateria != 3 }
																			{#if eInscripcionencu.materia.id == eMateriaAsignada.materia.id}
																				{#if !eInscripcionencu.respondio }
																					<button
																						on:click={() => llamarmodalencuesta(eMateriaAsignada.materia.id,eMateriaAsignada.materia.asignatura.nombre)}
																						class="btn btn-warning btn-sm mb-2"
																					><i class="fe fe-file-text"/> Realizar encuesta del sílabo</button
																					>
																				{/if}
																			{/if}
																		{/if}
																	{/if}
																{/if}
															{/if}
														{/each}
														<!-- {#if !eMateriaAsignada.automatricula}
															<br />
															<button
																type="button"
																class="btn btn-warning btn-sm mb-2"
																id="btnConfirmarAutomatricula{eMateriaAsignada.id}"
																on:click={() => confirmarAutomatricula(eMateriaAsignada.id)}
																>CONFIRMAR ACCESO AL MÓDULO</button
															>
														{:else if eMateriaAsignada.es_modulo_ingles && !eMateriaAsignada.importa_nota}
															<br />
															<button
																type="button"
																class="btn btn-warning btn-sm mb-2"
																id="btnImportarNota{eMateriaAsignada.id}"
																on:click={() => importarNotaIngles(eMateriaAsignada)}
																>IMPORTAR NOTA DE EXAMEN</button
															>
														{/if} -->
													{/if}
												</div>
											</td>
										</tr>
									{/each}
								{:else}
									<tr>
										<td colspan="8" class="text-center">NO EXISTE MATERIAS DISPONIBLES</td>
									</tr>
								{/if}
							</tbody>
						</table>
					</div>
				</div>
			</div>
		</div>
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
	<EncuentaGeneral mToggle={mToggleModal} mOpen={mOpenModal} aData={aDataModal} es_seguimiento={es_seguimiento} size="xl" />
{/if}
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

<Modal
	isOpen={mOpenConfirmarImportarNotasIngles}
	toggle={mToggleConfirmarImportarNotasIngles}
	size="xl"
	class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
	backdrop="static"
>
	<ModalHeader toggle={mToggleConfirmarImportarNotasIngles}>
		<h4>
			<span>Aceptación de nota de examen</span>
		</h4>
	</ModalHeader>
	<ModalBody>
		<div
			class="row row-cols-1 row-cols-sm-1 row-cols-md-2 row-cols-lg-2 row-cols-xl-2 row-cols-xxl-3 text-center"
		>
			{@html contenidoConfirmarImportarNotasIngles}
		</div>
	</ModalBody>
	<ModalFooter>
		<Button color="success" on:click={() => confirmarImportacionNotasIngles()}
			>Continuar con importación</Button
		>
		<Button color="primary" on:click={mToggleConfirmarImportarNotasIngles}>Cerrar</Button>
	</ModalFooter>
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
