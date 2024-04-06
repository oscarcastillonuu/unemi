<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import ComponentTipoVivienda from './frmTipoVivienda.svelte';
	import ComponentTipoViviendaPro from './frmTipoViviendaPro.svelte';
	import ComponentMaterialPared from './frmMaterialPared.svelte';
	import ComponentMaterialPiso from './frmMaterialPiso.svelte';
	import ComponentCantidadBannoDucha from './frmCantidadBannoDucha.svelte';
	import ComponentTipoServicioHigienico from './frmTipoServicioHigienico.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { apiPOST, browserGet, browserSet, getCurrentRefresh } from '$lib/utils/requestUtils';
	import { variables } from '$lib/utils/constants';
	import { goto } from '$app/navigation';
	import { decodeToken } from '$lib/utils/decodetoken';
	import { userData } from '$lib/store/userStore';
	import { addToast } from '$lib/store/toastStore';
	import Swal from 'sweetalert2';
	import { addNotification } from '$lib/store/notificationStore';
	import { navigating } from '$app/stores';
	let mOpenModal = false;
	const mToggleModal = () => (mOpenModal = !mOpenModal);
	let modalDetalleContent;
	let modalTitle;
	export let aData;
	let aDataModal;
	let eFichaSocioeconomica = {};
	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			eFichaSocioeconomica = aData.eFichaSocioeconomica ?? {};
		}
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'saveDatosCaracteristicaVivienda') {
			const menu = document.getElementById('menu_element_8');
			menu.click();
			mOpenModal = !mOpenModal;
		}
	};

	const openModalGenerico = (componente, title) => {
		modalDetalleContent = componente;
		mOpenModal = !mOpenModal;
		modalTitle = title;
		aDataModal = { eFichaSocioeconomica: eFichaSocioeconomica };
	};

	const eliminarElemento = async (field, texto) => {
		const mensaje = {
			title: `${texto}`,
			html: `Esta acción es irreversible`,
			type: 'warning',
			icon: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: `Si, deseo hacerlo!`,
			cancelButtonText: 'No, cancelar'
		};
		Swal.fire(mensaje)
			.then(async (result) => {
				if (result.value) {
					loading.setLoading(true, 'Procesando la información, espere por favor...');
					if (browserGet('refreshToken')) {
						const response = await getCurrentRefresh(
							fetch,
							`${variables.BASE_API_URI}/token/refresh`
						);
						if (response.status >= 400) {
							goto('/lock-screen');
						}
						if (response.ok == true) {
							const json = decodeToken(await response.json());
							browserSet('refreshToken', json.tokens.refresh);
							browserSet('accessToken', json.tokens.access);
							browserSet('dataSession', JSON.stringify(json));
							userData.set(json);
						}
					} else {
						goto('/login');
					}
					loading.setLoading(true, 'Eliminando la información, espere por favor...');
					const [res, errors] = await apiPOST(fetch, 'alumno/socioeconomica', {
						action: 'deleteCaracteristicaVivivenda',
						field: field
					});
					loading.setLoading(false, 'Eliminando la información, espere por favor...');
					if (errors.length > 0) {
						addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
						loading.setLoading(false, 'Cargando, espere por favor...');
						return;
					} else {
						loading.setLoading(false, 'Cargando, espere por favor...');
						if (!res.isSuccess) {
							addToast({ type: 'error', header: '¡ERROR!', body: res.message });
							return;
						} else {
							addToast({
								type: 'success',
								header: 'Exitoso',
								body: 'Se elimino correctamente la información'
							});
							const menu = document.getElementById('menu_element_8');
							menu.click();
						}
					}
				} else {
					loading.setLoading(false, 'Cargando, espere por favor...');
					addNotification({
						msg: 'Enhorabuena el registro esta salvado.!',
						type: 'info'
					});
				}
			})
			.catch((error) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				addNotification({
					msg: error.message,
					type: 'error'
				});
			});
	};
</script>

