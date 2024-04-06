<script lang="ts">
	import { createEventDispatcher, onMount, onDestroy } from 'svelte';
	import { loading } from '$lib/store/loadingStore';
	import { variables } from '$lib/utils/constants';
	import { addToast } from '$lib/store/toastStore';
	import { Icon } from 'sveltestrap';
	export let aData;
	let ePersona;
	let documento = '';
	const dispatch = createEventDispatcher();
	onMount(async () => {
		//console.log(aData);
	});
	const cerrarModal = () => {
		dispatch('actionRun', { action: 'closeModal' });
	};
	const searchPersona = async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const res = await fetch(`${variables.BASE_API_URI}/token/recoverypassword`, {
			method: 'POST',
			mode: 'cors',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				action: 'searchPerson',
				documento: `${documento}`
			})
		});
		if (res.status >= 400) {
			addToast({
				header: 'Error',
				body: 'Ocurrio un error inesperado',
				type: 'error'
			});
		} else if (!res.ok) {
			addToast({ type: 'error', header: 'Error de conexión', body: 'Ocurrio un error inesperado' });
		} else {
			const response = await res.json();
			if (!response.isSuccess) {
				addToast({
					header: 'Error',
					body: response.message,
					type: 'error'
				});
			} else {
				ePersona = response.data;
			}
		}
		loading.setLoading(false, 'Cargando, espere por favor...');
	};

	const generatePassword = async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const res = await fetch(`${variables.BASE_API_URI}/token/recoverypassword`, {
			method: 'POST',
			mode: 'cors',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				action: 'generatePassword',
				id: `${ePersona.id}`
			})
		});
		loading.setLoading(false, 'Cargando, espere por favor...');
		if (res.status >= 400) {
			addToast({
				header: 'Error',
				body: 'Ocurrio un error inesperado',
				type: 'error'
			});
		} else if (!res.ok) {
			addToast({ type: 'error', header: 'Error de conexión', body: 'Ocurrio un error inesperado' });
		} else {
			const response = await res.json();
			dispatch('actionRun', { action: 'closeModal' });
			if (!response.isSuccess) {
				addToast({
					header: 'Error',
					body: response.message,
					type: 'error'
				});
			} else {
				addToast({
					header: 'Proceso Exitoso',
					body: response.message,
					type: 'success'
				});
			}
		}
	};
</script>

{#if !ePersona}
	<div class="mb-4">
		<center>
			<form>
				<h2 class="texto-warning fw-bold" style="color: #FE9900">Recuperar datos de cuenta</h2>
				<p class="text-muted">Ingrese su número de documento <br />para validar su cuenta:</p>
				<!--<label class="form-label">Documento</label>-->
				<input
					bind:value={documento}
					class="form-control form-control-lg fs-6"
					type="text"
					name="documento"
					placeholder="Ingrese su número de cédula/ruc/pasaporte.."
				/>
				<button
					class="btn btn-lg btn-warning mt-3 px-6 rounded-pill px-8"
					style="background-color: #FA7E23;"
					on:click|preventDefault={searchPersona}>Validar</button
				>
			</form>
		</center>
	</div>
{:else}
	<div class="mb-4">
		<center>
			<img src="./assets/images/svg/icon_user_check.svg" style="width: 70px" />
			<h2 class="text-warning" style="color: #FE9900 !important;">Datos de cuenta</h2>
			<p class="text-primary fw-bold" style="color: #1c3247 !important;">
				{ePersona.nombre_completo}
			</p>
			<p class="text-muted">
				Su nombre de usuario es:
				<span class="text-primary fw-bold" style="color: #1c3247 !important;"
					>{ePersona.usuario}</span
				>
			</p>

			{#if ePersona.tieneCorreo}
				<p class="text-muted">
					Sus correos son:
					<span class="text-primary fw-bold" style="color: #1c3247 !important;"
						>{ePersona.correos}</span
					>
				</p>
				<div class="mt-3 d-grid gap-2 d-md-block">
					<button
						on:click={cerrarModal}
						class="btn btn-lg btn-secondary rounded-pill px-8"
						style="border-color: #E7E7E7;
						background-color: #E7E7E7;
						color: black;"
						>Cerrar
					</button>
					<button
						class="btn btn-lg btn-warning rounded-pill px-8"
						on:click|preventDefault={generatePassword}>Aceptar</button
					>
				</div>
			{:else}
				<p class="text-danger">
					Estimad{ePersona.es_mujer ? 'a' : 'o'}, en nuestra base de datos no tenemos registrado una
					cuenta de correo electrónico, por favor solicitar el cambio de contraseña al Balcón de
					Servicios.
				</p>
				<div class="mt-3 d-grid gap-2 d-md-block">
					<button
						on:click={cerrarModal}
						class="btn btn-lg btn-secondary rounded-pill px-8"
						style="border-color: #E7E7E7;
						background-color: #E7E7E7;
						color: black;"
						>Cerrar
					</button>
				</div>
			{/if}
		</center>
	</div>
{/if}
