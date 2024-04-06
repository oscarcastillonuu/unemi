<script context="module" lang="ts">
	import type { Load } from '@sveltejs/kit';

	export const load: Load = async ({ fetch }) => {
		let eSolicitudes = [];
		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/tutoria_academica', {
				action: 'loadSolicitudes'
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
					eSolicitudes = await res.data['eSolicitudes'];
				}
			}
		}

		return {
			props: {
				eSolicitudes
			}
		};
	};
</script>

<script lang="ts">
	import { onMount } from 'svelte';
	import { browserGet, apiGET, apiPOST, logOutUser } from '$lib/utils/requestUtils';
	import { loading } from '$lib/store/loadingStore';
	import { navigating } from '$app/stores';
	import { Spinner } from 'sveltestrap';
	import { addToast } from '$lib/store/toastStore';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import ComponentFormularioIndividual from './_forms/frmIndividual.svelte';
	import ComponentFormularioGrupal from './_forms/frmGrupal.svelte';
	import ComponentFormularioEncuesta from './_forms/frmEncuesta.svelte';
	import { goto } from '$app/navigation';
	import Swal from 'sweetalert2';
	export let eSolicitudes;
	import { variables } from "$lib/utils/constants";
	let load = true;
	let mOpenModal = false;
	let mTitleModal;
	let mClassModal =
		'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
	let mSizeModal = 'lg';
	const mToggleModal = () => (mOpenModal = !mOpenModal);
	let modalDetalleContent;
	let aDataModal;
	let inputTextSearch = '';
	//console.log($navigating);
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	let itemsBreadCrumb = [{ text: 'Tutorías académicas', active: true, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };

	onMount(async () => {
		if (eSolicitudes) {
			load = false;
		}
		//console.log(clasificacion);
	});

	const actionRun = async (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (['saveSolicitudTutoriaIndividual', 'saveEncuesta'].includes(action)) {
			mOpenModal = !mOpenModal;
			eSolicitudes = await loadSolicitudes('');
		}
	};

	const loadSolicitudes = async (filterText: string) => {
		return new Promise(async (resolve, reject) => {
			loading.setLoading(true, 'Consultado la información, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/tutoria_academica', {
				action: 'loadSolicitudes',
				search: filterText
			});
			if (errors.length > 0) {
				loading.setLoading(false, 'Consultado la información, espere por favor...');
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				reject([]);
			} else {
				if (!res.isSuccess) {
					loading.setLoading(false, 'Consultado la información, espere por favor...');
					addToast({ type: 'error', header: '¡ERROR!', body: res.message });
					if (!res.module_access) {
						goto('/');
					}
					reject([]);
				} else {
					let results = res.data.eSolicitudes;
					loading.setLoading(false, 'Consultado la información, espere por favor...');
					resolve(results);
				}
			}
		});
	};

	const openModal = (componente, eSolicitud, title, size) => {
		modalDetalleContent = componente;
		mOpenModal = !mOpenModal;
		mTitleModal = title;
		aDataModal = { eSolicitud: eSolicitud };
		mClassModal =
			'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
		mSizeModal = size;
	};

	const submitSearchSolicitudes = async () => {
		//console.log(inputTextSearch);
		eSolicitudes = await loadSolicitudes(inputTextSearch);
	};

	const resetSearchSolicitudes = async () => {
		inputTextSearch = '';
		eSolicitudes = await loadSolicitudes(inputTextSearch);
	};

	const openTutoria = async (eSolicitud) => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/tutoria_academica', {
			action: 'saveClaseTutoria',
			id: eSolicitud.pk
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
					body: 'Se guardo correctamente la asistencia'
				});
				eSolicitudes = await loadSolicitudes('');
				var a = document.createElement('a');
				a.target = '_blank';
				a.href = eSolicitud.profesor.urlzoom;
				a.click();
			}
		}
	};

	const eliminarRegistro = (body, pk, action) => {
		const mensaje = {
			title: `<p style='color:#FE9900;'><b>Acción irreversible</b></p>`,
			//html: `<p style='color:#ACAEAF;'>¿Desea eliminar familiar ${ePersonaDatosFamiliar.nombre}</p>`,
			html: body,
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
		Swal.fire({ ...mensaje }).then(async (result) => {
			if (result.value) {
				loading.setLoading(true, 'Cargando, espere por favor...');
				const [res, errors] = await apiPOST(fetch, 'alumno/tutoria_academica', {
					action: action,
					id: pk
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
							header: '¡Exitoso!',
							body: res.message
						});
						eSolicitudes = await loadSolicitudes('');
					}
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
			}
		});
	};

	const rangeInteger = (start, end, step = 1) => {
		const result = [];
		for (let i = start; i <= end; i += step) {
			result.push(i);
		}
		return result;
	};
</script>

<svelte:head>
	<title>Tutorías académicas</title>
