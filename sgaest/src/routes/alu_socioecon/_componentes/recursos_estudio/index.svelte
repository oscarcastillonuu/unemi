<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import ComponentOtrosRecursos from './frmOtrosRecursos.svelte';
	import ComponentOtrosSectores from './frmOtrosSector.svelte';
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
	let inputTieneFolleto = false;
	let inputTieneComputador = false;
	let inputTieneEnciclopedia = false;
	let inputTieneCyber = false;
	let inputTieneBiblioteca = false;
	let inputTieneMuseo = false;
	let inputTieneAreaRecreacion = false;
	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			eFichaSocioeconomica = aData.eFichaSocioeconomica ?? {};
			inputTieneFolleto = eFichaSocioeconomica.tienefolleto ?? false;
			inputTieneComputador = eFichaSocioeconomica.tienecomputador ?? false;
			inputTieneEnciclopedia = eFichaSocioeconomica.tieneenciclopedia ?? false;
			inputTieneCyber = eFichaSocioeconomica.tienecyber ?? false;
			inputTieneMuseo = eFichaSocioeconomica.tienemuseo ?? false;
			inputTieneBiblioteca = eFichaSocioeconomica.tienebiblioteca ?? false;
			inputTieneAreaRecreacion = eFichaSocioeconomica.tienearearecreacion ?? false;
		}
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'saveDatosRecursosEstudios') {
			const menu = document.getElementById('menu_element_14');
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
			action: 'saveDatosRecursosEstudios',
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
						action: 'deleteRecursosEstudio',
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
							const menu = document.getElementById('menu_element_14');
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

	const changeTieneFolleto = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienefolleto', { tienefolleto: checked ? 'true' : 'false' });
		if (result === false) {
			event.target.checked = !checked;
		}
	};
	const changeTieneComputador = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienecomputador', {
			tienecomputador: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};
	const changeTieneEnciclopedia = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tieneenciclopedia', {
			tieneenciclopedia: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};
	const changeTieneCyber = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienecyber', {
			tienecyber: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};

	const changeTieneBiblioteca = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienebiblioteca', {
			tienebiblioteca: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};

	const changeTieneMuseo = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienemuseo', {
			tienemuseo: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};

	const changeTieneAreaRecreacion = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienearearecreacion', {
			tienearearecreacion: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};
</script>

<div class="card border-0 mx-0">
	<div class="card-header d-lg-flex justify-content-between align-items-center">
		<div class="mb-3 mb-lg-0">
			<h3 class="mb-0">Recursos para el estudio</h3>
		</div>
		<!--<div>
				<button class="btn btn-success btn-sm" on:click={() => openModalEdit()}>Editar</button>
			</div>-->
	</div>
	<div class="card-body">
		<p class="mb-0">Recursos que cuenta al momento de realizar sus tareas</p>
		<div class="bg-light rounded border-1 p-2 mb-2">
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Folletos</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienefolleto"
								on:change={changeTieneFolleto}
								bind:checked={inputTieneFolleto}
							/>
							<label class="form-check-label" for="id_tienefolleto" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Computador</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienecomputador"
								on:change={changeTieneComputador}
								bind:checked={inputTieneComputador}
							/>
							<label class="form-check-label" for="id_tienecomputador" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Enciclopedias</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tieneenciclopedia"
								on:change={changeTieneEnciclopedia}
								bind:checked={inputTieneEnciclopedia}
							/>
							<label class="form-check-label" for="id_tieneenciclopedia" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
				<div class="d-flex align-items-center justify-content-between">
					<h5 class="mb-0 text-truncate">
						<span class="align-middle">Otros</span>
					</h5>
					<div>
						{#if eFichaSocioeconomica.otrosrecursos}
							<a
								href="javascript:void(0);"
								class="me-1 text-inherit text-warning"
								aria-label="Editar"
								on:click={() => openModalGenerico(ComponentOtrosRecursos, 'Actualizar')}
								data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
							>
							<a
								href="#"
								class="me-1 text-inherit text-danger"
								aria-label="Eliminar"
								on:click={() =>
									eliminarElemento('otrosrecursos', `¿Estas a punto de eliminar otros recursos?`)}
								data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
							>
						{:else}
							<a
								href="javascript:void(0);"
								on:click={() => openModalGenerico(ComponentOtrosRecursos, 'Adicionar')}
								class="me-1 text-inherit text-success"
								aria-label="Adicionar"
								data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
							>
						{/if}
					</div>
				</div>
				{#if eFichaSocioeconomica.otrosrecursos}
					<div class="p-2">
						<span class="text-primary fs-6">{eFichaSocioeconomica.otrosrecursos}</span>
					</div>
				{/if}
			</div>
		</div>
		<p class="mb-0">Cuenta en su sector con</p>
		<div class="bg-light rounded border-1 p-2 mb-2">
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Cyber</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienecyber"
								on:change={changeTieneCyber}
								bind:checked={inputTieneCyber}
							/>
							<label class="form-check-label" for="id_tienecyber" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Biblioteca</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienebiblioteca"
								on:change={changeTieneBiblioteca}
								bind:checked={inputTieneBiblioteca}
							/>
							<label class="form-check-label" for="id_tienebiblioteca" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Museo</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienemuseo"
								on:change={changeTieneMuseo}
								bind:checked={inputTieneMuseo}
							/>
							<label class="form-check-label" for="id_tienemuseo" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Área de recreación</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienearearecreacion"
								on:change={changeTieneAreaRecreacion}
								bind:checked={inputTieneAreaRecreacion}
							/>
							<label class="form-check-label" for="id_tienearearecreacion" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
				<div class="d-flex align-items-center justify-content-between">
					<h5 class="mb-0 text-truncate">
						<span class="align-middle">Otros</span>
					</h5>
					<div>
						{#if eFichaSocioeconomica.otrossector}
							<a
								href="javascript:void(0);"
								class="me-1 text-inherit text-warning"
								aria-label="Editar"
								on:click={() => openModalGenerico(ComponentOtrosSectores, 'Actualizar')}
								data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
							>
							<a
								href="#"
								class="me-1 text-inherit text-danger"
								aria-label="Eliminar"
								on:click={() =>
									eliminarElemento('otrossector', `¿Estas a punto de eliminar otros sectores?`)}
								data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
							>
						{:else}
							<a
								href="javascript:void(0);"
								on:click={() => openModalGenerico(ComponentOtrosSectores, 'Adicionar')}
								class="me-1 text-inherit text-success"
								aria-label="Adicionar"
								data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
							>
						{/if}
					</div>
				</div>
				{#if eFichaSocioeconomica.otrossector}
					<div class="p-2">
						<span class="text-primary fs-6">{eFichaSocioeconomica.otrossector}</span>
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
