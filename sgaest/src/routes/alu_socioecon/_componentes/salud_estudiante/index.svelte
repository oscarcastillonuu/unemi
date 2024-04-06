<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import ComponentSalubridadVida from './frmSalubridadVida.svelte';
	import ComponentEnfermedadComunes from './frmEnfermedadComunes.svelte';
	import ComponentEstadoGeneral from './frmEstadoGeneral.svelte';
	import ComponentTratamientoMedico from './frmTratamientoMedico.svelte';
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
	let inputTieneDiabetes = false;
	let inputTieneHipertencion = false;
	let inputTieneParkinson = false;
	let inputTieneCancer = false;
	let inputTieneAlzheimer = false;
	let inputTieneVitiligo = false;
	let inputTieneDesgastamiento = false;
	let inputTienePielBlanca = false;
	let inputTieneSida = false;
	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			eFichaSocioeconomica = aData.eFichaSocioeconomica ?? {};
			inputTieneDiabetes = eFichaSocioeconomica.tienediabetes ?? false;
			inputTieneHipertencion = eFichaSocioeconomica.tienehipertencion ?? false;
			inputTieneParkinson = eFichaSocioeconomica.tieneparkinson ?? false;
			inputTieneCancer = eFichaSocioeconomica.tienecancer ?? false;
			inputTieneAlzheimer = eFichaSocioeconomica.tienealzheimer ?? false;
			inputTieneVitiligo = eFichaSocioeconomica.tienevitiligo ?? false;
			inputTieneDesgastamiento = eFichaSocioeconomica.tienedesgastamiento ?? false;
			inputTienePielBlanca = eFichaSocioeconomica.tienepielblanca ?? false;
			inputTieneSida = eFichaSocioeconomica.tienesida ?? false;
		}
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'saveDatosSaludEstudiante') {
			const menu = document.getElementById('menu_element_15');
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
			action: 'saveDatosSaludEstudiante',
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
						action: 'deleteSaludEstudiante',
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
							const menu = document.getElementById('menu_element_15');
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

	const changeTieneDiabetes = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienediabetes', {
			tienediabetes: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};
	const changeTieneHipertencion = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienehipertencion', {
			tienehipertencion: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};
	const changeTieneParkison = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tieneparkinson', {
			tieneparkinson: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};
	const changeTieneCancer = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienecancer', {
			tienecancer: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};

	const changeTieneAlzheimer = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienealzheimer', {
			tienealzheimer: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};

	const changeTieneVitiligo = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienevitiligo', {
			tienevitiligo: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};

	const changeTieneDesgastamiento = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienedesgastamiento', {
			tienedesgastamiento: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};
	const changeTienePielBlanca = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienepielblanca', {
			tienepielblanca: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};
	const changeTieneSida = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienesida', {
			tienesida: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};
</script>

