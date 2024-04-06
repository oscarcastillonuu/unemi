<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import { navigating } from '$app/stores';
	import { loading } from '$lib/store/loadingStore';
	import ComponentFormBachiller from './forms/bachiller.svelte';
	import ComponentFormSuperior from './forms/superior.svelte';
	import ComponentViewPDF from '$components/viewPDF.svelte';
	import Swal from 'sweetalert2';
	import { apiPOST } from '$lib/utils/requestUtils';
	import { addToast } from '$lib/store/toastStore';
	import { Tooltip } from 'sveltestrap';
	let mOpenModal = false;
	const mToggleModal = () => (mOpenModal = !mOpenModal);
	let modalDetalleContent;
	export let aData;
	let activeFormacion = '';
	let aDataModal;
	let mView = false;
	let eTitulaciones = {};
	let eNivelBachilleres = [];
	let eNivelSuperiores = [];
	let mTitleModal;
	let mClassModal =
		'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
	let mSizeModal = 'lg';
	let verBtnBachillerAdd = false;
	let verBtnSuperiorAdd = false;
	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			eTitulaciones = aData.eTitulaciones ?? {};
			if (eTitulaciones) {
				eNivelBachilleres = eTitulaciones.eNivelBachilleres ?? [];
				eNivelSuperiores = eTitulaciones.eNivelSuperiores ?? [];
			}
		}
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'saveFormacionAcademicaTitulo') {
			mOpenModal = !mOpenModal;
			const menu = document.getElementById('menu_element_7');
			menu.click();
		}
	};

	const openModal = (component, title, data, isView) => {
		modalDetalleContent = component;
		mOpenModal = !mOpenModal;
		aDataModal = { ...data };
		mTitleModal = title;
		mView = isView;
	};

	const eliminarRegistro = async (body, pk, action) => {
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
				const [res, errors] = await apiPOST(fetch, 'alumno/hoja_vida', {
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
						const menu = document.getElementById('menu_element_7');
						menu.click();
					}
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
			}
		});
	};

	const checkRecordsWebService = async (action) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/general/data', {
			action: action
		});
		if (errors.length > 0) {
			errors.forEach((element) => {
				addToast({ type: 'error', header: 'Ocurrio un error', body: element.error });
			});
		} else {
			if (!res.isSuccess) {
				addToast({
					type: 'error',
					header: 'Ocurrio un error',
					body: 'FUENTE DE INFORMACIÓN INACTIVA'
				});
				if (action === 'get_titulos_educacion_bachiller') {
					verBtnBachillerAdd = true;
				}
				if (action === 'get_titulos_educacion_superior') {
					verBtnSuperiorAdd = true;
				}
			} else {
				addToast({
					type: 'success',
					header: '¡Exitoso!',
					body: res.message
				});
				if (res.data['cantidad'] > 0) {
					const menu = document.getElementById('menu_element_7');
					menu.click();
				} else {
					if (action === 'get_titulos_educacion_bachiller') {
						verBtnBachillerAdd = true;
					}
					if (action === 'get_titulos_educacion_superior') {
						verBtnSuperiorAdd = true;
					}
				}
			}
		}
		loading.setLoading(false, 'Cargando, espere por favor...');
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
	const actionActiveFormacion = (active) => {
		activeFormacion = active;
	};
</script>

