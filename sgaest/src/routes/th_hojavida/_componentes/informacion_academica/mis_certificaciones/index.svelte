<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import { navigating } from '$app/stores';
	import { loading } from '$lib/store/loadingStore';
	import ComponentFormIdioma from './forms/idioma.svelte';
	import ComponentFormCertificacion from './forms/certificacion.svelte';
	import ComponentViewPDF from '$components/viewPDF.svelte';
	import Swal from 'sweetalert2';
	import { apiPOST } from '$lib/utils/requestUtils';
	import { addToast } from '$lib/store/toastStore';
	import { html } from 'gridjs';
	import { Tooltip } from 'sveltestrap';
	let mOpenModal = false;
	const mToggleModal = () => (mOpenModal = !mOpenModal);
	let modalDetalleContent;
	export let aData;
	let aDataModal;
	let mView = false;
	let eCertificaciones = undefined;
	let eCertificadosIdiomas = [];
	let eCertificacionesPersona = [];
	let mTitleModal;
	let mClassModal =
		'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
	let mSizeModal = 'lg';
	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			eCertificaciones = aData.eCertificaciones ?? undefined;
			if (eCertificaciones) {
				eCertificadosIdiomas = eCertificaciones.eCertificadosIdiomas ?? [];
				eCertificacionesPersona = eCertificaciones.eCertificacionesPersona ?? [];
			}
		}
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'saveFormacionAcademicaCertificacion') {
			mOpenModal = !mOpenModal;
			const menu = document.getElementById('menu_element_9');
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
						const menu = document.getElementById('menu_element_9');
						menu.click();
					}
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
			}
		});
	};
</script>

