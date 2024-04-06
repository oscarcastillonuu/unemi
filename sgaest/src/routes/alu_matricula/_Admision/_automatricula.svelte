<script lang="ts">
	import { apiGET, apiPOST, browserGet, logOutUser } from '$lib/utils/requestUtils';
	import { variables } from '$lib/utils/constants';
	import { addToast } from '$lib/store/toastStore';
	import { onDestroy, onMount } from 'svelte';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import ModuleError from '../_Error.svelte';
	import { Button, Icon, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import { loading } from '$lib/store/loadingStore';
	import Swal from 'sweetalert2';
	import { addNotification } from '$lib/store/notificationStore';
	import { goto } from '$app/navigation';
	import { Steps } from 'svelte-steps';
	import InformacionPersonal from './_informacionPersonal.svelte';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import DetalleValores from '$components/Alumno/Matricula/DetalleValores.svelte';
	const DEBUG = import.meta.env.DEV;
	let itemsBreadCrumb = [{ text: 'Matriculación', active: true, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };
	let load = true;
	let Title = 'Automatriculación Online';
	let ePersona = undefined;
	let eInscripcion = undefined;
	let eCarrera = undefined;
	let eMalla = undefined;
	let FichaSocioEconomicaINEC = undefined;
	let ePeriodoMatricula = undefined;
	let ePeriodo = undefined;
	let eInscripcionMalla = undefined;
	let eNivelMalla = undefined;
	let eMatricula = undefined;
	let eMateriasAsignadas = [];
	let perdida_gratuidad = false;
	let valor_pendiente = 0;
	let valor_pagados = 0;
	let mensaje_gratuidad = '';
	let acept_t = false;
	let mSizeConfirmarMatricula = 'lg';
	let mOpenConfirmarMatricula = false;
	let eRazas;
	let ePerfilInscripcion;
	let eDiscapacidades;
	let lEstadosPermanencia;
	let ePaisesResidenciales;
	let eMigrantePersona;
	let eInstitucionDiscapacidades;
	let eNacionalidadIndigenas;
	let eCredos;
	let ePersonaReligion;
	let mOpenModal = false;
	let mTitleModal = '';
	let modalContent;
	let aDataModal = {};
	let es_admision = false;
	const mToggleModal = () => (mOpenModal = !mOpenModal);
	const mToggleConfirmarMatricula = () => (mOpenConfirmarMatricula = !mOpenConfirmarMatricula);
	export let aData;
	let steps = [{ text: 'Información personal y académica' }, { text: 'Aceptación' }];
	let current = 0;
	onMount(async () => {
		if (aData !== undefined) {
			load = false;
			Title = aData.Title;
			ePersona = aData.ePersona;
			eInscripcion = aData.eInscripcion;
			eCarrera = aData.eCarrera;
			eMalla = aData.eMalla;
			FichaSocioEconomicaINEC = aData.FichaSocioEconomicaINEC;
			ePeriodoMatricula = aData.ePeriodoMatricula;
			ePeriodo = ePeriodoMatricula.periodo;
			eInscripcionMalla = aData.eInscripcionMalla;
			eNivelMalla = aData.eNivelMalla;
			eMatricula = aData.eMatricula;
			eMateriasAsignadas = aData.eMateriasAsignadas;
			eRazas = aData.eRazas;
			ePerfilInscripcion = aData.ePerfilInscripcion;
			eDiscapacidades = aData.eDiscapacidades;
			lEstadosPermanencia = aData.lEstadosPermanencia;
			ePaisesResidenciales = aData.ePaisesResidenciales;
			eMigrantePersona = aData.eMigrantePersona;
			eInstitucionDiscapacidades = aData.eInstitucionDiscapacidades;
			eNacionalidadIndigenas = aData.eNacionalidadIndigenas;
			eCredos = aData.eCredos;
			ePersonaReligion = aData.ePersonaReligion;
			valor_pendiente = aData.valor_pendiente;
			es_admision = aData.es_admision;
		}
		load = false;
	});

	const loadAjax = async (data, url) =>
		new Promise(async (resolve, reject) => {
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
		});
	const closeConfirmarMatricula = () => {
		acept_t = false;
		mOpenConfirmarMatricula = false;
	};
	const openConfirmarMatricula = () => {
		loading.setLoading(false, 'Cargando, espere por favor...');
		if (ePeriodoMatricula.valida_terminos) {
			mSizeConfirmarMatricula = 'xl';
		} else {
			mSizeConfirmarMatricula = 'sm';
		}
		mOpenConfirmarMatricula = true;
	};

	const confirmarMatricula = () => {
		const acepto_terminos = acept_t;
		if (!acepto_terminos && ePeriodoMatricula.valida_terminos) {
			addNotification({
				msg: `Para continuar, por favor acepte los términos y condiciones.`,
				type: 'warning',
				target: 'newNotificationToast'
			});
			return false;
		}
		const _acept_t = acepto_terminos ? 1 : 0;
		const mensaje = {
			title: `NOTIFICACIÓN`,
			html: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
				ePersona.nombre_completo
			}, </br><b>¿Está ${ePersona.es_mujer ? 'segura' : 'seguro'} de aceptar la matrícula?</b>`,
			type: 'warning',
			icon: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonColor: 'rgb(25, 135, 84)',
			cancelButtonColor: '#d33',
			confirmButtonText: 'Sí, seguro',
			cancelButtonText: 'No, cancelar'
		};
		Swal.fire(mensaje)
			.then((result) => {
				if (result.value) {
					loading.setLoading(true, 'Cargando, espere por favor...');
					loadAjax(
						{
							action: 'aceptarAutomatricula',
							id: eInscripcion.id,
							termino: _acept_t
						},
						'alumno/matricula/admision'
					)
						.then((response) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							mOpenConfirmarMatricula = false;
							if (response.value.isSuccess) {
								const mensaje = {
									title: `¡MATRICULACIÓN EXITOSA!`,
									html: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
										ePersona.nombre_completo
									}, le informamos que el proceso de aceptación de matrícula ha finalizado.`,
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
											goto('/');
										}
									})
									.catch((error) => {
										loading.setLoading(false, 'Cargando, espere por favor...');
										addNotification({ msg: error.message, type: 'error' });
									});
							} else {
								loading.setLoading(false, 'Cargando, espere por favor...');
								addNotification({ msg: response.value.message, type: 'error' });
							}
						})
						.catch((error) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							addNotification({ msg: error.message, type: 'error' });
						});
				}
			})
			.catch((error) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				addNotification({ msg: error.message, type: 'error' });
			});
	};

	const rechazarMatricula = () => {
		const mensaje = {
			title: `NOTIFICACIÓN`,
			html: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
				ePersona.nombre_completo
			}, con esta acción usted estará liberando un cupo. </br><b>¿Está ${
				ePersona.es_mujer ? 'segura' : 'seguro'
			} de rechazar la matrícula?</b>`,
			type: 'warning',
			icon: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: 'Sí, seguro',
			cancelButtonText: 'No, cancelar'
		};
		Swal.fire(mensaje)
			.then((result) => {
				if (result.value) {
					loading.setLoading(true, 'Cargando, espere por favor...');
					loadAjax(
						{
							action: 'rechazoAutomatricula',
							id: eInscripcion.id
						},
						'alumno/matricula/admision'
					)
						.then((response) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							if (response.value.isSuccess) {
								const mensaje = {
									title: `NOTIFICACIÓN`,
									html: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
										ePersona.nombre_completo
									}, le informamos que el proceso de aceptación de matrícula ha finalizado.`,
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
										}
									})
									.catch((error) => {
										loading.setLoading(false, 'Cargando, espere por favor...');
										addNotification({ msg: error.message, type: 'error' });
									});
							} else {
								loading.setLoading(false, 'Cargando, espere por favor...');
								addNotification({ msg: response.value.message, type: 'error' });
							}
						})
						.catch((error) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							addNotification({ msg: error.message, type: 'error' });
						});
				}
			})
			.catch((error) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				addNotification({ msg: error.message, type: 'error' });
			});
	};

	const nextProccess = (value) => {
		current = value;
	};
	const actionRun = (event) => {
		console.log(event.detail);
		const detail = event.detail;
		const action = detail.action;
		const value = detail.value;
		if (action == 'nextProccess') {
			nextProccess(value);
		}
	};

	const viewDetailRubros = async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const url = `alumno/general/data`;
		const [res, errors] = await apiPOST(fetch, url, {
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
				console.log(res.data);
				aDataModal = res.data;
				modalContent = DetalleValores;
				mOpenModal = !mOpenModal;
				mTitleModal = 'Detalle de valores generados en la matrícula';
			}
		}
	};
