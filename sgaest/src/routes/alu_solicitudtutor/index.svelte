<script context="module" lang="ts">
	import type { Load } from '@sveltejs/kit';
	let clasificacion = 0;
	let display_clasificacion = undefined;
	let message_error = undefined;
	let is_error = false;
	let eSolicitudes = [];
	export const load: Load = async ({ params, fetch }) => {
		const ds = browserGet('dataSession');

		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const coordinacion = <Coordinacion>dataSession['coordinacion'];
			const display_clasificacion = coordinacion.display_clasificacion.toLowerCase();
			clasificacion = coordinacion.clasificacion;
			const url = `alumno/solicitud_tutor/${display_clasificacion}`;
			//console.log(url);
			const [res, errors] = await apiGET(fetch, url, {});
			if (errors.length > 0) {
				//addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				message_error = errors[0].error;
				is_error = true;
			} else {
				if (!res.module_access) {
					addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
					return {
						status: 302,
						redirect: '/'
					};
				}
				//console.log(res.message);
				if (!res.isSuccess) {
					message_error = res.message;
					is_error = true;
				} else {
					message_error = '';
					is_error = false;
					eSolicitudes = res.data.eSolicitudes;
				}
			}
		}
		return {
			props: {
				clasificacion,
				display_clasificacion,
				message_error,
				is_error,
				eSolicitudes
			}
		};
	};
</script>

<script lang="ts">
	import { onMount } from 'svelte';
	import type { Coordinacion } from '$lib/interfaces/user.interface';
	import { browserGet, apiGET } from '$lib/utils/requestUtils';
	import Pregrado from './_Pregrado/index.svelte';
	import Posgrado from './_Posgrado/index.svelte';
	import Admision from './_Admision/index.svelte';
	import ModuleError from './_Error.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { navigating } from '$app/stores';
	import { Spinner } from 'sveltestrap';
	import { addToast } from '$lib/store/toastStore';
	export let clasificacion;
	export let display_clasificacion;
	export let message_error;
	export let is_error;
	export let eSolicitudes;
	let load = true;
	//console.log($navigating);
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {
		if (clasificacion !== undefined) {
			load = false;
		}
		//console.log(clasificacion);
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
	};
</script>

{#if !load}
	{#if !is_error}
		{#if clasificacion === 1}
			<svelte:component this={Pregrado} {eSolicitudes} on:actionRun={actionRun} />
		{:else if clasificacion === 2}
			<svelte:component this={Posgrado} {eSolicitudes} on:actionRun={actionRun} />
		{:else if clasificacion === 3}
			<Admision />
		{:else}
			<ModuleError
				title="Consulta a tutor de {display_clasificacion}"
				message="No tiene definido una coordinación valida, favor contactarse con la coordinación de la carrera"
			/>
		{/if}
	{:else}
		<ModuleError title="Consulta a tutor de {display_clasificacion}" message={message_error} />
	{/if}
{:else}
	<div
		class="m-0 vh-100 row justify-content-center align-items-center"
		style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 1000; display: flex; flex-direction: column; align-items: center; justify-content: center;"
	>
		<div class="col-auto text-center">
			<Spinner color="primary" type="border" style="width: 3rem; height: 3rem;" />
			<h3>Verificando la información, espere por favor...</h3>
		</div>
	</div>
{/if}
