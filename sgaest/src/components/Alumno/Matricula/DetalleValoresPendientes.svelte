<script lang="ts">
	import { onMount } from 'svelte';
	export let aData;
	let eRubros = [];
	let tieneVencidos = false;
	let valorPendiente = 0;
	let valorAbono = 0;
	let valorTotal = 0;

	onMount(async () => {
		eRubros = aData.eRubros;
		tieneVencidos = aData.tieneVencidos;
		valorPendiente = aData.valorPendiente;
		valorAbono = aData.valorAbono;
		valorTotal = aData.valorTotal;
	});
</script>

<div class="table-responsive scrollbar">
	<table class="table table_primary tabla_responsive  m-0 p-0">
		<thead class="table-light">
			<tr>
				<th scope="col" class="text-center">#</th>
				<th class="text-center">Código Intermatico</th>
				<th class="text-center">Detalle</th>
				<th class="text-center">Cuota</th>
				<!--<th scope="col" class="text-center">Fecha Vencimiento</th>-->
				<th class="text-center">Valor</th>
				<th class="text-center">Total</th>
			</tr>
		</thead>
		<tbody>
			{#if eRubros.length > 0}
				{#each eRubros as eRubro, i}
					<tr class="text-dark">
						<td class="text-center" width="5%">{i + 1}</td>
						<td class="text-center" width="10%"
							><span class="badge bg-success">{eRubro.codigo_intermatico}</span></td
						>
						<td class="fs-6" width="60%">
							{eRubro.nombre}<br />
							<span class="fw-bold text-primary text-muted"
								><b class="text-warning">Fecha Generación:</b> {eRubro.fecha}</span
							>
							<br /><span class="fw-bold text-primary"
								><b class="text-danger">Fecha Vencimiento:</b> {eRubro.fechavence}</span
							>
						</td>
						<td class="text-center" width="5%">{eRubro.cuota}</td>

						<!--<td class="text-center">{eRubro.fechavence}</td>-->
						<td class="text-center" width="10%">$ {eRubro.valortotal}</td>
						<td class="text-end" width="10%">$ {eRubro.saldo}</td>
					</tr>
				{/each}
			{/if}
		</tbody>
		<tfoot>
			<tr class="text-dark ">
				<td colspan="2" class="border-0" />
				<td colspan="3" class="pb-0 text-end border-0">Valor Total:</td>
				<td class="pb-0 text-end border-0">$ {valorTotal}</td>
			</tr>
			<tr class="text-dark">
				<td colspan="2" class="border-0" />
				<td colspan="3" class="py-0 text-end border-0">Valor Abonado:*</td>
				<td class="py-0 text-end border-0">$ {valorAbono}</td>
			</tr>
			<tr class="text-dark">
				<td colspan="2" class="border-0" />
				<td colspan="3" class="border-top py-1 fw-bold text-end fs-3 border-0">PENDIENTE DE PAGO</td
				>
				<td class="border-top py-1 fw-bold text-end border-0"
					><span class="badge bg-{tieneVencidos ? 'danger' : 'warning text-dark'}"
						>$ {valorPendiente}</span
					></td
				>
			</tr>
		</tfoot>
	</table>
</div>
