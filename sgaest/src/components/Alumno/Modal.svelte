<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader } from 'sveltestrap';
	export let mOpen = false;
	export let mToggle;
	export let modalContent;
	export let mClass =
		'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down';
	export let aData;
	export let title;
	export let size = 'md';
	export let mClose = true;
	const dispatch = createEventDispatcher();
	function actionRun(event) {
		//alert(event.detail.text);
		dispatch('actionRun', event.detail);
	}
</script>

<Modal isOpen={mOpen} toggle={mToggle} {size} class={mClass} backdrop="static">
	{#if title}
		<ModalHeader toggle={mToggle} class="bg-primary text-white">
			<span class="text-white">{title}</span>
		</ModalHeader>
	{:else}
		<ModalHeader toggle={mToggle} class="text-white border-0" />
	{/if}
	<ModalBody>
		<svelte:component this={modalContent} {aData} on:actionRun={actionRun} />
	</ModalBody>
	{#if mClose}
		<ModalFooter>
			<Button color="warning" class="rounded-3 btn-sm" on:click={mToggle}>Cerrar</Button>
		</ModalFooter>
	{/if}
</Modal>
