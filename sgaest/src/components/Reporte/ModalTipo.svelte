<script lang="ts">
	import { addNotification } from '$lib/store/notificationStore';

	import { createEventDispatcher, onMount } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader } from 'sveltestrap';
	export let mOpen = false;
	export let mToggle;
	export let aData;
	export let title = 'Formato de descarga';
	export let size = 'sm';
	let aTipos = [];
	let selected = '';
	onMount(async () => {
		aTipos = aData.aTipos;
	});
	const dispatch = createEventDispatcher();

	const actionRun = () => {
		//alert(event.detail.text);

		if (selected === '') {
			addNotification({ msg: 'Favor seleccione un formato de descarga.', type: 'warning' });
			return;
		}
		dispatch('actionDownload', {
			type: selected
		});
	};
</script>

<Modal
	isOpen={mOpen}
	toggle={mToggle}
	{size}
	class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
	backdrop="static"
>
	<ModalHeader toggle={mToggle}>
		<h4>
			<span>{title}</span>
		</h4>
	</ModalHeader>
	<ModalBody>
		<div class="mb-3">
			<label class="form-label" for="selectOne">Seleccione:</label>
			{#if aTipos && aTipos.length > 0}
				<select class="form-select" bind:value={selected}>
					<option selected value="">---------</option>
					{#each aTipos as aTipo}
						<option value={aTipo.value}>{aTipo.text}</option>
					{/each}
				</select>
			{/if}
		</div>
	</ModalBody>
	<ModalFooter>
		<Button color="success" on:click={actionRun}>Descargar</Button>
		<Button color="primary" on:click={mToggle}>Cerrar</Button>
	</ModalFooter>
</Modal>
