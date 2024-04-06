<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import ComponentViewPDF from '$components/viewPDF.svelte';
	import ComponentFormulario from './form.svelte';
	import { navigating } from '$app/stores';
	import { loading } from '$lib/store/loadingStore';
	import { Tooltip } from 'sveltestrap';
	import { apiPOST } from '$lib/utils/requestUtils';
	import Swal from 'sweetalert2';
	import { addToast } from '$lib/store/toastStore';
	let mOpenModal = false;
	let mTitleModal;
	let mClassModal =
		'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
	let mSizeModal = 'lg';
	const mToggleModal = () => (mOpenModal = !mOpenModal);
	let modalDetalleContent;
	export let aData;
	let aDataModal;
	let eDeportistas = [];
	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			eDeportistas = aData.eDeportistas ?? [];
		}
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'saveDeporteCulturaDeportista') {
			mOpenModal = !mOpenModal;
			const menu = document.getElementById('menu_element_11');
			menu.click();
		}
	};

	const openModal = (eDeportista, title) => {
		modalDetalleContent = ComponentFormulario;
		mOpenModal = !mOpenModal;
		mTitleModal = title;
		aDataModal = { eDeportista: eDeportista };
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
						const menu = document.getElementById('menu_element_11');
						menu.click();
					}
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
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
</script>