</svelte:head>
{#if !load}
	<BreadCrumb
		title="Consultas al tutor de mis materias"
		items={itemsBreadCrumb}
		back={backBreadCrumb}
	/>
	<div class="container-fluid px-2">
		<div class="row row-cols-1 row-cols-sm-2 row-cols-md-2 mb-3 g-1">
			<div class="col">
				<button
					type="button"
					class="btn btn-info btn-sm"
					on:click={() =>
						openModal(
							ComponentFormularioIndividual,
							undefined,
							'Adicionar solicitud de tutoria individual',
							'md'
						)}><span class="fe fe-plus" /> Adicionar solicitud individual</button
				>

				<button
					type="button"
					class="btn btn-primary btn-sm"
					on:click={() =>
						openModal(
							ComponentFormularioGrupal,
							undefined,
							'Adicionar solicitud de tutoria grupal',
							'xl'
						)}><span class="fe fe-users" /> Adicionar solicitud grupal</button
				>
			</div>
			<div class="col">
				<form class="form-search" on:submit|preventDefault={submitSearchSolicitudes}>
					<div class="input-group">
						<input
							type="text"
							class="form-control form-control-sm"
							placeholder="Buscar..."
							aria-label="Buscar..."
							bind:value={inputTextSearch}
							aria-describedby="search"
						/>
						<button type="submit" class="btn btn-outline-secondary btn-sm" id="search"
							><i class="fe fe-search " /></button
						>
						<button
							type="button"
							on:click={resetSearchSolicitudes}
							class="btn btn-outline-primary btn-sm"><i class="fe fe-refresh-ccw " /></button
						>
					</div>
				</form>
			</div>
		</div>
		<div class="row mb-3 g-1">
			<div class="pt-2">
				<div class="alert alert-info"><h4 class="alert-heading">Asistencia de tutorias:</h4>
					La opción "<b>Ingresar a la tutoría</b>" estará disponible 30 minutos antes del horario programado en el día establecido por el docente </div>
			</div>
		</div>
		<div class="card ">
			<div class="card-body border-top border-6 rounded-3 border-dark-info">
				<div class="table-responsive scrollbar">
					<table class="table table_primary tabla_responsive">
						<thead class="table-light">
							<tr>
								<th class="text-center align-middle p-1" style="width: 30%;">Solicitud</th>
								<th class="text-center align-middle p-1" style="width: 15%;">Fechas</th>
								<th class="text-center align-middle p-1" style="width: 15%;">Horario</th>
								<th class="text-center align-middle p-1" style="width: 20%;">Estado</th>
								<th class="text-center align-middle p-1" style="width: 15%;">Detalle final</th>
								<th class="text-center align-middle p-1" style="width: 5%;"
									><i class="fe fe-settings" /></th
								>
							</tr>
						</thead>
						<tbody>
							{#if eSolicitudes.length > 0}
								{#each eSolicitudes as eSolicitud}
									<tr>
										<td>
											<p class="m-0 p-0 fs-6">
												<b>Materia: </b>{eSolicitud.materiaasignada.materia.asignatura.display}
											</p>
											<p class="m-0 p-0 fs-6">
												<b>Profesor: </b>{eSolicitud.profesor.persona.nombre_completo}
											</p>

											{#if eSolicitud.temas.length > 0}
												<p class="m-0 p-0 fs-6">
													<b>Tema: </b>
													{#each eSolicitud.temas as eTema}
														{eTema.descripcion}
													{/each}
												</p>
											{:else}
												<p class="m-0 p-0 fs-6"><b>Tema: </b><span>S/T</span></p>
											{/if}
											{#if eSolicitud.observacion_estudiante}
												<p class="m-0 p-0 fs-6">
													<b>Observación: </b>{eSolicitud.observacion_estudiante}
												</p>
											{/if}

											<p class="m-0 p-0 fs-6">
												{#if eSolicitud.topico === 1}
													<b>Tópico:</b>
													<span class="fw-bold text-success">{eSolicitud.topico_display}</span>
												{:else if eSolicitud.topico == 2}
													<b>Tópico:</b>
													<span class="fw-bold text-info">{eSolicitud.topico_display}</span>
												{/if}
											</p>
											<p class="m-0 p-0 fs-6">
												{#if eSolicitud.topico === 1}
													<b>Tipo:</b>
													<span class="fw-bold text-success">{eSolicitud.tipo_display}</span>
												{:else if eSolicitud.topico == 2}
													<b>Tipo:</b>
													<span class="fw-bold text-secondary">{eSolicitud.tipo_display}</span>
												{:else}
													<b>Tipo:</b>
													<span class="fw-bold text-warning">{eSolicitud.tipo_display}</span>
												{/if}
											</p>
										</td>
										<td>
											{#if eSolicitud.fechasolicitud}
												<p class="m-0 p-0 fs-6">
													<b>Fecha Solicitud: </b><br />{eSolicitud.fechasolicitud}
												</p>
											{/if}
											{#if eSolicitud.fechatutoria}
												<p class="m-0 p-0 fs-6">
													<b>Fecha Tutoria: </b><br />{eSolicitud.fechatutoria}
												</p>
											{/if}
											{#if eSolicitud.tutoriacomienza}
												<p class="m-0 p-0 fs-6">
													<b>Desde: </b>{eSolicitud.tutoriacomienza}
												</p>
											{/if}
											{#if eSolicitud.tutoriatermina}
												<p class="m-0 p-0 fs-6">
													<b>Hasta: </b>{eSolicitud.tutoriatermina}
												</p>
											{/if}
										</td>
										<td class="text-center">
											<p class="m-0 p-0 fs-6">
												{eSolicitud.horario ? eSolicitud.horario.display : ''}
											</p></td
										>
										<td class="text-center">
											<p class="m-0 p-0 fs-6">
												{#if eSolicitud.estado === 1}
													<span class="fw-bold text-warning">{eSolicitud.estado_display}</span>
												{:else if eSolicitud.estado == 2}
													<span class="fw-bold text-info">{eSolicitud.estado_display}</span>
												{:else if eSolicitud.estado == 3}
													<span class="fw-bold text-success">{eSolicitud.estado_display}</span>
												{:else if eSolicitud.estado == 4}
													<span class="fw-bold text-danger">{eSolicitud.estado_display}</span>
												{/if}
												{#if eSolicitud.profesor.urlzoom}
													{#if eSolicitud.puede_aperturar_tutoria}
														<br><br><a style="border: 2px solid; border-color: #ffaa46!important;"
																href="javascript:;" data-bs-toggle="tooltip"
																title="Ingresar a la tutoría"
																on:click={() => openTutoria(eSolicitud)}
																class="btn btn-default btn-sm rounded-5">
															<img src="{variables.BASE_API}/static/images/icons/google-meet-logo-6.png" style="width: 16px;margin-bottom: 0;">&nbsp;&nbsp;Ingresar a la tutoría
															</a>
													{/if}
												{/if}
											</p>
										</td>
										<td>
											<p class="m-0 p-0 fs-6">
												{#if eSolicitud.estado >= 3}
													<b>Asistencia:</b>
													{#if eSolicitud.asistencia}
														<i class="fe fe-check fw-bold text-success fs-5" />
													{:else}
														<i class="fe fe-x fw-bold text-danger fs-5" />
													{/if}
												{/if}
											</p>
											{#if eSolicitud.resultadoencuesta > 0}
												<p class="m-0 p-0 fs-6">
													<b>Encuesta:</b>
													<span>
														{#each rangeInteger(1, 5, 1) as number}
															<i
																class="mdi mdi-star me-n1 {number <= eSolicitud.resultadoencuesta
																	? 'text-warning'
																	: 'text-light'}  ms-1 fs-4"
															/>
														{/each}
													</span>
												</p>
												<div />
											{/if}									
											
										</td>
										<td class="align-middle text-center">
											{#if eSolicitud.estado !== 4 && !eSolicitud.resultadoencuesta}
											<!-- && eSolicitud.puede_aperturar_tutoria -->
												<div class="dropdown dropstart">
													<a
														class="btn-icon btn btn-ghost btn-sm rounded-circle"
														href="#"
														role="button"
														id="Dropdown1"
														data-bs-toggle="dropdown"
														aria-haspopup="true"
														aria-expanded="false"
													>
														<i class="fe fe-more-vertical" />
													</a>
													<div class="dropdown-menu" aria-labelledby="Dropdown1" style="">
														{#if eSolicitud.estado == 1}
															<a
																class="dropdown-item"
																href="javascript:;"
																on:click={() =>
																	openModal(
																		ComponentFormularioIndividual,
																		eSolicitud,
																		'Editar registro de solicitud',
																		'md'
																	)}
															>
																<i class="fe fe-edit dropdown-item-icon" />Editar
															</a>

															<a
																class="dropdown-item"
																href="javascript:;"
																on:click={() =>
																	eliminarRegistro(
																		`<p style='color:#ACAEAF;'>¿Desea eliminar datos de la solicitud?</p>`,
																		eSolicitud.pk,
																		'deleteSolicitudTutoriaIndividual'
																	)}
															>
																<i class="fe fe-trash dropdown-item-icon" />Eliminar
															</a>
														{/if}
														{#if !eSolicitud.resultadoencuesta}
															<!--{#if eSolicitud.puede_aperturar_tutoria} -->
																	<a
																		class="dropdown-item"
																		href="javascript:;"
																		on:click={() =>
																			openModal(
																				ComponentFormularioEncuesta,
																				eSolicitud,
																				`Encuesta de tutoria recibida ${eSolicitud.materiaasignada.materia.asignatura.nombre} de fecha (${eSolicitud.fechatutoria})`,
																				'md'
																			)}
																	>
																		<i class="fe fe-bar-chart dropdown-item-icon" />Encuesta
																	</a>
															<!--{/if} -->
														{/if}
													</div>
												</div>
											{/if}
										</td>
									</tr>
								{/each}
							{:else}
								<tr>
									<td colspan="6" class="text-center">Sin registros existentes</td>
								</tr>
							{/if}
						</tbody>
					</table>
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
	<svelte:component
		this={modalDetalleContent}
		aData={aDataModal}
		{mOpenModal}
		mToggle={mToggleModal}
		mTitle={mTitleModal}
		mClass={mClassModal}
		mSize={mSizeModal}
		on:actionRun={actionRun}
	/>
{/if}

<style>
	.border-dark-info {
		border-color: #ffff !important;
	}
</style>
