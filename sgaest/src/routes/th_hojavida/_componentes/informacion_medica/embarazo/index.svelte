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
	let ePersonaDetalleMaternidades = [];
	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			ePersonaDetalleMaternidades = aData.ePersonaDetalleMaternidades ?? [];
		}
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'saveDatosPersonalesEmbarazo') {
			mOpenModal = !mOpenModal;
			const menu = document.getElementById('menu_element_6');
			menu.click();
		}
	};

	const openModal = (ePersonaDetalleMaternidad, title) => {
		modalDetalleContent = ComponentFormulario;
		mOpenModal = !mOpenModal;
		mTitleModal = title;
		aDataModal = { ePersonaDetalleMaternidad: ePersonaDetalleMaternidad };
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
						const menu = document.getElementById('menu_element_6');
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

{#if ePersonaDetalleMaternidades}
	<div class="card">
		<div class="card-header d-sm-flex justify-content-between align-items-center">
			<div class="headtitle  mb-lg-0 m-0">
				<h3 class="mx-2 m-0 p-0">Gestación</h3>
				<h6 class="mx-2 m-0 p-0 ">Listado de embarazos registrados</h6>
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
							<th class="text-center align-middle p-1">Inicio</th>
							<th class="text-center align-middle p-1">Parto</th>
							<th class="text-center align-middle p-1">Nro. semanas</th>
							<th class="text-center align-middle p-1">¿Se encuentra en lactancia?</th>
							<th />
						</tr>
					</thead>
					<tbody>
						{#if ePersonaDetalleMaternidades.length > 0}
							{#each ePersonaDetalleMaternidades as ePersonaDetalleMaternidad}
								<tr>
									<td class="text-center align-middle"
										>{ePersonaDetalleMaternidad.fechainicioembarazo}</td
									>
									<td class="text-center align-middle">
										{#if ePersonaDetalleMaternidad.fechaparto}
											{ePersonaDetalleMaternidad.fechaparto}
										{:else}
											<p class="m-0 p-0" style="color: #172c54">Gestación</p>
										{/if}
									</td>
									<td class="text-center align-middle">
										{#if ePersonaDetalleMaternidad.semanasembarazo}
											{ePersonaDetalleMaternidad.semanasembarazo}
										{/if}
									</td>
									<td class="text-center align-middle">
										{#if ePersonaDetalleMaternidad.lactancia}
											<i class="fe fe-check text-success" />
										{:else}
											<i class="fe fe-x text-danger" />
										{/if}
									</td>
									<td class="align-middle text-center">
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
														openModal(ePersonaDetalleMaternidad, 'Editar registro de gestación')}
												>
													<i class="fe fe-edit dropdown-item-icon" />Editar
												</a>

												<a
													class="dropdown-item"
													href="#eliminar"
													on:click={() =>
														eliminarRegistro(
															`<p style='color:#ACAEAF;'>¿Desea eliminar datos de gestación</p>`,
															ePersonaDetalleMaternidad.pk,
															'deleteDatosPersonalesEmbarazo'
														)}
												>
													<i class="fe fe-trash dropdown-item-icon" />Eliminar
												</a>
											</div>
										</div></td
									>
								</tr>
							{/each}
						{:else}
							<tr>
								<td colspan="5" class="text-center">Sin registros existentes</td>
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
