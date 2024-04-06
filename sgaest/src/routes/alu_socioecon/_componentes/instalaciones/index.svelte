<script lang="ts">
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
	let inputTieneSala = false;
	let inputTieneComedor = false;
	let inputTieneCocina = false;
	let inputTieneBanio = false;
	let inputTieneLuz = false;
	let inputTieneAgua = false;
	let inputTieneTelefono = false;
	let inputTieneAlcantarilla = false;
	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			eFichaSocioeconomica = aData.eFichaSocioeconomica ?? {};
			inputTieneSala = eFichaSocioeconomica.tienesala ?? false;
			inputTieneComedor = eFichaSocioeconomica.tienecomedor ?? false;
			inputTieneCocina = eFichaSocioeconomica.tienecocina ?? false;
			inputTieneBanio = eFichaSocioeconomica.tienebanio ?? false;
			inputTieneLuz = eFichaSocioeconomica.tieneluz ?? false;
			inputTieneAgua = eFichaSocioeconomica.tieneagua ?? false;
			inputTieneTelefono = eFichaSocioeconomica.tienetelefono ?? false;
			inputTieneAlcantarilla = eFichaSocioeconomica.tienealcantarilla ?? false;
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
			action: 'saveDatosInstalaciones',
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

	const changeTieneSala = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienesala', { tienesala: checked ? 'true' : 'false' });
		if (result === false) {
			event.target.checked = !checked;
		}
	};

	const changeTieneComedor = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienecomedor', {
			tienecomedor: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};

	const changeTieneCocina = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienecocina', {
			tienecocina: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};
	const changeTieneBanio = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienebanio', {
			tienebanio: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};
	const changeTieneLuz = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tieneluz', {
			tieneluz: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};

	const changeTieneAgua = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tieneagua', {
			tieneagua: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};

	const changeTieneTelefono = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienetelefono', {
			tienetelefono: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};

	const changeTieneAlcantarillado = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('tienealcantarilla', {
			tienealcantarilla: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};
</script>

<div class="card border-0 mx-0">
	<div class="card-header d-lg-flex justify-content-between align-items-center">
		<div class="mb-3 mb-lg-0">
			<h3 class="mb-0">Instalaciones</h3>
			<!--<p class="mb-0">Here is list of package/product that you have subscribed.</p>-->
		</div>
		<!--<div>
				<button class="btn btn-success btn-sm" on:click={() => openModalEdit()}>Editar</button>
			</div>-->
	</div>
	<div class="card-body px-lg-16">
		<div class="bg-light rounded border-1 p-2 mb-4">
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Sala</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienesala"
								on:change={changeTieneSala}
								bind:checked={inputTieneSala}
							/>
							<label class="form-check-label" for="id_tienesala" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Comedor</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienecomedor"
								on:change={changeTieneComedor}
								bind:checked={inputTieneComedor}
							/>
							<label class="form-check-label" for="id_tienecomedor" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Cocina</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienecocina"
								on:change={changeTieneCocina}
								bind:checked={inputTieneCocina}
							/>
							<label class="form-check-label" for="id_tienecocina" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Baño</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienebanio"
								on:change={changeTieneBanio}
								bind:checked={inputTieneBanio}
							/>
							<label class="form-check-label" for="id_tienebanio" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Luz</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tieneluz"
								on:change={changeTieneLuz}
								bind:checked={inputTieneLuz}
							/>
							<label class="form-check-label" for="id_tieneluz" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Agua</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tieneagua"
								on:change={changeTieneAgua}
								bind:checked={inputTieneAgua}
							/>
							<label class="form-check-label" for="id_tieneagua" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Teléfono</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienetelefono"
								on:change={changeTieneTelefono}
								bind:checked={inputTieneTelefono}
							/>
							<label class="form-check-label" for="id_tienetelefono" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Alcantarillado</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_tienealcantarilla"
								on:change={changeTieneAlcantarillado}
								bind:checked={inputTieneAlcantarilla}
							/>
							<label class="form-check-label" for="id_tienealcantarilla" />
						</div>
					</div>
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
