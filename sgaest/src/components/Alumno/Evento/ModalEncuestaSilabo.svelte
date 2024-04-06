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
        class="modal-dialog modal-dialog-scrollable modal-dialog-centered modal-customized"
        backdrop="static"
>
    <ModalHeader class="border-0 pb-0" style="align-self: end">
        <slot name="modal-content-header">
            <Button class="btn-icon btn btn-white btn-lg rounded-circle" on:click={mToggle}>
                <svg class="p-1" xmlns="http://www.w3.org/2000/svg" width="33.941" height="33.941"
                     viewBox="0 0 33.941 33.941">
                    <g id="Grupo_775" data-name="Grupo 775" transform="translate(-687.308 -1024.598) rotate(45)">
                        <line id="Línea_1" data-name="Línea 1" y2="44" transform="translate(1234.5 216.5)" fill="none"
                              stroke="#1c3247" stroke-width="4"/>
                        <line id="Línea_2" data-name="Línea 2" y2="44" transform="translate(1256.5 238.5) rotate(90)"
                              fill="none" stroke="#1c3247" stroke-width="4"/>
                    </g>
                </svg>
            </Button>
        </slot>
    </ModalHeader>
    <ModalBody class="pt-0">
        <slot name="modal-content-body"></slot>
    </ModalBody>

</Modal>