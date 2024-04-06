<script lang="ts">
	import { onMount } from 'svelte';
	import { converToAscii, action_print_ireport } from '$lib/helpers/baseHelper';

	export let aData;
	let libros = [];
			//console.log(aData);
	onMount(async () => {
		libros = aData.libros;

	});
	const searchCitas = (e) => {
		//console.log(e);
		
		const tableRowsInterno = document.querySelectorAll('#rwd-table-biblio tbody tr');
		for (let i = 0; i < tableRowsInterno.length; i++) {
			const rowInterno = tableRowsInterno[i];
			const nombre_interno = rowInterno.querySelector('.nombre');
			if (
				converToAscii(nombre_interno.innerText.toLowerCase()).indexOf(
					converToAscii(e.toLowerCase())
				) === -1
			) {
				rowInterno.style.display = 'none';
			} else {
				rowInterno.style.display = '';
			}
		}
		
		
	};

</script>


<div class="card-body">
	<input
						type="search"
						class="form-control"
						placeholder="Buscar libro"
						style="width: 100% !important;"
						on:keyup={({ target: { value } }) => searchCitas(value)}
					/>
	<div class="table-responsive">
		<table class="table table-sm mb-0 text-nowrap table-border table-hover" id = "rwd-table-biblio" >
			<thead class="table-light">
				<tr>
					<th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;">Nombre del libro</th
					>
					<th scope="col" class="border-top-0 text-center align-middle " style="width: 15rem;">Autor</th>
					<th scope="col" class="border-top-0 text-center align-middle " style="width: 15rem;">Año publicación</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Ubicación en biblioteca</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Cant.</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Visitas</th>

				</tr>
			</thead>
			<tbody>
				{#if libros.length > 0}
					{#each libros as lib}
						<tr>
							<td class="fs-6 align-middle border-top-0 text-wrap nombre" style="width: 22rem;">
								{lib.nombre}
								<br>
								{#if lib.ciudad}
									<b>Ciudad: </b>{lib.ciudad}<br>
								{/if}
								{#if lib.editorial}
									<b>Editorial: </b>{lib.editorial}<br>
								{/if}

							</td>
							<td class="fs-6 align-middle border-top-0 text-center text-wrap autor"
								style="width: 15rem;">
								{lib.autor}
							</td>
							<td class="fs-6 align-middle border-top-0 text-wrap text-center"
								style="width: 15rem;" >
								{lib.aniopublicacion}
							</td>
							<td class="fs-6 align-middle border-top-0 text-center">
								{#if lib.carrera }
									{lib.carrera.mi_coordinacion} <br>
									{lib.carrera.nombre}<br>
								{/if}
								{#if lib.hilera}
								<b>Hilera: </b>{lib.hilera}
								{/if}

							</td>
							<td class="fs-6 align-middle border-top-0 text-center">
								{lib.cantidad}
							</td>
						
							<td class="fs-6 align-middle border-top-0 text-center">
									<span class="badge bg-warning">{lib.visitas}</span>
							</td>
						</tr>
					{/each}
				{:else}
					<tr>
						<td colspan="8" class="text-center">NO EXISTE MATERIAS DISPONIBLES</td>
					</tr>
				{/if}
			</tbody>
		</table>
	</div>
</div>