<script lang="ts">
	import { apiPOST, browserGet, browserSet } from '$lib/utils/requestUtils';
	import { variables } from '$lib/utils/constants';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import { createEventDispatcher, onMount } from 'svelte';
	import { addNotification } from '$lib/store/notificationStore';
	import { decodeToken } from '$lib/utils/decodetoken';
	import type { UserResponse } from '$lib/interfaces/user.interface';
	import { Icon } from 'sveltestrap';
	import { encodeQueryString } from '$lib/helpers/baseHelper';
	export let aData;
	let ePersona;
	let password1 = '';
	let password2 = '';
	let password3 = '';
	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		ePersona = aData.ePersona;
	});

	const handleChangePassword = async () => {
		if (password1 == password2) {
			addToast({ type: 'warning', header: 'Advertencia', body: 'Contraseñas antigua y nueva son iguales' });
			return;
		}

		if (password2 != password3) {
			addToast({ type: 'warning', header: 'Advertencia', body: 'Contraseñas no son iguales' });
			return;
		}
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'changepassword', {
			action: 'changePassword',
			password1: password1,
			password2: password2,
			password3: password3
		});
		loading.setLoading(false, 'Cargando, espere por favor...');
		//console.log(errorsCertificates);
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			goto('/');
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				if (!res.module_access) {
					goto('/');
				}
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: res.message });
				dispatch('actionRun', { action: 'closeModal' });
			}
		}
	};

	const keyUPPassword = (e) => {
		const pswd = e;
		let habilitar = true;

		if (pswd.length < 8) {
			document.getElementById('length').style = 'color: red;';
			habilitar = false;
		} else {
			document.getElementById('length').style = 'color: green;';
		}
		if (pswd.match(/[A-z]/)) {
			document.getElementById('letter').style = 'color: green;';
		} else {
			habilitar = false;
			document.getElementById('letter').style = 'color: red;';
		}
		if (pswd.match(/[A-Z]/) && pswd.match(/[a-z]/)) {
			document.getElementById('capital').style = 'color: green;';
		} else {
			habilitar = false;
			document.getElementById('capital').style = 'color: red;';
		}
		if (pswd.match(/\d/)) {
			document.getElementById('number').style = 'color: green;';
		} else {
			habilitar = false;
			document.getElementById('number').style = 'color: red;';
		}
		if (password1.length > 0) {
			document.getElementById('antiguaclave').style = 'color: green;';
		} else {
			habilitar = false;
			document.getElementById('antiguaclave').style = 'color: red;';
		}
		if (password1 != password2) {
			document.getElementById('antiguanuevaclave').style = 'color: green;';
		} else {
			habilitar = false;
			document.getElementById('antiguanuevaclave').style = 'color: red;';
		}
		if (password2 === password3) {
			document.getElementById('nuevarepetir').style = 'color: green;';
		} else {
			habilitar = false;
			document.getElementById('nuevarepetir').style = 'color: red;';
		}
		let x = document.getElementById('btnGuardarPassword');
		let xx = document.getElementsByClassName('blink_me');
		if (habilitar) {
			x.style.display = 'block';
			xx[0].style.display = 'none';
		} else {
			x.style.display = 'none';
			xx[0].style.display = 'block';
		}
	};
</script>

{#if ePersona}
	<div class="p-4">
		<div class="mb-1">
			<h6 class="fs-6">
				<Icon name="info-circle" /> La contraseña debe cumplir con los siguientes parámetros:
			</h6>
			<ul style="font-size: 11px;">
				<li style="list-style-type: circle;" id="antiguaclave">
					<strong>Contraseña actual</strong>
				</li>
				<li style="list-style-type: circle;" id="antiguanuevaclave">
					<strong>Contraseña actual debe ser diferente a la contraseña nueva</strong>
				</li>
				<li style="list-style-type: circle;" id="letter">
					Al menos <strong>una letra</strong>
				</li>
				<li style="list-style-type: circle;" id="capital">
					Al menos <strong>una letra en mayúscula y una letra en minúscula</strong>
				</li>
				<li style="list-style-type: circle;" id="number">
					Al menos <strong>un número</strong>
				</li>
				<li style="list-style-type: circle;" id="length">
					Al menos ha de contener <strong>8 caracteres</strong>
				</li>
				<li style="list-style-type: circle;" id="nuevarepetir">
					La nueva contraseña <strong>debe ser igual</strong> confirmar contraseña.
				</li>
			</ul>
		</div>

		<form on:submit|preventDefault={handleChangePassword}>
			<div class="row g-2 mb-3 mt-3">
				<div class="col-md">
					<div class="form-floating">
						<input
							type="password"
							class="form-control"
							id="floatingInputGridPassword1"
							placeholder="*********"
							bind:value={password1}
						/>
						<label for="floatingInputGridPassword1">Contraseña actual</label>
					</div>
				</div>
				<div class="col-md">
					<div class="form-floating">
						<input
							type="password"
							class="form-control"
							id="floatingInputGridPassword2"
							placeholder="*********"
							bind:value={password2}
							on:keyup={({ target: { value } }) => keyUPPassword(value)}
						/>
						<label for="floatingInputGridPassword2">Nueva contraseña</label>
					</div>
				</div>
				<div class="col-md">
					<div class="form-floating">
						<input
							type="password"
							class="form-control"
							id="floatingInputGridPassword3"
							placeholder="*********"
							bind:value={password3}
							on:keyup={({ target: { value } }) => keyUPPassword(value)}
						/>
						<label for="floatingInputGridPassword3">Confirmar contraseña</label>
					</div>
				</div>
			</div>
			<div class="row text-center">
				<div class="col-12">
					<div class="mb-3 d-grid">
						<button
							type="submit"
							id="btnGuardarPassword"
							style="display: none;"
							class="btn btn-primary"
						>
							<Icon name="save" /> Cambiar contraseña
						</button>
						<p class="fs-6 blink_me"><b>Complete los campos de contraseña</b></p>
					</div>
				</div>
				<!-- /.col -->
			</div>
		</form>
		<!-- Form -->
	</div>
{/if}

<style>
	.blink_me {
		animation: blinker 1s linear infinite;
		color: rgb(243, 156, 18) !important;
	}

	@keyframes blinker {
		50% {
			opacity: 0;
		}
	}
</style>