{#if eTitulaciones}
	<div class="row">
		<div class="col-xxl-10 col-xl-10 col-lg-12 col-12">
			<div class="card ">
				<div class="card-header d-lg-flex justify-content-between align-items-center">
					<div class="headtitle mb-lg-0 m-0">
						<h3 class="mx-2 m-0 p-0">Bachiller</h3>
					</div>
					<div>
						<button
							class="btn btn-warning btn-sm rounded-3 text-black"
							on:click={() => checkRecordsWebService('get_titulos_educacion_bachiller')}
						>
							<i class="fe fe-search " /> Consultar MINEDUC
						</button>
						{#if verBtnBachillerAdd}
							<button
								class="btn btn-success btn-sm rounded-3 text-white"
								on:click={() =>
									openModal(
										ComponentFormBachiller,
										`Adicionar titulo de bachiller`,
										{
											eBachiller: undefined
										},
										false
									)}
							>
								<i class="fe fe-plus " /> Adicionar
							</button>
						{/if}
					</div>
				</div>
				<div class="card-body" id="formacion-academica-mis-titulos/secundaria" tabindex="-1">
					<div class="table-responsive scrollbar">
						<table class="table table_primary tabla_responsive table-hover table-centered">
							<thead class="table-light">
								<tr class="fs-6">
									<th class="text-center align-middle p-1" scope="col" style="width:10%;">
										Fecha Inicio
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:10%;">
										Fecha Obtención
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:35%;">
										Título
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:20%;">
										Archivo
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:8%;"> Info </th>
									<th scope="col" style="width:10%; p-1" />
								</tr>
							</thead>
							<tbody>
								{#if eNivelBachilleres.length}
									{#each eNivelBachilleres as eBachiller}
										<tr class="">
											<td class="text-center align-middle p-1 fs-6">
												{eBachiller.fechainicio ?? ''}
											</td>
											<td class="text-center align-middle p-1 fs-6">
												{#if eBachiller.detalletitulacionbachiller}
													{#if eBachiller.detalletitulacionbachiller.fechagrado}
														{eBachiller.detalletitulacionbachiller.fechagrado}
													{:else if eBachiller.detalletitulacionbachiller.aniofinperiodograduacion}
														{eBachiller.detalletitulacionbachiller.aniofinperiodograduacion}
													{:else}
														CURSANDO
													{/if}
												{/if}
											</td>
											<td class="text-left align-middle p-1 fs-6">
												{eBachiller.titulo.nombre}

												{#if eBachiller.colegio}
													<br /><b>{eBachiller.colegio.nombre}</b>
												{/if}
											</td>
											<td class="text-center align-middle p-1 fs-6">
												{#if eBachiller.detalletitulacionbachiller}
													{#if eBachiller.detalletitulacionbachiller.download_actagrado}
														<a
															href="javascript:;"
															class="text-danger fs-3"
															on:click={() =>
																view_pdf(eBachiller.detalletitulacionbachiller.download_actagrado)}
															id="tooltip-1-{eBachiller.id}"
														>
															<i class="bi bi-file-pdf" />
														</a>
														<Tooltip target="tooltip-1-{eBachiller.id}" placement="bottom"
															>Ver acta de grado</Tooltip
														>
													{/if}
												{/if}
											</td>
											<td class="text-center align-middle p-1">
												<a
													id="btn_info_id_{eBachiller.id}"
													href="javascript:;"
													class="text-info fs-3"
													on:click={() =>
														openModal(
															ComponentFormBachiller,
															`Información del titulo de bachiller`,
															{
																eBachiller: eBachiller
															},
															true
														)}
												>
													<svg
														xmlns="http://www.w3.org/2000/svg"
														width="17"
														height="17"
														fill="currentColor"
														class="bi bi-info-circle-fill me-2"
														viewBox="0 0 16 16"
													>
														<path
															d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"
														/>
													</svg>
												</a>
												<Tooltip target="btn_info_id_{eBachiller.id}" placement="top"
													>Para mas información dar click aquí!</Tooltip
												>
											</td>
											<td class="text-center align-middle p-1">
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
														<a
															class="dropdown-item"
															href="#editar"
															on:click={() =>
																openModal(
																	ComponentFormBachiller,
																	`Editar titulo ${eBachiller.titulo.nombre}`,
																	{ eBachiller: eBachiller },
																	false
																)}
														>
															<i class="fe fe-edit dropdown-item-icon" />Editar
														</a>
														{#if !eBachiller.verificado}
															<a
																class="dropdown-item"
																href="#eliminar"
																on:click={() =>
																	eliminarRegistro(
																		`<p style='color:#ACAEAF;'>¿Desea eliminar formación académica <b>${eBachiller.titulo.nombre}</b></p>`,
																		eBachiller.pk,
																		'deleteFormacionAcademicaMisTitulos'
																	)}
															>
																<i class="fe fe-trash dropdown-item-icon" />Eliminar
															</a>
														{/if}
													</div>
												</div>
											</td>
										</tr>
									{/each}
								{:else}
									<tr>
										<td colspan="6" class="text-center">No existe registro de títulos</td>
									</tr>
								{/if}
							</tbody>
						</table>
					</div>
				</div>
			</div>
			<div class="card mt-4">
				<div class="card-header d-lg-flex justify-content-between align-items-center">
					<div class="headtitle mb-lg-0 m-0">
						<h3 class="mx-2 m-0 p-0">Superior</h3>
					</div>
					<div>
						<button
							class="btn btn-warning btn-sm rounded-3 text-black"
							on:click={() => checkRecordsWebService('get_titulos_educacion_superior')}
						>
							<i class="fe fe-search " /> Consultar SENESCYT
						</button>
						{#if verBtnSuperiorAdd}
							<button
								class="btn btn-success btn-sm rounded-3 text-white"
								on:click={() =>
									openModal(
										ComponentFormSuperior,
										`Adicionar titulo superior`,
										{
											eSuperior: undefined
										},
										false
									)}
							>
								<i class="fe fe-plus " /> Adicionar
							</button>
						{/if}
					</div>
				</div>
				<div class="card-body" id="formacion-academica-mis-titulos/superior" tabindex="-1">
					<div class="table-responsive scrollbar">
						<table class="table table_primary tabla_responsive table-hover table-centered">
							<thead class="table-light">
								<tr class="fs-6">
									<th class="text-center align-middle p-1" scope="col" style="width:10%;">
										Fecha Inicio
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:10%;">
										Fecha Obtención
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:35%;">
										Título/Institución
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:20%;">
										Archivo
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:8%;"> Info </th>
									<th scope="col" style="width:10%; p-1" />
								</tr>
							</thead>
							<tbody>
								{#if eNivelSuperiores.length}
									{#each eNivelSuperiores as eSuperior}
										<tr class="">
											<td class="text-center align-middle p-1 fs-6">
												{eSuperior.fechainicio ?? ''}
											</td>
											<td class="text-center align-middle p-1 fs-6">
												{eSuperior.fecharegistro ?? 'CURSANDO'}
											</td>
											<td class="text-left align-middle p-1 fs-6">
												{eSuperior.titulo.nombre}
												{#if eSuperior.institucion}
													<br /><b>{eSuperior.institucion.nombre}</b>
												{/if}
											</td>
											<td class="text-center align-middle p-1 fs-6">
												{#if eSuperior.download_archivo}
													<a
														href="javascript:;"
														class="text-danger fs-3"
														on:click={() => view_pdf(eSuperior.download_archivo)}
														id="tooltip-2-{eSuperior.id}"
													>
														<i class="bi bi-file-pdf" />
													</a>
													<Tooltip target="tooltip-2-{eSuperior.id}" placement="bottom"
														>Ver título</Tooltip
													>
												{/if}
												{#if eSuperior.download_registroarchivo}
													<a
														href="javascript:;"
														class="text-primary fs-3"
														on:click={() => view_pdf(eSuperior.download_registroarchivo)}
														id="tooltip-3-{eSuperior.id}"
													>
														<i class="bi bi-file-pdf" />
													</a>
													<Tooltip target="tooltip-3-{eSuperior.id}" placement="bottom"
														>Ver SENESCYT</Tooltip
													>
												{/if}
											</td>
											<td class="text-center align-middle p-1 fs-6">
												<a
													id="tooltip-id_superior-{eSuperior.id}"
													href="javascript:;"
													class="text-info"
													on:click={() =>
														openModal(
															ComponentFormSuperior,
															`Información del titulo superior`,
															{
																eSuperior: eSuperior
															},
															true
														)}
												>
													<svg
														xmlns="http://www.w3.org/2000/svg"
														width="17"
														height="17"
														fill="currentColor"
														class="bi bi-info-circle-fill me-2"
														viewBox="0 0 16 16"
													>
														<path
															d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"
														/>
													</svg>
												</a>
												<Tooltip target="tooltip-id_superior-{eSuperior.id}" placement="top"
													>Para mas información dar click aquí!</Tooltip
												>
											</td>
											<td class="text-center align-middle p-1 fs-6">
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
														<a
															class="dropdown-item"
															href="#editar"
															on:click={() =>
																openModal(
																	ComponentFormSuperior,
																	`Editar titulo ${eSuperior.titulo.nombre}`,
																	{ eSuperior: eSuperior },
																	false
																)}
														>
															<i class="fe fe-edit dropdown-item-icon" />Editar
														</a>
														{#if !eSuperior.verificadosenescyt && !eSuperior.verificado}
															<a
																class="dropdown-item"
																href="#eliminar"
																on:click={() =>
																	eliminarRegistro(
																		`<p style='color:#ACAEAF;'>¿Desea eliminar formación académica <b>${eSuperior.titulo.nombre}</b></p>`,
																		eSuperior.pk,
																		'deleteFormacionAcademicaMisTitulos'
																	)}
															>
																<i class="fe fe-trash dropdown-item-icon" />Eliminar
															</a>
														{/if}
													</div>
												</div>
											</td>
										</tr>
									{/each}
								{:else}
									<tr>
										<td colspan="6" class="text-center">No existe registro de títulos</td>
									</tr>
								{/if}
							</tbody>
						</table>
					</div>
				</div>
			</div>
		</div>
		<div
			class="col-xxl-2 col-xl-2 col-lg-2 col-12 d-none
			d-xl-block "
		>
			<div class="position-fixed end-0 p-0 m-0">
				<div class="position-sticky mt-0" style="top: 0px;">
					<div class="sidebar-nav-fixed">
						<span class="px-4 mb-2 d-block text-uppercase ls-md fw-semibold fs-6"
							>Niveles de educación</span
						>
						<ul class="list-unstyled">
							<!--<li>
								<a
									href="#formacion-academica-mis-titulos/primaria"
									class={activeFormacion === 'primaria' ? 'active' : ''}
									on:click={() => actionActiveFormacion('primaria')}
								>
									Básica
								</a>
							</li>-->
							<li>
								<a
									href="#formacion-academica-mis-titulos/secundaria"
									class={activeFormacion === 'secundaria' ? 'active' : ''}
									on:click={() => actionActiveFormacion('secundaria')}
								>
									Bachiller
								</a>
							</li>
							<li>
								<a
									href="#formacion-academica-mis-titulos/superior"
									class={activeFormacion === 'superior' ? 'active' : ''}
									on:click={() => actionActiveFormacion('superior')}
								>
									Superior
								</a>
							</li>
						</ul>
					</div>
				</div>
			</div>
		</div>
	</div>
{/if}

{#if mOpenModal}
	<svelte:component
		this={modalDetalleContent}
		aData={aDataModal}
		mToggle={mToggleModal}
		mTitle={mTitleModal}
		mSize={mSizeModal}
		mClass={mClassModal}
		{mOpenModal}
		{mView}
		on:actionRun={actionRun}
	/>
{/if}

<style>
	.headtitle {
		border-left-color: #fe9900;
	}
	.btn-cian-opacity:hover {
		background-color: #9bc7ee !important;
		border-color: #9bc7ee;
	}

	.btn-cian-opacity {
		background-color: #92bddf !important;
		color: #1f354a !important;
		border-color: #92bddf;
		font-weight: 400;
	}
	.table_striped tbody tr:nth-child(even),
	.table_striped tbody tr:nth-child(even) {
		background-color: #e7eef5;
	}

	.table_striped tbody tr:nth-child(odd),
	.table_striped tbody tr:nth-child(odd) {
		background-color: #f2f6fb;
	}

	.table_striped thead th,
	.table_striped thead td,
	.table_striped tbody th,
	.table_striped tbody td {
		border-right: 1px solid white;
	}

	.table_striped thead th:nth-child(1),
	.table_striped thead th:nth-child(2),
	.table_striped thead td:nth-child(1),
	.table_striped thead td:nth-child(2),
	.table_striped tbody td:nth-child(1),
	.table_striped tbody td:nth-child(2),
	.table_striped tbody th:nth-child(1),
	.table_striped tbody th:nth-child(2) {
		border-right: none;
	}

	.table_striped tbody th:nth-child(2),
	.table_striped tbody td:nth-child(2) {
		color: #000;
	}

	.table_striped a.btn {
		padding-bottom: 0.5rem !important;
		padding-top: 0.5rem !important;
	}

	.table_striped a.btn .fa {
		font-size: 9px;
		margin-right: 3px;
	}

	.table_striped thead th {
		text-align: center;
		color: #1e121e;
		font-size: 13px;
		vertical-align: middle;
		text-transform: uppercase;
	}

	.table_primary thead th {
		background-color: #abcae6;
	}

	.table_primary thead th:first-child,
	.table_primary thead td:first-child {
		border-left: 5px solid #1c3247;
	}

	.table_primary tbody th,
	.table_primary tbody td {
		font-size: 13px;
		vertical-align: middle !important;
	}

	.table_warning thead th {
		background-color: #f9ebd6;
	}

	.table_warning thead th:first-child,
	.table_warning thead td:first-child {
		border-left: 5px solid #fe9900;
	}

	.table_warning tbody th,
	.table_warning tbody td {
		font-size: 13px;
		vertical-align: middle !important;
	}

	.table_danger thead th {
		background-color: #fadbd8;
	}

	.table_danger thead th:first-child,
	.table_danger thead td:first-child {
		border-left: 5px solid #e74c3c;
	}

	.table_danger tbody th,
	.table_danger tbody td {
		font-size: 13px;
		vertical-align: middle !important;
	}
</style>