<div class="card border-0 mx-0">
	<div class="card-header d-lg-flex justify-content-between align-items-center">
		<div class="mb-3 mb-lg-0">
			<h3 class="mb-0">Salud del estudiante</h3>
		</div>
		<!--<div>
				<button class="btn btn-success btn-sm" on:click={() => openModalEdit()}>Editar</button>
			</div>-->
	</div>
	<div class="card-body">
		<p class="mb-0">Enfermedades hereditarias</p>
		<div class="bg-light rounded border-1 p-2 mb-2">
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Diabetes</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienefolleto"
								on:change={changeTieneDiabetes}
								bind:checked={inputTieneDiabetes}
							/>
							<label class="form-check-label" for="id_tienediabetes" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Hipertensión</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienehipertencion"
								on:change={changeTieneHipertencion}
								bind:checked={inputTieneHipertencion}
							/>
							<label class="form-check-label" for="id_tienehipertencion" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Parkinson</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tieneparkinson"
								on:change={changeTieneParkison}
								bind:checked={inputTieneParkinson}
							/>
							<label class="form-check-label" for="id_tieneparkinson" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Cáncer</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienecancer"
								on:change={changeTieneCancer}
								bind:checked={inputTieneCancer}
							/>
							<label class="form-check-label" for="id_tienecancer" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Alzheimer</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienealzheimer"
								on:change={changeTieneAlzheimer}
								bind:checked={inputTieneAlzheimer}
							/>
							<label class="form-check-label" for="id_tienealzheimer" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Vitíligo</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienevitiligo"
								on:change={changeTieneVitiligo}
								bind:checked={inputTieneVitiligo}
							/>
							<label class="form-check-label" for="id_tienevitiligo" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Desgastamiento cerebral</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienedesgastamiento"
								on:change={changeTieneDesgastamiento}
								bind:checked={inputTieneDesgastamiento}
							/>
							<label class="form-check-label" for="id_tienedesgastamiento" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Piel blanca</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienepielblanca"
								on:change={changeTienePielBlanca}
								bind:checked={inputTienePielBlanca}
							/>
							<label class="form-check-label" for="id_tienepielblanca" />
						</div>
					</div>
				</div>
			</div>
		</div>
		<p class="mb-0">Otras enfermedades</p>
		<div class="bg-light rounded border-1 p-2 mb-2">
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Existen casos de VIH/SIDA en la familia </span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienesida"
								on:change={changeTieneSida}
								bind:checked={inputTieneSida}
							/>
							<label class="form-check-label" for="id_tienesida" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
				<div class="d-flex align-items-center justify-content-between">
					<h5 class="mb-0 text-truncate">
						<span class="align-middle">Enfermedades comunes en la familia </span>
					</h5>
					<div>
						{#if eFichaSocioeconomica.enfermedadescomunes}
							<a
								href="javascript:void(0);"
								class="me-1 text-inherit text-warning"
								aria-label="Editar"
								on:click={() => openModalGenerico(ComponentEnfermedadComunes, 'Actualizar')}
								data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
							>
							<a
								href="#"
								class="me-1 text-inherit text-danger"
								aria-label="Eliminar"
								on:click={() =>
									eliminarElemento(
										'enfermedadescomunes',
										`¿Estas a punto de eliminar enfermedades comunes en la familia?`
									)}
								data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
							>
						{:else}
							<a
								href="javascript:void(0);"
								on:click={() => openModalGenerico(ComponentEnfermedadComunes, 'Adicionar')}
								class="me-1 text-inherit text-success"
								aria-label="Adicionar"
								data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
							>
						{/if}
					</div>
				</div>
				{#if eFichaSocioeconomica.enfermedadescomunes}
					<div class="p-2">
						<span class="text-primary fs-6">{eFichaSocioeconomica.enfermedadescomunes}</span>
					</div>
				{/if}
			</div>
			<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
				<div class="d-flex align-items-center justify-content-between">
					<h5 class="mb-0 text-truncate">
						<span class="align-middle">Salubridad de las condiciones de vida </span>
					</h5>
					<div>
						{#if eFichaSocioeconomica.salubridadvida}
							<a
								href="javascript:void(0);"
								class="me-1 text-inherit text-warning"
								aria-label="Editar"
								on:click={() => openModalGenerico(ComponentSalubridadVida, 'Actualizar')}
								data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
							>
							<a
								href="#"
								class="me-1 text-inherit text-danger"
								aria-label="Eliminar"
								on:click={() =>
									eliminarElemento(
										'salubridadvida',
										`¿Estas a punto de eliminar condiciones de vida?`
									)}
								data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
							>
						{:else}
							<a
								href="javascript:void(0);"
								on:click={() => openModalGenerico(ComponentSalubridadVida, 'Adicionar')}
								class="me-1 text-inherit text-success"
								aria-label="Adicionar"
								data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
							>
						{/if}
					</div>
				</div>
				{#if eFichaSocioeconomica.salubridadvida}
					<div class="p-2">
						<span class="text-primary fs-6">{eFichaSocioeconomica.salubridadvida_display}</span>
					</div>
				{/if}
			</div>
			<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
				<div class="d-flex align-items-center justify-content-between">
					<h5 class="mb-0 text-truncate">
						<span class="align-middle">Estado general de salud de el/la estudiante</span>
					</h5>
					<div>
						{#if eFichaSocioeconomica.estadogeneral}
							<a
								href="javascript:void(0);"
								class="me-1 text-inherit text-warning"
								aria-label="Editar"
								on:click={() => openModalGenerico(ComponentEstadoGeneral, 'Actualizar')}
								data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
							>
							<a
								href="#"
								class="me-1 text-inherit text-danger"
								aria-label="Eliminar"
								on:click={() =>
									eliminarElemento(
										'estadogeneral',
										`¿Estas a punto de eliminar estado general de salud?`
									)}
								data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
							>
						{:else}
							<a
								href="javascript:void(0);"
								on:click={() => openModalGenerico(ComponentEstadoGeneral, 'Adicionar')}
								class="me-1 text-inherit text-success"
								aria-label="Adicionar"
								data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
							>
						{/if}
					</div>
				</div>
				{#if eFichaSocioeconomica.estadogeneral}
					<div class="p-2">
						<span class="text-primary fs-6">{eFichaSocioeconomica.estadogeneral_display}</span>
					</div>
				{/if}
			</div>
			<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
				<div class="d-flex align-items-center justify-content-between">
					<h5 class="mb-0 text-truncate">
						<span class="align-middle">En caso de tratamiento médico sigue</span>
					</h5>
					<div>
						{#if eFichaSocioeconomica.tratamientomedico}
							<a
								href="javascript:void(0);"
								class="me-1 text-inherit text-warning"
								aria-label="Editar"
								on:click={() => openModalGenerico(ComponentTratamientoMedico, 'Actualizar')}
								data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
							>
							<a
								href="#"
								class="me-1 text-inherit text-danger"
								aria-label="Eliminar"
								on:click={() =>
									eliminarElemento(
										'tratamientomedico',
										`¿Estas a punto de eliminar tratamiento médico?`
									)}
								data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
							>
						{:else}
							<a
								href="javascript:void(0);"
								on:click={() => openModalGenerico(ComponentTratamientoMedico, 'Adicionar')}
								class="me-1 text-inherit text-success"
								aria-label="Adicionar"
								data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
							>
						{/if}
					</div>
				</div>
				{#if eFichaSocioeconomica.tratamientomedico}
					<div class="p-2">
						<span class="text-primary fs-6">{eFichaSocioeconomica.tratamientomedico}</span>
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
