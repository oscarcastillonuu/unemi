<script lang="ts">
import { disableScrollHandling } from '$app/navigation';
import { variables } from '$lib/utils/constants';

	import { loading } from '$lib/store/loadingStore';
	import { addNotification } from '$lib/store/notificationStore';
	import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';

	import { onMount } from 'svelte';
	export let aData;
	let guia_practica = [];
	let materia = "";
	onMount(async () => {
		guia_practica = aData.guia_practica;
		materia = aData.materia;

	});
	const GenerarArchivoPractica = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/aulavirtual', {
			action: 'practica_indpdf',
			id: id
		});
		loading.setLoading(false, 'Cargando, espere por favor...');
		if (errors.length > 0) {
			addNotification({
				msg: errors[0].error,
				type: 'error'
			});
		} else {
			if (!res.isSuccess) {
				addNotification({
					msg: res.message,
					type: 'error'
				});
			} else {
				open(res.data.file,'_blank')

			}
		}
	};
</script>


<div class="card-body">
	<div class="text-center">
		<b>{materia}</b>
	<br>
	<br>
	</div>
	<div class="table-responsive">
		<table class="table table-sm mb-0 text-nowrap table-border table-hover">
			<thead class="table-light">
				<tr>
					<th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;">Semana</th
					>
					<th scope="col" class="border-top-0 text-center align-middle " style="width: 15rem;">Práctica</th>
					<th scope="col" class="border-top-0 text-center align-middle " style="width: 15rem;">N. práctica</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Estado</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Instrucciones G.P</th>
					<th scope="col" class="border-top-0 text-center align-middle ">Guía Práctica</th>

				</tr>
			</thead>
			<tbody>
				{#if guia_practica.length > 0}
					{#each guia_practica as guia}
						<tr>
							<td class="fs-6 align-middle border-top-0 text-wrap" style="width: 22rem;">
									<strong>Nº Semana: </strong>{guia.silabosemanal.cronograma_silabo_n_semana }<br>
									<strong>Fecha inicio: </strong>{guia.silabosemanal.cronograma_silabo_semana.fechainicio }<br>
									<strong>Fecha fin: </strong>{guia.silabosemanal.cronograma_silabo_semana.fechafin }<br>

							</td>
							<td class="fs-6 align-middle border-top-0 text-center text-wrap"
								style="width: 15rem;">
								{guia.temapractica.display }
							</td>
							<td class="fs-6 align-middle border-top-0 text-wrap text-center"
								style="width: 15rem;" >
								{guia.numeropractica }

							</td>
							<td class="fs-6 align-middle border-top-0 text-center">
								{#if guia.id_estado_guiapractica == 1}
								<span class="badge bg-warning">{guia.nombre_estado_guiapractica}</span>
								{:else}
									{#if guia.id_estado_guiapractica == 2}
									<span class="badge bg-warning">{guia.nombre_estado_guiapractica}</span>

									{:else}
										{#if guia.id_estado_guiapractica == 3}
										<span class="badge bg-success">{guia.nombre_estado_guiapractica}</span>

										{:else}
										<span class="badge bg-danger">{guia.nombre_estado_guiapractica}</span>
											
										{/if}										
									{/if}

								{/if}
							</td>
							<td class="fs-6 align-middle border-top-0 text-center">
								{#if guia.mi_instruccion.archivo }<a href='{  guia.mi_instruccion.download_link }' 
								target="_blank" title="Descargar Archivo de Instrucciones" class='btn btn-secondary btn-sm mb-2'>
								<i class="bi bi-file-earmark-arrow-down-fill"></i> Descargar</a> {/if}
							</td>
						
							<td class="fs-6 align-middle border-top-0 text-center">
								<button class='btn btn-secondary btn-sm mb-2'  on:click={() => GenerarArchivoPractica(guia.id)}> <i class="bi bi-file-earmark-arrow-down-fill"></i> Descargar</button>
							</td>
						</tr>
					{/each}
				{:else}
					<tr>
						<td colspan="8" class="text-center">NO EXISTEN GUÍAS DE PRÁCTICAS REGISTRADAS</td>
					</tr>
				{/if}
			</tbody>
		</table>
	</div>
</div>