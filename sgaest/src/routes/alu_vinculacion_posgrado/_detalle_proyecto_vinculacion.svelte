<script lang="ts">
	import { onMount } from 'svelte';

	export let aData;
	let participanteproyectov = {};
	let proyectovinculacion = {};
	let descripcion = '';
	let listdetalleaprobacion = [];


	console.log(aData.participanteproyectov + 'aDATA');
	onMount(async () => {
		console.log(aData);
		participanteproyectov = aData.participanteproyectov;
		proyectovinculacion = aData.participanteproyectov.proyectovinculacion;
		descripcion = proyectovinculacion.descripcion;
		listdetalleaprobacion = aData.detalle_aprobacion;

	});


	/* Ver mas, ver menos */
	let mycollapsemore = (valor, id) => {
		let spancompleted = document.getElementById(id);
		let btnvermas = document.getElementById(`btn_vermas_${id}`);
		let btnvermenos = document.getElementById(`btn_vermenos_${id}`);
		if (valor) {
			spancompleted.style.display = '';
			btnvermas.style.display = 'none';
			btnvermenos.style.display = '';
		} else {
			spancompleted.style.display = 'none';
			btnvermas.style.display = '';
			btnvermenos.style.display = 'none';
		}
	};

</script>

<div>
	<!-- <label><h5><b>Total:</b> {total}</h5></label> -->
</div>
<div class="card-body">
	<div class="table-responsive">

		<table class="table mb-4 table-bordered" id="rwd-table-manual">
			<tbody>
				<tr>
					<th scope="col" class="border-top-0  align-middle"  style="width: 10rem;">Título:</th>
					<td class="border-top-0 align-middle fs-6" style="width: 90rem;" > {proyectovinculacion.titulo} </td>
				</tr>
				<tr>
					<th scope="col" class="border-top-0  align-middle"  style="width: 10rem;">Descripción:</th>
					<td class="border-top-0  align-middle fs-6" style="width: 90rem;">

						<span>
							{descripcion.slice(0, 150)}</span>
						<span id={participanteproyectov.id} style="display: none;">
							{descripcion.slice(150, descripcion.length)}</span>

						{#if descripcion.length > 150}
							<a id="btn_vermas_{participanteproyectov.id}" 
							href="javascript:void(0)"
							on:click={() => mycollapsemore(true, participanteproyectov.id)}
							class="badge"
							 style="border:1px solid rgba(157, 157, 157, 0.55);
							border-radius:10px;color:black;font-weight: normal;background-color:
							 #fff;cursor:pointer;">...Ver más</a>												
						{/if}	
						<a id="btn_vermenos_{participanteproyectov.id}" 
							href="javascript:void(0)"
							on:click={() => mycollapsemore(false,participanteproyectov.id)}
							class="badge"
							style="display: none; border:1px solid rgba(157, 157, 157, 0.55);
							border-radius:10px;color:black;font-weight: normal;background-color:
							 #fff;cursor:pointer;">...Ver menos</a>
					
					</td>
				</tr>
			</tbody>
		</table>

		<table class="table mb-0 table-hover" id="rwd-table-manual">
			<thead class="table-light">
				<tr>
					<th scope="col" class="border-top-0 text-center align-middle" style="width: 10%;">Observación</th>
					<th scope="col" class="border-top-0 text-center align-middle" style="width: 10%;">Estado</th>
					<th scope="col" class="border-top-0 text-center align-middle" style="width: 10%;">Fecha/Hora</th>
					<th scope="col" class="border-top-0 text-center align-middle" style="width: 70%;">Aprobador/Solicitante</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td class="border-top-0 text-center align-middle fs-6"> NINGUNA </td>
					<td class="border-top-0 text-center align-middle">
					
						<!-- {#if proyectovinculacion["estadoaprobacion"] === 1}
							<span class="badge bg-success">APROBADO</span>
						{/if}
						{#if proyectovinculacion["estadoaprobacion"] === 2}
							<span class="badge bg-secondary"> PENDIENTE</span>
						{/if}
						{#if proyectovinculacion["estadoaprobacion"] === 3}
							<span class="badge bg-danger"> RECHAZADO</span>
						{/if} -->

						<span class="badge bg-secondary"> PENDIENTE</span>

					</td>
					<td class="border-top-0 text-center align-middle fs-6">
						 <i class="bi bi-calendar3"/> {participanteproyectov['fecha']}<br />
						<i class="bi bi-clock"/> {participanteproyectov['hora']}
					</td>
					<td class="border-top-0 text-center align-middle">
						{participanteproyectov['nombre']}
					</td>
				</tr>

				{#each listdetalleaprobacion as detalleaprobacion, i}
					<tr>
						<td class="border-top-0 text-center align-middle fs-6"> 
							{detalleaprobacion['observacion']} 
						</td>
						<td class="border-top-0 text-center align-middle">
							{#if detalleaprobacion['estadoaprobacion'] === 1}
								<span class="badge bg-success">APROBADO</span>
							{/if}
							{#if detalleaprobacion['estadoaprobacion'] === 2}
								<span class="badge bg-secondary"> PENDIENTE</span>
							{/if}
							{#if detalleaprobacion['estadoaprobacion'] === 3}
								<span class="badge bg-danger"> RECHAZADO</span>
							{/if}
						</td>
						<td class="border-top text-center align-middle fs-6">
							<i class="bi bi-calendar3"/> {detalleaprobacion['fecha']}<br />
							<i class="bi bi-clock"/> {detalleaprobacion['hora']}
						</td>
						<td class="border-top-0 text-center align-middle fs-6">
							{detalleaprobacion['persona']}
						</td>
					</tr>
				{/each}

			</tbody>
		</table>
	</div>
</div>
