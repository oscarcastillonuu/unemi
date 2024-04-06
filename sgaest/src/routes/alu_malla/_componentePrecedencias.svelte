<script lang="ts">
	import { onMount } from 'svelte';
	export let aData;
	let predecesoras = [];
	onMount(async () => {
		
		if (aData.predecesoras) {
			predecesoras = aData.predecesoras;
      //console.log(predecesoras);
		}
	});
</script>

<div class="row">
	<div class="col-12">
		<div class="table-responsive">
			<table class="table table-bordered align-middle table-sm">
				<thead class="">
					<tr class="">
						<th scope="col" class="text-center fs-6">Asignaturas</th>
						<th scope="col" class="text-center fs-6">Nivel</th>
					</tr>
				</thead>
				<tbody class="">
					{#each predecesoras as p}
						<tr class="">
							<td class="fs-6">{p.predecesora.asignatura.nombre}</td>
							<td class="fs-6">{p.predecesora.nivelmalla.nombre}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
</div>
