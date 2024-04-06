<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import { navigating } from '$app/stores';
	import { loading } from '$lib/store/loadingStore';
	import ComponentViewPDF from '$components/viewPDF.svelte';
	import FormularioExterno from './forms/externa.svelte';
	import Swal from 'sweetalert2';
	import { apiPOST } from '$lib/utils/requestUtils';
	import { addToast } from '$lib/store/toastStore';
	import { html } from 'gridjs';
	import { Tooltip } from 'sveltestrap';
	let mOpenModal = false;
	const mToggleModal = () => (mOpenModal = !mOpenModal);
	let modalDetalleContent;
	let item = 1;
	export let aData;
	let aDataModal;
	let mView = false;
	let eBecasInternas = [];
	let eBecasExternas = [];
	let mTitleModal;
	let mClassModal =
		'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
	let mSizeModal = 'lg';
	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			eBecasInternas = aData.eBecasInternas ?? [];
			eBecasExternas = aData.eBecasExternas ?? [];
		}
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'saveFormacionAcademicaBecaExterna') {
			mOpenModal = !mOpenModal;
			const menu = document.getElementById('menu_element_13');
			menu.click();
		}
	};

	const openModal = (component, title, data, isView) => {
		modalDetalleContent = component;
		mOpenModal = !mOpenModal;
		aDataModal = { ...data };
		mTitleModal = title;
		mSizeModal = 'md';
		mView = isView;
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

	const actionLoad = (link) => {
		item = link;
		//dispatch('actionRun', { action: 'selectItem', data: { item: item } });
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
						const menu = document.getElementById('menu_element_13');
						menu.click();
					}
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
			}
		});
	};
</script>

