<script lang="ts">
	import { variables } from '$lib/utils/constants';
	import { createEventDispatcher } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader } from 'sveltestrap';
	export let mOpen = false;
	export let mToggle;
	export let modalContent;
	export let aData;
	export let title;
	export let size = 'md';
    export let saveInsignia;
	const dispatch = createEventDispatcher();
	function actionRun(event) {
		//alert(event.detail.text);
		dispatch('actionRun', event.detail);
	}
</script>

<Modal
	isOpen={mOpen}
	toggle={mToggle}
	{size}
	class="modal-dialog modal-dialog-centered modal-dialog-scrollable "
	backdrop="static"
    contentClassName="bg-transparent border-0"
>
	<svelte:component this={modalContent} {aData} {mToggle} {saveInsignia} on:actionRun={actionRun} />
</Modal>
