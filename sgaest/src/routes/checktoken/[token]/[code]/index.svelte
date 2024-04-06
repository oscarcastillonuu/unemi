<script context="module" lang="ts">
	import type { Load } from '@sveltejs/kit';
	import { session, page, navigating } from '$app/stores';

	export const load: Load = async ({ params, fetch }) => {
		const token = params.token;
		const code = params.code;
		const ds = browserGet('dataSession');
		let ePersonaLogin = {};
		let eInscripcionLogin = {};
		let ePersonaToken = {};
		let eInscripcionToken = {};
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			ePersonaLogin = dataSession['persona'];
			const PerfilPrincipal = dataSession['perfilprincipal'];
			const Inscripcion = dataSession['inscripcion'];
			let perfiles = [];
			const eperfiles = dataSession['perfiles'];
			for (const i in eperfiles) {
				perfiles.push(eperfiles[i]);
			}
			perfiles.forEach((element) => {
				//console.log(element.id);
				//console.log(PerfilPrincipal);
				if (element.id === PerfilPrincipal.id) {
					eInscripcionLogin = {
						id: Inscripcion.id,
						carrera: {
							nombre: element.carrera
						}
					};
				}
			});
			const res = await fetch(`${variables.BASE_API_URI}/token/check`, {
				method: 'POST',
				mode: 'cors',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					token: `${token}`,
					code: `${code}`
				})
			});
			if (res.status >= 400) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: 'Usuario no identificado' });
				return {
					status: 302,
					redirect: '/login'
				};
			} else if (!res.ok) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: 'Error de conexión' });
				return {
					status: 302,
					redirect: '/login'
				};
			}
			const response = await res.json();
			if (!response.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: `${response.message}` });
				return {
					status: 302,
					redirect: '/login'
				};
			} else {
				ePersonaToken = response.data.ePersona;
				eInscripcionToken = response.data.eInscripcion;
				if (ePersonaToken.id === ePersonaLogin.id) {
					return {
						status: 302,
						redirect: '/'
					};
				}
			}
		}
		return {
			props: {
				ePersonaLogin,
				eInscripcionLogin,
				ePersonaToken,
				eInscripcionToken,
				token,
				code
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
	export let ePersonaLogin;
	export let eInscripcionLogin;
	export let ePersonaToken;
	export let eInscripcionToken;
	export let token;
	export let code;
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (ePersonaLogin.id === undefined && ePersonaToken.id === undefined) {
			loading.setLoading(true, 'Cargando, espere por favor...');
			const res = await fetch(`${variables.BASE_API_URI}/token/check`, {
				method: 'POST',
				mode: 'cors',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					token: `${token}`,
					code: `${code}`
				})
			});
			if (res.status >= 400) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: 'Usuario no identificado' });
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
				ePersonaToken = response.data.ePersona;
				eInscripcionToken = response.data.eInscripcion;
			}
			loading.setLoading(false, 'Cargando, espere por favor...');
		}
	});

	const checkLogin = async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const res = await fetch(`${variables.BASE_API_URI}/token/logincheck`, {
			method: 'POST',
			mode: 'cors',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				token: `${token}`,
				code: `${code}`
			})
		});
		if (res.status >= 400) {
			addNotification({
				msg: 'Usuario no identificado',
				type: 'error'
			});
		} else if (!res.ok) {
			addNotification({
				msg: 'Error de conexión',
				type: 'error'
			});
		}
		const response = await res.json();
		const json = decodeToken(response);
		const UserResponse: UserResponse = json;
		if (UserResponse.tokens) {
			browserSet('refreshToken', UserResponse.tokens.refresh);
			browserSet('accessToken', UserResponse.tokens.access);
			browserSet('dataSession', JSON.stringify(UserResponse));
			await goto('/');
		}
		loading.setLoading(false, 'Cargando, espere por favor...');
	};
</script>

{#if eInscripcionLogin.carrera && eInscripcionToken.carrera}
	<div class="row row-cols-2 row-cols-md-12 g-4">
		<div class="col">
			<div class="card h-100">
				<div class="card-body">
					<div class="text-center">
						<img
							alt="avatar"
							src={ePersonaLogin.foto}
							onerror="this.onerror=null;this.src='./image.png'"
							class="rounded-circle avatar-xl mb-3"
						/>
						<h4 class="mb-0">{ePersonaLogin.nombre_completo}</h4>
						<p class="mb-0">{eInscripcionLogin.carrera.nombre}</p>
					</div>
				</div>
				<div class="card-footer">
					<small class="text-muted">Perfil Anterior</small>
				</div>
			</div>
		</div>
		<div class="col">
			<div class="card h-100">
				<div class="card-body">
					<div class="text-center">
						<img
							alt="avatar"
							src={ePersonaToken.foto_perfil}
							onerror="this.onerror=null;this.src='./image.png'"
							class="rounded-circle avatar-xl mb-3"
						/>
						<h4 class="mb-0">{ePersonaToken.nombre_completo}</h4>
						<p class="mb-0">{eInscripcionToken.carrera.nombre}</p>
					</div>
				</div>
				<div class="card-footer">
					<small class="text-muted">Perfil a Ingresar</small>
				</div>
			</div>
		</div>
	</div>

	<div class="d-grid gap-2 mt-3">
		<button class="btn btn-primary" type="button" on:click|preventDefault={() => checkLogin()}
			>Cambiar de perfil</button
		>
	</div>
{:else if eInscripcionToken.carrera}
	<div class="row row-cols-1 row-cols-md-12 g-4">
		<div class="col">
			<div class="card h-100">
				<div class="card-body">
					<div class="text-center">
						<img
							alt="avatar"
							src={ePersonaToken.foto_perfil}
							onerror="this.onerror=null;this.src='./image.png'"
							class="rounded-circle avatar-xl mb-3"
						/>
						<h4 class="mb-0">{ePersonaToken.nombre_completo}</h4>
						<p class="mb-0">{eInscripcionToken.carrera.nombre}</p>
					</div>
				</div>
				<div class="card-footer">
					<small class="text-muted">Perfil a Ingresar</small>
				</div>
			</div>
		</div>
	</div>

	<div class="d-grid gap-2 mt-3">
		<button class="btn btn-primary" type="button" on:click|preventDefault={() => checkLogin()}
			>Ingresar</button
		>
	</div>
{:else}
	<div class="spinner-border" role="status">
		<span class="visually-hidden">Loading...</span>
	</div>
{/if}
