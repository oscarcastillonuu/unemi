<script context="module" lang="ts">
	import type { Load } from '@sveltejs/kit';

	export const load: Load = async () => {
		return {
			props: {}
		};
	};
</script>

<script lang="ts">
	import { apiPOST, browserGet } from '$lib/utils/requestUtils';
	import { addToast } from '$lib/store/toastStore';
	import { onMount } from 'svelte';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';

	let itemsBreadCrumb = [{ text: 'Matriculación', active: true, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };
	onMount(async () => {
		//console.log('pasa Admisión');
	});
</script>

<svelte:head>
	<title>Adicionar y Quitar Materia Admisión</title>
</svelte:head>
<BreadCrumb title="Matriculación Admisión" items={itemsBreadCrumb} back={backBreadCrumb} />
