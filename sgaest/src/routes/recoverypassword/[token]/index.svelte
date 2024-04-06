<script context="module" lang="ts">
	import type { Load } from '@sveltejs/kit';
	import { session, page, navigating } from '$app/stores';

	export const load: Load = async ({ params, fetch }) => {
		const token = await params.token;

		return {
			props: {
				token
			}
		};
	};
</script>

<script lang="ts">
	import { apiPOST, browserGet, browserSet } from '$lib/utils/requestUtils';
	import { variables } from '$lib/utils/constants';
	import { goto } from '$app/navigation';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import { onMount } from 'svelte';
	import { addNotification } from '$lib/store/notificationStore';
	import { decodeToken } from '$lib/utils/decodetoken';
	import type { UserResponse } from '$lib/interfaces/user.interface';
	import { Icon } from 'sveltestrap';
	import { encodeQueryString } from '$lib/helpers/baseHelper';
	export let token;
	let ePersona;
	let eUserToken;
	let password1 = '';
	let password2 = '';
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		if (token) {
			const res = await fetch(`${variables.BASE_API_URI}/token/recoverypassword`, {
				method: 'POST',
				mode: 'cors',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					action: 'verifyToken',
					token: `${token}`
				})
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (res.status >= 400) {
				addToast({ type: 'error', header: 'Error', body: 'Ocurrio un error inesperado' });
				goto('/login');
			} else if (!res.ok) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: 'Error de conexión' });
				goto('/login');
			}
			const response = await res.json();
			if (!response.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: `${response.message}` });
				goto('/login');
			} else {
				ePersona = response.data.ePersona;
				eUserToken = response.data.eUserToken;
			}
		} else {
			goto('/login');
		}
	});

	const handleChangePassword = async () => {
		
		if (password1 != password2){
			addToast({ type: 'error', header: 'Error', body: 'Contraseñas no son iguales' });
			return;
		}
		loading.setLoading(true, 'Cargando, espere por favor...');
		const res = await fetch(`${variables.BASE_API_URI}/token/recoverypassword`, {
				method: 'POST',
				mode: 'cors',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					action: 'changePassword',
					token: `${token}`,
					password1: `${password1}`,
					password2: `${password2}`,
				})
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (res.status >= 400) {
				addToast({ type: 'error', header: 'Error', body: 'Ocurrio un error inesperado' });
				return;
			} else if (!res.ok) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: 'Error de conexión' });
				return;
			}
			const response = await res.json();
			if (!response.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: `${response.message}` });
				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: `${response.message}` });
				goto("/login");
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
		if (password1 === password2) {
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
	<div class="card card-outline card-primary">
		<div class="card-header text-center">
			<h2 class="mb-1 fw-bold">Recuperar contraseña</h2>
		</div>
		<!-- Card body -->
		<div class="card-body p-4">
			<div class="mb-1">
				<p class="text-center">
					Hola <b>{ePersona.nombre_completo}</b>, estás a un paso de tu nueva contraseña, recupera tu contraseña ahora.
				</p>
				<h6 class="fs-6">
					<Icon name="info-circle" /> La contraseña debe cumplir con los siguientes parámetros:
				</h6>
				<ul style="font-size: 11px;">
					<li style="list-style-type: circle;" id="letter">Al menos <strong>una letra</strong></li>
					<li style="list-style-type: circle;" id="capital">
						Al menos <strong>una letra en mayúscula y una letra en minúscula</strong>
					</li>
					<li style="list-style-type: circle;" id="number">Al menos <strong>un número</strong></li>
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
								on:keyup={({ target: { value } }) => keyUPPassword(value)}
							/>
							<label for="floatingInputGridPassword1">Contraseña</label>
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
							<label for="floatingInputGridPassword2">Confirmar contraseña</label>
						</div>
					</div>
				</div>
				<!--<div class="input-group mb-2">
					<input
						type="password"
						bind:value={password1}
						class="form-control"
						placeholder="Contraseña"
					/>
					<div class="input-group-append">
						<div class="input-group-text">
							<Icon name="lock-fill" />
						</div>
					</div>
				</div>
				<div class="input-group mb-2">
					<input
						type="password"
						bind:value={password2}
						class="form-control"
						placeholder="Confirmar Contraseña"
					/>
					<div class="input-group-append">
						<div class="input-group-text">
							<Icon name="lock-fill" />
						</div>
					</div>
				</div>-->
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
			<p class="mt-3 mb-1">
				<a href="/" style="color: rgb(243, 156, 18) !important;"
					><Icon name="arrow-left-circle" /> <b>Inicio de sesión</b></a
				>
			</p>
		</div>
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
