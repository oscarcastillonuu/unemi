<script lang="ts">
	import ComponentCantidadCelularHogar from './frmCantidadCelularHogar.svelte';
	import ComponentProveedorServicio from './frmProveedorServicio.svelte';
	import { createEventDispatcher, onMount } from 'svelte';
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
	let inputTieneInternet = false;
	let inputTieneDesktop = false;
	let inputTieneLaptop = false;
	let inputInternetPanf = false;
	let inputEquipoTieneCamara = false;

	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			eFichaSocioeconomica = aData.eFichaSocioeconomica ?? {};
			inputTieneInternet = eFichaSocioeconomica.tieneinternet ?? false;
			inputTieneDesktop = eFichaSocioeconomica.tienedesktop ?? false;
			inputTieneLaptop = eFichaSocioeconomica.tienelaptop ?? false;
			inputInternetPanf = eFichaSocioeconomica.internetpanf ?? false;
			inputEquipoTieneCamara = eFichaSocioeconomica.equipotienecamara ?? false;
		}
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'saveDatosAccesoTecnologia') {
			const menu = document.getElementById('menu_element_11');
			menu.click();
			mOpenModal = !mOpenModal;
		}
	};

	const saveElemento = async (field, data) => {
		loading.setLoading(true, 'Procesando la información, espere por favor...');
		if (browserGet('refreshToken')) {
			const response = await getCurrentRefresh(fetch, `${variables.BASE_API_URI}/token/refresh`);
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
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/socioeconomica', {
			action: 'saveDatosAccesoTecnologia',
			field: field,
			...data
		});
		loading.setLoading(false, 'Guardando la información, espere por favor...');
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			loading.setLoading(false, 'Cargando, espere por favor...');
			return false;
		} else {
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (!res.isSuccess) {
				addToast({ type: 'error', header: '¡ERROR!', body: res.message });
				return false;
			} else {
				addToast({
					type: 'success',
					header: 'Exitoso',
					body: 'Se guardo correctamente los datos'
				});
				return true;
			}
		}
		return false;
	};

	const changeTieneInternet = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tieneinternet', {
			tieneinternet: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};

	const changeTieneDesktop = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienedesktop', {
			tienedesktop: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};

	const changeTieneLaptop = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienelaptop', { tienelaptop: checked ? 'true' : 'false' });
		if (result === false) {
			event.target.checked = !checked;
		}
	};

	const changeInternetPanf = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('internetpanf', { internetpanf: checked ? 'true' : 'false' });
		if (result === false) {
			event.target.checked = !checked;
		}
	};

	const changeEquipoTieneCamara = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('equipotienecamara', {
			equipotienecamara: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
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
						action: 'deleteAccesoTecnologia',
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
							const menu = document.getElementById('menu_element_11');
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
			<h3 class="mb-0">Acceso a tecnología</h3>
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
							<span class="align-middle">¿Tiene el hogar servicio de internet? </span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tieneinternet"
								on:change={changeTieneInternet}
								bind:checked={inputTieneInternet}
							/>
							<label class="form-check-label" for="id_tieneinternet" />
						</div>
					</div>
				</div>
			</div>
			{#if inputTieneInternet}
				<div class="list-group list-group-flush border-1 ">
					<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
						<div class="d-flex align-items-center justify-content-between">
							<h5 class="mb-0 text-truncate">
								<span class="align-middle"
									>¿Su conexión de internet es de una persona ajena a su núcleo familiar?
								</span>
							</h5>
							<div class="form-check form-switch">
								<input
									type="checkbox"
									class="form-check-input"
									id="id_internetpanf"
									on:change={changeInternetPanf}
									bind:checked={inputInternetPanf}
								/>
								<label class="form-check-label" for="id_internetpanf" />
							</div>
						</div>
					</div>
				</div>
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">¿Cuál es su proveedor de servicio de internet? </span>
						</h5>
						<div>
							{#if eFichaSocioeconomica.proveedorinternet}
								<a
									href="javascript:void(0);"
									class="me-1 text-inherit text-warning"
									aria-label="Editar"
									on:click={() => openModalGenerico(ComponentProveedorServicio, 'Actualizar')}
									data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
								>
								<a
									href="#"
									class="me-1 text-inherit text-danger"
									aria-label="Eliminar"
									on:click={() =>
										eliminarElemento(
											'proveedorinternet',
											'¿Estas a punto de eliminar el proveedor de internet?'
										)}
									data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
								>
							{:else}
								<a
									href="javascript:void(0);"
									on:click={() => openModalGenerico(ComponentProveedorServicio, 'Adicionar')}
									class="me-1 text-inherit text-success"
									aria-label="Adicionar"
									data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
								>
							{/if}
						</div>
					</div>
					{#if eFichaSocioeconomica.proveedorinternet}
						<div class="p-2">
							<span class="text-primary fs-6">{eFichaSocioeconomica.proveedorinternet.nombre}</span>
						</div>
					{/if}
				</div>
			{/if}
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">¿Tiene computadora de escritorio? </span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienedesktop"
								on:change={changeTieneDesktop}
								bind:checked={inputTieneDesktop}
							/>
							<label class="form-check-label" for="id_tienedesktop" />
						</div>
					</div>
				</div>
			</div>
			{#if inputTieneDesktop}
				<div class="list-group list-group-flush border-1 ">
					<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
						<div class="d-flex align-items-center justify-content-between">
							<h5 class="mb-0 text-truncate">
								<span class="align-middle">¿Su equipo cuenta con cámara? </span>
							</h5>
							<div class="form-check form-switch">
								<input
									type="checkbox"
									class="form-check-input"
									id="id_equipotienecamara"
									on:change={changeEquipoTieneCamara}
									bind:checked={inputEquipoTieneCamara}
								/>
								<label class="form-check-label" for="id_equipotienecamara" />
							</div>
						</div>
					</div>
				</div>
			{/if}

			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">¿Tiene computadora portátil? </span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienelaptop"
								on:change={changeTieneLaptop}
								bind:checked={inputTieneLaptop}
							/>
							<label class="form-check-label" for="id_tienelaptop" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
				<div class="d-flex align-items-center justify-content-between">
					<h5 class="mb-0 text-truncate">
						<span class="align-middle">¿Cuántos celulares activados tienen en el hogar? </span>
					</h5>
					<div>
						{#if eFichaSocioeconomica.cantcelulares}
							<a
								href="javascript:void(0);"
								class="me-1 text-inherit text-warning"
								aria-label="Editar"
								on:click={() => openModalGenerico(ComponentCantidadCelularHogar, 'Actualizar')}
								data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
							>
							<a
								href="#"
								class="me-1 text-inherit text-danger"
								aria-label="Eliminar"
								on:click={() =>
									eliminarElemento(
										'cantcelulares',
										'¿Estas a punto de eliminar la cantidad de celulares?'
									)}
								data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
							>
						{:else}
							<a
								href="javascript:void(0);"
								on:click={() => openModalGenerico(ComponentCantidadCelularHogar, 'Adicionar')}
								class="me-1 text-inherit text-success"
								aria-label="Adicionar"
								data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
							>
						{/if}
					</div>
				</div>
				{#if eFichaSocioeconomica.cantcelulares}
					<div class="p-2">
						<span class="text-primary fs-6">{eFichaSocioeconomica.cantcelulares.nombre}</span>
					</div>
				{/if}
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
