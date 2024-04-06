<script lang="ts">
	import { onMount } from 'svelte';
	import { converToDecimal } from '$lib/formats/formatDecimal';

	export let aData;
	let historicos = [];
	let record = '';
	onMount(async () => {
		if (aData.eRecordAcademico) {
			record = aData.eRecordAcademico;
			historicos = aData.eHistoricoRecord;
		}
	});
</script>

<div class="row">
	<div class="col-12 text-center">
		<h3 class="">{record.display}</h3>
	</div>
</div>
<div class="card-body">
	<div class="table-responsive">
		<table class="table table-sm mb-0 text-nowrap table-border table-hover">
			<thead class="table-light">
				<tr>
					<th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;">Asignatura</th
					>
					<th scope="col" class="border-top-0 text-center align-middle " style="width: 15rem;">Cred</th>
					<th scope="col" class="border-top-0 text-center align-middle " style="width: 15rem;">Hrs.</th>
					<th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;">Profesor/Observaciones</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Nota</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Asist.(%)</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Fecha</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Suf.</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Sin Asist.</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Hom.</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Cred.</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Prom.</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Estado</th>

				</tr>
			</thead>
			<tbody>
				{#if historicos.length > 0}
					{#each historicos as historico}
						<tr>
							<td class="fs-6 align-middle border-top-0 text-wrap" style="width: 22rem;">
								{historico.asignatura.display }
								<br>
								{#if historico.nivel_asignatura.display}
								<span class="badge bg-info"> {historico.nivel_asignatura.display }
								</span>
								{/if}
								


							</td>
							<td class="fs-6 align-middle border-top-0 text-center text-wrap"
								style="width: 15rem;">
								{converToDecimal(historico.creditos, 4)}

							</td>
							<td class="fs-6 align-middle border-top-0 text-wrap text-center"
								style="width: 15rem;" >
								{historico.horas}
							</td> 
							<td class="fs-6 align-middle border-top-0 text-center text-wrap" style="width: 22rem;" >
								{#if historico.materiaregular }
									{historico.materiaregular.nivel.periodo.nombre} <br>
									{historico.materiaregular.profesor_principal.display} 
								{:else if historico.materiacurso}
										{historico.materiacurso.profesor.display} 
								{/if}
								{#if historico.observaciones}
								<br> <strong>Observaciones:</strong> {historico.observaciones}
								{/if}


							</td>
					
							<td class="fs-6 align-middle border-top-0 text-center">
								{converToDecimal(historico.nota, 2)}
							</td>
							<td class="fs-6 align-middle border-top-0 text-center">
								{historico.asistencia}%
							</td>
							<td class="fs-6 align-middle border-top-0 text-center">
								{historico.fecha}
							</td>
							<td class="fs-6 align-middle border-top-0 text-center">
								{#if historico.suficiencia}
									<span class="badge bg-success"> <i class="bi bi-check-circle-fill"></i> </span>
								{/if}
							</td>
							<td class="fs-6 align-middle border-top-0 text-center">
								{#if historico.sinasistencia}
									<span class="badge bg-success"> <i class="bi bi-check-circle-fill"></i> </span>
								{/if}
							</td>
							<td class="fs-6 align-middle border-top-0 text-center">
								{#if historico.homologada || historico.convalidacion }
									{#if historico.datos_homologacion && historico.datos_homologacion.archivo }
									<a href="{historico.datos_homologacion.archivo.url}" class="btn btn-secondary btn-sm mb-2"
															target="_blank"><span class="fe fe-link" /> </a>
									{:else}
									<span class="badge bg-success"> <i class="bi bi-check-circle-fill"></i> </span>

									{/if}
									
								{/if}
							</td>
							<td class="fs-6 align-middle border-top-0 text-center">
								{#if historico.valida}
									<span class="badge bg-success"> <i class="bi bi-check-circle-fill"></i> </span>
								{/if}
							</td>
							<td class="fs-6 align-middle border-top-0 text-center">
								{#if historico.validapromedio}
									<span class="badge bg-success"> <i class="bi bi-check-circle-fill"></i> </span>
								{/if}
							</td>
							<td class="fs-6 align-middle border-top-0 text-center">
								{#if historico.noaplica}
									<span class="badge bg-warning"> NO APLICA </span>
								{:else}
									{#if historico.aprobada}
										<span class="badge bg-success"> APROBADA </span>
									{:else}
										<span class="badge bg-danger"> REPROBADA </span>

									{/if}

								{/if}
							</td>
							
							


						</tr>
					{/each}
				{:else}
					<tr>
						<td colspan="14" class="text-center">NO EXISTEN DETALLES HISTORICOS DE RECORD ACADEMICO</td>
					</tr>
				{/if}
			</tbody>
		</table>
	</div>
</div>