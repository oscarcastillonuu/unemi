<script lang="ts">
	import { onMount } from 'svelte';
	import { converToAscii, action_print_ireport } from '$lib/helpers/baseHelper';
    import { variables } from '$lib/utils/constants';

	export let aData;
	let eDocumentos = [];
	onMount(async () => {
		eDocumentos = aData.eDocumentos;

	});

</script>

<div class="card-body">

	<div class="table-responsive">
		<table class="table table-sm mb-0 text-nowrap table-border table-hover" id = "rwd-table-biblio" >
			<thead class="table-light">
				<tr>
					<th scope="col" class="border-top-0 text-center align-middle " style="width: 10rem;">Tipo</th
					>
					<th scope="col" class="border-top-0 text-center align-middle " style="width: 15rem;">Archivo</th>
					<th scope="col" class="border-top-0 text-center align-middle " style="width: 15rem;">Estado</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Observación</th>


				</tr>
			</thead>
			<tbody>
				{#if eDocumentos.length > 0}
					{#each eDocumentos as documento}
						<tr>
							<td class="fs-6 align-middle border-top-0 text-wrap text-center nombre" style="width: 22rem;">
								<b>{documento[0]}</b>
							</td>
							<td class="fs-6 align-middle border-top-0 text-center text-wrap autor"
								style="width: 15rem;">
                                {#if documento[1]}
                                <a title="" href="{variables.BASE_API}{documento[1]}" target="_blank" class="btn btn-success btn-sm"><i class="bi bi-download"></i> Descargar</a>
                                {/if}
                            </td>
							<td class="fs-6 align-middle border-top-0 text-wrap text-center"
								style="width: 15rem;" >
                                {#if documento[1]}
                                    {#if documento[3] == 1}
                                    <span class="badge bg-info text-white" 
                                    >{documento[2]}</span>
                                    
                                    {:else if documento[3] == 2}
                                    <span class="badge bg-success" 
                                    >{documento[2]}</span>
                                    {:else}
                                    <span class="badge bg-danger" 
                                    >{documento[2]}</span>
                                    {/if}
                                {:else}
                                    <span class="badge bg-warning" 
                                    >NO CARGADO</span>
                                {/if}


							</td>
							<td class="fs-6 align-middle border-top-0 text-center">
								{#if documento[4] }
								{documento[4]}
								{/if}
                                        
							</td>
		
						</tr>
					{/each}
				{:else}
					<tr>
						<td colspan="8" class="text-center">NO EXISTEN ARCHIVOS</td>
					</tr>
				{/if}
			</tbody>
		</table>
	</div>
</div>