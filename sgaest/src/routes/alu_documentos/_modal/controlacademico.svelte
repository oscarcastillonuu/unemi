<script lang="ts">
	import { onMount } from 'svelte';
import Automatricula from '../../alu_matricula/_Pregrado/_automatricula.svelte';
	export let aData;
	let preguntas = [];
	let periodo=0;
	let modalidadcarrera=0;
	//console.log(aData);
	onMount(async () => {
		preguntas = aData.preguntas;
		periodo = aData.periodo;
		modalidadcarrera = aData.modalidadcarrera;
	});
</script>

<div class="card-body">
	<div class="table-responsive">
		<table class="table table-sm mb-0 text-nowrap table-border table-hover">
			<thead class="table-light">
				<tr>
					<th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;">Materia/Profesor</th
					>
					<th scope="col" class="border-top-0 text-center align-middle " style="width: 15rem;">Tema</th>
					<th scope="col" class="border-top-0 text-center align-middle " style="width: 15rem;">Pregunta</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Archivo</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Estado</th>
					<!-- <th scope="col" class="border-top-0 text-center align-middle ">Acciones</th> -->

				</tr>
			</thead>
			<tbody>
				{#if preguntas.length > 0}
					{#each preguntas as preg}
						<tr>
							<td class="fs-6 align-middle border-top-0 text-wrap" style="width: 22rem;">
							{#if modalidadcarrera != 3 }
								{preg.profersormateria.materia.nombre_mostrar}

							{:else}
								{#if periodo >= 100 }
								{preg.profersormateria.materia.nombre_mostrar_virtual}
								{:else}
								{preg.profersormateria.materia.nombre_mostrar}
								{/if}
							{/if}
							</td>
							<td class="fs-6 align-middle border-top-0 text-center text-wrap"
								style="width: 15rem;">
								{preg.tema }
							</td>
							<td class="fs-6 align-middle border-top-0 text-wrap text-center"
								style="width: 15rem;" >
								{preg.pregunta }

							</td>
							<td class="fs-6 align-middle border-top-0 text-center">
								{#if preg.archivo}
									<a class='btn btn-secondary btn-sm mb-2' href='{ preg.archivo }' > <i class="bi bi-file-earmark-arrow-down-fill"></i> Descargar</a>
								{:else}
									<span class="badge bg-danger">SIN ARCHIVO</span>

								{/if}
								
							</td>
							<td class="fs-6 align-middle border-top-0 text-center">
								{#if !preg.en_uso}
								<span class="badge bg-warning">SIN RESPUESTA</span>

								{:else}
									{#if preg.estadolecturaalumno}
									<span class="badge bg-success">MENSAJE NUEVO</span>
									{/if}
								{/if}
							</td>
						
							<!-- <td class="fs-6 align-middle border-top-0 text-center">

							</td> -->
						</tr>
					{/each}
				{:else}
					<tr>
						<td colspan="8" class="text-center">NO EXISTEN PREGUNTAS</td>
					</tr>
				{/if}
			</tbody>
		</table>
	</div>
</div>