<script lang="ts">
	import { onMount } from 'svelte';
	import { apiGET, apiPOST } from '$lib/utils/requestUtils';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import ComponentFormularioMatricula from './forms/frmMatricula.svelte';
	import ComponentFormularioMateria from './forms/frmMateria.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { navigating } from '$app/stores';
	import { Spinner, Tooltip } from 'sveltestrap';
	import { addToast } from '$lib/store/toastStore';
	import Swal from 'sweetalert2';
	import ComponentViewPDF from '$components/viewPDF.svelte';
	import { goto } from '$app/navigation';
	export let eSolicitudes;
	let eDocentes = [];
	let eTutores = [];
	let itemsBreadCrumb = [
		{ text: 'Solicitudes al tutor de mis materias', active: false, href: undefined }
	];
	let backBreadCrumb = { href: '/', text: 'Atrás' };
	let load = true;
	let title = 'Solicitudes al tutor de mis materias';
	let mOpenModal = false;
	let mTitleModal;
	let mClassModal =
		'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
	let mSizeModal = 'lg';
	let inputTextSearch = '';
	const mToggleModal = () => (mOpenModal = !mOpenModal);
	let modalDetalleContent;
	//console.log($navigating);
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	let aDataModal;
	let item = 1;
	onMount(async () => {
		if (eSolicitudes) {
			eDocentes = eSolicitudes.eDocentes ?? [];
			eTutores = eSolicitudes.eTutores ?? [];
			load = false;
		}
	});

	const actionRun = async (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (
			action == 'saveSolicitudTutorSoporteMateria' ||
			action == 'saveSolicitudTutorSoporteMatricula'
		) {
			mOpenModal = !mOpenModal;
			eSolicitudes = await loadSolicitudes('');
			if (eSolicitudes) {
				eDocentes = eSolicitudes.eDocentes ?? [];
				eTutores = eSolicitudes.eTutores ?? [];
			}
		}
	};

	const loadSolicitudes = async (filterText: string) => {
		return new Promise(async (resolve, reject) => {
			loading.setLoading(true, 'Consultado la información, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/solicitud_tutor/posgrado', {
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

	const view_pdf = (url) => {
		aDataModal = { url: url };
		modalDetalleContent = ComponentViewPDF;
		mOpenModal = !mOpenModal;
		mTitleModal = 'Ver pdf';
		mClassModal =
			'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
		mSizeModal = 'xl';
	};

	const openModal = (componente, eSolicitud, title) => {
		modalDetalleContent = componente;
		mOpenModal = !mOpenModal;
		mTitleModal = title;
		aDataModal = { eSolicitud: eSolicitud };
		mClassModal =
			'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
		mSizeModal = 'md';
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
				const [res, errors] = await apiPOST(fetch, 'alumno/solicitud_tutor/posgrado', {
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
						if (eSolicitudes) {
							eDocentes = eSolicitudes.eDocentes ?? [];
							eTutores = eSolicitudes.eTutores ?? [];
						}
					}
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
			}
		});
	};
	const actionLoad = (link) => {
		item = link;
		//dispatch('actionRun', { action: 'selectItem', data: { item: item } });
	};
	const submitSearchSolicitudes = async () => {
		//console.log(inputTextSearch);
		eSolicitudes = await loadSolicitudes(inputTextSearch);
		if (eSolicitudes) {
			eDocentes = eSolicitudes.eDocentes ?? [];
			eTutores = eSolicitudes.eTutores ?? [];
		}
	};

	const resetSearchSolicitudes = async () => {
		inputTextSearch = '';
		eSolicitudes = await loadSolicitudes(inputTextSearch);
		if (eSolicitudes) {
			eDocentes = eSolicitudes.eDocentes ?? [];
			eTutores = eSolicitudes.eTutores ?? [];
		}
	};
</script>

<svelte:head>
	<title>{title}</title>
</svelte:head>
{#if !load}
	<BreadCrumb
		title="Consultas al tutor de mis materias"
		items={itemsBreadCrumb}
		back={backBreadCrumb}
	/>
	<div class="container-fluid px-2">
		<div class="row">
			<div class="col-lg-3">
				<!-- card -->
				<a href="javascript:;" class="texto-blue" on:click={() => actionLoad(1)}>
					<div
						class="card mb-2 border-top border-muted border-4 card-hover-with-icon {item == 1
							? 'active'
							: ''}"
						style="border: 0px"
					>
						<!-- card body -->
						<div class="card-body">
							<span class="fs-6 text-uppercase fw-semi-bold">SOLICITUD DOCENTE</span>
							<div class="mt-0 d-flex justify-content-between align-items-center">
								<div class="lh-1">
									<h2 class="h1 fw-bold mb-1 text-secondary"><i class="fe fe-user-check" /></h2>
								</div>
							</div>
						</div>
					</div>
				</a>
			</div>
			<div class="col-lg-3">
				<!-- card -->
				<a href="javascript:;" class="texto-blue" on:click={() => actionLoad(2)}>
					<div
						class="card mb-2 border-top border-muted border-4 card-hover-with-icon {item == 2
							? 'active'
							: ''}"
						style="border: 0px"
					>
						<!-- card body -->
						<div class="card-body">
							<span class="fs-6 text-uppercase fw-semi-bold">SOLICITUD TUTOR</span>
							<div class="mt-0 d-flex justify-content-between align-items-center">
								<div class="lh-1">
									<h2 class="h1 fw-bold mb-1 text-secondary"><i class="fe fe-user-plus" /></h2>
								</div>
							</div>
						</div>
					</div>
				</a>
			</div>
		</div>
		{#if item == 1}
			<div class="card ">
				<div class="card-body border-top border-6 rounded-3 border-dark-info">
					<div class="row row-cols-1 row-cols-sm-2 row-cols-md-2 mb-3 g-1">
						<div class="col">
							<button
								type="button"
								class="btn btn-info btn-sm"
								on:click={() =>
									openModal(
										ComponentFormularioMatricula,
										undefined,
										'Adicionar registro de consulta'
									)}><span class="fe fe-plus" /> Adicionar consulta a docente asignado</button
							>
						</div>
						<!--<div class="col">
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
						</div>-->
					</div>
					<div class="table-responsive scrollbar">
						<table class="table table_primary tabla_responsive">
							<thead class="table-light">
								<tr>
									<th class="text-center align-middle p-1">Fecha solicitud</th>
									<th class="text-center align-middle p-1">Motivo</th>
									<th class="text-center align-middle p-1">Archivo</th>
									<th class="text-center align-middle p-1">Estado</th>
									<th class="text-center align-middle p-1"><i class="fe fe-settings" /></th>
								</tr>
							</thead>
							<tbody>
								{#if eDocentes.length > 0}
									{#each eDocentes as eSolicitud}
										<tr>
											<td class="text-left align-middle">
												{eSolicitud.fecha_creacion}
											</td>
											<td class="text-left" style="vertical-align: top;">
												{eSolicitud.descripcion}
											</td>
											<td class="text-center align-middle">
												{#if eSolicitud.download_archivo}
													<a
														href="javascript:;"
														class="text-danger fs-3"
														on:click={() => view_pdf(eSolicitud.download_archivo)}
														id="tooltip-id-archivo-{eSolicitud.id}"
													>
														<i class="bi bi-file-pdf" />
													</a>
													<Tooltip target="tooltip-id-archivo-{eSolicitud.id}" placement="bottom"
														>Ver archivo</Tooltip
													>
												{/if}
											</td>
											<td class="text-center align-middle">
												{#if eSolicitud.estado === 1}
													<span class="text-primary fw-bold">{eSolicitud.estado_display}</span>
												{:else if eSolicitud.estado === 2}
													<span class="text-warning fw-bold">{eSolicitud.estado_display}</span>
												{:else if eSolicitud.estado === 3}
													<span class="text-success fw-bold">{eSolicitud.estado_display}</span>
												{:else if eSolicitud.estado === 4}
													<span class="text-danger fw-bold">{eSolicitud.estado_display}</span>
												{:else}
													<span class="text-dark fw-bold">{eSolicitud.estado_display}</span>
												{/if}
											</td>
											<td class="align-middle text-center">
												{#if [1, 4].includes(eSolicitud.estado)}
													<div class="dropdown dropstart">
														<a
															class="btn-icon btn btn-ghost btn-sm rounded-circle"
															href="javascript:;"
															role="button"
															id="Dropdown1"
															data-bs-toggle="dropdown"
															aria-haspopup="true"
															aria-expanded="false"
														>
															<i class="fe fe-more-vertical" />
														</a>
														<div class="dropdown-menu" aria-labelledby="Dropdown1" style="">
															<a
																class="dropdown-item"
																href="javascript:;"
																on:click={() =>
																	openModal(
																		ComponentFormularioMatricula,
																		eSolicitud,
																		'Editar registro de solicitud'
																	)}
															>
																<i class="fe fe-edit dropdown-item-icon" />Editar
															</a>

															<a
																class="dropdown-item"
																href="javascript:;"
																on:click={() =>
																	eliminarRegistro(
																		`<p style='color:#ACAEAF;'>¿Desea eliminar solicitud?</p>`,
																		eSolicitud.pk,
																		'deleteSolicitudTutorSoporteMatricula'
																	)}
															>
																<i class="fe fe-trash dropdown-item-icon" />Eliminar
															</a>
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
		{/if}
		{#if item == 2}
			<div class="card ">
				<div class="card-body border-top border-6 rounded-3 border-dark-info">
					<div class="row row-cols-1 row-cols-sm-2 row-cols-md-2 mb-3 g-1">
						<div class="col">
							<button
								type="button"
								class="btn btn-info btn-sm"
								on:click={() =>
									openModal(
										ComponentFormularioMateria,
										undefined,
										'Adicionar registro de consulta'
									)}><span class="fe fe-plus" /> Adicionar consulta a tutor asignado</button
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
					<div class="table-responsive scrollbar">
						<table class="table table_primary tabla_responsive">
							<thead class="table-light">
								<tr>
									<th class="text-center align-middle p-1">Profesor/Materia</th>
									<th class="text-center align-middle p-1">Consulta</th>
									<th class="text-center align-middle p-1">Estado</th>
									<th class="text-center align-middle p-1">Fecha respuesta</th>
									<th class="text-center align-middle p-1"><i class="fe fe-settings" /></th>
								</tr>
							</thead>
							<tbody>
								{#if eTutores.length > 0}
									{#each eTutores as eSolicitud}
										<tr>
											<td class="text-left" style="vertical-align: top;">
												<p class="p-0 m-0">
													<b>Profesor: </b>
													{eSolicitud.profesor.persona.nombre_completo}
												</p>
												<p class="p-0 m-0">
													<b>Materia: </b>
													{eSolicitud.materiaasignada.materia.asignatura.nombre}
												</p>
											</td>
											<td class="text-left align-middle">
												<p class="p-0 m-0"><b>Tipo: </b> {eSolicitud.tipo_display}</p>
												<p class="p-0 m-0"><b>Descripción: </b> {eSolicitud.descripcion}</p>
												{#if eSolicitud.download_archivo}
													<p class="p-0 m-0">
														<b>Archivo: </b>
														<a
															href="javascript:;"
															class="text-danger fs-3"
															on:click={() => view_pdf(eSolicitud.download_archivo)}
															id="tooltip-id-archivo-{eSolicitud.id}"
														>
															<i class="bi bi-file-pdf" />
														</a>
														<Tooltip target="tooltip-id-archivo-{eSolicitud.id}" placement="bottom"
															>Ver archivo</Tooltip
														>
													</p>
												{/if}
											</td>
											<td class="text-center align-middle">
												{#if eSolicitud.estado === 1}
													<span class="text-primary fw-bold">{eSolicitud.estado_display}</span>
												{:else if eSolicitud.estado === 2}
													<span class="text-warning fw-bold">{eSolicitud.estado_display}</span>
												{:else if eSolicitud.estado === 3}
													<span class="text-success fw-bold">{eSolicitud.estado_display}</span>
												{:else if eSolicitud.estado === 4}
													<span class="text-danger fw-bold">{eSolicitud.estado_display}</span>
												{:else}
													<span class="text-dark fw-bold">{eSolicitud.estado_display}</span>
												{/if}
											</td>
											<td class="text-center align-middle">
												{eSolicitud.fecharespuesta ?? ''}
											</td>
											<td class="align-middle text-center">
												{#if [1, 4].includes(eSolicitud.estado)}
													<div class="dropdown dropstart">
														<a
															class="btn-icon btn btn-ghost btn-sm rounded-circle"
															href="javascript:;"
															role="button"
															id="Dropdown1"
															data-bs-toggle="dropdown"
															aria-haspopup="true"
															aria-expanded="false"
														>
															<i class="fe fe-more-vertical" />
														</a>
														<div class="dropdown-menu" aria-labelledby="Dropdown1" style="">
															<a
																class="dropdown-item"
																href="javascript:;"
																on:click={() =>
																	openModal(
																		ComponentFormularioMateria,
																		eSolicitud,
																		'Editar registro de solicitud'
																	)}
															>
																<i class="fe fe-edit dropdown-item-icon" />Editar
															</a>

															<a
																class="dropdown-item"
																href="javascript:;"
																on:click={() =>
																	eliminarRegistro(
																		`<p style='color:#ACAEAF;'>¿Desea eliminar solicitud?</p>`,
																		eSolicitud.pk,
																		'deleteSolicitudTutorSoporteMateria'
																	)}
															>
																<i class="fe fe-trash dropdown-item-icon" />Eliminar
															</a>
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
		border-color: #ffaa46 !important;
	}
	.card-hover-with-icon.active,
	.card-hover-with-icon:focus,
	.card-hover-with-icon:hover {
		border-top-color: #1c3247 !important;
		box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05) !important;
		transition: 1s ease;
	}

	.card-hover-with-icon {
		cursor: pointer;
		transition: box-shadow 0.25s ease;
	}
</style>
