<script lang="ts">
	import { onMount } from 'svelte';

	export let aData;
	let carreras = [];
	let ccarreras = [];
	let total;

	console.log(aData + 'aDATA');
	onMount(async () => {
		carreras = aData.carreras;
		total = aData.total;
	});
</script>

<div>
	<label><h5><b>Total:</b> {total}</h5></label>
</div>
<div class="card-body">
	
	<div class="table-responsive">
		<table class="table mb-0 table-hover" id="rwd-table-manual">
			<thead class="table-light">
				<tr>
					<th scope="col" class="border-top-0 text-center align-middle " style="width: 8%">Nº</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Nombre</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Modalidad</th>
				</tr>
			</thead>
			<tbody>
				{#each carreras as carrera, i}

					
                    <tr>
                        <td>
                            
                            <label class="label label-inverse"> {i + 1}</label>
                        </td>
                        <td>
                            {carrera.display}
                        </td>
                        <td>
                            {carrera.modalidad}
                        </td>

						
					

                    </tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>
