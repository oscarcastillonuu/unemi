<script lang="ts">
	import { onMount } from 'svelte';
	import { converToAscii, action_print_ireport } from '$lib/helpers/baseHelper';
	import { variables } from '$lib/utils/constants';
	export let aData;
	let historial = [];
	let tema = '';

	onMount(async () => {
		if (aData.historial && aData.tema) {
			historial = aData.historial;
			tema = aData.tema;
		}
	});
</script>

<table class="table  table-responsive" id="rwd-table-histo">
	<thead class="table-light">
		<tr>
			<th scope="col" class="border-top-0 text-center align-middle" colspan="5"
				><b>Tema:</b> {tema}</th
			>
		</tr>
		<tr>
			<th scope="col" class="border-top-0 text-center align-middle " style="width: 10rem;">Fecha</th
			>
			<th scope="col" class="border-top-0 text-center align-middle " style="width: 15rem;"
				>Persona</th
			>
			<th scope="col" class="border-top-0 text-center align-middle " style="width: 25rem;"
				>Observación</th
			>
			<th scope="col" class="border-top-0 text-center align-middle ">Archivo revisión</th>
			<th scope="col" class="border-top-0 text-center align-middle ">Estado</th>
		</tr>
	</thead>
	<tbody>
		{#if historial.length > 0}
			{#each historial as his}
				<tr>
					<td class="fs-6 align-middle border-top-0 text-wrap nombre" style="width: 22rem;">
						{his.fecha_creacion}
					</td>
					<td
						class="fs-6 align-middle border-top-0 text-center text-wrap autor"
						style="width: 15rem;"
					>
						{his.persona}
					</td>
					<td class="fs-6 align-middle border-top-0 text-wrap text-center" style="width: 15rem;">
						{his.observacion}
					</td>
					<td class="fs-6 align-middle border-top-0 text-center">
						{#if his.archivo}
							<a  class ="btn btn-info btn-xs" target="_blank" href="{variables.BASE_API}{his.archivo}" title="Evidencia">
								<i class="bi bi-download" />
							</a>
						{:else}
							S/N
						{/if}
					</td>
					<td class="fs-6 align-middle border-top-0 text-center">
						{#if his.estado == 1}
							<span class="badge bg-warning">SOLICITADO</span>
						{:else if his.estado == 2}
							<span class="badge bg-success">APROBADO</span>
						{:else}
							<span class="badge bg-danger">RECHAZADO</span>
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
