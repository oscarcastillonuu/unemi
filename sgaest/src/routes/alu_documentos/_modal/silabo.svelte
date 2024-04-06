<script lang="ts">
import { disableScrollHandling } from '$app/navigation';
import { variables } from '$lib/utils/constants';

	import { onMount } from 'svelte';
	import { loading } from '$lib/store/loadingStore';
	import { addNotification } from '$lib/store/notificationStore';
	import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';

	export let aData;
	let silabos = [];
	let horassegundos = 0; 
	let aprobar = 0;
	let rechazar = 0;
	let pendiente = 0;
	//console.log(aData);
	onMount(async () => {
		silabos = aData.silabos;
		horassegundos = aData.horassegundos;
		aprobar = aData.aprobar;
		rechazar = aData.rechazar;
		pendiente = aData.pendiente;

	});
	const GenerarSilabo = async (idm, idp) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/aulavirtual', {
			action: 'mostrarsilabodigital',
			idm: idm,
			idp: idp
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
	<div class="table-responsive">
		<table class="table table-sm mb-0 text-nowrap table-border table-hover">
			<thead class="table-light">
				<tr>

					<th   style="width: 15px">N.V</th>
					<th scope="col" class="border-top-0 text-center align-middle "  style="width: 500px">Silabo</th>
					<th scope="col" class="border-top-0 text-center align-middle "  style="width: 80px">Sílabo</th>
					<th scope="col" class="border-top-0 text-center align-middle "   style="width: 80px">Estado de Aprobación</th>

				</tr>
			</thead>
			<tbody>
				{#if silabos.length > 0}
					{#each silabos as sil, i}
						<tr>
							<td  style="width: 15px">
								{i+1}
							</td>
							<td class="fs-6 align-middle border-top-0 text-center text-wrap"
								style="width: 15rem;">
								{sil.materia.asignaturamalla.display} - [P  {sil.materia.paralelo}]   - {sil.materia.nivel.paralelo} - {sil.fecha_creacion} <br>
								<span style="color: #0e90d2"><strong>Tiene
									{#if sil.estado_planificacion_clases >= 100 } 
									100% Planificado
									{:else}{ sil.estado_planificacion_clases }% Planificado 
									{#if sil.estado_planificacion_clases > 80 } Temas pendientes de planificar{/if}
									{/if} 
								  </strong></span>
								
								
							</td>
							<td class="fs-6 align-middle border-top-0 text-wrap text-center"
								style="width: 15rem;" >
								{#if sil.codigoqr}
								<a target="_blank"
									class="btn btn-success btn-sm mb-2"
									href="{variables.BASE_API}/media/qrcode/silabodocente/qr_silabo_{sil.id}.pdf?v={horassegundos}"
									><i class="fa fa-qrcode" /> Sílabo digital QR</a>													
								{:else}
									{#if sil.materia.tiene_silabo_aprobado }
									<!-- <a class="btn btn-mini"> <i class="bi bi-bookmarks-fill"></i> Bibliografía </a> -->
									<button class='btn btn-secondary btn-sm mb-2' on:click={() => GenerarSilabo(sil.materia.id, sil.materia.profesor.id)}> Generar Silabo</button>
									{/if}
								
								{/if}
							</td>
							<td class="fs-6 align-middle border-top-0 text-center">
								{#if sil.estado_aprobacion}
									{#if sil.estado_aprobacion.estadoaprobacion == aprobar}
										<span class="badge bg-success"> APROBADO </span>
									{:else}
										{#if sil.estado_aprobacion.estadoaprobacion == rechazar}
											<span class="badge bg-danger"> RECHAZADO </span>
										{:else}
											<span class="badge bg-warning"> PENDIENTE </span>

										{/if}

									{/if}

								{:else}
									<span class="badge bg-warning"> PENDIENTE </span>

								{/if}

							</td>

						</tr>
					{/each}
				{:else}
					<tr>
						<td colspan="8" class="text-center">NO EXISTE SILABOS DISPONIBLES</td>
					</tr>
				{/if}
			</tbody>
		</table>
	</div>
</div>
