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
	let inputCompraVestCC = false;
	let inputUsaInternet = false;
	let inputUsaCorreoTrab = false;
	let inputRegistroRedSocial = false;
	let inputLeidoLibro = false;
	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			eFichaSocioeconomica = aData.eFichaSocioeconomica ?? {};
			inputCompraVestCC = eFichaSocioeconomica.compravestcc ?? false;
			inputUsaInternet = eFichaSocioeconomica.usainternetseism ?? false;
			inputUsaCorreoTrab = eFichaSocioeconomica.usacorreonotrab ?? false;
			inputRegistroRedSocial = eFichaSocioeconomica.registroredsocial ?? false;
			inputLeidoLibro = eFichaSocioeconomica.leidolibrotresm ?? false;
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
			action: 'saveDatosHabitoConsumo',
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

	const changeCompraVestCC = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('compravestcc', { compravestcc: checked ? 'true' : 'false' });
		if (result === false) {
			event.target.checked = !checked;
		}
	};

	const changeUsaInternet = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('usainternetseism', {
			usainternetseism: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};

	const changeUsaCorreoTrab = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('usacorreonotrab', {
			usacorreonotrab: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};
	const changeRegistroRedSocial = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('registroredsocial', {
			registroredsocial: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};
	const changeLeidoLibro = async (event) => {
		// console.log(event.target.checked);
		const checked = event.target.checked;
		const result = await saveElemento('leidolibrotresm', {
			leidolibrotresm: checked ? 'true' : 'false'
		});
		if (result === false) {
			event.target.checked = !checked;
		}
	};
</script>

<div class="card border-0 mx-0">
	<div class="card-header d-lg-flex justify-content-between align-items-center">
		<div class="mb-3 mb-lg-0">
			<h3 class="mb-0">Hábitos de consumo</h3>
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
							<span class="align-middle"
								>¿Alguien en el hogar compra vestimenta en centros comerciales?
							</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_compravestcc"
								on:change={changeCompraVestCC}
								bind:checked={inputCompraVestCC}
							/>
							<label class="form-check-label" for="id_compravestcc" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle"
								>¿En el hogar alguien ha usado el internet en los &uacute;ltimos 6 meses?
							</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_usainternetseism"
								on:change={changeUsaInternet}
								bind:checked={inputUsaInternet}
							/>
							<label class="form-check-label" for="id_usainternetseism" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle"
								>¿En el hogar alguien utiliza correo electr&oacute;nico que no es del trabajo?
							</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_usacorreonotrab"
								on:change={changeUsaCorreoTrab}
								bind:checked={inputUsaCorreoTrab}
							/>
							<label class="form-check-label" for="id_usacorreonotrab" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle"
								>¿En el hogar alguien est&aacute; registrado en una red social?
							</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_registroredsocial"
								on:change={changeRegistroRedSocial}
								bind:checked={inputRegistroRedSocial}
							/>
							<label class="form-check-label" for="id_registroredsocial" />
						</div>
					</div>
				</div>
			</div>
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle"
								>¿Alguien del hogar ha leido algun libro completo en los &uacute;ltimos 3 meses?
								(exceptuar libros de estudio)
							</span>
						</h5>
						<div class="form-check form-switch">
							<input
								type="checkbox"
								class="form-check-input"
								id="id_leidolibrotresm"
								on:change={changeLeidoLibro}
								bind:checked={inputLeidoLibro}
							/>
							<label class="form-check-label" for="id_leidolibrotresm" />
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
