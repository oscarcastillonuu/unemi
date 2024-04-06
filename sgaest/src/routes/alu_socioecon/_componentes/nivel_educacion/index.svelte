<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import ComponentNivelEstudio from './frmNivelEstudio.svelte';
	import ComponentOcupacion from './frmOcupacion.svelte';
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
	let inputAlguienAfiliado = false;
	let inputAlguienSeguro = false;
	let eFichaSocioeconomica = {};
	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			eFichaSocioeconomica = aData.eFichaSocioeconomica ?? {};
			inputAlguienAfiliado = eFichaSocioeconomica.alguienafiliado ?? false;
			inputAlguienSeguro = eFichaSocioeconomica.alguienseguro ?? false;
		}
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'saveDatosNivelEducacion') {
			const menu = document.getElementById('menu_element_7');
			menu.click();
			mOpenModal = !mOpenModal;
		}
	};

	const openModalNivelEstudio = (title) => {
		modalDetalleContent = ComponentNivelEstudio;
		mOpenModal = !mOpenModal;
		modalTitle = title;
		aDataModal = { eFichaSocioeconomica: eFichaSocioeconomica };
	};

	const openModalOcupacion = (title) => {
		modalDetalleContent = ComponentOcupacion;
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
						action: 'deleteNivelEducacion',
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
							const menu = document.getElementById('menu_element_7');
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
			action: 'saveDatosNivelEducacion',
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

	const changeAlguienAfiliado = async (event) => {
		console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('alguienafiliado', {
			alguienafiliado: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};

	const changeAlguienSeguro = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('alguienseguro', {
			alguienseguro: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};
</script>

<div class="card border-0 mx-0">
	<div class="card-header d-lg-flex justify-content-between align-items-center">
		<div class="mb-3 mb-lg-0">
			<h3 class="mb-0">Nivel de educación y actividad económica del hogar</h3>
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
							<span class="align-middle">¿Cuál es el nivel de estudios del Jefe del Hogar? </span>
						</h5>
						<div>
							{#if eFichaSocioeconomica.niveljefehogar}
								<a
									href="javascript:void(0);"
									class="me-1 text-inherit text-warning"
									aria-label="Editar"
									on:click={() => openModalNivelEstudio('Actualizar nivel de estudio')}
									data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
								>
								<a
									href="#"
									class="me-1 text-inherit text-danger"
									aria-label="Eliminar"
									on:click={() =>
										eliminarElemento(
											'niveljefehogar',
											'¿Estas a punto de eliminar el nivel de estudio?'
										)}
									data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
								>
							{:else}
								<a
									href="javascript:void(0);"
									on:click={() => openModalNivelEstudio('Adicionar nivel de estudio')}
									class="me-1 text-inherit text-success"
									aria-label="Adicionar"
									data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
								>
							{/if}
						</div>
					</div>
					{#if eFichaSocioeconomica.niveljefehogar}
						<div class="p-2">
							<span class="text-primary fs-6">{eFichaSocioeconomica.niveljefehogar.nombre}</span>
						</div>
					{/if}
				</div>
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle"
								>¿Alguien en el hogar está afiliado al IESS y/o seguro ISSPOL o ISSFA?
							</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_alguienafiliado"
								on:change={changeAlguienAfiliado}
								bind:checked={inputAlguienAfiliado}
							/>
							<label class="form-check-label" for="id_alguienafiliado" />
						</div>
					</div>
				</div>
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle"
								>¿Alguien en el hogar tiene seguro de salud privada, con o sin hospitalización y/o
								seguro de vida?
							</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_alguienseguro"
								on:change={changeAlguienSeguro}
								bind:checked={inputAlguienSeguro}
							/>
							<label class="form-check-label" for="id_alguienseguro" />
						</div>
					</div>
				</div>
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">¿Cuál es la ocupación del Jefe del Hogar? </span>
						</h5>
						<div>
							{#if eFichaSocioeconomica.ocupacionjefehogar}
								<a
									href="javascript:void(0);"
									class="me-1 text-inherit text-warning"
									aria-label="Editar"
									on:click={() => openModalOcupacion('Actualizar ocupación del jefe del hogar')}
									data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
								>
								<a
									href="#"
									class="me-1 text-inherit text-danger"
									aria-label="Eliminar"
									on:click={() =>
										eliminarElemento(
											'ocupacionjefehogar',
											'¿Estas a punto de eliminar ocupación del jefe del hogar?'
										)}
									data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
								>
							{:else}
								<a
									href="javascript:void(0);"
									on:click={() => openModalOcupacion('Adicionar ocupación del jefe del hogar')}
									class="me-1 text-inherit text-success"
									aria-label="Adicionar"
									data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
								>
							{/if}
						</div>
					</div>
					{#if eFichaSocioeconomica.ocupacionjefehogar}
						<div class="p-2">
							<span class="text-primary fs-6">
								{eFichaSocioeconomica.ocupacionjefehogar.nombre}
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
