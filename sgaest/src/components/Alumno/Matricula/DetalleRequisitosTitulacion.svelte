<script lang="ts">
	import { onMount } from 'svelte';
	export let aData;
	let eRequisitos = 0;

	onMount(async () => {
		eRequisitos = aData.eRequisitos;
	});
</script>

<div class="row">
	<div class="col-12">
		<div class="table-responsive mb-12">
			<table class="table mb-0 text-nowrap table-borderless">
				<thead class="table-light">
					<tr>
						<th scope="col" class="text-center" style="width: 80%;">Requisito</th>
						<th scope="col" class="text-center" style="width: 20%;">Cumple</th>
					</tr>
				</thead>
				<tbody>
					{#if eRequisitos.length > 0}
						{#each eRequisitos as eRequisito}
							<tr class="text-dark">
								<td class="">
									<p class="fw-bold fs-5 p-0 m-0">{eRequisito.requisito.nombre}</p>
									{#if !eRequisito.cumple && eRequisito.requisito.mensajenocumple}
										<p class="lh-base fst-italic fs-6 p-0 m-0">
											{eRequisito.requisito.mensajenocumple}
										</p>
									{/if}
								</td>
								<td class="text-center">
									{#if eRequisito.cumple}
										<span class="badge rounded-pill bg-success">SI</span>
									{:else}
										<span class="badge rounded-pill bg-danger">NO</span>
									{/if}
								</td>
							</tr>
						{/each}
					{/if}
				</tbody>
			</table>
		</div>
	</div>
</div>
