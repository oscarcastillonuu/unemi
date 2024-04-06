<script lang="ts">
	import Automatricula from './_automatricula.svelte';
	import Matricula from './_matricula.svelte';
	import { onMount } from 'svelte';
	import { Spinner } from 'sveltestrap';
	let load = true;
	export let data;

	onMount(async () => {
		if (data.tipo !== undefined) {
			load = false;
		}
	});
</script>

{#if !load}
	{#if data.tipo === 'matricula'}
		<Matricula aData={data.aData} />
	{:else if data.tipo === 'automatricula'}
		<Automatricula aData={data.aData} />
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
