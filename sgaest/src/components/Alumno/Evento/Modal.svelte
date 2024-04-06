<script lang="ts">
    import {Button, Modal, ModalBody, ModalFooter, ModalHeader} from "sveltestrap";
    export let mOpen = false;
    export let mToggle;
    export let size = 'md';
</script>
<Modal
    isOpen={mOpen}
    toggle={mToggle}
    {size}
    class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
    backdrop="static"
>
    <ModalHeader class="pt-2 pb-2" toggle={mToggle} style="background-color: #ddd; !important; color: #0c0c0c;">
        <slot name="modal-content-header"></slot>
    </ModalHeader>
    <ModalBody>
        <slot name="modal-content-body"></slot>
    </ModalBody>
    <ModalFooter class="pt-1 pb-1">
        <slot name="modal-content-footer">
            <Button outline="secondary" class="pt-1 pb-1 btn-sm" on:click={mToggle}>
               <i class="mdi mdi-close"></i> Cerrar
            </Button>
        </slot>
    </ModalFooter>
</Modal>