<script lang="ts">
	import { loginIn, browserSet, browserGet, logOutUser, apiGET } from '$lib/utils/requestUtils';
	import { decodeToken } from '$lib/utils/decodetoken';
	import { goto } from '$app/navigation';
	import type { UserResponse } from '$lib/interfaces/user.interface';
	import type { CustomError } from '$lib/interfaces/error.interface';
	import { loading } from '$lib/store/loadingStore';
	import { onMount } from 'svelte';
	import { addToast } from '$lib/store/toastStore';
	import { navigating } from '$app/stores';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import componenteCronogramaModalidad from './_modal/cronogramaModalidad.svelte';
	import componenteCronogramaCarrera from './_modal/cronogramaCarrera.svelte';
	import componenteCronogramaJornada from './_modal/cronogramaJornada.svelte';

	let persona = {};
	let username = '',
		password = '',
		errors: Array<CustomError>;
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	let aCronograma = {};
	let mOpenModalGenerico = false;
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);
	let modalTitle = '';
	let modalDetalleContent;
	let modalClose = false;
	let mSize = 'xs';
	let aDataModal;
	let aModalidades = [];
	let mClass =
		'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down';
	onMount(async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const ds = browserGet('dataSession');
		if (ds != null || ds != undefined) {
			loading.setLoading(true, 'Cargando, espere por favor...');
			const dataSession = JSON.parse(ds);
			persona = dataSession['persona'];
			username = dataSession['user']['username'];
			//await loadCronograma();
		}
		loading.setLoading(false, 'Cargando, espere por favor...');
	});

	const handleLogin = async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		if (browserGet('refreshToken')) {
			localStorage.removeItem('refreshToken');
		}
		const [res, err] = await loginIn(fetch, 'token/login', {
			username: username,
			password: password
		});
		const json = decodeToken(res);
		//console.log(json);
		const response: UserResponse = json;
		if (err.length > 0) {
			//const noty = { title: err[0].error, type: 'error', icon: 'error' };
			addToast({ type: 'error', header: 'Ocurrio un error', body: err[0].error });
		} else if (response.tokens) {
			browserSet('refreshToken', response.tokens.refresh);
			browserSet('accessToken', response.tokens.access);
			browserSet('dataSession', JSON.stringify(response));
			await goto('/');
		}
		loading.setLoading(false, 'Cargando, espere por favor...');
	};
	const closeModal = () => {
		mOpenModalGenerico = false;
		aDataModal = {};
	};

	const actionRun = async (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'closeModal') {
			closeModal();
		} else if (action === 'openModalidades') {
			mOpenModalGenerico = false;
			aDataModal = {};
			//await closeModal();
			await openModalidades(aModalidades);
		} else if (action === 'openCarreras') {
			mOpenModalGenerico = false;
			aDataModal = {};
			//await closeModal();
			await openCarreras(detail.aModalidad);
		} else if (action === 'openJornadas') {
			mOpenModalGenerico = false;
			aDataModal = {};
			//await closeModal();
			await openJornadas(detail.aModalidad, detail.aCoordinacion, detail.aCarrera);
		}
	};

	const openModalidades = async (_aModalidades) => {
		mOpenModalGenerico = false;
		aDataModal = undefined;
		if (_aModalidades.length > 0) {
			mOpenModalGenerico = true;
			modalDetalleContent = componenteCronogramaModalidad;
			modalTitle = 'Cronograma de matriculación de pregrado Abril - Agosto 2024';
			modalClose = false;
			mSize = 'lg';
			mClass =
				'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down';
			aDataModal = { aModalidades: _aModalidades };
		}
	};

	const openCarreras = async (aModalidad) => {
		let aCoordinaciones = [];
		mOpenModalGenerico = false;
		aDataModal = undefined;
		if (aModalidad) {
			aModalidad['aCoordinaciones'].forEach((aCoordinacion) => {
				aCoordinaciones.push({ ...aCoordinacion });
			});
			mOpenModalGenerico = true;
			modalDetalleContent = componenteCronogramaCarrera;
			modalTitle = 'Cronograma de matriculación de pregrado Abril - Agosto 2024';
			modalClose = false;
			mSize = 'xl';
			mClass =
				'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-lg-down';
			console.log(aCoordinaciones);
			aDataModal = {
				aModalidad: { ...aModalidad },
				//aModalidades: [...aModalidades],
				aCoordinaciones: [...aCoordinaciones]
			};
		}
	};

	const openJornadas = async (aModalidad, aCoordinacion, aCarrera) => {
		let aJornadas = [];
		mOpenModalGenerico = false;
		aDataModal = undefined;
		if (aCarrera) {
			aCarrera['aSecciones'].forEach((aSeccion) => {
				aJornadas.push({ ...aSeccion });
			});
			mOpenModalGenerico = true;
			modalDetalleContent = componenteCronogramaJornada;
			modalTitle = 'Cronograma de matriculación de pregrado Abril - Agosto 2024';
			modalClose = false;
			mSize = 'lg';
			mClass =
				'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-lg-down';
			//console.log(aCoordinaciones);
			aDataModal = {
				aModalidad: { ...aModalidad },
				aCoordinacion: { ...aCoordinacion },
				aCarrera: { ...aCarrera },
				aJornadas: [...aJornadas]
			};
		}
	};

	const loadCronograma = async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		aModalidades = [];
		const [res, errors] = await apiGET(fetch, 'cronograma', {});
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
			} else {
				aCronograma = res.data['aCronograma'] ?? undefined;
				if (aCronograma) {
					if (aCronograma) {
						aCronograma['aModalidades'].forEach((aModalidad) => {
							aModalidades.push({ ...aModalidad });
						});
					}
					await openModalidades(aModalidades);
				}
			}
		}
		loading.setLoading(false, 'Cargando, espere por favor...');
	};
