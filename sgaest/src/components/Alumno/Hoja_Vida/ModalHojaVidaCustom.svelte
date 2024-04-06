<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader } from 'sveltestrap';
	export let mOpen = false;
	export let mToggle;
	export let modalContent;
	export let mClass =
		'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down modal-relative';
	export let aData;
	export let title;
	export let size = 'md';
	const dispatch = createEventDispatcher();
	function actionRun(event) {
		//alert(event.detail.text);
		dispatch('actionRun', event.detail);
	}
</script>

<Modal isOpen={mOpen} toggle={mToggle} {size} class={mClass} backdrop="static">
	<ModalHeader toggle={mToggle} class="bg-primary text-white">
		<span class="text-white">{title}</span>
	</ModalHeader>
	<ModalBody>
		<svelte:component this={modalContent} {aData} {mToggle} on:actionRun={actionRun} />
	</ModalBody>
	<!-- <ModalFooter>
		<Button color="warning" class="rounded-3 btn-sm" on:click={mToggle}>Cerrar</Button>
	</ModalFooter> -->
</Modal>
