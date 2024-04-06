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
	let eArtistas = [];
	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			eArtistas = aData.eArtistas ?? [];
		}
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'saveDeporteCulturaArtista') {
			mOpenModal = !mOpenModal;
			const menu = document.getElementById('menu_element_10');
			menu.click();
		}
	};

	const openModal = (eArtista, title) => {
		modalDetalleContent = ComponentFormulario;
		mOpenModal = !mOpenModal;
		mTitleModal = title;
		aDataModal = { eArtista: eArtista };
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
						const menu = document.getElementById('menu_element_10');
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

{#if eArtistas}
	<div class="card">
		<div class="card-header d-sm-flex justify-content-between align-items-center">
			<div class="headtitle  mb-lg-0 m-0">
				<h3 class="mx-2 m-0 p-0">Artista</h3>
				<h6 class="mx-2 m-0 p-0 ">Listado de información registrada</h6>
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
							<th class="text-center align-middle p-1" style="width: 20%;">Campos artísticos</th>
							<th class="text-center align-middle p-1" style="width: 20%;">Grupo pertenece</th>
							<th class="text-center align-middle p-1" style="width: 30%;">Fechas</th>
							<th class="text-center align-middle p-1" style="width: 6%;">Documento</th>
							<th class="text-center align-middle p-1" style="width: 6%;">Vigente</th>
							<th />
						</tr>
					</thead>
					<tbody>
						{#if eArtistas.length > 0}
							{#each eArtistas as eArtista}
								<tr>
									<td class="text-left align-middle p-1 fs-6">
										{#if eArtista.campoartistico}
											<ul class="list-group ">
												{#each eArtista.campoartistico as eCampoArtistico}
													<li class="list-group-item border-0 m-0 p-0">
														<input
															class="form-check-input me-1"
															type="checkbox"
															value=""
															disabled
															checked
														/>
														{eCampoArtistico.descripcion}
													</li>
												{/each}
											</ul>
										{/if}
									</td>
									<td class="text-center align-middle p-1 fs-6">
										{eArtista.grupopertenece}
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
													aria-label="..."
												/>
												<span><b>Fecha inicio:</b> {eArtista.fechainicioensayo}</span>
											</li>
											{#if eArtista.fechafinensayo}
												<li class="list-group-item border-0 m-0 p-0">
													<input
														class="form-check-input me-1"
														type="checkbox"
														value=""
														disabled
														checked
														aria-label="..."
													/>
													<span><b>Fecha fin:</b> {eArtista.fechafinensayo}</span>
												</li>
											{/if}
										</ul>
									</td>
									<td class="text-center align-middle p-1 fs-6">
										{#if eArtista.download_archivo}
											<a
												href="javascript:;"
												class="text-danger fs-3"
												on:click={() => view_pdf(eArtista.download_archivo)}
												id="tooltip-id-{eArtista.id}"
											>
												<i class="bi bi-file-pdf" />
											</a>
											<Tooltip target="tooltip-id-{eArtista.id}" placement="bottom"
												>Ver archivo</Tooltip
											>
										{/if}
									</td>
									<td class="text-center align-middle p-1 fs-6">
										{#if eArtista.vigente}
											<i
												class="fe fe-check text-success fw-bold"
												id="tooltip-estado-id-{eArtista.id}"
											/>
											<Tooltip target="tooltip-estado-id-{eArtista.id}" placement="left"
												>Vigente</Tooltip
											>
										{:else}
											<i class="fe fe-x text-danger fw-bold" id="tooltip-estado-id-{eArtista.id}" />
											<Tooltip target="tooltip-estado-id-{eArtista.id}" placement="left"
												>No Vigente</Tooltip
											>
										{/if}
									</td>
									<td class="align-middle text-center p-1 fs-6">
										{#if !eArtista.verificado}
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
														on:click={() => openModal(eArtista, 'Editar registro de artista')}
													>
														<i class="fe fe-edit dropdown-item-icon" />Editar
													</a>

													<a
														class="dropdown-item"
														href="#eliminar"
														on:click={() =>
															eliminarRegistro(
																`<p style='color:#ACAEAF;'>¿Desea eliminar datos de artista?</p>`,
																eArtista.pk,
																'deleteDatosArtista'
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