<div class="row">
	<div class="col-lg-4">
		<!-- card -->
		<a
			href="#bacas_internas"
			class="texto-blue"
			on:click={() => actionLoad(1)}
			id="menu_element_12"
		>
			<div
				class="card mb-2 border-top border-muted border-4 card-hover-with-icon {item == 1
					? 'active'
					: ''}"
				style="border: 0px"
			>
				<!-- card body -->
				<div class="card-body">
					<span class="fs-6 text-uppercase fw-semi-bold">BECAS INTERNAS</span>
					<div class="mt-0 d-flex justify-content-between align-items-center">
						<div class="lh-1">
							<h2 class="h1 fw-bold mb-1 text-secondary"><i class="fe fe-user-check" /></h2>
						</div>
					</div>
				</div>
			</div>
		</a>
	</div>
	<div class="col-lg-4">
		<!-- card -->
		<a href="#becas_externas" class="texto-blue" on:click={() => actionLoad(2)}>
			<div
				class="card mb-2 border-top border-muted border-4 card-hover-with-icon {item == 2
					? 'active'
					: ''}"
				style="border: 0px"
			>
				<!-- card body -->
				<div class="card-body">
					<span class="fs-6 text-uppercase fw-semi-bold">BECAS EXTERNAS</span>
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
{#if item === 1}
	{#if eBecasInternas}
		<div class="row">
			<div class="col-12">
				<div class="card ">
					<div class="card-header d-lg-flex justify-content-between align-items-center">
						<div class="headtitle mb-lg-0 m-0">
							<h3 class="mx-2 m-0 p-0">Becas internas</h3>
							<h6 class="mx-2 m-0 p-0">Listado de becas internas registrados</h6>
						</div>
					</div>
					<div class="card-body" tabindex="-1">
						<div class="table-responsive scrollbar">
							<table class="table table_primary tabla_responsive table-hover table-centered">
								<thead class="table-light">
									<tr class="">
										<th class="text-center align-middle p-1" scope="col" style="width:30%;">
											Periodo
										</th>
										<th class="text-center align-middle p-1" scope="col" style="width:20%;">
											Institución
										</th>
										<th class="text-center align-middle p-1" scope="col" style="width:35%;">
											Tipo de beca
										</th>
										<th class="text-center align-middle p-1" scope="col" style="width:10%;">
											Fecha
										</th>
										<th class="text-center align-middle p-1" scope="col" style="width:10%;">
											Vigente
										</th>
									</tr>
								</thead>
								<tbody>
									{#if eBecasInternas.length}
										{#each eBecasInternas as eBeca}
											<tr class="">
												<td class="text-center align-middle p-1 px-2 fs-6">
													{eBeca.periodo ?? ''}
												</td>
												<td class="text-center align-middle p-1 px-2 fs-6">
													{eBeca.institucion ?? ''}
												</td>
												<td class="text-center align-middle p-1 px-2 fs-6">
													{eBeca.tipobeca ?? ''}
												</td>
												<td class="text-center align-middle p-1 px-2 fs-6">
													{eBeca.fecha ?? ''}
												</td>
												<td class="text-center align-middle p-1 px-2 fs-6">
													{#if !eBeca.finalizo}
														<span class="text-success">Si</span>
													{:else}
														<span class="text-danger">No</span>
													{/if}
												</td>
											</tr>
										{/each}
									{:else}
										<tr>
											<td colspan="5" class="text-center">No existe registro de becas</td>
										</tr>
									{/if}
								</tbody>
							</table>
						</div>
					</div>
				</div>
			</div>
		</div>
	{/if}
{/if}

{#if item === 2}
	{#if eBecasExternas}
		<div class="row">
			<div class="col-12">
				<div class="card ">
					<div class="card-header d-lg-flex justify-content-between align-items-center">
						<div class="headtitle mb-lg-0 m-0">
							<h3 class="mx-2 m-0 p-0">Becas externas</h3>
							<h6 class="mx-2 m-0 p-0">Listado de becas externas registrados</h6>
						</div>
						<div>
							<button
								class="btn  btn-sm btn-success"
								on:click={() =>
									openModal(
										FormularioExterno,
										`Adicionar registro de beca externa`,
										{ eBeca: undefined },
										false
									)}><i class="fe fe-plus " /> Adicionar</button
							>
						</div>
					</div>
					<div class="card-body" tabindex="-1">
						<div class="table-responsive scrollbar">
							<table class="table table_primary tabla_responsive table-hover table-centered">
								<thead class="table-light">
									<tr class="">
										<th class="text-center align-middle p-1" scope="col" style="width:30%;">
											Fechas
										</th>
										<th class="text-center align-middle p-1" scope="col" style="width:20%;">
											Institución
										</th>
										<th class="text-center align-middle p-1" scope="col" style="width:35%;">
											Certificado
										</th>
										<th class="text-center align-middle p-1" scope="col" style="width:10%;">
											Verificado
										</th>
										<th class="text-center align-middle p-1" scope="col" style="width:10%;" />
									</tr>
								</thead>
								<tbody>
									{#if eBecasExternas.length}
										{#each eBecasExternas as eBeca}
											<tr class="">
												<td class="text-left align-middle p-1 fs-6">
													<span><b>Inicio: </b>{eBeca.fechainicio}</span><br />
													<span><b>Fin: </b>{eBeca.fechafin}</span>
												</td>
												<td class="text-left align-middle p-1  fs-6">
													{eBeca.institucion.nombre ?? ''}
													({eBeca.tipoinstitucion_display ?? ''})
												</td>
												<td class="text-center align-middle p-1 fs-6">
													{#if eBeca.download_archivo}
														<a
															href="javascript:;"
															class="text-primary fs-3"
															on:click={() => view_pdf(eBeca.download_archivo)}
															id="tooltip-3-{eBeca.id}"
														>
															<i class="bi bi-file-pdf" />
														</a>
														<Tooltip target="tooltip-3-{eBeca.id}" placement="bottom"
															>Ver certificado</Tooltip
														>
													{/if}
												</td>
												<td class="text-center align-middle p-1 fs-6">
													{#if eBeca.verificado}
														<span class="text-success">Si</span>
													{:else}
														<span class="text-danger">No</span>
													{/if}
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
																		FormularioExterno,
																		`Editar beca externa ${eBeca.institucion.nombre}`,
																		{ eBeca: eBeca },
																		false
																	)}
															>
																<i class="fe fe-edit dropdown-item-icon" />Editar
															</a>
															{#if !eBeca.verificado}
																<a
																	class="dropdown-item"
																	href="#eliminar"
																	on:click={() =>
																		eliminarRegistro(
																			`<p style='color:#ACAEAF;'>¿Desea eliminar beca externa <b>${eBeca.institucion.nombre}</b></p>`,
																			eBeca.pk,
																			'deleteFormacionAcademicaBecaExterna'
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
											<td colspan="5" class="text-center">No existe registro de becas</td>
										</tr>
									{/if}
								</tbody>
							</table>
						</div>
					</div>
				</div>
			</div>
		</div>
	{/if}
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
