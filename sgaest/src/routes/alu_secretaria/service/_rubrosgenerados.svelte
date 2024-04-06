<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { createEventDispatcher, onDestroy } from 'svelte';

	const dispatch = createEventDispatcher();

	export let aData;
	let eRubros = [];

	onMount(async () => {
		if (aData.eRubros) {
			eRubros = aData.eRubros;
		}
		console.log(eRubros);
	});
</script>

<div class="card-body">
	<div class="table-responsive">
		<table class="table mb-0 table-hover" id="rwd-table-manual">
			<thead class="table-light">
				<tr>
					<th scope="col" class="border-top-0 text-center align-middle">Código</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Nombre</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Fecha vence</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Valor</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Abono</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Saldo</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Vencido</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Cancelado</th>
				</tr>
			</thead>
			<tbody>
				{#if eRubros.length > 0}
					{#each eRubros as eRubro}
						<tr>
							<td class="text-wrap fs-6" style="text-align: center; vertical-align: middle">
								{eRubro.id}
							</td>
							<td class="text-wrap fs-6" style="text-align: center; vertical-align: middle" width="25%">
								{eRubro.nombre}
							</td>
							<td class="text-wrap fs-6" style="text-align: center; vertical-align: middle">
								{eRubro.fechavence}
							</td>
							<td class="text-wrap fs-6" style="text-align: center; vertical-align: middle">
								$ {eRubro.valortotal}.00
							</td>
							<td class="text-wrap fs-6" style="text-align: center; vertical-align: middle">
								$ {eRubro.total_pagado}.00
							</td>
							<td class="text-wrap fs-6" style="text-align: center; vertical-align: middle">
								$ {eRubro.total_adeudado}.00
							</td>
							<td class="text-wrap fs-6" style="text-align: center; vertical-align: middle">
								{#if eRubro.vencido == 'SI'}
									<span class="badge rounded-pill bg-danger">{eRubro.vencido}</span>
								{:else}
									<span class="badge rounded-pill bg-success">{eRubro.vencido}</span>
								{/if}
							</td>
							<td class="text-wrap fs-6" style="text-align: center; vertical-align: middle">
								{#if eRubro.cancelado == 'SI'}
									<span class="badge rounded-pill bg-success">{eRubro.cancelado}</span>
								{:else}
									<span class="badge rounded-pill bg-danger">{eRubro.cancelado}</span>
								{/if}
							</td>
						</tr>
					{/each}
				{:else}
					<tr>
						<td class="text-wrap fs-6" colspan="8" style="text-align: center; vertical-align: middle">
							NO HAY REGISTRO DE VALORES GENERADOS
						</td>
					</tr>
				{/if}
			</tbody>
		</table>
	</div>
</div>
