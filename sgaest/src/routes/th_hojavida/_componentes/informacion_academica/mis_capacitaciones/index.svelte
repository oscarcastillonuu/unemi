<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import { navigating } from '$app/stores';
	import { loading } from '$lib/store/loadingStore';
	import ComponentFormCapacitacion from './form.svelte';
	import Swal from 'sweetalert2';
	import { apiPOST } from '$lib/utils/requestUtils';
	import { addToast } from '$lib/store/toastStore';
	import { Tooltip } from 'sveltestrap';
	import ComponentViewPDF from '$components/viewPDF.svelte';
	let mOpenModal = false;
	const mToggleModal = () => (mOpenModal = !mOpenModal);
	let modalDetalleContent;
	export let aData;
	let activeFormacion = '';
	let aDataModal;
	let mView = false;
	let eCapacitaciones = [];
	let mTitleModal;
	let mClassModal =
		'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
	let mSizeModal = 'lg';
	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			eCapacitaciones = aData.eCapacitaciones ?? [];
		}
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'saveFormacionAcademicaCapacitacion') {
			mOpenModal = !mOpenModal;
			const menu = document.getElementById('menu_element_8');
			menu.click();
		}
	};

	const openModal = (component, title, data, isView) => {
		modalDetalleContent = component;
		mOpenModal = !mOpenModal;
		aDataModal = { ...data };
		mTitleModal = title;
		mView = isView;
		mSizeModal = 'xl';
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
						const menu = document.getElementById('menu_element_10');
						menu.click();
					}
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
			}
		});
	};

	const actionActiveFormacion = (active) => {
		activeFormacion = active;
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
</script>

{#if eCapacitaciones}
	<div class="row">
		<div class="col-12">
			<div class="card">
				<div class="card-header d-lg-flex justify-content-between align-items-center">
					<div class="headtitle mb-lg-0 m-0">
						<h3 class="mx-2 m-0 p-0">Mis capacitaciones</h3>
						<h6 class="mx-2 m-0 p-0">Listado de capacitaciones registradas</h6>
					</div>
					<div>
						<button
							class="btn btn-success btn-sm rounded-3 text-white"
							on:click={() =>
								openModal(
									ComponentFormCapacitacion,
									`Adicionar capacitación`,
									{
										eCapacitacion: undefined
									},
									false
								)}
						>
							<i class="fe fe-plus " /> Adicionar
						</button>
					</div>
				</div>
				<div class="card-body" id="formacion-academica-mis-titulos/secundaria" tabindex="-1">
					<div class="table-responsive scrollbar">
						<table class="table table_primary tabla_responsive table-hover table-centered">
							<thead class="table-light">
								<tr class="">
									<th class="text-center align-middle p-1" scope="col" style="width:10%;">
										Fecha<br />Inicio
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:10%;">
										Fecha<br />Fin
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:35%;">
										Institución/Evento/Horas
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:20%;">
										Documento
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:8%;"> Info </th>
									<th scope="col" style="width:10%; p-1" />
								</tr>
							</thead>
							<tbody>
								{#if eCapacitaciones.length}
									{#each eCapacitaciones as eCapacitacion}
										<tr class="">
											<td class="text-center align-middle p-1 fs-6">
												{eCapacitacion.fechainicio ?? ''}
											</td>
											<td class="text-center align-middle p-1 fs-6">
												{eCapacitacion.fechafin ?? ''}
											</td>
											<td class="text-left align-middle p-1 fs-6">
												<b>Institución: </b>
												{eCapacitacion.institucion ?? 'NO IDENTIFICADA'}<br />
												<b>Evento: </b>
												{eCapacitacion.nombre ?? 'S/N'}<br />
												<b>Horas: </b>
												{eCapacitacion.horas ?? '0'}<br />
											</td>
											<td class="text-center align-middle p-1 fs-6">
												{#if eCapacitacion.download_archivo}
													<a
														href="javascript:;"
														class="text-danger fs-3"
														on:click={() => view_pdf(eCapacitacion.download_archivo)}
														id="tooltip-1-{eCapacitacion.id}"
													>
														<i class="bi bi-file-pdf" />
													</a>
													<Tooltip target="tooltip-1-{eCapacitacion.id}" placement="bottom"
														>Ver certificado</Tooltip
													>
												{/if}
											</td>
											<td class="text-center align-middle p-1 fs-6">
												<a
													id="tooltip-id_capacitacion-{eCapacitacion.id}"
													href="javascript:;"
													class="text-info"
													on:click={() =>
														openModal(
															ComponentFormCapacitacion,
															`Información de la capacitación ${eCapacitacion.nombre}`,
															{
																eCapacitacion: eCapacitacion
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
												<Tooltip target="tooltip-id_capacitacion-{eCapacitacion.id}" placement="top"
													>Para mas información dar click aquí!</Tooltip
												>
											</td>
											<td class="text-center align-middle p-1 fs-6">
												{#if !eCapacitacion.verificado}
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
																		ComponentFormCapacitacion,
																		`Editar capacitación ${eCapacitacion.nombre}`,
																		{ eCapacitacion: eCapacitacion },
																		false
																	)}
															>
																<i class="fe fe-edit dropdown-item-icon" />Editar
															</a>

															<a
																class="dropdown-item"
																href="#eliminar"
																on:click={() =>
																	eliminarRegistro(
																		`<p style='color:#ACAEAF;'>¿Desea eliminar capacitación <b>${eCapacitacion.nombre}</b></p>`,
																		eCapacitacion.pk,
																		'deleteFormacionAcademicaMisCapacitaciones'
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
										<td colspan="6" class="text-center">No existe registro de títulos</td>
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

{#if mOpenModal}
	<svelte:component
		this={modalDetalleContent}
		aData={aDataModal}
		mToggle={mToggleModal}
		mTitle={mTitleModal}
		mSize={mSizeModal}
		{mView}
		{mOpenModal}
		on:actionRun={actionRun}
	/>
{/if}
