<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import ComponentTipoHogar from './frmTipoHogar.svelte';
	import ComponentPersonaCubreGasto from './frmPersonaCubreGasto.svelte';
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
	let inputEsCabezaFamiliar = false;
	let inputEsDependiente = false;
	let eFichaSocioeconomica = {};
	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			eFichaSocioeconomica = aData.eFichaSocioeconomica ?? {};
			inputEsCabezaFamiliar = eFichaSocioeconomica.escabezafamilia ?? false;
			inputEsDependiente = eFichaSocioeconomica.esdependiente ?? false;
		}
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'saveDatosEstructuraFamiliar') {
			const menu = document.getElementById('menu_element_6');
			menu.click();
			mOpenModal = !mOpenModal;
		}
	};

	const openModalTipoHogar = (title) => {
		modalDetalleContent = ComponentTipoHogar;
		mOpenModal = !mOpenModal;
		modalTitle = title;
		aDataModal = { eFichaSocioeconomica: eFichaSocioeconomica };
	};

	const openModalPersonaCubreGasto = (title) => {
		modalDetalleContent = ComponentPersonaCubreGasto;
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
						action: 'deleteEstructuraFamiliar',
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
							const menu = document.getElementById('menu_element_6');
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
			action: 'saveDatosEstructuraFamiliar',
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
				// const menu = document.getElementById('menu_element_6');
				// menu.click();
				return true;
			}
		}
		return false;
	};

	const changeEsCabezaFamiliar = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('escabezafamilia', {
			escabezafamilia: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};

	const changeEsDependiente = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('esdependiente', {
			esdependiente: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};
</script>

<div class="card border-0 mx-0">
	<div class="card-header d-lg-flex justify-content-between align-items-center">
		<div class="mb-3 mb-lg-0">
			<h3 class="mb-0">Estructura familiar y datos económicos</h3>
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
							<span class="align-middle">Tipo De Hogar: </span>
						</h5>
						<div>
							{#if eFichaSocioeconomica.tipohogar}
								<a
									href="javascript:void(0);"
									class="me-1 text-inherit text-warning"
									aria-label="Editar"
									on:click={() => openModalTipoHogar('Actualizar tipo de hogar')}
									data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
								>
								<a
									href="#"
									class="me-1 text-inherit text-danger"
									aria-label="Eliminar"
									on:click={() =>
										eliminarElemento('tipohogar', '¿Estas a punto de eliminar el tipo de hogar?')}
									data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
								>
							{:else}
								<a
									href="javascript:void(0);"
									on:click={() => openModalTipoHogar('Adicionar tipo de hogar')}
									class="me-1 text-inherit text-success"
									aria-label="Adicionar"
									data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
								>
							{/if}
						</div>
					</div>
					{#if eFichaSocioeconomica.tipohogar}
						<div class="p-2">
							<span class="text-primary fs-6">{eFichaSocioeconomica.tipohogar.nombre}</span>
						</div>
					{/if}
				</div>
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">¿El estudiante es cabeza de familia? </span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_escabezafamilia"
								on:change={changeEsCabezaFamiliar}
								bind:checked={inputEsCabezaFamiliar}
							/>
							<label class="form-check-label" for="id_escabezafamilia" />
						</div>
					</div>
				</div>
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle"
								>¿El estudiante depende económicamente de sus padres u otras personas?
							</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_esdependiente"
								on:change={changeEsDependiente}
								bind:checked={inputEsDependiente}
							/>
							<label class="form-check-label" for="id_esdependiente" />
						</div>
					</div>
				</div>
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">¿Quién cubre los gastos del estudiante? </span>
						</h5>
						<div>
							{#if eFichaSocioeconomica.personacubregasto}
								<a
									href="javascript:void(0);"
									class="me-1 text-inherit text-warning"
									aria-label="Editar"
									on:click={() => openModalPersonaCubreGasto('Actualizar quien cubre gastos')}
									data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
								>
								<a
									href="#"
									class="me-1 text-inherit text-danger"
									aria-label="Eliminar"
									on:click={() =>
										eliminarElemento(
											'personacubregasto',
											'¿Estas a punto de eliminar quien cubre gastos?'
										)}
									data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
								>
							{:else}
								<a
									href="javascript:void(0);"
									on:click={() => openModalPersonaCubreGasto('Adicionar quien cubre gastos')}
									class="me-1 text-inherit text-success"
									aria-label="Adicionar"
									data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
								>
							{/if}
						</div>
					</div>
					{#if eFichaSocioeconomica.personacubregasto}
						<div class="p-2">
							<span class="text-primary fs-6">
								{eFichaSocioeconomica.personacubregasto.nombre}
								{#if eFichaSocioeconomica.personacubregasto['pk'] == 7 && eFichaSocioeconomica.otroscubregasto != ''}
									: {eFichaSocioeconomica.otroscubregasto}
								{/if}
							</span>
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
