<script lang="ts">
	import { onMount } from 'svelte';
	import { converToAscii, action_print_ireport } from '$lib/helpers/baseHelper';
	export let aData;

</script>

<table class="table  table-responsive" id="rwd-table-histo">
	<thead class="table-light">
	
		<tr>
			<th scope="col" class="border-top-0 text-center align-middle " style="width: 10rem;">Fecha</th
			>
			<th scope="col" class="border-top-0 text-center align-middle " style="width: 15rem;"
				>Persona</th
			>
			<th scope="col" class="border-top-0 text-center align-middle ">Estado</th>
          
		</tr>
	</thead>
	<tbody>
		{#if aData.historial_prorroga_propuesta.length > 0}
			{#each aData.historial_prorroga_propuesta as historial}
				<tr>
					<td class="fs-6 align-middle border-top-0 text-wrap nombre" style="width: 22rem;">
						{historial.fecha_creacion}
					</td>
					<td
						class="fs-6 align-middle border-top-0 text-center text-wrap autor"
						style="width: 15rem;"
					>
						{historial.persona.display}
					</td>

                    <td class="fs-6 align-middle border-top-0 text-center">
						{#if historial.estado == 1}
							<span class="badge bg-warning">{historial.estado_display}</span>
						{:else if historial.estado == 2}
							<span class="badge bg-success">{historial.estado_display}</span>
						{:else}
							<span class="badge bg-danger">{historial.estado_display}</span>
						{/if}
					</td>

				
					
					
				</tr>
			{/each}
		{:else}
			<tr>
				<td colspan="5" class="text-center">No existen registros </td>
			</tr>
		{/if}
	</tbody>
</table>
