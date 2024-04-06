<script context="module" lang="ts">
	import type { Load } from '@sveltejs/kit';
	let clasificacion = 0;
	let display_clasificacion = undefined;
	let message_error = undefined;
	let is_error = false;
	let data = Object;
	export const load: Load = async () => {
		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const coordinacion = <Coordinacion>dataSession['coordinacion'];
			const connectionToken = dataSession['connectionToken'];
			display_clasificacion = coordinacion.display_clasificacion.toLowerCase();			
			clasificacion = coordinacion.clasificacion;
			const url = `alumno/matricula/${display_clasificacion}`;			
			//console.log(url);
			const [res, errors] = await apiGET(fetch, url, {});						
			//console.log(res);
			if (errors.length > 0) {
				//addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				message_error = errors[0].error;
				is_error = true;
			} else {
				if (!res.module_access) {
					if (res.redirect) {
						if (res.token) {
							return (window.location.href = `${connectionToken}&ret=/${res.redirect}`);
						} else {
							addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
							return {
								status: 302,
								redirect: `${res.redirect}`
							};
						}
					} else {
						addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
						return {
							status: 302,
							redirect: '/'
						};
					}
					addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });

					//addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				}
				//console.log(res.message);
				if (!res.isSuccess) {
					message_error = res.message;
					is_error = true;
				} else {
					message_error = '';
					is_error = false;
					data = res.data;
				}
			}
		}

		return {
			props: {
				clasificacion,
				display_clasificacion,
				message_error,
				is_error,
				data
			}
		};
	};
</script>

<script lang="ts">
	import { onMount } from 'svelte';
	import type { Coordinacion } from '$lib/interfaces/user.interface';
	import { browserGet, apiGET } from '$lib/utils/requestUtils';
	import Pregrado from './_Pregrado/_index.svelte';
	import Posgrado from './_Posgrado/_index.svelte';
	import Admision from './_Admision/_index.svelte';
	import ModuleError from './_Error.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { navigating } from '$app/stores';
	import { Spinner } from 'sveltestrap';
	import { addToast } from '$lib/store/toastStore';
	import { goto } from '$app/navigation';

	export let clasificacion;
	export let display_clasificacion;
	export let message_error;
	export let is_error;
	export let data;
	let load = true;
	//console.log($navigating);
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {
		if (clasificacion !== undefined) {
			load = false;
		}
	});

	$: {
		//console.log($navigating);
	}
</script>

{#if !load}
	{#if !is_error}
		{#if clasificacion === 1}
			<Pregrado {data} />
		{:else if clasificacion === 2}			
			<Posgrado {data} />
		{:else if clasificacion === 3}
			<Admision {data} />
		{:else}
			<ModuleError
				title="Matriculación {display_clasificacion}"
				message="No tiene definido una coordinación valida, favor contactarse con la coordinación de la carrera"
			/>
		{/if}
	{:else}
		<ModuleError title="Matriculación {display_clasificacion}" message={message_error} />
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
