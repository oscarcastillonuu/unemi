<script lang="ts">
    import {variables} from "$lib/utils/constants";
    import {loading} from '$lib/store/loadingStore';
    import {onMount} from 'svelte';
    import {createEventDispatcher} from 'svelte';
    import {Icon, Button, Modal, ModalBody, ModalFooter, ModalHeader, Form, Spinner} from 'sveltestrap';

    import {navigating} from "$app/stores";
    import Swal from "sweetalert2";
    import {apiPOST} from "$lib/utils/requestUtils";
    import {addToast} from "$lib/store/toastStore";

    export let aData;
    export let mOpen = false;
    export let mToggle;
    export let size = 'md';
    let load = true;
    let ePersona;
    let mensaje_load = 'Cargando la información, espere por favor...';


    $: loading.setNavigate(!!$navigating);
    $: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
    const delay = (ms) => new Promise((res) => setTimeout(res, ms));

    const dispatch = createEventDispatcher();

    onMount(async () => {

        load = false;
    });


    const actionSaveSede = async (id_sede,padronelectoral_id,display) => {
		const mensaje = {
			title: 'CONFIRMACIÓN DE SEDE',
			html: '¿ESTÁ SEGURO DE REGISTRASE EN LA SEDE DE: <b>'+display+ '</b>?',
			icon: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: `Confirmar`,
			cancelButtonText: 'Cancelar'
		};
		Swal.fire(mensaje)
		.then(async (result)=>{
			if (result.value) {
				loading.setLoading(true, 'Cargando, espere por favor...');
				const [res, errors] = await apiPOST(fetch, 'alumno/sedeelectoral/save', {
					id:id_sede,
					periodoelectoral:padronelectoral_id,
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				if (errors.length > 0) {
					addToast({ type: 'warning', header: 'Advertencia', body: errors[0].error });
					return;
				} else {
					if (!res.isSuccess) {
						addToast({ type: 'warning', header: 'Advertencia', body: res.message });
						return;
					} else {
                        mOpen = !mOpen;
                        addToast({ type: 'success', header: 'Correcto', body: res.data['mensaje'] });

					}
				}
			}
		}).catch((error) => {
			addToast({ type: 'warning', header: 'Advertencia', body: error });
			return;
		});
	}



</script>

{#if !load}
    <Modal
            isOpen={mOpen}
            toggle={mToggle}
            {size}
            class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
            backdrop="static"
    >
        {#if !aData.obligatoria}
            <ModalHeader toggle={mToggle} class="bg-primary text-white">
                <span class="text-white">Confirmación lugar de votación</span>
            </ModalHeader>
        {:else}
            <ModalHeader class="bg-primary text-white">
                <span class="text-white">Confirmación lugar de votación</span>
            </ModalHeader>
        {/if}

        <ModalBody>
            {#if !load}
                <h2 style="text-align: center">
                    { aData.padronelectoral.nombre }
                </h2>



                <div class='row-fluid'>
                    <p class="text-warning text-center"  >
                        <i class="fe fe-help-circle"></i> Recuerda seleccionar con <b>responsabilidad</b> tu lugar de
                        votación. Este proceso es <b>obligatorio</b>.
                    </p>

                    <div id="no-more-tables">
                        <table class="table table-bordered table-responsive">
                            <thead>
                            <tr>
                                <th style="text-align: center">Cantón</th>
                                <th style="text-align: center"><i class="fe fe-check-circle"></i></th>
                            </tr>
                            </thead>
                            <tbody>
                            {#each aData.listadosedes as l}
                                <tr>
                                    <td data-title='Cantón:' style="text-align: center">{ l.canton.nombre }</td>
                                    <td data-title='Acción:' style="text-align: center">
                                        <a href="javascript:void(0)" on:click={actionSaveSede(l.pk,aData.padronelectoral.pk,l.canton.nombre)} class="btn btn-xs btn-success">Seleccionar</a>
                                    </td>
                                </tr>
                            {:else }

                            {/each}

                            </tbody>
                        </table>
                    </div>

                     {#if aData.padronelectoral.fechalimiteconfirmacionsede }
                        <p class="text-danger text-center"  >
                            <i class="fe fe-alert-triangle"></i> Límite para la selección de sedes,
                            <b>{aData.padronelectoral.fechalimiteconfirmacionsede_letra} </b>. De no efectuar el
                            registro su sede de votacion será la <b>Ciudad de Milagro</b>.
                        </p>
                    {/if}
                </div>

            {:else}
                <div class="m-0 my-5 justify-content-center align-items-center">
                    <div class="text-center align-middle">
                        <Spinner color="primary" type="border" style="width: 3rem; height: 3rem;"/>
                    </div>
                </div>
            {/if}
        </ModalBody>
        <ModalFooter>
            {#if !aData.obligatoria}
            <Button color="secondary" class="rounded-3 btn-sm" on:click={mToggle}>Cerrar</Button>
            {/if}

        </ModalFooter>
    </Modal>
{/if}

<style>
    .form-select {
        border-color: #aaa;
    }

    .form-control {
        border-color: #aaa;
    }
</style>