</script>

<svelte:head>
	<title>{Title}</title>
</svelte:head>

{#if !load}
	<BreadCrumb title={Title} items={itemsBreadCrumb} back={backBreadCrumb} />
	<div class="bg-default">
		<div class="container">
			<div class="align-items-center justify-content-center g-0 row">
				<div class="col-md-10">
					<div class="align-items-center  row">
						<div class="text-center text-lg-start order-1  col-xl-6 col-lg-7 col-md-12 col-sm-12">
							<div class="py-5 py-lg-0">
								<h2 class="mb-2 display-4 fw-bold mb-3">
									Hola <span class="text-primary">{ePersona.nombre_completo}</span>
								</h2>
								<p class="text-black-50 mb-4 lead">
									La Universidad Estatal de Milagro te da la bienvenida a este nuevo reto ({ePeriodo.display}).
								</p>
								{#if current == 1}
									{#if valor_pendiente > 0}
										<button
											class="btn btn-warning"
											type="button"
											on:click={() => viewDetailRubros()}
											>Detalle de valores generados en la matrícula</button
										>
									{/if}
								{/if}
							</div>
						</div>
						<div
							class="mb-6 mb-lg-0 text-center  col-xl-5 col-lg-5 col-md-12 col-sm-12 offset-xl-1 order-lg-2"
						>
							<img
								src={ePersona.foto_perfil}
								onerror="this.onerror=null;this.src='./image.png'"
								alt=""
								class="img-fluid"
							/>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>

	<div class="row mt-5">
		<div class="col-12">
			<div class="p-3 bg-default">
				<div class="container">
					<div class="align-items-center justify-content-center g-0 row">
						<div class="col-md-12">
							<div class="align-items-center  row">
								<Steps
									{steps}
									{current}
									clickable={false}
									on:click={(e) => {
										console.log(e);
									}}
								/>
								{#if current === 0}
									<svelte:component
										this={InformacionPersonal}
										{ePersona}
										{eRazas}
										{ePerfilInscripcion}
										{eDiscapacidades}
										{lEstadosPermanencia}
										{ePaisesResidenciales}
										{eMigrantePersona}
										{eInstitucionDiscapacidades}
										{eNacionalidadIndigenas}
										{eCredos}
										{ePersonaReligion}
										on:actionRun={actionRun}
									/>
								{:else if current === 1}
									<!-- Table -->
									<div
										class="table table-striped text-nowrap mb-0 table-responsive border-0 overflow-y-hidden table-sm"
									>
										<table class="table mb-0 text-nowrap">
											<thead class="table-light">
												<tr>
													<th class="border-0 text-center" scope="row">#</th>
													<!--<th class="border-0">Carrera</th>-->
													<th class="border-0 text-center">Asignatura</th>
													<th class="border-0 text-center">Nivel</th>
													<th class="border-0 text-center">Paralelo</th>
													<th class="border-0 text-center">Sección</th>
												</tr>
											</thead>
											<tbody>
												{#each eMateriasAsignadas as eMateriaAsignada, i}
													<tr
														class="accordion-toggle collapsed"
														id="accordion1"
														data-bs-toggle="collapse"
														data-bs-parent="#accordion1"
														data-bs-target="#collapseOne"
													>
														<td scope="row" class="align-middle border-top-0 text-center">
															{i + 1}
														</td>
														<!--<td class="align-middle border-top-0">
						{eMateriaAsignada.matricula.inscripcion.carrera.nombre}
					</td>-->
														<td class="align-middle border-top-0">
															{eMateriaAsignada.materia.asignaturamalla.asignatura.nombre}
														</td>
														<td class="align-middle border-top-0 text-center">
															{eMateriaAsignada.materia.asignaturamalla.nivelmalla.nombre}
														</td>
														<td class="align-middle border-top-0 text-center">
															{eMateriaAsignada.materia.paralelomateria.nombre}
														</td>
														<td class="align-middle border-top-0 text-center">
															{eMateriaAsignada.matricula.inscripcion.sesion.nombre}
														</td>
													</tr>
												{/each}
											</tbody>
										</table>
									</div>
								{/if}
							</div>
							<br />
							<br />
							<!-- <div class="card-footer text-muted"> -->
							<div class="d-grid gap-2 d-md-flex justify-content-md-end">
								{#if current == 1}
									<button
										class="btn btn-success"
										type="button"
										on:click={() => openConfirmarMatricula()}>CONFIRMAR MATRÍCULA</button
									>
									<!--<button class="btn btn-danger" type="button" on:click={() => rechazarMatricula()}
										>RECHAZAR MATRÍCULA</button
									>-->
								{/if}
							</div>
							<!-- </div> -->
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
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
			{#if perdida_gratuidad}
				<div class="alert alert-danger" role="alert">
					<p>{@html mensaje_gratuidad}</p>
					<hr />
					<p class="mb-0">
						Una vez confirmada la matriculación, podrá consultar los rubros a pagar a través del
						módulo "Mis Finanzas".
					</p>
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
							<!-- <td style="text-align: center !important; vertical-align: middle; "> -->
							<!--<input name="acept_t" type="checkbox" bind:checked={acept_t} />-->
							<!-- <div class="form-check form-switch">
									<input
										name="acept_t"
										id="acept_t"
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
							</td> -->
							<td style=" vertical-align: middle;">
								<div class="terminos">
									{#if es_admision}
										{@html ePeriodoMatricula.terminos_nivelacion}
									{/if}
								</div>
							</td>
						</tr>
					</tbody>
				</table>
			{/if}
			<div class="row">
				<div class="col-8">
					<p>
						{ePersona.es_mujer ? 'Estimada' : 'Estimado'}
						{ePersona.nombre_completo}, al confirmar usted estará aceptando (<b
							>{eMateriasAsignadas.length}</b
						>) {eMateriasAsignadas.length > 1 ? 'materias' : 'materia'}.
						<!--<b class="fs-5">¿Está {ePersona.es_mujer ? 'segura' : 'seguro'} de aceptar la matrícula?</b>-->
					</p>
				</div>
				<div class="col-4">
					<div class="d-grid gap-2 d-md-flex justify-content-md-end">
						<div class="form-check form-switch text-left">
							<input
								name="acept_t"
								id="acept_t"
								class="form-check-input"
								type="checkbox"
								bind:checked={acept_t}
							/>
							{#if !acept_t}
								<label class="form-check-label text-muted fs-6 fw-bold" for="acept_t"
									>Aceptar términos</label
								>
							{/if}
						</div>
					</div>
				</div>
			</div>
		</ModalBody>
		<ModalFooter>
			<Button color="success" on:click={() => confirmarMatricula()}>Continuar</Button>

			<Button color="danger" on:click={() => closeConfirmarMatricula()}>Cerrar</Button>
		</ModalFooter>
	</Modal>
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
		class="m-0 vh-100 row justify-content-center align-items-center"
		style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 1000; display: flex; flex-direction: column; align-items: center; justify-content: center;"
	>
		<div class="col-auto text-center">
			<Spinner color="dark" type="border" style="width: 3rem; height: 3rem;" />
			<h3>Verificando la información, espere por favor...</h3>
		</div>
	</div>
{/if}
