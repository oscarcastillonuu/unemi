<script lang="ts">
    import { converToDecimal } from '$lib/formats/formatDecimal';
	import ModalTipo from '$components/Reporte/ModalTipo.svelte';
	import { onMount } from 'svelte';
	import { loading } from '$lib/store/loadingStore';
	import { action_print_ireport } from '$lib/helpers/baseHelper';
	import Swal from 'sweetalert2';
	export let aData;
    let eHistorialPago = {}

    onMount(async () => {
        if (aData.eHistorialComp) {
            eHistorialPago = aData.eHistorialComp;
        }
    });
</script>

<div class="card-body">
    <div class="table-responsive">
        <table class="table table-sm mb-0 text-nowrap table-border table-hover" id = "rwd-table-histo" >
            <thead class="table-light">
                <tr>
                    <th scope="col" class="border-top-0 text-center align-middle " style="width: 10rem;">Fecha</th
                        >
                    <th scope="col" class="border-top-0 text-center align-middle " style="width: 15rem;">Persona</th>
                    <th scope="col" class="border-top-0 text-center align-middle " style="width: 25rem;">Observación</th>
                    <th scope="col" class="border-top-0 text-center align-middle ">Estado</th>
                </tr>
            </thead>
            <tbody>
                {#if eHistorialPago.length >0}
                    {#each eHistorialPago as his}
                    <tr>
                        <td class="fs-6 align-middle border-top-0 text-wrap nombre" style="width: 22rem;">
                            {his.fecha}
                        </td>
                        <td class="fs-6 align-middle border-top-0 text-center text-wrap autor"
                            style="width: 15rem;">
                            {his.persona.nombre_completo}
                        </td>
                        <td class="fs-6 align-middle border-top-0 text-wrap text-center"
                            style="width: 15rem;" >
                            {his.observacion}
                        </td>
                        <td class="fs-6" style="text-align: center; color: green;">
                            {#if his.estado == 1}
                            <span class="badge bg-secondary ">{ his.estado_display }</span>
                            {:else if his.estado == 2}
                                <span class="badge bg-info ">{ his.estado_display }</span>

                            {:else if his.estado == 3}
                                <span class="badge bg-danger ">{ his.estado_display }</span>

                            {:else if his.estado == 4}
                                <span class="badge bg-success ">{ his.estado_display } </span>

                            {/if}
                        </td>
                    </tr>
                    {/each}
                {:else}
					<tr>
						<td colspan="5" class="text-center">NO EXISTE HISTORIAL DISPONIBLE</td>
					</tr>
                {/if}
            </tbody>
        </table>
    </div>
</div>