{#if eCertificaciones}
	<div class="row">
		<div class="col-12">
			<div class="card ">
				<div class="card-header d-lg-flex justify-content-between align-items-center">
					<div class="headtitle mb-lg-0 m-0">
						<h3 class="mx-2 m-0 p-0">Suficiencias en idiomas</h3>
						<h6 class="mx-2 m-0 p-0">
							Listado de certificados de suficiencias en idiomas registrados
						</h6>
					</div>
					<div>
						<button
							class="btn btn-success btn-sm rounded-3 text-white"
							on:click={() =>
								openModal(
									ComponentFormIdioma,
									`Adicionar certificación de idioma`,
									{
										eCertificacion: undefined
									},
									false
								)}
						>
							<i class="fe fe-plus " /> Adicionar
						</button>
					</div>
				</div>
				<div class="card-body" tabindex="-1">
					<div class="table-responsive scrollbar">
						<table class="table table_primary tabla_responsive table-hover table-centered">
							<thead class="table-light">
								<tr class="">
									<th class="text-center align-middle p-1" scope="col" style="width:30%;">
										Institución certificadora
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:20%;">
										Idioma
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:15%;">
										Nivel de suficiencia
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:10%;">
										Fecha certificación
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:15%;">
										Documento
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:10%;">
										Info
									</th>
									<th scope="col" style="width:10%; p-1" />
								</tr>
							</thead>
							<tbody>
								{#if eCertificadosIdiomas.length}
									{#each eCertificadosIdiomas as eIdioma}
										<tr class="">
											<td class="text-center align-middle p-1 fs-6">
												{#if eIdioma.institucioncerti}
													{eIdioma.institucioncerti.nombre ?? ''}
												{:else}
													S/N
												{/if}
											</td>
											<td class="text-center align-middle p-1 fs-6">
												{#if eIdioma.idioma}
													{eIdioma.idioma.nombre ?? ''}
												{:else}
													S/N
												{/if}
											</td>
											<td class="text-center align-middle p-1 fs-6">
												{#if eIdioma.nivelsuficencia}
													{eIdioma.nivelsuficencia.descripcion ?? ''}
												{:else}
													S/N
												{/if}
											</td>
											<td class="text-center align-middle p-1 fs-6">
												{eIdioma.fechacerti ?? ''}
											</td>
											<td class="text-center align-middle p-1 fs-6">
												{#if eIdioma.download_archivo}
													<a
														href="javascript:;"
														class="text-danger fs-3"
														on:click={() => view_pdf(eIdioma.download_archivo)}
														id="tooltip-idioma-{eIdioma.id}"
													>
														<i class="bi bi-file-pdf" />
													</a>
													<Tooltip target="tooltip-idioma-{eIdioma.id}" placement="bottom"
														>Ver certificación</Tooltip
													>
												{/if}
											</td>
											<td class="text-center align-middle p-1 fs-6">
												<a
													id="tooltip-id_superior-{eIdioma.id}"
													href="javascript:;"
													class="text-info"
													on:click={() =>
														openModal(
															ComponentFormIdioma,
															`Información certificación ${eIdioma.idioma.nombre}`,
															{
																eCertificacion: eIdioma
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
												<Tooltip target="tooltip-id_superior-{eIdioma.id}" placement="top"
													>Para mas información dar click aquí!</Tooltip
												>
											</td>
											<td class="text-center align-middle p-1 fs-6">
												{#if eIdioma.estado != 1}
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
																		ComponentFormIdioma,
																		`Editar certificación ${eIdioma.idioma.nombre}`,
																		{ eCertificacion: eIdioma },
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
																		`<p style='color:#ACAEAF;'>¿Desea eliminar certificación de idioma <b>${eIdioma.idioma.nombre}</b></p>`,
																		eIdioma.pk,
																		'deleteFormacionAcademicaIdioma'
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
										<td colspan="7" class="text-center">No existe registro de idiomas</td>
									</tr>
								{/if}
							</tbody>
						</table>
					</div>
				</div>
			</div>
			<div class="card  mt-4">
				<div class="card-header d-lg-flex justify-content-between align-items-center">
					<div class="headtitle mb-lg-0 m-0">
						<h3 class="mx-2 m-0 p-0">Internacionales</h3>
						<h6 class="mx-2 m-0 p-0">
							Listado de certificados internacionales registradas validados
						</h6>
					</div>
					<div>
						<button
							class="btn btn-success btn-sm rounded-3"
							on:click={() =>
								openModal(
									ComponentFormCertificacion,
									`Adicionar certificación internacional`,
									{
										eCertificacion: undefined
									},
									false
								)}
						>
							<i class="fe fe-plus " /> Adicionar
						</button>
					</div>
				</div>
				<div class="card-body" tabindex="-1">
					<div class="table-responsive scrollbar">
						<table class="table table_primary tabla_responsive table-hover table-centered">
							<thead class="table-light">
								<tr class="fs-6">
									<th class="text-center align-middle p-1" scope="col" style="width:30%;">
										Nombre de la certificación
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:20%;">
										Autoridad emisora de la certificación
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:15%;">
										Fecha Desde / Hasta
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:20%;">
										Archivo / Enlace
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:10%;">
										Info
									</th>
									<th scope="col" style="width:10%; p-1" />
								</tr>
							</thead>
							<tbody>
								{#if eCertificacionesPersona.length}
									{#each eCertificacionesPersona as eCertificacion}
										<tr class="">
											<td class="text-center align-middle p-1 fs-6">
												{eCertificacion.nombres ?? ''}
											</td>
											<td class="text-center align-middle p-1 fs-6">
												{eCertificacion.autoridad_emisora ?? ''}
											</td>
											<td class="text-center align-middle p-1 fs-6">
												{#if eCertificacion.fechadesde}
													{eCertificacion.fechadesde}
												{/if}
												{@html eCertificacion.fechahasta ?? '<br> Nunca expira'}
											</td>
											<td class="text-center align-middle p-1 fs-6">
												{#if eCertificacion.download_archivo}
													<a
														href="javascript:;"
														class="text-danger fs-3"
														on:click={() => view_pdf(eCertificacion.download_archivo)}
														id="tooltip-internacional-{eCertificacion.id}"
													>
														<i class="bi bi-file-pdf" />
													</a>
													<Tooltip
														target="tooltip-internacional-{eCertificacion.id}"
														placement="bottom">Ver certificación</Tooltip
													>
												{/if}
												{#if eCertificacion.enlace}
													<a
														href={eCertificacion.enlace}
														target="_blank"
														class="text-primary fs-3"
														id="tooltip-internacional-url-{eCertificacion.id}"
													>
														<i class="bi bi-link" />
													</a>
													<Tooltip
														target="tooltip-internacional-url-{eCertificacion.id}"
														placement="bottom">URL</Tooltip
													>
													<!--<a
														class="btn btn-link btn-sm text-primary"
														on:click={() => view_pdf(eCertificacion.enlace)}
													>
														<p class="m-0 p-0">
															Ver URL
															<i class="bi bi-link" />
														</p>
													</a>-->
												{/if}
											</td>
											<td class="text-center align-middle p-1 fs-6">
												<a
													id="tooltip-id_info-{eCertificacion.id}"
													href="javascript:;"
													class="text-info"
													on:click={() =>
														openModal(
															ComponentFormCertificacion,
															`Información certificación ${eCertificacion.nombres}`,
															{
																eCertificacion: eCertificacion
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
												<Tooltip target="tooltip-id_info-{eCertificacion.id}" placement="top"
													>Para mas información dar click aquí!</Tooltip
												>
											</td>
											<td class="text-center align-middle p-1">
												{#if !eCertificacion.verificado}
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
																		ComponentFormCertificacion,
																		`Editar certificación ${eCertificacion.nombre}`,
																		{ eCertificacion: eCertificacion },
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
																		`<p style='color:#ACAEAF;'>¿Desea eliminar formación académica <b>${eCertificacion.nombre}</b></p>`,
																		eCertificacion.pk,
																		'deleteFormacionAcademicaCertificacion'
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
										<td colspan="6" class="text-center"
											>No existe registro de certificaciones internacionales</td
										>
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
		mClass={mClassModal}
		{mOpenModal}
		{mView}
		on:actionRun={actionRun}
	/>
{/if}