<div class="card border-0 mx-0">
	<div class="card-header d-lg-flex justify-content-between align-items-center">
		<div class="mb-3 mb-lg-0">
			<h3 class="mb-0">Características de la vivienda</h3>
			<!--<p class="mb-0">Here is list of package/product that you have subscribed.</p>-->
		</div>
		<!--<div>
				<button class="btn btn-success btn-sm" on:click={() => openModalEdit()}>Editar</button>
			</div>-->
	</div>
	<div class="card-body">
		<div class="bg-light rounded border-1 p-2 mb-4">
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">¿Cuál es el tipo de vivienda? </span>
						</h5>
						<div>
							{#if eFichaSocioeconomica.tipovivienda}
								<a
									href="javascript:void(0);"
									class="me-1 text-inherit text-warning"
									aria-label="Editar"
									on:click={() => openModalGenerico(ComponentTipoVivienda, 'Actualizar')}
									data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
								>
								<a
									href="#"
									class="me-1 text-inherit text-danger"
									aria-label="Eliminar"
									on:click={() =>
										eliminarElemento(
											'tipovivienda',
											'¿Estas a punto de eliminar el tipo de vivienda?'
										)}
									data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
								>
							{:else}
								<a
									href="javascript:void(0);"
									on:click={() => openModalGenerico(ComponentTipoVivienda, 'Adicionar')}
									class="me-1 text-inherit text-success"
									aria-label="Adicionar"
									data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
								>
							{/if}
						</div>
					</div>
					{#if eFichaSocioeconomica.tipovivienda}
						<div class="p-2">
							<span class="text-primary fs-6">{eFichaSocioeconomica.tipovivienda.nombre}</span>
						</div>
					{/if}
				</div>
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle"
								>¿Su vivienda es propia o arrendada o cedida por familiares?
							</span>
						</h5>
						<div>
							{#if eFichaSocioeconomica.tipoviviendapro}
								<a
									href="javascript:void(0);"
									class="me-1 text-inherit text-warning"
									aria-label="Editar"
									on:click={() => openModalGenerico(ComponentTipoViviendaPro, 'Actualizar')}
									data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
								>
								<a
									href="#"
									class="me-1 text-inherit text-danger"
									aria-label="Eliminar"
									on:click={() =>
										eliminarElemento(
											'tipoviviendapro',
											`¿Estas a punto de eliminar su vivenda ${eFichaSocioeconomica.tipoviviendapro}?`
										)}
									data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
								>
							{:else}
								<a
									href="javascript:void(0);"
									on:click={() => openModalGenerico(ComponentTipoViviendaPro, 'Adicionar')}
									class="me-1 text-inherit text-success"
									aria-label="Adicionar"
									data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
								>
							{/if}
						</div>
					</div>
					{#if eFichaSocioeconomica.tipoviviendapro}
						<div class="p-2">
							<span class="text-primary fs-6">{eFichaSocioeconomica.tipoviviendapro.nombre}</span>
						</div>
					{/if}
				</div>
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Material Predominante en las paredes </span>
						</h5>
						<div>
							{#if eFichaSocioeconomica.materialpared}
								<a
									href="javascript:void(0);"
									class="me-1 text-inherit text-warning"
									aria-label="Editar"
									on:click={() => openModalGenerico(ComponentMaterialPared, 'Actualizar')}
									data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
								>
								<a
									href="#"
									class="me-1 text-inherit text-danger"
									aria-label="Eliminar"
									on:click={() =>
										eliminarElemento(
											'materialpared',
											`¿Estas a punto de eliminar el dato del material predominante en las paredes?`
										)}
									data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
								>
							{:else}
								<a
									href="javascript:void(0);"
									on:click={() => openModalGenerico(ComponentMaterialPared, 'Adicionar')}
									class="me-1 text-inherit text-success"
									aria-label="Adicionar"
									data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
								>
							{/if}
						</div>
					</div>
					{#if eFichaSocioeconomica.materialpared}
						<div class="p-2">
							<span class="text-primary fs-6">{eFichaSocioeconomica.materialpared.nombre}</span>
						</div>
					{/if}
				</div>
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Material Predominante en el piso </span>
						</h5>
						<div>
							{#if eFichaSocioeconomica.materialpiso}
								<a
									href="javascript:void(0);"
									class="me-1 text-inherit text-warning"
									aria-label="Editar"
									on:click={() => openModalGenerico(ComponentMaterialPiso, 'Actualizar')}
									data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
								>
								<a
									href="#"
									class="me-1 text-inherit text-danger"
									aria-label="Eliminar"
									on:click={() =>
										eliminarElemento(
											'materialpiso',
											`¿Estas a punto de eliminar el dato del material predominante en el piso?`
										)}
									data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
								>
							{:else}
								<a
									href="javascript:void(0);"
									on:click={() => openModalGenerico(ComponentMaterialPiso, 'Adicionar')}
									class="me-1 text-inherit text-success"
									aria-label="Adicionar"
									data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
								>
							{/if}
						</div>
					</div>
					{#if eFichaSocioeconomica.materialpiso}
						<div class="p-2">
							<span class="text-primary fs-6">{eFichaSocioeconomica.materialpiso.nombre}</span>
						</div>
					{/if}
				</div>
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">¿Cuántos cuartos de baño con ducha tiene el hogar? </span>
						</h5>
						<div>
							{#if eFichaSocioeconomica.cantbannoducha}
								<a
									href="javascript:void(0);"
									class="me-1 text-inherit text-warning"
									aria-label="Editar"
									on:click={() => openModalGenerico(ComponentCantidadBannoDucha, 'Actualizar')}
									data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
								>
								<a
									href="#"
									class="me-1 text-inherit text-danger"
									aria-label="Eliminar"
									on:click={() =>
										eliminarElemento(
											'cantbannoducha',
											`¿Estas a punto de eliminar datos de cantidad de baños con duchas?`
										)}
									data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
								>
							{:else}
								<a
									href="javascript:void(0);"
									on:click={() => openModalGenerico(ComponentCantidadBannoDucha, 'Adicionar')}
									class="me-1 text-inherit text-success"
									aria-label="Adicionar"
									data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
								>
							{/if}
						</div>
					</div>
					{#if eFichaSocioeconomica.cantbannoducha}
						<div class="p-2">
							<span class="text-primary fs-6">{eFichaSocioeconomica.cantbannoducha.nombre}</span>
						</div>
					{/if}
				</div>
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle"
								>El tipo de servicio higiénico con que cuenta el hogar es:
							</span>
						</h5>
						<div>
							{#if eFichaSocioeconomica.tiposervhig}
								<a
									href="javascript:void(0);"
									class="me-1 text-inherit text-warning"
									aria-label="Editar"
									on:click={() => openModalGenerico(ComponentTipoServicioHigienico, 'Actualizar')}
									data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
								>
								<a
									href="#"
									class="me-1 text-inherit text-danger"
									aria-label="Eliminar"
									on:click={() =>
										eliminarElemento(
											'tiposervhig',
											`¿Estas a punto de eliminar el tipo de servicio higiénico?`
										)}
									data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
								>
							{:else}
								<a
									href="javascript:void(0);"
									on:click={() => openModalGenerico(ComponentTipoServicioHigienico, 'Adicionar')}
									class="me-1 text-inherit text-success"
									aria-label="Adicionar"
									data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
								>
							{/if}
						</div>
					</div>
					{#if eFichaSocioeconomica.tiposervhig}
						<div class="p-2">
							<span class="text-primary fs-6">{eFichaSocioeconomica.tiposervhig.nombre}</span>
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
</div>
{#if mOpenModal}
	<svelte:component
		this={modalDetalleContent}
		aData={aDataModal}
		mTitle={modalTitle}
		mToggle={mToggleModal}
		on:actionRun={actionRun}
	/>
{/if}
