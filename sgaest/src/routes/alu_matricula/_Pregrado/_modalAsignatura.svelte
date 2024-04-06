<script>
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader } from 'sveltestrap';
	export let Open;
	export let Toggle;
	export let Title;
</script>

<Modal isOpen={Open} toggle={Toggle} size="xl">
	<ModalHeader toggle={Toggle}>{Title}</ModalHeader>
	<ModalBody />
	<ModalFooter>
		<Button color="primary" on:click={Toggle}>Cerrar</Button>
	</ModalFooter>
</Modal>