{#if eDeportistas}
	<div class="card">
		<div class="card-header d-sm-flex justify-content-between align-items-center">
			<div class="headtitle  mb-lg-0 m-0">
				<h3 class="mx-2 m-0 p-0">Eventos de deporte</h3>
				<h6 class="mx-2 m-0 p-0 ">Listado de eventos asistidos</h6>
			</div>
			<div>
				<button
					class="btn btn-success btn-sm"
					on:click={() => openModal(undefined, 'Adicionar registro')}
					><i class="fe fe-plus " /> Adicionar</button
				>
			</div>
		</div>
		<div class="card-body">
			<div class="table-responsive scrollbar">
				<table class="table table_primary tabla_responsive">
					<thead class="table-light">
						<tr>
							<th class="text-center align-middle p-1" style="width: 20%;">Disciplinas</th>
							<th class="text-center align-middle p-1" style="width: 30%;">Evento/País/Equipo</th>
							<th class="text-center align-middle p-1" style="width: 30%;">Fechas</th>
							<th class="text-center align-middle p-1" style="width: 10%;">Documentos</th>
							<th class="text-center align-middle p-1" style="width: 10%;">Vigente</th>
							<th class="text-center align-middle p-1" style="width: 10%;" />
						</tr>
					</thead>
					<tbody>
						{#if eDeportistas.length > 0}
							{#each eDeportistas as eDeportista}
								<tr>
									<td class="text-left align-middle p-1 fs-6">
										{#if eDeportista.disciplina}
											<ul class="list-group ">
												{#each eDeportista.disciplina as eDisciplinaDeportiva}
													<li class="list-group-item border-0 m-0 p-0">
														<input
															class="form-check-input me-1"
															type="checkbox"
															value=""
															disabled
															checked
														/>
														{eDisciplinaDeportiva.descripcion}
													</li>
												{/each}
											</ul>
										{/if}
									</td>
									<td class="text-left align-middle p-1 fs-6">
										<ul class="list-group ">
											<li class="list-group-item border-0 m-0 p-0">
												<input
													class="form-check-input me-1"
													type="checkbox"
													value=""
													disabled
													checked
												/>
												<span><b>Evento:</b> {eDeportista.evento}</span>
											</li>
											{#if eDeportista.paisevento}
												<li class="list-group-item border-0 m-0 p-0">
													<input
														class="form-check-input me-1"
														type="checkbox"
														value=""
														disabled
														checked
													/>
													<span><b>País:</b> {eDeportista.paisevento.nombre}</span>
												</li>
											{/if}
											{#if eDeportista.equiporepresenta}
												<li class="list-group-item border-0 m-0 p-0">
													<input
														class="form-check-input me-1"
														type="checkbox"
														value=""
														disabled
														checked
													/>
													<span><b>Equipo:</b> {eDeportista.equiporepresenta}</span>
												</li>
											{/if}
										</ul>
									</td>
									<td class="text-left align-middle p-1 fs-6">
										<ul class="list-group ">
											{#if eDeportista.fechainicioevento}
												<li class="list-group-item border-0 m-0 p-0">
													<input
														class="form-check-input me-1"
														type="checkbox"
														value=""
														disabled
														checked
														aria-label="..."
													/>
													<span><b>Fecha inicio evento:</b> {eDeportista.fechainicioevento}</span>
												</li>
											{/if}
											{#if eDeportista.fechafinevento}
												<li class="list-group-item border-0 m-0 p-0">
													<input
														class="form-check-input me-1"
														type="checkbox"
														value=""
														disabled
														checked
														aria-label="..."
													/>
													<span><b>Fecha fin evento:</b> {eDeportista.fechafinevento}</span>
												</li>
											{/if}
											{#if eDeportista.fechainicioentrena}
												<li class="list-group-item border-0 m-0 p-0">
													<input
														class="form-check-input me-1"
														type="checkbox"
														value=""
														disabled
														checked
														aria-label="..."
													/>
													<span><b>Fecha inicio entrena:</b> {eDeportista.fechainicioentrena}</span>
												</li>
											{/if}
											{#if eDeportista.fechafinentrena}
												<li class="list-group-item border-0 m-0 p-0">
													<input
														class="form-check-input me-1"
														type="checkbox"
														value=""
														disabled
														checked
														aria-label="..."
													/>
													<span><b>Fecha fin entrena:</b> {eDeportista.fechafinentrena}</span>
												</li>
											{/if}
										</ul>
									</td>
									<td class="text-center align-middle p-1 fs-6">
										{#if eDeportista.download_archivoevento}
											<a
												href="javascript:;"
												class="text-danger fs-3"
												on:click={() => view_pdf(eDeportista.download_archivoevento)}
												id="tooltip-id-evento-{eDeportista.id}"
											>
												<i class="bi bi-file-pdf" />
											</a>
											<Tooltip target="tooltip-id-evento-{eDeportista.id}" placement="bottom"
												>Ver archivo evento</Tooltip
											>
										{/if}
										{#if eDeportista.download_archivoentrena}
											<a
												href="javascript:;"
												class="text-primary fs-3"
												on:click={() => view_pdf(eDeportista.download_archivoentrena)}
												id="tooltip-id-entrena-{eDeportista.id}"
											>
												<i class="bi bi-file-pdf" />
											</a>
											<Tooltip target="tooltip-id-entrena-{eDeportista.id}" placement="bottom"
												>Ver archivo entrenamiento</Tooltip
											>
										{/if}
									</td>
									<td class="text-center align-middle p-1 fs-6">
										{#if eDeportista.vigente}
											<i
												class="fe fe-check text-success fw-bold"
												id="tooltip-estado-id-{eDeportista.id}"
											/>
											<Tooltip target="tooltip-estado-id-{eDeportista.id}" placement="left"
												>Vigente</Tooltip
											>
										{:else}
											<i
												class="fe fe-x text-danger fw-bold"
												id="tooltip-estado-id-{eDeportista.id}"
											/>
											<Tooltip target="tooltip-estado-id-{eDeportista.id}" placement="left"
												>No Vigente</Tooltip
											>
										{/if}
									</td>
									<td class="align-middle text-center p-1 fs-6">
										{#if !eDeportista.verificado}
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
														on:click={() => openModal(eDeportista, 'Editar registro de deportista')}
													>
														<i class="fe fe-edit dropdown-item-icon" />Editar
													</a>

													<a
														class="dropdown-item"
														href="#eliminar"
														on:click={() =>
															eliminarRegistro(
																`<p style='color:#ACAEAF;'>¿Desea eliminar datos de deportista?</p>`,
																eDeportista.pk,
																'deleteDatosDeportista'
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
