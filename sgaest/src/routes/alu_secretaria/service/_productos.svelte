<script lang="ts">
	import Swal from 'sweetalert2';
	import { addToast } from '$lib/store/toastStore';
	import { browserGet, apiPOSTFormData, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import { onMount } from 'svelte';
	import { loading } from '$lib/store/loadingStore';
	import { converToAscii, action_print_ireport } from '$lib/helpers/baseHelper';
	import ComponenteCertificado from './_certificados.svelte';
	import ComponenteTitulacion from './_titulaciones.svelte';
	import { addNotification } from '$lib/store/notificationStore';
	import { Spinner, Tooltip } from 'sveltestrap';
	
	import { createEventDispatcher, onDestroy } from 'svelte';

	const dispatch = createEventDispatcher();

	export let eServicio;
	let eProductos = [];
	let dataExtras = {};
	let eMallaCulminada = '0';
	let eSolicitudT = []; 

	onMount(async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/secretary/product', {
			id: eServicio.id
		});
		loading.setLoading(false, 'Cargando, espere por favor...');
		if (errors.length > 0) {
			addNotification({
				msg: errors[0].error,
				type: 'error'
			});
		} else {
			if (!res.isSuccess) {
				addNotification({
					msg: res.message,
					type: 'error'
				});
			} else {
				//console.log(res.data);
				eProductos = res.data['eProductos'];
				dataExtras = res.data['extras'];
				eMallaCulminada = res.data['eMallaCulminada'];
				eSolicitudT = res.data['eSolicitudT']
			}
		}
	});
	const actionRun = (event) => {
		dispatch('actionRun', { action: event.detail.action, value: event.detail.value });
	};
</script>

{#if eServicio}
	{#if eServicio.proceso === 1 || eServicio.proceso === 2 || eServicio.proceso === 3 || eServicio.proceso === 8 || eServicio.proceso === 10}
		<ComponenteCertificado {eServicio} eCertificados={eProductos} dataExtras={dataExtras} eMallaCulminada={eMallaCulminada} on:actionRun={actionRun} />
	{:else if eServicio.proceso === 9 || eServicio.proceso === 7}	
		<ComponenteTitulacion {eServicio} eTitulaciones={eProductos} eSolicitudHom={eSolicitudT} on:actionRun={actionRun} />
	{/if}
{/if}
