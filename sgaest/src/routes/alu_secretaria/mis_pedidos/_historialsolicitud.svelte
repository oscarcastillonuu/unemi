<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { createEventDispatcher, onDestroy } from 'svelte';

	const dispatch = createEventDispatcher();

	export let aData;
	let eHistorial = [];
//	let eHistorial2 = [];
//	let ePagos = [];
//	let eRubro;

	onMount(async () => {
		if (aData.eHistorial) {
			eHistorial = aData.eHistorial;
//			eHistorial2 = aData.eHistorial2;
//			ePagos = aData.ePagos;
//			eRubro = aData.eRubro;
		}
		console.log(eHistorial);
	});
</script>

<div class="card-body">
	<div class="table-responsive">
		<table class="table mb-0 table-hover" id="rwd-table-manual">
			<thead class="table-light">
				<tr>
					<th scope="col" class="border-top-0 text-center align-middle " style="width: 8%">Nº</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Solicitud</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Responsable</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Observacion</th>

					<!--<th scope="col" class="border-top-0 text-center align-middle ">Pagos</th>
 -->
					<th scope="col" class="border-top-0 text-center align-middle ">Fecha </th>
					<th scope="col" class="border-top-0 text-center align-middle ">Estado</th>
				</tr>
			</thead>
			<tbody>
				{#if eHistorial}
					{#each eHistorial as historial, i}
						<tr>
							<td>
								<label class="label label-inverse"> {i + 1}</label>
							</td>
							<td>
								{historial.solicitud.codigo}
							</td>
							<td>
								{historial.responsable.nombre_completo}
							</td>
							<td>
								{historial.observacion}
<!---								{#if eHistorial2}
									{#each eHistorial2 as histo}
										{#if histo.id == historial.id}
											${histo.pago.valortotal}

										{/if}
									{/each}
								{/if}-->
							</td>

							<td>
								{historial.fecha}
								{historial.hora}
							</td>
							<td>
								{historial.estado_display}
							</td>
						</tr>
						
					{/each}
				{:else}
					<tr> SIN HISTORIAL </tr>
				{/if}
			</tbody>
		</table>
	</div>
</div>