</script>

<svelte:head>
	<title>Inicio de sesión | SGA</title>
</svelte:head>

<div class="text-center w-95 m-auto">
	<img
		src={persona.foto}
		height="64"
		onerror="this.onerror=null;this.src='./image.png'"
		class="rounded-circle shadow"
	/>
	<h4 class="text-dark-50 text-center mt-3 fw-bold" style="color: orange ">
		¡Bienvenido de nuevo!
	</h4>
	<h3 class="text-dark-50 text-center mt-3 fw-bold">{persona.nombre_completo}</h3>
	<p class="text-muted mb-4">Introduzca su contraseña para desbloquear.</p>
</div>
<form on:submit|preventDefault={handleLogin}>
	<div class="mb-3">
		<!--label for="password" class="form-label">Contraseña</label>-->
		<div class="input-group mb-4">
			<span class="input-group-text"><i class="fe fe-lock" /></span>
			<input
				bind:value={password}
				type="password"
				id="password"
				class="form-control"
				name="password"
				placeholder="**************"
				required
			/>
		</div>
	</div>
	<div class="d-grid gap-2 mb-2 text-center">
		<button type="submit" class="btn btn-large btn-warning mb-0">Desbloquear</button>
	</div>
	<!--<div class="d-grid gap-2 mb-0 text-center">
		<a
			href="javascript:void(0);"
			on:click={() => loadCronograma()}
			style="color: #f39c12 !important"><b>Consultar cronograma de matriculación</b></a
		>
	</div>-->
</form>

<div class="mt-5 text-center" style="color: #f39c12 !important">
	<button type="button" on:click|preventDefault={logOutUser} class="btn btn-outline-secondary "
		>¡Desconectar!</button
	>
</div>
<hr class="my-4" />
<div class="mt-4 text-center">
	<a
		href="https://www.facebook.com/UNEMIEcuador"
		target="_blank"
		class="btn-social btn-social-outline btn-facebook"
	>
		<i class="fe fe-facebook fs-4" />
	</a>
	<a
		href="https://twitter.com/UNEMIEcuador"
		target="_blank"
		class="btn-social btn-social-outline btn-twitter"
	>
		<i class="fe fe-twitter fs-4" />
	</a>
	<a
		href="https://www.instagram.com/UNEMIEcuador/"
		target="_blank"
		class="btn-social btn-social-outline btn-linkedin"
	>
		<i class="fe fe-linkedin" />
	</a>
	<a
		href="https://www.unemi.edu.ec/"
		target="_blank"
		class="btn-social btn-social-outline btn-github"
	>
		<i class="fe fe-chrome" />
	</a>
</div>
{#if mOpenModalGenerico}
	<ModalGenerico
		mToggle={mToggleModalGenerico}
		mOpen={mOpenModalGenerico}
		modalContent={modalDetalleContent}
		mClose={modalClose}
		title={modalTitle}
		aData={aDataModal}
		size={mSize}
		{mClass}
		on:actionRun={actionRun}
	/>
{/if}
