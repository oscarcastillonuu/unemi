<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import { Spinner } from 'sveltestrap';
	import { navigating } from '$app/stores';
	import { loading } from '$lib/store/loadingStore';
	import Iframe from '$components/Iframe.svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	export let aData;
	export let mToggle;
	export let mOpenModal;
	export let mTitle;
	export let mClass =
		'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-lg-down';
	export let mSize = 'lg';
	let url = undefined;
	let load = true;

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		url = aData.url ?? url;
		await delay(2000);
		load = false;
	});
</script>

{#if mOpenModal}
	<Modal isOpen={mOpenModal} toggle={mToggle} size={mSize} class={mClass} backdrop="static">
		{#if mTitle}
			<ModalHeader toggle={mToggle} class="bg-primary text-white">
				<span class="text-white">{mTitle}</span>
			</ModalHeader>
		{/if}
		<ModalBody>
			{#if !load}
				{#if url}
					<Iframe app="pdf" {url} />
				{/if}
			{:else}
				<div class="row justify-content-center align-items-center p-5 m-0">
					<div class="col-auto text-center">
						<Spinner color="primary" type="border" style="width: 3rem; height: 3rem;" />
						<h3>Construyendo la información, espere por favor...</h3>
					</div>
				</div>
			{/if}
		</ModalBody>

		<ModalFooter class="p-1">
			<Button color="secondary" class="rounded-5 btn-sm " on:click={mToggle}
				><i class="fe fe-x" /> Cancelar</Button
			>
		</ModalFooter>
	</Modal>
{/if}
