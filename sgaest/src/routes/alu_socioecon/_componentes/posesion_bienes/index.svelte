<script lang="ts">
	import ComponentCantidadTVColorHogar from './frmCantidadTVColorHogar.svelte';
	import ComponentCantidadVehiculoHogar from './frmCantidadVehiculoHogar.svelte';
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
	let inputTieneTelefonoConv = false;
	let inputTieneCocinaHorno = false;
	let inputTieneRefrigeradora = false;
	let inputTieneLavadora = false;
	let inputTieneMusica = false;
	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			eFichaSocioeconomica = aData.eFichaSocioeconomica ?? {};
			inputTieneTelefonoConv = eFichaSocioeconomica.tienetelefconv ?? false;
			inputTieneCocinaHorno = eFichaSocioeconomica.tienecocinahorno ?? false;
			inputTieneRefrigeradora = eFichaSocioeconomica.tienerefrig ?? false;
			inputTieneLavadora = eFichaSocioeconomica.tienelavadora ?? false;
			inputTieneMusica = eFichaSocioeconomica.tienemusica ?? false;
		}
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'saveDatosPosesionBienes') {
			const menu = document.getElementById('menu_element_10');
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
			action: 'saveDatosPosesionBienes',
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

	const changeTieneTelefonoConv = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienetelefconv', {
			tienetelefconv: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};

	const changeTieneCocinaHorno = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienecocinahorno', {
			tienecocinahorno: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};

	const changeTieneRefrigeradora = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienerefrig', { tienerefrig: checked ? 'true' : 'false' });
		if (result === false) {
			event.target.checked = !checked;
		}
	};
	const changeTieneLavadora = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienelavadora', {
			tienelavadora: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};
	const changeTieneMusica = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienemusica', { tienemusica: checked ? 'true' : 'false' });
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
						action: 'deletePosesionBienes',
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
							const menu = document.getElementById('menu_element_10');
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
			<h3 class="mb-0">Posesión de bienes</h3>
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
							<span class="align-middle">¿Tiene el hogar servicio de telefóno convencional? </span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienetelefconv"
								on:change={changeTieneTelefonoConv}
								bind:checked={inputTieneTelefonoConv}
							/>
							<label class="form-check-label" for="id_tienetelefconv" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">¿Tiene el hogar cocina con horno? </span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienecocinahorno"
								on:change={changeTieneCocinaHorno}
								bind:checked={inputTieneCocinaHorno}
							/>
							<label class="form-check-label" for="id_tienecocinahorno" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">¿Tiene el hogar una refrigeradora? </span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienerefrig"
								on:change={changeTieneRefrigeradora}
								bind:checked={inputTieneRefrigeradora}
							/>
							<label class="form-check-label" for="id_tienerefrig" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">¿Tiene el hogar una lavadora? </span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienelavadora"
								on:change={changeTieneLavadora}
								bind:checked={inputTieneLavadora}
							/>
							<label class="form-check-label" for="id_tienelavadora" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">¿Tiene el hogar un equipo de sonido? </span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienemusica"
								on:change={changeTieneMusica}
								bind:checked={inputTieneMusica}
							/>
							<label class="form-check-label" for="id_tienemusica" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
				<div class="d-flex align-items-center justify-content-between">
					<h5 class="mb-0 text-truncate">
						<span class="align-middle">¿Cuántos TV a color tienen en el hogar? </span>
					</h5>
					<div>
						{#if eFichaSocioeconomica.canttvcolor}
							<a
								href="javascript:void(0);"
								class="me-1 text-inherit text-warning"
								aria-label="Editar"
								on:click={() => openModalGenerico(ComponentCantidadTVColorHogar, 'Actualizar')}
								data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
							>
							<a
								href="#"
								class="me-1 text-inherit text-danger"
								aria-label="Eliminar"
								on:click={() =>
									eliminarElemento(
										'canttvcolor',
										`¿Estas a punto de eliminar la cantidad de TV a color tienen en el hogar?`
									)}
								data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
							>
						{:else}
							<a
								href="javascript:void(0);"
								on:click={() => openModalGenerico(ComponentCantidadTVColorHogar, 'Adicionar')}
								class="me-1 text-inherit text-success"
								aria-label="Adicionar"
								data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
							>
						{/if}
					</div>
				</div>
				{#if eFichaSocioeconomica.canttvcolor}
					<div class="p-2">
						<span class="text-primary fs-6">{eFichaSocioeconomica.canttvcolor.nombre}</span>
					</div>
				{/if}
			</div>
			<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
				<div class="d-flex align-items-center justify-content-between">
					<h5 class="mb-0 text-truncate">
						<span class="align-middle">¿Cuántos Vehículos de uso exclusivo tiene el hogar?</span>
					</h5>
					<div>
						{#if eFichaSocioeconomica.cantvehiculos}
							<a
								href="javascript:void(0);"
								class="me-1 text-inherit text-warning"
								aria-label="Editar"
								on:click={() => openModalGenerico(ComponentCantidadVehiculoHogar, 'Actualizar')}
								data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
							>
							<a
								href="#"
								class="me-1 text-inherit text-danger"
								aria-label="Eliminar"
								on:click={() =>
									eliminarElemento(
										'cantvehiculos',
										`¿Estas a punto de eliminar la cantidad de Vehículos de uso exclusivo tiene el hogar?`
									)}
								data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
							>
						{:else}
							<a
								href="javascript:void(0);"
								on:click={() => openModalGenerico(ComponentCantidadVehiculoHogar, 'Adicionar')}
								class="me-1 text-inherit text-success"
								aria-label="Adicionar"
								data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
							>
						{/if}
					</div>
				</div>
				{#if eFichaSocioeconomica.cantvehiculos}
					<div class="p-2">
						<span class="text-primary fs-6">{eFichaSocioeconomica.cantvehiculos.nombre}</span>
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
